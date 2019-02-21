# Benchmarking Quorum with Istanbul BFT 

Here are instructions of how to set up and run KVStore benchmark for Quorum blockchain that uses Istanbul BFT (or IBFT).

### Install quorum
Go to every node and excute

`./install.sh`

After that, add the newly install `geth` in `quorum/build/bin` to the $PATH variable.

### Setup
We use istanbul-too to generate configuration files for IBFT. It can be found at: 
[https://github.com/getamis/istanbul-tools](https://github.com/getamis/istanbul-tools)

Important variables are set in `env.sh` file. Please change it first. When running in a cluster, replace paths
starting with `/users/dinhtta` with a NFS paths, and others with non-NFS paths. 

For permissioned settings, Quorum requires a `static-nodes` file that containing identities (enodes) of all
nodes in the system. The following command is executed **once** at the beginning of *all* experiments:

`fab setup_all:<N>`

It creates necessary files for the network with 1,4,7,11,... nodes (fewer than $$N$$), as follows:
1. Use istanbul tools to generate necessary configuration files
2. Change these files with the correct IP addresses and gas limits. 

### Running experiments
Before running, change `CONFIRM_BLOCK_LENGTH` variable in `src/macro/kvstore/ycsbcc.cc` to `1`, then
re-compile the driver again. This is needed because IBFT consensus is final, as opposed to PoW. 

Run `python run.py` to starts the experiment. It reads running parameters from `config.py` file, which
contains the following important field:

+ `FS, NR_CLIENTS`: lists of values for $$f$$ and number of clients, respectively.
+ `QUORUM_HOME`: current directory 
+ `YCSB_DIR`: where to find the driver for clients. 

### Parsing results
Run `python parse_result.py` to see summary of throughput and latency
