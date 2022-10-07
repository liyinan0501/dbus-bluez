#!/usr/bin/python3

# initiate device scanning and track details of devices discovered and reported in InterfacesAdded signals.
from gi.repository import GLib
import bluetooth_utils
import bluetooth_constants
import dbus
import dbus.mainloop.glib
import sys

sys.path.insert(0, ".")

adapter_interface = None
mainloop = None
timer_id = None

devices = {}

managed_objects_found = 0

def get_known_devices(bus):
    global managed_objects_found
    object_manager = dbus.Interface(bus.get_object(bluetooth_constants.BLUEZ_SERVICE_NAME, '/'), bluetooth_constants.DBUS_OM_IFACE)
    
    managed_objects = object_manager.GetManagedObjects()

    for path, ifaces in managed_objects.items():
        for iface_name in ifaces:
            if iface_name == bluetooth_constants.DEVICE_INTERFACE:
                managed_objects_found += 1
                print("EXI path : ", path)
                device_properties = ifaces[bluetooth_constants.DEVICE_INTERFACE]
                devices[path] = device_properties
                if 'Address' in device_properties:
                    print("EXI bdaddr: ", bluetooth_utils.dbus_to_python(device_properties['Address']))
                    print("------------------------------")


def properties_changed(interface, changed, invalidated, path):
    if interface != bluetooth_constants.DEVICE_INTERFACE:
        return
    if path in devices:
        devices[path] = dict(devices[path].items())
        devices[path].update(changed.items())
    else:
        devices[path] = changed
    
    dev = devices[path]
    print("CHG path :", path)
    if 'Address' in dev:
        print("CHG bdaddr: ", bluetooth_utils.dbus_to_python(dev['Address']))
    if 'Name' in dev:
        print("CHG name : ", bluetooth_utils.dbus_to_python(dev['Name']))
    if 'RSSI' in dev:
        print("CHG RSSI : ", bluetooth_utils.dbus_to_python(dev['RSSI']))
    print("------------------------------")

def interfaces_removed(path, interfaces):
    # interfaces is an array of dictionary entries
    if not bluetooth_constants.DEVICE_INTERFACE in interfaces:
        return
    if path in devices:
        dev = devices[path]
        if 'Address' in dev:
            print('DEL bdaddr: ', bluetooth_utils.dbus_to_python(dev['Address']))
        else:
            print("DEL path : ", path)
            print("------------------------------")
        del devices[path]

# handle InterfacesAdded signals when received
def interfaces_added(path, interfaces):
    # interfaces is an array of dictionary entries
    if not bluetooth_constants.DEVICE_INTERFACE in interfaces:
        return
    device_properties = interfaces[bluetooth_constants.DEVICE_INTERFACE]
    if path not in devices:
        print("NEW path :", path)
        devices[path] = device_properties
        dev = devices[path]

        if "Address" in dev:
            print("NEW bdaddr: ", bluetooth_utils.dbus_to_python(dev["Address"]))
        if "Name" in dev:
            print("NEW name : ", bluetooth_utils.dbus_to_python(dev["Name"]))
        if "RSSI" in dev:
            print("NEW RSSI : ", bluetooth_utils.dbus_to_python(dev["RSSI"]))
        print("------------------------------")

def list_devices_found():
    print("Full list of devices",len(devices),"discovered:")
    print("------------------------------")
    # print(devices['/org/bluez/hci0/dev_88_C9_E8_6B_DD_2C'])
    for path in devices:
        dev = devices[path]
        print(bluetooth_utils.dbus_to_python(dev['Address']))

def discovery_timeout():
    global adapter_interface
    global mainloop
    global timer_id
    # remove the timer
    GLib.source_remove(timer_id)
    # stop event loop
    mainloop.quit()
    # call Bluez for stop discovery
    adapter_interface.StopDiscovery()
    bus = dbus.SystemBus()
    # unregister the InterfacesAdded signal receiver
    bus.remove_signal_receiver(interfaces_added,"InterfacesAdded")
    bus.remove_signal_receiver(interfaces_added,"InterfacesRemoved")
    bus.remove_signal_receiver(properties_changed,"PropertiesChanged")
    list_devices_found()
    return True


def discover_devices(bus, timeout):
    global adapter_interface
    global mainloop
    global timer_id
    adapter_path = (
        bluetooth_constants.BLUEZ_NAMESPACE + bluetooth_constants.ADAPTER_NAME
    )

    # acquire an adapter proxy object and its Adapter1 interface so we can call its methods
    # .get_object(org.bluez, /org/bluez/hci0)
    adapter_object = bus.get_object(
        bluetooth_constants.BLUEZ_SERVICE_NAME, adapter_path
    )
    # acquire the Adapter1 interface
    adapter_interface = dbus.Interface(
        adapter_object, bluetooth_constants.ADAPTER_INTERFACE
    )

    # register signal handler functions so we can asynchronously report discovered devices

    # InterfacesAdded signal is emitted by BlueZ when an advertising packet from a device it doesn't already know about is received
    # add_signal_receiver to indicate to D-Bus that we want to receive InterfacesAdded signals. Note that this signal belongs to the ObjectManager.
    bus.add_signal_receiver(
        interfaces_added,
        dbus_interface=bluetooth_constants.DBUS_OM_IFACE,
        signal_name="InterfacesAdded",
    )

    # Register a InterfacesRemoved to DBus
    # InterfacesRemoved signal is emitted by BlueZ when a device "goes away"
    bus.add_signal_receiver(interfaces_removed, dbus_interface = bluetooth_constants.DBUS_OM_IFACE, signal_name = "InterfacesRemoved")

    # Register a PropertiesChanged to DBus
    bus.add_signal_receiver(properties_changed, dbus_interface=bluetooth_constants.DBUS_PROPERTIES, signal_name='PropertiesChanged',path_keyword = "path")

    mainloop = GLib.MainLoop()
    # discovery_timeout will be called after the timeout elapsed.
    timer_id = GLib.timeout_add(timeout, discovery_timeout)
    adapter_interface.StartDiscovery(byte_arrays=True)

    mainloop.run()


if len(sys.argv) != 2:
    print("usage: python3 client_discover_devices.py [scantime (secs)]")
    sys.exit(1)

scantime = int(sys.argv[1]) * 1000

# dbus initialisation steps
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()

# ask for a list of devices already known to the BlueZ daemon
print("Listing devices already known to BlueZ:")
get_known_devices(bus)
print("Found ",managed_objects_found," managed device objects")

print("Scanning")
discover_devices(bus, scantime)
