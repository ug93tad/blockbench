//
//  ycsbc.cc
//  YCSB-C
//
//  Created by Jinglei Ren on 12/19/14.
//  Copyright (c) 2014 Jinglei Ren <jinglei@ren.systems>.
//

#include <cstring>
#include <string>
#include <iostream>
#include <vector>
#include <future>
#include <atomic>
#include <sstream>
#include "core/utils.h"
#include "core/timer.h"
#include "core/client.h"
#include "core/core_workload.h"
#include "core/statistic.h"
#include "db/db_factory.h"
#include "db/ethereum_kvdb.h"
#include "db/hyperledger_kvdb.h"
#include "db/parity_kvdb.h"
using namespace std;
using ycsbc::EthereumKVDB;
using ycsbc::HyperLedgerKVDB;
using ycsbc::ParityKVDB;
const unsigned int BLOCK_POLLING_INTERVAL = 2;
const unsigned int CONFIRM_BLOCK_LENGTH = 5;
const unsigned int HL_CONFIRM_BLOCK_LENGTH = 1;
const unsigned int PARITY_CONFIRM_BLOCK_LENGTH = 1;

int txrate = 10; 
std::atomic<unsigned long long> latency(0);
std::atomic<unsigned long long> latency_interval(0);
std::atomic<unsigned long long> ops(0);

std::unordered_map<string, double> pendingtx;

void UsageMessage(const char *command);
bool StrStartWith(const char *str, const char *pre);
string ParseCommandLine(int argc, const char *argv[], utils::Properties &props);

// locking the pendingtx queue
SpinLock spinlock_, txlock_;

utils::Timer<double> stat_timer;

int DelegateClient(ycsbc::DB *db, ycsbc::CoreWorkload *wl, Statistic *stat,
                   const int num_ops, bool is_loading) {
  db->Init();
  ycsbc::Client client(*db, *wl);
  int oks = 0;
  double tx_sleep_time = 1.0/txrate; // how long to sleep between sending txs
  for (int i = 0; i < num_ops; ++i) {
    if (is_loading) {
      oks += client.DoInsert();
      //utils::sleep(0.1); 
      utils::sleep(tx_sleep_time); 
    } else {
      //utils::Timer<double> timer;
      //timer.Start();
      oks += client.DoTransaction();
      utils::sleep(tx_sleep_time);
      /*
      double duration = timer.End();
      unsigned long long accummulated_ops = ++ops;
      if (accummulated_ops % stat->GetInterval() == 0 && accummulated_ops) {
        spinlock_.lock();
        double time_interval = stat_timer.Toc();
        stringstream stm;
        stm << "Avg latency from ";
        stm << accummulated_ops - stat->GetInterval() << "-th op to ";
        stm << accummulated_ops << "-th op is "
            << latency_interval / 1000000.0 / stat->GetInterval() << " sec\n";

        stm << "Avg Throughput (KTPS) is "
            << stat->GetInterval() / 1000.0 / time_interval << "\n";

        stat->Send(stm.str());
        latency_interval.store(0);
        spinlock_.unlock();
      }
      unsigned long long l =
          static_cast<unsigned long long>(duration * 1000000.0);
      latency.fetch_add(l);
      latency_interval.fetch_add(l);
      */
    }
  }
  db->Close();
  return oks;
}

// wakeup every interval second to poll, for max_running_time in total
// when first started, the block height is start_block_height
int StatusThread(string dbname, ycsbc::DB *db, double interval,
                 double max_running_time, int start_block_height) {
  int cur_block_height = start_block_height;
  EthereumKVDB *dbHandler_eth;
  HyperLedgerKVDB *dbHandler_hl;
  ParityKVDB *dbHandler_parity;
  if (dbname == "ethereum")
    dbHandler_eth = static_cast<EthereumKVDB *>(db);
  else if (dbname == "parity")
    dbHandler_parity = static_cast<ParityKVDB *>(db);
  else
    dbHandler_hl = static_cast<HyperLedgerKVDB *>(db);

  long start_time;
  long end_time;
  int txcount = 0;
  long latency;
  int confirm_duration = 1;
  if (dbname == "ethereum")
    confirm_duration = CONFIRM_BLOCK_LENGTH;
  else if (dbname == "parity")
    confirm_duration = PARITY_CONFIRM_BLOCK_LENGTH;
  else
    confirm_duration = HL_CONFIRM_BLOCK_LENGTH;

  while (true) {
    start_time = utils::time_now();
    int tip = 0;
    if (dbname == "ethereum")
      tip = dbHandler_eth->get_tip_block_number();
    else if (dbname == "parity")
      tip = dbHandler_parity->get_tip_block_number();
    else
      tip = dbHandler_hl->get_tip_block_number();
    cout << "current tip = " << tip << endl;
    if (tip == -1)  // fail
      utils::sleep(interval);
    while (cur_block_height + confirm_duration <= tip) {
      vector<string> txs;
      if (dbname == "ethereum")
        txs = dbHandler_eth->poll_tx(cur_block_height);
      else if (dbname == "parity")
        txs = dbHandler_parity->poll_tx(cur_block_height);
      else
        txs = dbHandler_hl->poll_tx(cur_block_height);

      cout << "polled block " << cur_block_height << " : " << txs.size()
           << " txs " << endl;
      cur_block_height++;
      long block_time = utils::time_now();
      // cout << "polling block " << cur_block_height<< " #txs = " << txs.size()
      // << endl;
      txlock_.lock();
      for (string tmp : txs) {
        string s = (dbname == "ethereum" || dbname == "parity")
                       ? tmp.substr(1, tmp.length() - 2)  // get rid of ""
                       : tmp;
        // cout << "Checking tx " << s << endl;
        if (pendingtx.find(s) != pendingtx.end()) {  //
          txcount++;
          latency += (block_time - pendingtx[s]);
          // then remove
          pendingtx.erase(s);
        }
      }
      txlock_.unlock();
    }
    cout << "In the last " << interval << "s, tx count = " << txcount
         << " latency = " << latency / 1000000000.0
         << " outstanding request = " << pendingtx.size() << endl;
    txcount = 0;
    latency = 0;

    end_time = utils::time_now();

    // cout << "Time elapsed now " << (end_time-start_time) << endl;
    // cout << "Sleeping for " << interval-(end_time-start_time) << endl;
    // 2. Get all tx from cur_block_height until tip-CONFIRM_BLOCK_LENGTH
    // 3. Process the tx, update the stats
    // 4. Sleep for INTERVAL - (time taken to do 1-3)

    // sleep in nanosecond
    utils::sleep(interval - (end_time - start_time) / 1000000000.0);
    // std::this_thread::sleep_for(std::chrono::seconds(5));
  }
}

int main(const int argc, const char *argv[]) {
  utils::Properties props;
  string file_name = ParseCommandLine(argc, argv, props);

  ycsbc::DB *db = ycsbc::DBFactory::CreateDB(props);
  if (!db) {
    cout << "Unknown database name " << props["dbname"] << endl;
    exit(0);
  }

  EthereumKVDB *dbhandler_eth;
  HyperLedgerKVDB *dbhandler_hl;
  ParityKVDB* dbhandler_parity;
  int current_tip = 0;
  if (props["dbname"] == "ethereum") {
    dbhandler_eth = static_cast<EthereumKVDB *>(db);
    dbhandler_eth->Init(&pendingtx, &txlock_);
    current_tip = dbhandler_eth->get_tip_block_number();
  } else if (props["dbname"] == "parity") {
    dbhandler_parity = static_cast<ParityKVDB *>(db);
    dbhandler_parity->Init(&pendingtx, &txlock_);
    current_tip = dbhandler_parity->get_tip_block_number();
  } else if (props["dbname"] == "hyperledger") {
    dbhandler_hl = static_cast<HyperLedgerKVDB *>(db);
    dbhandler_hl->Init(&pendingtx, &txlock_);
    current_tip = dbhandler_hl->get_tip_block_number();
  }

  cout << "Current TIP = " << current_tip << endl;
  ycsbc::CoreWorkload wl;
  wl.Init(props);

  const int num_threads = stoi(props.GetProperty("threadcount", "1"));

  Statistic *stat = Statistic::GetInstance(
      props["stat_output"], 100);  // stoi(props["ops_interval"]));

  utils::Timer<double> stat_timer;

  // Loads data
  vector<future<int>> actual_ops;
  int total_ops = stoi(props[ycsbc::CoreWorkload::RECORD_COUNT_PROPERTY]);
  for (int i = 0; i < num_threads; ++i) {
    actual_ops.emplace_back(async(launch::async, DelegateClient, db, &wl, stat,
          total_ops / num_threads, true));
  }

  // const int poll_interval = stoi(props.GetProperty("poll_interval"));
  const int max_running_time = 10000;


  auto status = async(launch::async, StatusThread, props["dbname"],
      db, BLOCK_POLLING_INTERVAL, max_running_time,
      current_tip);

  int sum = 0;
  for (auto &n : actual_ops) {
    assert(n.valid());
    sum += n.get();
  }
  cerr << "Done loading records:\t" << sum << endl;
  utils::sleep(10);
  // Peforms transactions
  actual_ops.clear();
  total_ops = stoi(props[ycsbc::CoreWorkload::OPERATION_COUNT_PROPERTY]);
  for (int i = 0; i < num_threads; ++i) {
    actual_ops.emplace_back(async(launch::async, DelegateClient, db, &wl,
          stat,
          total_ops / num_threads, false));
  }
  sum = 0;
  for (auto &n : actual_ops) {
    assert(n.valid());
    sum += n.get();
  }
  cerr << "Done issuing op requests" << endl;
}

string ParseCommandLine(int argc, const char *argv[],
                        utils::Properties &props) {
  int argindex = 1;
  string filename;
  while (argindex < argc && StrStartWith(argv[argindex], "-")) {
    if (strcmp(argv[argindex], "-threads") == 0) {
      argindex++;
      if (argindex >= argc) {
        UsageMessage(argv[0]);
        exit(0);
      }
      props.SetProperty("threadcount", argv[argindex]);
      argindex++;
    } else if (strcmp(argv[argindex], "-ops") == 0) {
      argindex++;
      if (argindex >= argc) {
        UsageMessage(argv[0]);
        exit(0);
      }
      props.SetProperty("ops_interval", argv[argindex]);
      argindex++;
    } else if (strcmp(argv[argindex], "-stat") == 0) {
      argindex++;
      if (argindex >= argc) {
        UsageMessage(argv[0]);
        exit(0);
      }
      props.SetProperty("stat_output", argv[argindex]);
      argindex++;
    } else if (strcmp(argv[argindex], "-db") == 0) {
      argindex++;
      if (argindex >= argc) {
        UsageMessage(argv[0]);
        exit(0);
      }
      props.SetProperty("dbname", argv[argindex]);
      argindex++;
    } else if (strcmp(argv[argindex], "-host") == 0) {
      argindex++;
      if (argindex >= argc) {
        UsageMessage(argv[0]);
        exit(0);
      }
      props.SetProperty("host", argv[argindex]);
      argindex++;
    } else if (strcmp(argv[argindex], "-port") == 0) {
      argindex++;
      if (argindex >= argc) {
        UsageMessage(argv[0]);
        exit(0);
      }
      props.SetProperty("port", argv[argindex]);
      argindex++;
    } else if (strcmp(argv[argindex], "-slaves") == 0) {
      argindex++;
      if (argindex >= argc) {
        UsageMessage(argv[0]);
        exit(0);
      }
      props.SetProperty("slaves", argv[argindex]);
      argindex++;
    } else if (strcmp(argv[argindex], "-retry") == 0) {
      argindex++;
      if (argindex >= argc) {
        UsageMessage(argv[0]);
        exit(0);
      }
      props.SetProperty("retry", argv[argindex]);
      argindex++;
    } else if (strcmp(argv[argindex], "-retry_time_interval") == 0) {
      argindex++;
      if (argindex >= argc) {
        UsageMessage(argv[0]);
        exit(0);
      }
      props.SetProperty("time_interval", argv[argindex]);
      argindex++;
    } else if (strcmp(argv[argindex], "-minimum_depth") == 0) {
      argindex++;
      if (argindex >= argc) {
        UsageMessage(argv[0]);
        exit(0);
      }
      props.SetProperty("minimum_depth", argv[argindex]);
      argindex++;
    } else if (strcmp(argv[argindex], "-endpoint") == 0) {
      argindex++;
      if (argindex >= argc) {
        UsageMessage(argv[0]);
        exit(0);
      }
      props.SetProperty("endpoint", argv[argindex]);
      argindex++;
    }
    else if (strcmp(argv[argindex], "-txrate")==0){
      argindex++;
      txrate = atoi(argv[argindex]);
      argindex++; 
    }
    else if (strcmp(argv[argindex], "-P") == 0) {
      argindex++;
      if (argindex >= argc) {
        UsageMessage(argv[0]);
        exit(0);
      }
      filename.assign(argv[argindex]);
      ifstream input(argv[argindex]);
      try {
        props.Load(input);
      } catch (const string &message) {
        cout << message << endl;
        exit(0);
      }
      input.close();
      argindex++;
    } else if (strcmp(argv[argindex], "-txrate")==0){
      argindex++; 
      txrate = atoi(argv[argindex]);
      argindex++; 
    }
    else {
      cout << "Unknown option '" << argv[argindex] << "'" << endl;
      exit(0);
    }
  }

  if (argindex == 1 || argindex != argc) {
    UsageMessage(argv[0]);
    exit(0);
  }

  return filename;
}

void UsageMessage(const char *command) {
  cout << "Usage: " << command << " [options]" << endl;
  cout << "Options:" << endl;
  cout << "  -threads n: execute using n threads (default: 1)" << endl;
  cout << "  -ops ops_interval: per ops_interval operations we will do a "
          "statistic output "
          "to file" << endl;
  cout << "  -stat statistic_output_file: per ops_interval operations we will "
          "do a statistic output "
          "to THIS file" << endl;
  cout << "  -db dbname: specify the name of the DB to use (default: basic)"
       << endl;
  cout << "  -P propertyfile: load properties from the given file. Multiple "
          "files can" << endl;
  cout << "                   be specified, and will be processed in the order "
          "specified" << endl;
}

inline bool StrStartWith(const char *str, const char *pre) {
  return strncmp(str, pre, strlen(pre)) == 0;
}
