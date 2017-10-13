#include "db/hyperledger_kvdb.h"

#include <restclient-cpp/restclient.h>
#include <string>
#include <vector>
#include <mutex>

using std::string;
using std::vector;
using namespace RestClient;

const string CHAIN_END_POINT = "/chain";
const string BLOCK_END_POINT = "/chain/blocks";

namespace ycsbc {

std::once_flag init_flag;

//const string API_ENDPOINT = "ciidaa-a20:7050/chaincode/";
const string REQUEST_HEADERS = "text/json";
const string CHAINCODE_ID =
    "0b608da26a3960fd8488145c9bd3567a8aae478177968dfd758e1d15f36e782c4a57ae50d7"
    "b8a69b3e98a7cf8e0636113bb944808c650f3d4da485f259a5608c";

const string COMMON_COMMAND_1 = "\"}, \"ctorMsg\": {\"function\": \"";
const string COMMON_COMMAND_2 = "\",\"args\":[";
const string COMMON_COMMAND_SUFFIX = "] } }, \"id\": 1 }";

const string INVOKE_COMMAND_PREFIX =
    "{\
  \"jsonrpc\": \"2.0\", \
  \"method\": \"invoke\", \
  \"params\": { \
                \"type\": 1, \
                \"chaincodeID\":{ \"name\":\"" +
    CHAINCODE_ID + COMMON_COMMAND_1;

const string QUERY_COMMAND_PREFIX =
    "{\
  \"jsonrpc\": \"2.0\", \
  \"method\": \"query\", \
  \"params\": { \
                \"type\": 1, \
                \"chaincodeID\":{ \"name\":\"" +
    CHAINCODE_ID + COMMON_COMMAND_1 + "read" + COMMON_COMMAND_2;

const string DEPLOY_COMMAND =
    "{ \
    \"jsonrpc\": \"2.0\", \
    \"method\": \"deploy\", \
    \"params\": { \
                  \"type\": 1, \
                  \"chaincodeID\":{ \"path\": \
                     \"https://github.com/ug93tad/chaincode-test/kvstore-v0.6\" }, \
                  \"ctorMsg\": { \"function\":\"init\", \"args\":[] }\
                }, \
    \"id\": 1 \
    }";

string compose_read(const string &key) {
  return QUERY_COMMAND_PREFIX + "\"" + key + "\"" + COMMON_COMMAND_SUFFIX;
}

string compose_write(const string &key, const string &val) {
  return INVOKE_COMMAND_PREFIX + "write" + COMMON_COMMAND_2 + "\"" + key +
         "\", \"" + val + "\"" + COMMON_COMMAND_SUFFIX;
}

string compose_del(const string &key) {
  return INVOKE_COMMAND_PREFIX + "del" + COMMON_COMMAND_2 + "\"" + key + "\"" +
         COMMON_COMMAND_SUFFIX;
}

HyperLedgerKVDB::HyperLedgerKVDB(const string &endpoint) : endpoint_(endpoint), post_count_(0) {
  post(endpoint, REQUEST_HEADERS, DEPLOY_COMMAND);
}

// ignore table
// ignore field
// read value indicated by a key
int HyperLedgerKVDB::Read(const string &table, const string &key,
                          const vector<string> *fields,
                          vector<KVPair> &result) {
  Response r = post(endpoint_, REQUEST_HEADERS, compose_read(key));
  return DB::kOK;
}

// ignore table
// update value indicated by a key
int HyperLedgerKVDB::Update(const string &table, const string &key,
                            vector<KVPair> &values) {
  string val = "";
  for (auto v : values) {
    val += v.first + "=" + v.second + " ";
  }
  for (auto &x : val) {
    if (x == '\"') x = ' ';
  }
  Response r = post(endpoint_, REQUEST_HEADERS, compose_write(key, val));
  
  string txn_hash = get_json_field(r.body, "message"); 
  txlock_->lock();
  
  (*pendingtx_)[txn_hash] = utils::time_now(); 
  
  txlock_->unlock(); 
  return DB::kOK;
}

// ignore table
// ignore field
// concate values in KVPairs into one long value
int HyperLedgerKVDB::Insert(const string &table, const string &key,
                            vector<KVPair> &values) {
  return Update(table, key, values); 
  /*
  string val = "";
  for (auto v : values) {
    val += v.first + "=" + v.second + " ";
  }
  for (auto &x : val) {
    if (x == '\"') x = ' ';
  }
  Response r = post(endpoint_, REQUEST_HEADERS, compose_write(key, val));
  return DB::kOK;
  */
}

// ignore table
// delete value indicated by a key
int HyperLedgerKVDB::Delete(const string &table, const string &key) {
  Response r = post(endpoint_, REQUEST_HEADERS, compose_del(key));
  return DB::kOK;
}

vector<string> HyperLedgerKVDB::find_tx(string json){
  vector<string> ss; 
  int key_pos = json.find("txid"); 
  while (key_pos!=string::npos){
    auto quote_sign_pos_1 = json.find('\"', key_pos + 1);
    auto quote_sign_pos_2 = json.find('\"', quote_sign_pos_1 + 1);
    auto quote_sign_pos_3 = json.find('\"', quote_sign_pos_2 + 1);
    ss.push_back(json.substr(quote_sign_pos_2 + 1,
                     quote_sign_pos_3 - quote_sign_pos_2 - 1));
    key_pos = json.find("txid", quote_sign_pos_3+1);
  }
  return ss; 
}

string HyperLedgerKVDB::get_json_field(const string &json, const string &key) {
  auto key_pos = json.find(key);
  auto quote_sign_pos_1 = json.find('\"', key_pos + 1);
  auto quote_sign_pos_2 = json.find('\"', quote_sign_pos_1 + 1);
  auto quote_sign_pos_3 = json.find('\"', quote_sign_pos_2 + 1);
  return json.substr(quote_sign_pos_2 + 1,
                     quote_sign_pos_3 - quote_sign_pos_2 - 1);
}

int HyperLedgerKVDB::find_tip(string json){
  if (json.find("Failed")!=string::npos) {
    return -1; 
  }
  int key_pos = json.find("height"); 
  auto close_quote_pos = json.find('\"',key_pos+1);   
  auto comma_pos = json.find(',', key_pos+1); 
  string sval = json.substr(close_quote_pos+2, comma_pos-close_quote_pos-2); 
  return stoi(sval); 
}

// get all tx from the start_block until latest
vector<string> HyperLedgerKVDB::poll_tx(int block_number) {
  string request = endpoint_.substr(0,endpoint_.find("/chaincode"))+BLOCK_END_POINT+"/"+std::to_string(block_number); 
  return find_tx(get(request).body); 
}

unsigned int HyperLedgerKVDB::get_tip_block_number(){
  string request = endpoint_.substr(0,endpoint_.find("/chaincode"))+CHAIN_END_POINT; 
  return find_tip(get(request).body); 
}

}  // ycsbc

