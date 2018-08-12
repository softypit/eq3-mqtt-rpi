#!/usr/bin/python3
# -*-coding: utf-8 -*-

import datetime
import subprocess
import time
import sys


class EQ3Thermostat(object):

    def __init__(self, address):
        self.address = address
        self.locked = False
        self.auto = False
        self.manual = False
        self.eco = False
        self.boost = False
        self.temperature = 0
        self.openpc = 0
        self.done = False
        self.error = False

    def update(self, value):
        """Reads the current temperature from the thermostat. We need to kill
        the gatttool process as the --listen option puts it into an infinite
        loop."""
        p = subprocess.Popen(["timeout", "-s", "INT", "5", "gatttool", "-b",
                              self.address, "--char-write-req", "-a", "0x0411",
                              "-n", value, "--listen"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
        out, err = p.communicate()
        value_string = out.decode("utf-8")
       
        #print("value is {}".format(value_string))

        if "error" in value_string:
            #print("error")
            self.error = True
            self.done = True
            try:
                subprocess.Popen.kill(p)
            except ProcessLookupError:
                pass

        elif "Notification handle" in value_string:
            #print("Got response {}".format(value_string))
            value_string_splt = value_string.split()
            #temperature = value_string_splt[-1]
            #boost = value_string_splt[-3]
            #locked = value_string_splt[-4]
            baseidx = 10;
            temperature = value_string_splt[baseidx + 5]
            self.openpc = value_string_splt[baseidx + 3]
            state = int(value_string_splt[baseidx + 2], 16)
            try:
                subprocess.Popen.kill(p)
            except ProcessLookupError:
                pass

            #print("Boost {} Locked {} temp {}".format(boost, locked, temperature))
            #print("value {}".format(value_string))

            self.boost = False
            self.locked = False
            self.manual = False
            self.eco = False
            self.battlow = False
            if state & 0x01:
                self.manual = True
            if state & 0x02:
                self.eco = True
            if state & 0x04:
                self.boost = True
            if state & 0x20:
                self.locked = True
            if state & 0x80:
                self.battlow = True
            #else:
            #    print("Could not understand {} lockstate of {}".format(locked, self.address))
            #    self.error = True

            try:
                self.temperature = int(temperature, 16) / 2
            except Exception as e:
                #print("Getting temperature of {} failed {}".format(self.address, e))
                self.error = True

            self.done = True
        else:
            self.error = True
            self.done = True
            try:
                subprocess.Popen.kill(p)
            except ProcessLookupError:
                pass
    def poll(self):
        """Poll trv for current status"""
        cmd = "03"
        self.update(cmd)

    def activate_boostmode(self):
        """Boostmode fully opens the thermostat for 300sec."""
        cmd = "4501"
        self.update(cmd)

    def deactivate_boostmode(self):
        """Use only to stop boostmode before 300sec."""
        cmd = "4500"
        self.update(cmd)

    def set_automatic_mode(self):
        """Put thermostat in automatic mode."""
        cmd = "4000"
        self.update(cmd)

    def set_manual_mode(self):
        """Put thermostat in manual mode."""
        cmd = "4040"
        self.update(cmd)

    def set_eco_mode(self):
        """Put thermostat in eco mode."""
        cmd = "4080"
        self.update(cmd)

    def lock_thermostat(self):
        """Locks the thermostat for manual use."""
        cmd = "8001"
        self.update(cmd)

    def unlock_thermostat(self):
        """Unlocks the thermostat for manual use."""
        cmd = "8000"
        self.update(cmd)

    def set_temperature(self, temperature):
        temperature = hex(int(2 * float(temperature)))[2:]
        cmd = "41{}".format(temperature)
        self.update(cmd)

    def set_temperature_offset(self, offset):
        """Untested."""
        #temperature = hex(int(2 * (float(offset)) + 7.0))[2:]
        temp = (int(2 * (float(offset)) + 7.0))
        #cmd = "13{:02x}".format(temperature)
        cmd = "13{:02x}".format(temp)
        #print("Temp offset cmd {}".format(cmd))
        self.update(cmd)

    def set_day(self):
        """Puts thermostat into day mode (sun icon)."""
        cmd = "43"
        self.update(cmd)

    def set_night(self):
        """Puts thermostat into night mode (moon icon)."""
        cmd = "44"
        self.update(cmd)

    def set_day_night(self, night, day):
        """Sets comfort temperature for day and night."""
        day = hex(int(2 * float(day)))[2:]
        night = hex(int(2 * float(night)))[2:]
        cmd = "11{}{}".format(day, night)
        self.update(cmd)

    def set_windows_open(self, temperature, duration_min):
        """Untested."""
        temperature = hex(int(2 * float(temperature)))[2:]
        duration_min = hex(int(duration_min / 5.0))[2:]
        cmd = "11{}{}".format(temperature, duration_min)
        self.update(cmd)

    def set_time(self, datetimeobj):
        """Takes a datetimeobj (like datetime.datetime.now()) and sets the time
        in the thermostat."""
        command_prefix = "03"
        year = "{:02X}".format(datetimeobj.year % 100)
        month = "{:02X}".format(datetimeobj.month)
        day = "{:02X}".format(datetimeobj.day)
        hour = "{:02X}".format(datetimeobj.hour)
        minute = "{:02X}".format(datetimeobj.minute)
        second = "{:02X}".format(datetimeobj.second)
        control_string = "{}{}{}{}{}{}{}".format(
                          command_prefix, year, month, day, hour, minute, second)
        self.update(control_string)

if __name__ == '__main__':
    if len(sys.argv) > 2:
        #print("mac is {}\n".format(sys.argv[1]))
        h = EQ3Thermostat(format(sys.argv[1]))
        #print("command is {}\n".format(sys.argv[2]))
        cmd = format(sys.argv[2])
        if cmd == "settemp":
            if len(sys.argv) < 3:
                print("Insufficient arguments for settemp")
                sys.exit(0)

            #print("temp is {}\n".format(sys.argv[3]))
            h.set_temperature(format(sys.argv[3]))
        elif cmd == "offset":
            if len(sys.argv) < 3:
                print("Insufficient arguments for setoffset")
                sys.exit(0)

            #print("temp is {}\n".format(sys.argv[3]))
            h.set_temperature_offset(format(sys.argv[3]))
        elif cmd == "boost":
            h.activate_boostmode()
        elif cmd == "unboost":
            h.deactivate_boostmode()
        elif cmd == "poll":
            h.poll()
        elif cmd == "auto":
            h.set_automatic_mode()
        elif cmd == "manual":
            h.set_manual_mode()
        elif cmd == "lock":
            h.lock_thermostat()
        elif cmd == "unlock":
            h.unlock_thermostat()
        else:
            print("Unknown command {}".format(cmd))
            sys.exit(0)

        while h.done != True:
            time.sleep(1)

        print("{{\"trv\":\"{}\",".format(h.address), end='')
        if h.error == True:
            print("\"error\":\"TRV not available\"}", end='')
        else:
            print("\"temp\":\"{}\",\"boost\":\"".format(h.temperature), end='')
            if h.boost == True:
                print("active", end='')
            else:
                print("inactive", end='')
            print("\",\"mode\":\"", end='')
            if h.eco == True:
                print("eco", end='')
            else:
                if h.manual == True:
                    print("manual", end='')
                else:
                    print("auto", end='')
            print("\",\"state\":\"", end='')
            if h.locked == True:
                print("locked", end='')
            else:
                print("unlocked", end='')
            intpc = int(h.openpc)
            print("\",\"valve\":\"{0}% open\"".format(intpc), end='')
            #print("\",\"valve\":\"{}% open\"".format(h.openpc), end='')
            print(",\"battery\":\"", end='')
            if h.battlow == True:
                print("LOW", end='')
            else:
                print("GOOD", end='')
            print("\"}", end='')


