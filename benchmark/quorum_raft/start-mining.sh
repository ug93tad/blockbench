#!/bin/bash
cd `dirname ${BASH_SOURCE-$0}`
. env.sh
echo "[*] start-mining.sh"

i=$1
LOG=$2"/log"
mkdir -p $2

/users/dinhtta/clock 

PRIVATE_CONFIG=ignore nohup ${QUORUM} --datadir $QUO_DATA/dd$i  --nodiscover --verbosity 2 --raft --rpc --rpcaddr 0.0.0.0 --rpcapi admin,db,eth,debug,miner,net,shh,txpool,personal,web3,quorum,raft --emitcheckpoints --rpcport 8000 --raftblocktime 1000 --unlock 0 --password <(echo -n "") > $LOG 2>&1 &
#echo --datadir $QUO_DATA --rpc --rpcaddr 0.0.0.0 --rpcport 8000 --port 9000 --raft --raftport 50400 --raftblocktime 2000 --unlock 0 --password <(echo -n "") 
echo "[*] miner started"
sleep 1

#for com in `cat $QUO_HOME/addPeer.txt`; do
 #    geth --exec "eth.blockNumber" attach $QUO_DATA/geth.ipc
     #geth  attach ipc:/$ETH_DATA/geth.ipc
#done

