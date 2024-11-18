from CustomLibs import display_functions
from CustomLibs import config
from CustomLibs import time_conversion as TC
from datetime import datetime as dt
import datetime
import pytz
import struct

def filetime_to_datetime(filetime_bytes):
    # Unpack the bytes as a little-endian 64-bit integer
    filetime_int = int.from_bytes(filetime_bytes, byteorder='little')

    # Convert FILETIME to a datetime object
    # FILETIME epoch is January 1, 1601, so we calculate from that date
    windows_epoch = datetime.datetime(1601, 1, 1)
    timestamp = windows_epoch + datetime.timedelta(microseconds=filetime_int // 10)

    return timestamp.replace(microsecond=0)

def convert_timezone(timestamp):
    # Parse the timestamp into a naive datetime object
    naive_datetime = dt.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

    # set naive timezone
    original_timezone = pytz.timezone("UTC")
    localized_datetime = original_timezone.localize(naive_datetime)

    # Convert to the target timezone (e.g., 'US/Eastern')
    target_timezone = pytz.timezone(config.timezone)
    converted_datetime = localized_datetime.astimezone(target_timezone)

    return converted_datetime

# parse computer name
def parse_computer_name(reg, all=False):
    key = reg.open("ControlSet001\\Control\\ComputerName\\ComputerName")
    computer_name_list = []
    computer_name_list.append(key.value("ComputerName").value())
    output = display_functions.one_value("Computer Name", computer_name_list)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output

# parse timezone
def parse_timezone(reg, all=False):
    key = reg.open(r"ControlSet001\Control\TimeZoneInformation")
    timezone_list = []

    # get timezone data
    timezone_key_name = key.value("TimeZoneKeyName").value()
    bias = key.value("Bias").value()
    if bias >= 2**31:
        bias = bias - 2**32

    daylight_bias = key.value("DaylightBias").value()
    if daylight_bias >= 2**31:
        daylight_bias = daylight_bias - 2**32

    active_time_bias = key.value("ActiveTimeBias").value()
    if active_time_bias >= 2**31:
        active_time_bias = active_time_bias - 2**32

    # append to timezone list
    timezone_list.append([timezone_key_name, str(bias), str(daylight_bias), str(active_time_bias)])

    # display data
    output = ["TIME ZONE INFORMATION"]
    output += display_functions.four_values("Timezone Key Name", "Bias", "Daylight Bias",
                                           "Active Time Bias", timezone_list)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output

# get USB information
def parse_USB_devices(reg, all=False):
    key = reg.open("ControlSet001\\Enum\\USB")
    USB_list = []

    for vid_key in key.subkeys():
        for device_key in vid_key.subkeys():
            try:
                timestamp_collection = ""
                try:
                    friendly_name = device_key.value("FriendlyName").value()
                except Exception:
                    friendly_name = ""
                device_name = device_key.value("DeviceDesc").value()
                for properties in device_key.subkeys():
                    for guid in properties.subkeys():
                        for folder in guid.subkeys():
                            for value in folder.values():
                                try:
                                    timestamp = str(filetime_to_datetime(value.raw_data()))
                                    timestamp = str(convert_timezone(timestamp))
                                    if not timestamp.startswith("1601") and not timestamp.startswith("1600"):
                                        if len(timestamp_collection) == 0:
                                            timestamp_collection = timestamp
                                        else:
                                            timestamp_collection += f" :: {timestamp}"
                                except Exception:
                                    pass
                    if timestamp_collection != "":
                        USB_list.append([device_name, friendly_name, timestamp_collection])
            except Exception:
                pass

    USB_list.sort(key=lambda x: x[1], reverse=True)
    output = ["USB DEVICES"]
    output += display_functions.three_values("Device Name", "Friendly Name", "Timestamps", USB_list)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output

# get USB storage
def parse_USB_storage(reg, all=False):
    USB_storage_list = []
    key = reg.open("ControlSet001\\Enum\\USBSTOR")

    for device in key.subkeys():  # search device key
        first_installed, last_connected, last_removed, device_name = "", "", "", ""
        for serial_num in device.subkeys():  # search serial number key
            try:
                device_name = serial_num.value("FriendlyName").value()
            except Exception:
                continue
            for folder in serial_num.subkeys():  # search folders under serial_num key
                if folder.name() == "Properties":  # only search the "Properties" subkey
                    for guid in folder.subkeys():  # look through guid subkeys
                        for data in guid.subkeys():  # look through all the folders in the guid subkey
                            if data.name() == "0064":  # search for "first installed" time
                                try:
                                    first_installed = data.value("(default)").value()
                                    first_installed = str(first_installed)[:19]
                                    first_installed = str(convert_timezone(first_installed))
                                except Exception:
                                    first_installed = ""
                            elif data.name() == "0066":  # search for "last connected"
                                try:
                                    last_connected = data.value("(default)").value()
                                    last_connected = str(last_connected)[:19]
                                    last_connected = str(convert_timezone(last_connected))
                                except Exception:
                                    last_connected = ""
                            elif data.name() == "0067":  # search for "last removed"
                                try:
                                    last_removed = data.value("(default)").value()
                                    last_removed = str(last_removed)[:19]
                                    last_removed = str(convert_timezone(last_removed))
                                except Exception:
                                    last_removed = ""

        USB_storage_list.append([device_name, first_installed, last_connected, last_removed])

    if ['', '', '', ''] in USB_storage_list:
        USB_storage_list.remove(['', '', '', ''])

    output = ["USB STORAGE"]
    output += display_functions.four_values("Device Name", "First Installed", "Last Connected", "Last Removed",
                                           USB_storage_list)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output

# parse last shutdown time
def parse_last_shutdown(reg, all=False):
    shutdown = []
    key = reg.open("ControlSet001\\Control\\Windows")
    data = key.value("ShutdownTime").value()
    decoded_data = struct.unpack("<Q", data)[0]
    timestamp = str(TC.filetime_convert(decoded_data))
    shutdown.append(timestamp)

    output = display_functions.one_value("Last Shutdown", shutdown)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output
