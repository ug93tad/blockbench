#!/bin/bash
#args: number_of_nodes
cd `dirname ${BASH_SOURCE-$0}`
. env.sh

i=$1

echo "[*] init.sh"
mkdir -p $QUO_DATA/dd$i/{keystore,geth}

#cp keys/key$i $QUO_DATA/dd$i/keystore
ls -l keys/* && cp keys/static-nodes$2.json $QUO_DATA/dd$i/static-nodes.json
cp keys/nodekey$i $QUO_DATA/dd$i/geth/nodekey
${QUORUM} --datadir=$QUO_DATA/dd$i init $QUO_HOME/genesis_quorum.json
${QUORUM} --datadir=$QUO_DATA/dd$i account new --password <(echo -n "")
