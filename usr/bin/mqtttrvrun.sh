#!/bin/bash
##########################
# MQTT Shell Listen & Exec
host="127.0.0.1"
port=1883
intopic="/rpiradin/trv"
outtopic="/rpiradout/status"
[ "$#" -gt 1 ] && host=$1
[ "$#" -gt 2 ] && port=$2
[ "$#" -gt 3 ] && intopic=$3
[ "$#" -gt 4 ] && outtopic=$4
p="/tmp/mqtttrvbackpipe"
pidfile="/tmp/mqtttrvsubpid"

listen(){
    ([ ! -p "$p" ]) && mkfifo $p
    echo "pipe error $?"
    (mosquitto_sub -h $host -p $port -t $intopic >$p) &
    echo "$!" > pidfile
    while true
    do
      read line <$p
      #echo "Got $line"
      resp=$(/usr/bin/eq3mqtt.py $line)
      #echo "Sending $resp"
      mosquitto_pub -h $host -p $port -t $outtopic -m "$resp"
    done
    echo "Exit"
    rm $p
}

#echo "host is $host"
#echo "port is $port"
#echo "intopic $intopic"
#echo "outtopic $outtopic"
rm -rf $p

# Wait a while for broker to start
sleep 30s
listen

