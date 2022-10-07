#!/usr/bin/python3

# 1-Calling Methods
# -retrieves the Hostname property from the org.freedesktop.hostname1 DBus service
import dbus

# 1.connect to the DBuse system bus
bus = dbus.SystemBus()
# 2.create a proxy
# .get_object(service, object)
proxy = bus.get_object("org.freedesktop.hostname1", "/org/freedesktop/hostname1")
# 3.obtain a reference to org.freedesktop.DBus.Properties
interface = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")

# 4.call interface Get method
# .Get(service, Properties)
hostname = interface.Get("org.freedesktop.hostname1", "Hostname")
print("The host name is ", hostname)

# all_props = interface.GetAll("org.freedesktop.hostname1")
# print(all_props)
