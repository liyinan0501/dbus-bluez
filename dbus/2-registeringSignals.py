#!/usr/bin/python3

# 2-Registering Singals
# -registers for a signal which delivers a string value as an argument and prints that argument whenever the expected signal is received.

# generates the signal with a commend dbus-send:
# example: dbus-send --system --type=signal / com.example.greeting.GreetingSignal string:"hello"

import dbus
import dbus.mainloop.glib
from gi.repository import GLib

mainloop = None

# callback when a signal comes in.
def greeting_signal_received(greeting):
    print(greeting)


# attach to a main loop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

# connect to the system bus
bus = dbus.SystemBus()
# register to receive the signal
bus.add_signal_receiver(
    greeting_signal_received,
    dbus_interface="com.example.greeting",
    signal_name="GreetingSignal",
)

# acquire mainloop
mainloop = GLib.MainLoop()
# start a mainloop
mainloop.run()
