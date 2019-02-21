#!/bin/bash
# nr_nodes
# write to keys folder 
cd `dirnam ${BASH_SOURCE-$0}`

rm -rf keys && mkdir -p keys && cd keys
istanbul setup --num $1 --verbose --quorum --nodes --save


. env.sh
ip=$1
rm -rf $ETH_DATA && geth --datadir=$ETH_DATA init genesis_quorum.json && geth --datadir=$ETH_DATA --password <(echo -n "") account new
mkdir -p keys
geth --datadir=$ETH_DATA --rpc --rpcaddr 0.0.0.0 --rpcport "8000" --rpccorsdomain "*" --gasprice 0 --unlock 0 --password <(echo -n "") js <(echo 'console.log(admin.nodeInfo.enode);') 2>/dev/null |grep enode | perl -pe "s/\[\:\:\]/$ip/g" | perl -pe "s/^/\"/; s/\s*$/\"/;"
echo ""
cat $ETH_DATA/keystore/* 
echo ""
cat $ETH_DATA/geth/nodekey
