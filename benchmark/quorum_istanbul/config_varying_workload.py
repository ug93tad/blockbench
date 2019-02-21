import os

#oFS = [1,2,3,4,5,6]
FS=[4]
THREADS = [16]
TXRATES=[16]
NR_CLIENTS=[1,2,4,8,16,32,48,64]
LOG_HOST = 'ciidaa'

RUNS=range(3)

HOSTSFILE = 'hosts'
HOSTNAME = 'slave-{}'

QUORUM_HOME='/users/dinhtta/blockbench/benchmark/quorum_istanbul'
SERVER_LOG_PREFIX='/data/dinhtta'
YCSB_DIR='/users/dinhtta/blockbench/src/macro/kvstore_quorum'
LOG_SUFFIX='quorum_ibft_n{}_threads{}_rate{}_clients{}_run{}'
ENDPOINT = '{}:8000'

SLEEP_TIME = 200
INIT_CMD = 'cd {}; ./init-all.sh {}; ./start-all.sh {} {}/{}'

#server log is specified at env.sh: /data/dinhtta/quorum/logs
#client log

CLIENT_CMD = '"mkdir -p {}; cd {}; nohup ./driver -db ethereum -threads {} -P workloads/workloada.spec -endpoint {}:8000 -txrate {} -wl ycsb -wt 20 > {}/client_{} 2>&1 &"'

KILL_CLIENT_CMD = 'killall -KILL driver'
KILL_SERVER_CMD = '{}/stop.sh'

def execute(cmd):
  print cmd
  os.system(cmd)

