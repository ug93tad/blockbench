# Benchmarking Tendermint 

Here are instructions of how to set up and run distributed benchmark for Tendermint. Tendermint
implements a consensus protocol and exposes APIs to application to make use of the consensus. Thus,
building a complete blockchain on top of Tendermint means implement other components of the stack,
such as storage, data model and execution engine. 

Although we cannot yet run BLOCKBENCH benchmarks for Tendermint (integration is work in progress),
we can use the `tm-bench` tool provided by Tendermint. `tm-bench` uses the simple key-value store
example of Tendermint --- one without most features of a blockchain. 

### Install Tendermint and tm-bench 
Go to every node and excute

`./install.sh`

### Setup
For permissioned settings, tendermint comes with a tool to setup a private testnet, using
`tendermint testnet ...` command. The following command is executed **once** at the beginning of *all* experiments:

`fab setup_all:<N>`

It creates necessary files for the network with 1,3,5,7,9,... nodes (fewer than $$N$$) by using
`tendermint testnet` for each network size.  

### Running experiments
Run `python run.py` to starts experiments. It reads running parameters from `config.py` file, which
contains the following important field:

+ `FS, NR_CLIENTS`: lists of values for $$f$$ and number of clients, respectively.
+ `TM_HOME`: current directory 

### Parsing results
Run `python parse_result.py` to see summary of throughput and latency
