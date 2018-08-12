
#eq3mqtt.py

**python/bash solution to control eq3 thermostats using mqtt.**
Enables EQ3 Thermostatic Radiator Valve interaction with MQTT. Valve parameters can be set via mqtt and valve status is published in response.

Time and schedules are not programmable using this application - it is intended to be used with a heating-management system which will control the valves directly without using their internal schedules.

eq3 control is derived from mpex/EQ3-Thermostat which requires the gatttool from bluez library.
mosquitto command line is used for mqtt (mosquitto_sub/mosquitto_pub).

Tested on RPi2 with CSR bluetooth dongle. Should also work on RPi3 and PiZeroW.

/usr/bin/mqtttrv.sh to be run from init.d/systemctl.
/usr/bin/mqtttrvrun.sh is the actual daemon that listens for mqtt commands
/usr/bin/eq3mqtt.py is the python script that handles interractions with an eq3 trv

mqtttrvrun is executed with up to 4 arguments - host, port, intopic and outtopic.
e.g. /usr/bin/mqtttrvrun.sh 127.0.0.1 1883 /rpiradin/trv /rpiradout/status

if these arguments are not specified the above defaults are used.

publish commands to the intopic (default /rpiradin/trv)

commands are:
settemp <temp>      range 5.0 to 29.5 in 0.5 increments
offset <temp>       range -3.5 to 3.5 in 0.5 increments
boost               set boost (300 seconds)
unboost             cancel boost
poll                no-operation - used to acquire status response
auto                auto mode - use valve temperature schedules
manual              manual mode - valve will not use its own schedules
lock                lock valve (disable buttons)
unlock              unlock valve

response to all commands is json formatted and published to outtopic (default /rpiradout/status):

{"trv":"[bleaddr]","error":"TRV not available"}
or
{"trv":"[bleaddr]","temp":"[settemp]","boost":"<inactive/active>","mode":"<eco/manual/auto>","state":"<locked/unlocked>","valve":"[openpc]%","battery":"<LOW/GOOD>"}
