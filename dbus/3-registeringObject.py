#!/usr/bin/python3

# 3-Registering Object
# -register object with method for receiving method calls from other D-Bus services.
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

mainloop = None

# inherits from dbus.service.OBject is required for supporting D-BUs introspection
class Calculator(dbus.service.Object):
    def __init__(self, bus):
        self.path = "/com/example/calculator"
        # exports the object to the specified bus.
        dbus.service.Object.__init__(self, bus, self.path)

    # @dbus.service.method(interfaceName, type of input, type of return)
    # the method accepts two 32-bit integer arguments as input and returns a single 32-bit result.
    @dbus.service.method(
        "com.example.calculator_interface", in_signature="ii", out_signature="i"
    )
    def Add(self, a1, a2):
        sum = a1 + a2
        print(a1, " + ", a2, " = ", sum)
        return sum


dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
# create a instance passing an instance of the D-Bus system bus into the constructor
calc = Calculator(bus)
mainloop = GLib.MainLoop()
print("waiting for some calculations to do....")
mainloop.run()
