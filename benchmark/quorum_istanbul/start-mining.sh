#!/bin/bash
cd `dirname ${BASH_SOURCE-$0}`
. env.sh
echo "[*] start-mining.sh"

i=$1
LOG=$2"/log"
rm -rf $LOG && mkdir -p $2

#ARGS="--nodiscover --istanbul.blockperiod 1 --istanbul.requesttimeout 100000 --syncmode "full" --mine --rpc --rpcaddr 0.0.0.0 --rpcapi admin,db,eth,debug,miner,net,shh,txpool,personal,web3,quorum,istanbul"

ARGS="--nodiscover --verbosity 2 --syncmode full --mine --rpc --rpcaddr 0.0.0.0 --rpcapi admin,db,eth,debug,miner,net,shh,txpool,personal,web3,quorum,istanbul"

/users/dinhtta/clock

PRIVATE_CONFIG=ignore nohup ${QUORUM} --datadir $QUO_DATA/dd$i $ARGS --rpcport 8000 --unlock 0 --password <(echo -n "") > $LOG 2>&1 &

echo "[*] miner started"
sleep 1

#for com in `cat $QUO_HOME/addPeer.txt`; do
 #    geth --exec "eth.blockNumber" attach $QUO_DATA/geth.ipc
     #geth  attach ipc:/$ETH_DATA/geth.ipc
#done

