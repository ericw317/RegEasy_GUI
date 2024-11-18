from CustomLibs import display_functions
from CustomLibs import config
from CustomLibs import time_conversion as TC
from Registry import Registry
import struct
from datetime import datetime
import pytz

def format_date(date_str):
    # Ensure the input is a string and exactly 8 characters long
    if len(date_str) != 8 or not date_str.isdigit():
        raise ValueError("Date must be in YYYYMMDD format")

    # Extract the year, month, and day parts
    year = date_str[:4]
    month = date_str[4:6]
    day = date_str[6:]

    # Format the date as YYYY-MM-DD
    formatted_date = f"{year}-{month}-{day}"
    return formatted_date

# decode date
def decode_date(date_bytes):
    # Unpack the data in little-endian format
    year, month, unknown, day, hour, minute, second, _ = struct.unpack('<HHHHHHHH', date_bytes)

    # Construct datetime object
    dt_utc = datetime(year, month, day, hour, minute, second, tzinfo=pytz.UTC)

    # Convert to the target timezone
    dt_converted = dt_utc.astimezone(pytz.timezone("America/New_York"))

    return dt_converted

# parse operating system information
def parse_OS_info(reg, all=False):
    key = reg.open(r"Microsoft\Windows NT\CurrentVersion")
    OS_info_list = []

    product_name = key.value("ProductName").value()
    install_date = key.value("InstallDate").value()
    install_date = str(TC.convert_unix_epoch_seconds(install_date))
    registered_owner = key.value("RegisteredOwner").value()

    OS_info_list.append([product_name, install_date, registered_owner])

    # print values
    output = ["OPERATING SYSTEM INFORMATION"]
    output += display_functions.three_values("Product Name", "Install Date", "Registered Owner",
                                            OS_info_list)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output

# parse last logged on user
def parse_last_logged_on_user(reg, all=False):
    key = reg.open(r"Microsoft\Windows\CurrentVersion\Authentication\LogonUI")
    user = []

    last_user = str(key.value("LastLoggedOnUser").value())
    last_user = last_user.replace(".\\", "")
    user.append(last_user)

    # print values
    output = display_functions.one_value("LAST LOGGED ON USER", user)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output

# parse installed apps
def parse_installed_applications(reg, all=False):
    key = reg.open(r"Microsoft\Windows\CurrentVersion\Uninstall")
    installed_applications_list = []
    for application in key.subkeys():
        try:
            # check values
            display_name = application.value("DisplayName").value()
            publisher = application.value("Publisher").value()
            install_date = format_date(application.value("InstallDate").value())
            install_location = application.value("InstallLocation").value()
            # add to lists
            installed_applications_list.append([display_name, publisher, install_date, install_location])
        except Registry.RegistryValueNotFoundException:
            pass

    # print values and write to file
    output = ["INSTALLED APPLICATIONS"]
    output += display_functions.four_values("Display Name", "Publisher", "Install Date",
                                           "Install Location", installed_applications_list)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output

# parse installed apps
def parse_autostart_programs(reg, all=False):
    key = reg.open(r"Microsoft\Windows\CurrentVersion\Run")
    autostart_programs_list = []

    for program in key.values():
        try:
            # check values
            program_name = program.name()
            install_location = program.value()
            # add to list
            autostart_programs_list.append([program_name, install_location])
        except Registry.RegistryValueNotFoundException:
            pass

    # print values
    output = ["AUTOSTART PROGRAMS"]
    output += display_functions.two_values("Program Name", "Install Location", autostart_programs_list)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output

# parse network list
def parse_network_list(reg, all=False):
    key = reg.open(r"Microsoft\Windows NT\CurrentVersion\NetworkList\Profiles")
    network_list = []

    for profile in key.subkeys():
        # get profile name
        network_name = profile.value("ProfileName").value()

        # get profile type
        network_type = profile.value("NameType").value()
        if network_type == 6:
            network_type = "Wired"
        elif network_type == 71:
            network_type = "Wireless"
        elif network_type == 53:
            network_type = "Virtual"
        else:
            network_type = "Unknown"

        # get first and last connected dates
        first_connected = str(decode_date(profile.value("DateCreated").value()))
        last_connected = str(decode_date(profile.value("DateLastConnected").value()))

        network_list.append([network_name, network_type, first_connected, last_connected])

    # display values
    output = ["NETWORK LIST"]
    output += display_functions.four_values("Network Name", "Type", "First Connected",
                                           "Last Connected", network_list)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output

# parse svchost services
def parse_svchost(reg, all=False):
    key = reg.open(r"Microsoft\Windows NT\CurrentVersion\Svchost")
    svchost_list = []

    for service in key.values():
        service_name = service.name()
        svchost_list.append(service_name)

    output = display_functions.one_value("SVCHOST SERVICES", svchost_list)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output
