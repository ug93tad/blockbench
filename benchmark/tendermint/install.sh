#!/bin/bash
set -ue
TM_HOME=/data/dinhtta/src/github.com/tendermint
cd /data/dinhtta && rm -rf $TM_HOME && mkdir -p $TM_HOME && cd $TM_HOME
git clone https://github.com/tendermint/tendermint.git 
cd tendermint && make get_tools get_vendor_deps install && cd tools/tm-bench && go install

