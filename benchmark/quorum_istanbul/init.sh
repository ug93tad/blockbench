#!/bin/bash
#args: number_of_nodes
cd `dirname ${BASH_SOURCE-$0}`
. env.sh

i=$1

echo "[*] init.sh"
rm -rf $QUO_DATA && mkdir -p $QUO_DATA/dd$i/{keystore,geth}

cp keys/n$2/static-nodes.json $QUO_DATA/dd$i/static-nodes.json
cp keys/n$2/nodekey$i $QUO_DATA/dd$i/geth/nodekey
${QUORUM} --datadir=$QUO_DATA/dd$i init keys/n$2/genesis.json
${QUORUM} --datadir=$QUO_DATA/dd$i account new --password <(echo -n "")
