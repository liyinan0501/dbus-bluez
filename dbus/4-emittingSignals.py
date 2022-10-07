#!/usr/bin/python3

# 4-Emitting Signals
# -an object signal must be exported in the same way as for exposing a method which can be remotely called.
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import time

mainloop = None


class Counter(dbus.service.Object):
    def __init__(self, bus):
        self.path = "/come/example/counter"
        self.c = 0
        dbus.service.Object.__init__(self, bus, self.path)

    # declare and export a signal using @dbus.service.signal
    @dbus.service.signal("com.example.Counter")
    def CounterSingal(self, counter):
        pass

    def emitCounterSignal(self):
        self.CounterSingal(self.c)

    def increment(self):
        self.c += 1
        print(self.c)


dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
counter = Counter(bus)

while True:
    counter.increment()
    # emit the signal
    counter.emitCounterSignal()
    time.sleep(1)
