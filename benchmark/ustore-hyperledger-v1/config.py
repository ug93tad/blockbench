DEPLOY_PATH="/data/dinhtta/hyperledger"
CLIENT_PREFIX="/users/dinhtta/ustore-hyperledger-v1"
CLIENT_LOG_PATH = CLIENT_PREFIX+"/logs"

BUILD_PATH="/data/dinhtta/src/github.com/hyperledger/fabric/build/bin"
SERVER_LOG_PATH = BUILD_PATH+"/logs"

# change these
LOG_PATH = "/data/dinhtta/ustore-hyperledger"
CLIENT_LOG_DIR = CLIENT_PREFIX+"/logs"
POST_PROCESS_DIR = CLIENT_PREFIX+"/post_processing"

MSPCONFIG_PATH = BUILD_PATH+"/network/crypto-config/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/msp"
CHANNEL_MSPCONFIG_PATH = BUILD_PATH+"/network/crypto-config/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp"

GENESIS_PATH = BUILD_PATH+"/network/genesis.block"
ORDERER_PATH = DEPLOY_PATH+"/orderer"
ORDERER_MSP_PATH = BUILD_PATH+"/network/crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/msp"
PEER_LOG = "{}/{}_{}threads_{}rate"

PEER_CHANNEL_HOST ="localhost:7050"
PEER_CHANNEL_NAME = "mychannel"
PEER_CHANNEL_PATH = BUILD_PATH+"/network/mychannel.tx"

CHAINCODE_NAME = "ioheavy"
CHAINCODE_PATH = "github.com/ioheavy" #relative to GOPATH
CHAINCODE_CONSTRUCTOR_OPTS = "'{\"Args\":[\"\"]}'"
CHAINCODE_POLICY_OPTS = "\"OR ('Org1MSP.member', 'Org2MSP.member')\""
LOGGING_LEVEL = "info"  

DEFAULT_SAMPLE_READ = 127
DEFAULT_SAMPLE_WRITE = 0
PEER_ENV_TEMPLATE = ("CORE_VM_ENDPOINT=unix:///var/run/docker.sock "
                     "CORE_PEER_ID=peer0.org1.example.com "
                     "CORE_PEER_LOCALMSPID=Org1MSP "
                     "CORE_PEER_MSPCONFIGPATH={} "
                     "CORE_PEER_ADDRESS=localhost:7051 "
                     "CORE_PEER_FILESYSTEMPATH={} "
                     "CORE_LEDGER_STATE_STATEDATABASE={} "
                     "CORE_CHAINCODE_EXECUTETIMEOUT=300000s "
                     "SAMPLE_INTERVAL_STATEDB_READ={} "
                     "SAMPLE_INTERVAL_STATEDB_WRITE={} "
                    )

ORDERER_ENV_TEMPLATE = ("ORDERER_GENERAL_LOGLEVEL=info "
                        "ORDERER_GENERAL_LISTENADDRESS=0.0.0.0 "
                        "ORDERER_GENERAL_GENESISMETHOD=file "
                        "ORDERER_GENERAL_GENESISFILE={} "
                        "ORDERER_GENERAL_LOCALMSPID=OrdererMSP "
                        "ORDERER_GENERAL_LOCALMSPDIR={} "
                        "ORDERER_FILELEDGER_LOCATION={} "
                      )



START_ORDERER_CMD = "mkdir -p {}; rm -rf {}; cd {}; {} ./orderer > {}/orderer_{} 2>&1 & "
START_PEER_CMD = "cd {}; {} ./peer node start --logging-level={} > {}/peer_{} 2>&1 & "
START_CHANNEL_CMD = "cd {}; {} ./peer channel create -o {} -c mychannel {} -f {} > {}/channel_{} 2>&1"
JOIN_CHANNEL_CMD = "cd {}; {} ./peer channel join -b {}.block > {}/channel_join_{} 2>&1"
INSTALL_CHAINCODE_CMD = "cd {}; {} ./peer chaincode install -n {} -v 1.0 -p {} > {}/install_cc_{} 2>&1"
INSTANTIATE_CHAINCODE_CMD = "cd {}; {} ./peer chaincode instantiate -o {} -C {} -n {} -v 1.0 -c {} -P {} > {}/deploy_cc_{} 2>&1"
KILL_CMD = "killall -KILL peer; killall -KILL orderer"


CLIENT_CMD = "mkdir -p {}; cd {}; nodejs invoke.js {} {} {} > {}/client_{} 2>&1"
