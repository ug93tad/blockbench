#!/bin/bash
# ip 
. env.sh
ip=$1
rm -rf $ETH_DATA && geth --datadir=$ETH_DATA init genesis_quorum.json && geth --datadir=$ETH_DATA account new --password <(echo -n "")
mkdir -p keys
geth --datadir=$ETH_DATA --rpc --rpcaddr 0.0.0.0 --rpcport "8000" --rpccorsdomain "*" --gasprice 0 --unlock 0 --password <(echo -n "") js <(echo 'console.log(admin.nodeInfo.enode);') 2>/dev/null |grep enode | perl -pe "s/\[\:\:\]/$ip/g" | perl -pe "s/^/\"/; s/\s*$/\"/;"
echo ""
cat $ETH_DATA/geth/nodekey
