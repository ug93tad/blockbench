THREADS=[16]
TXRATES=[32]
BOOTSTRAP_HOSTNO=50     # <-- where there server (running HL) is
CLIENT_HOSTNO=90        # <-- where the driver/client is
HOST="slave-{}"
DEPLOY_PATH="/data/dinhtta/hyperledger"   # <-- where the HL is store (for rocksdb)
                                          # for UStore, data is store in
                                          # $HL/fabric/build/bin/ustore_data

CLIENT_PREFIX="/users/dinhtta/ustore-hyperledger"   # <-- where this current directory is
HL_PATH="/data/dinhtta/src/github.com/hyperledger/fabric"  # <-- where HL source code is

BUILD_PATH=HL_PATH+"/build/bin" 
CLIENT_PATH=CLIENT_PREFIX+"/ycsb"
USTOREDB_GOPATH=HL_PATH+"/ustoredb" 

WORKLOAD_FILE="ycsb/workloads/workload_ustore.spec"
SLEEP_TIME = 40              # <-- default running time (killed after this period)

# change these
LOG_PATH = "/data/dinhtta/ustore-hyperledger" # <-- server log
CLIENT_LOG_DIR = CLIENT_PREFIX+"/logs"        # <-- client/driver log
POST_PROCESS_DIR = CLIENT_PREFIX+"/post_processing"

PEER_LOG = "{}/{}_{}threads_{}rate"


LOGGING_LEVEL = "warning:consensus/pbft,consensus/executor,ledger,db=info"  

ENV_TEMPLATE = ("CORE_PEER_ID=vp{} CORE_PEER_ADDRESSAUTODETECT=true "
                "CORE_PEER_NETWORK=blockbench "
                "CORE_PEER_VALIDATOR_CONSENSUS_PLUGIN=pbft "
                "CORE_PEER_FILE_SYSTEM_PATH="+DEPLOY_PATH+" "
                "CORE_VM_ENDPOINT=http://localhost:2375 "
                "CORE_PBFT_GENERAL_MODE=batch "
                "CORE_PBFT_GENERAL_TIMEOUT_REQUEST=100s "
                "CORE_PBFT_GENERAL_TIMEOUT_VIEWCHANGE=10s "
                "CORE_PBFT_GENERAL_TIMEOUT_RESENDVIEWCHANGE=10s "
                "CORE_PBFT_GENERAL_SGX={} " 
                "CORE_PBFT_GENERAL_N={} "
                "CORE_PBFT_GENERAL_F={} "
                "LEDGER_SAMPLE_INTERVAL={} "
                "CORE_EXECUTION_SAMPLE_INTERVAL={} "
                "CORE_PBFT_GENERAL_BATCHSIZE={} "
                "CORE_PEER_DB_DBTYPE={}")

ENV_EXTRA = "CORE_PEER_DISCOVERY_ROOTNODE={}:7051"

CMD="\"rm -rf {}; rm -rf {}; mkdir -p {}; mkdir -p {}; cd {}/; cp -r {}/conf .; rm -rf ustore_data; {} nohup ./peer node start --logging-level={} > {} 2>&1 &\"" 
KILL_SERVER_CMD = "pkill -TERM peer"

CLIENT_CMD = "\"mkdir -p {}; cd {}; nohup ./driver -db hyperledger -threads {} -P {}/{} -endpoint {}:7050/chaincode -txrate {} > {}/client_{}_{}_{} 2>&1 &\""
KILL_CLIENT_CMD = "sudo killall -KILL driver"
