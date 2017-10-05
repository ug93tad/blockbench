#!/bin/bash
set -u

CUR_DIR=`pwd`
USTORE_PATH="/data/dinhtta"
HYPERLEDGER_PATH=$USTORE_PATH"/src/github.com/hyperledger"
USTORE_GIT="https://github.com/bulldosers/USTORE"
USTORE_BRANCH="wj-go-binding"
CHAINCODE_PATH="/data/dinhtta/src/github.com/ioheavy"
BUILD_PATH=$HYPERLEDGER_PATH/fabric/build/bin

SWIG_DIR="/data/dinhtta"

#Install dependencies
#cryptopp, cmake3 and nodejs
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
sudo apt-get install -y libcryptopp-dev cmake3 nodejs
#swig
scp slave-60:/data/dinhtta/swig-3.0.12.tar.gz $SWIG_DIR"/"
cd $SWIG_DIR
tar -zxvf swig-3.0.12.tar.gz
cd swig-3.0.12; ./configure; make; sudo make install

#Install UStore, will install ustore at $GOPATH
cd $USTORE_PATH
rm -rf USTORE
echo "*** Installing USTORE ***"
git clone $USTORE_GIT
cd USTORE; git checkout $USTORE_BRANCH
mkdir build; cd build
cmake ..
make -j4

#Install Hyperledger-v1-ustore
rm -rf $HYPERLEDGER_PATH
mkdir -p $HYPERLEDGER_PATH
cd $HYPERLEDGER_PATH; git clone https://github.com/ug93tad/fabric-1 fabric
cd fabric; make peer; make orderer

#Copy chaincode
mkdir -p $CHAINCODE_PATH
cp $CUR_DIR/chaincode/* $CHAINCODE_PATH
#Copy network creds
cp -r $CUR_DIR/network $BUILD_PATH/
#Copy invoke.js
cp $CUR_DIR/invoke.js $BUILD_PATH/
#Copy ustore conf directory
cp -r $USTORE_PATH/USTORE/conf $BUILD_PATH/

#install fabric-client 
cd $BUILD_PATH; npm install fabric-client

#add peer name
sudo sh -c "echo 127.0.0.1 orderer.example.com >> /etc/hosts"
sudo sh -c "echo 127.0.0.1 peer0.exmple.com >> /etc/hosts"
sudo sh -c "echo 127.0.0.1 peer1.exmple.com >> /etc/hosts"

#copy creds to ~/.hfc-key-store [if not already]
cd $CUR_DIR
