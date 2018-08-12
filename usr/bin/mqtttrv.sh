#!/bin/sh

start() {
    /usr/bin/mqtttrvrun.sh &
}

stop() {
    pkill mqtttrvrun
}

case $1 in 
  start|stop) "$1" ;;
esac

