#ifndef YCSB_C_HYPERLEDGER_KV_DB_H_
#define YCSB_C_HYPERLEDGER_KV_DB_H_

#include "core/db.h"

#include <iostream>
#include <string>
#include <atomic>
#include "core/properties.h"
#include <unordered_map>
#include <core/timer.h>
#include <core/utils.h>

using std::cout;
using std::endl;
using std::string;
using std::vector;
using std::unordered_map; 
using std::atomic;
namespace ycsbc {

class HyperLedgerKVDB : public DB {
 public:
  HyperLedgerKVDB(const string &endpoint);

  void Init(unordered_map<string, double> *pendingtx, SpinLock *lock){
    pendingtx_ = pendingtx;
    txlock_ = lock; 
  }
  int Read(const string &table, const string &key, const vector<string> *fields,
           vector<KVPair> &result);

  // no scan operation support
  int Scan(const string &table, const string &key, int len,
           const vector<string> *fields, vector<vector<KVPair>> &result) {
    return DB::kOK;
  }

  int Update(const string &table, const string &key, vector<KVPair> &values);

  int Insert(const string &table, const string &key, vector<KVPair> &values);

  int Delete(const string &table, const string &key);

  int find_tip(string json);
  vector<string> poll_tx(int block_number); 
  unsigned int get_tip_block_number(); 
 private:
  string endpoint_;
  unordered_map<string, double> *pendingtx_;
  SpinLock *txlock_; 

  string get_json_field(const string &json, const string &key); 
  vector<string> find_tx(string json); 
  atomic<long> post_count_;
};

}  // ycsbc

#endif  // YCSB_C_HYPERLEDGER_KV_DB_H_
