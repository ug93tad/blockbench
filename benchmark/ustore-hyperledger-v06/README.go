# UStore + Hyperledger v0.6

## Setup:
1. Installing USTORE with GO binding

  Fetch from https://github.com/bulldosers/USTORE  at branch wj-go-binding

2. Setup Hyperledger:
  Fetch from https://github.com/ug93tad/fabric

  Copy it to `$GOPATH/src/github.com/hyperledger` in the local directory

3. Script configuration
Important configurations for running the experiments are in `config.py` file. For example:

Look out for the `# <---` lines where the values may need to changes

## Main script

  `python ustore-hyperledger.py <db> <nrecords> <nops> <w ratio> <r ratio> <batch size> <ledger sample interval> <commit sample interval>`

where:
  * `db` : either "ustore" or "rocksdb"
  * `nrecords` : total number of records to preload
  * `nops`: total number of operations (read and write) after preloading
  * `write ratio`: ratio of write operations / nops, in between `[0,1]`
  * `read ratio`: ratio of read operations / nops, in between `[0,1]`
  * `batch size`: how many transactions per block
  * `ledger sample interval`: sample interval of read/write operations. A value of `2^x-1` means sampling
  every `2^x` operations
  * `commit sample interval`: sample interval of commit operations.


Example: 
  `python ustore-hyplerdger.py ustore 8192 8192 0.5 0.5 100 127 0`

will run the kvstore workload on UStore, inserting 8192 keys before 8192 updates/read operations. The block
size is 100, and read/write latencies are sampled every 128 operations, whereas commit latency is printed out
every time. 

## Output examples

#reads: 0        #total time (ms): 0     average (ms): 0
#writes: 13384   #total time (ms): 240.3947      average (ms): 0.0179613493724
#commits: 134    #total time (ms): 1957.388539   average (ms): 14.6073771567
#blocks: 134
avg block size: 99.8872180451
avg client throughput (tx/s): 271.12244898
avg client latency (s): 25.7635067241
db size: 73643113
