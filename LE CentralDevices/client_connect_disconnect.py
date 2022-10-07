#!/usr/bin/python3
#
# Connects to a specified device
# Run from the command line with a bluetooth device address argument
import bluetooth_constants
import bluetooth_utils
import dbus
import sys
import time
sys.path.insert(0, '.')

bus = None
device_interface = None

def connect(device_path):
    global bus
    global device_interface
    try:
        device_interface.Connect()
    except Exception as e:
        print("Failed to connect")
        print(e.get_dbus_name())
        print(e.get_dbus_message())
        if ("UnknownObject" in e.get_dbus_name()):
            print("Try scanning first to resolve this problem")
        return bluetooth_constants.RESULT_EXCEPTION
    else:
        print("Connected OK")
        return bluetooth_constants.RESULT_OK

def disconnect():
    global bus
    global device_interface
    try:
        device_interface.Disconnect()
    except Exception as e:
        print('Failed to disconnect')
        print(e.get_dbus_name())
        print(e.get_dbus_message())
        return bluetooth_constants.RESULT_EXCEPTION
    else:
        print("Disconnected OK")
        return bluetooth_constants.RESULT_OK


if (len(sys.argv) != 2):
    print("usage: python3 client_connect_disconnect.py [bdaddr]")
    sys.exit(1)

bdaddr = sys.argv[1]
bus = dbus.SystemBus()
adapter_path = bluetooth_constants.BLUEZ_NAMESPACE + bluetooth_constants.ADAPTER_NAME
device_path = bluetooth_utils.device_address_to_path(bdaddr, adapter_path)
device_proxy = bus.get_object(bluetooth_constants.BLUEZ_SERVICE_NAME,device_path)
device_interface = dbus.Interface(device_proxy,bluetooth_constants.DEVICE_INTERFACE)
print("Connecting to " + bdaddr)
connect(device_path)
# time.sleep(30)
# print(f'Disconnecting from {bdaddr}')
# disconnect()

# getting the properties from the bluetooth devices
device_properties = dbus.Interface(device_proxy, bluetooth_constants.DBUS_PROPERTIES)
print(device_properties.Get(bluetooth_constants.DEVICE_INTERFACE,'Name'))
print(device_properties.Get(bluetooth_constants.DEVICE_INTERFACE,'Address'))
print(device_properties.Get(bluetooth_constants.DEVICE_INTERFACE,'Connected'))