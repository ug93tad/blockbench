import os

#oFS = [1,2,3,4,5,6]
#FS=[0,2,6,10,14,18,22]
FS=[1]
THREADS = [16]
TXRATES=[16]
NR_CLIENTS=[10]

HOSTSFILE = 'hosts'
HOSTNAME = 'slave-{}'

RUNS=range(1)
QUORUM_HOME='/users/dinhtta/blockbench/benchmark/quorum_raft'
SERVER_LOG_PREFIX='/data/dinhtta'
YCSB_DIR='/users/dinhtta/blockbench/src/macro/kvstore'
LOG_SUFFIX='quorum_raft_varying_f_n{}_threads{}_rate{}_clients{}_run{}'
ENDPOINT = '{}:8000'

SLEEP_TIME = 200
INIT_CMD = 'cd {}; ./init-all.sh {}; ./start-all.sh {} {}/{}'

#server log is specified at env.sh: /data/dinhtta/quorum/logs
#client log

CLIENT_CMD = '"mkdir -p {}; cd {}; nohup ./driver -db ethereum -threads {} -P workloads/workloada.spec -endpoint {}:8000 -txrate {} -wl ycsb > {}/client_{} 2>&1 &"'

KILL_CLIENT_CMD = 'killall -KILL driver'
KILL_SERVER_CMD = '{}/stop.sh'

def execute(cmd):
  print cmd
  os.system(cmd)
