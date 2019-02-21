# Benchmarking Quorum Raft

Here are instructions of how to set up and run KVStore benchmark for Quorum blockchain that uses Raft.

### Install quorum
Go to every node and excute

`./install.sh`

After that, add the newly install `geth` in `quorum/build/bin` to the $PATH variable.

### Setup
Important variables are set in `env.sh` file. Please change it first. When running in a cluster, replace paths
starting with `/users/dinhtta` with a NFS paths, and others with non-NFS paths. 

For permissioned settings, Quorum requires a `static-nodes` file that containing identities (enodes) of all
nodes in the system. The following command is executed **once** at the beginning of *all* experiments:

`fab setup:<N>`

It creates necessary files for the network with 1,3,5,7,9,... nodes (fewer than $$N$$), as follows:
1. It extracts IP addresses of N hosts listed in `hosts` files.
2. It starts `geth` at every node and collects the lists of N enodes indentifiers. It also generates N
`nodekey` files. 
3. For each network size `M`, it creates `static-nodesM.json` consistsing of M enodes.

### Running experiments
Before running, change `CONFIRM_BLOCK_LENGTH` variable in `src/macro/kvstore/ycsbcc.cc` to `1`, then
re-compile the driver again. This is needed because Raft consensus is final, as opposed to PoW. 

Run `python run.py` to starts the experiment. It reads running parameters from `config.py` file, which
contains the following important field:

+ `FS, NR_CLIENTS`: lists of values for $$f$$ and number of clients, respectively.
+ `QUORUM_HOME`: current directory 
+ `YCSB_DIR`: where to find the driver for clients. 

### Parsing results
Run `python parse_result.py` to see summary of throughput and latency
