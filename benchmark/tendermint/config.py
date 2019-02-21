import os

#oFS = [1,2,3,4,5,6]
#FS=[0,1,2,4,6,8,10,12,14,16,18,20]
#FS=[1,4,6,8,10,12,14,16]
#FS=[0,2,4,6,8,10,12,14,16,18,20]
#FS=[0,2,4,6,8,10,12,14,16,18,20]
FS=[0,2,6,10,14,18,22]
TXRATES=[16]
#NR_CLIENTS=[6,8,10]
NR_CLIENTS=[10]
RUNS=range(3)

LOG_HOST = 'ciidaa'

HOSTSFILE = 'hosts'
HOSTNAME = 'slave-{}'

TM_HOME='/users/dinhtta/blockbench/benchmark/tendermint'
TM_DATA='/data/dinhtta'
LOG_SUFFIX='tendermint_varying_f_n{}_rate{}_clients{}_run{}'

SLEEP_TIME = 100

#server log is specified at env.sh: /data/dinhtta/quorum/logs
#client log

CLIENT_CMD = '"mkdir -p {}; nohup tm-bench -c 16 -T {} -r {} {}:26657 > {}/client_{} 2>&1 &"'
SERVER_CMD = '"/users/dinhtta/clock; rm -rf {}; mkdir -p {} {}; cp -r {} {}; nohup tendermint node --home {} --proxy_app=persistent_kvstore > {}/log 2>&1 &"'
KILL_CLIENT_CMD = 'killall -KILL tm-bench'
KILL_SERVER_CMD = '"killall -KILL tendermint; rm -rf {}"'

def execute(cmd):
  print cmd
  os.system(cmd)

