from Registry import Registry
from CustomLibs import time_conversion as TC
from CustomLibs import display_functions
import pytz
from datetime import timezone
from CustomLibs import config
import os
import struct
import io
import sys
import re
from impacket.examples.secretsdump import LocalOperations, SAMHashes

def key_value_exists(user_key, value_name):
    try:
        # Try to access the value
        user_key.value(value_name)
        return True
    except Registry.RegistryValueNotFoundException:
        # Value doesn't exist
        return False

# parse account data
def parse_account_data(data):
    # Extract information based on offsets and formats
    header = data[0:8]  # Offset 00-07
    last_login_time = struct.unpack_from("<Q", data, 8)[0]  # Offset 08-15
    last_password_change = struct.unpack_from("<Q", data, 24)[0]  # Offset 24-31
    last_incorrect_password_date = struct.unpack_from("<Q", data, 40)[0]  # Offset 40-47
    invalid_login_count = struct.unpack_from("<H", data, 64)[0]  # Offset 64
    total_login_count = struct.unpack_from("<H", data, 66)[0]  # Offset 66

    # Convert FILETIME timestamps to datetime
    last_login_time = str(TC.filetime_convert(last_login_time))
    last_password_change = str(TC.filetime_convert(last_password_change))
    last_incorrect_password_date = str(TC.filetime_convert(last_incorrect_password_date))

    if last_login_time.startswith(("1601", "1600")):
        last_login_time = ""
    if last_password_change.startswith(("1601", "1600")):
        last_password_change = ""
    if last_incorrect_password_date.startswith(("1601", "1600")):
        last_incorrect_password_date = ""

    return {
        "Header": header,
        "Last Login Time": last_login_time,
        "Last Password Change": last_password_change,
        "Last Incorrect Password Date": last_incorrect_password_date,
        "Invalid Login Count": invalid_login_count,
        "Total Login Count": total_login_count,
    }

# Extract and return NTLM hashes as a dictionary
def extract_ntlm_hashes(sam_hive, system_hive):
    try:
        # Initialize LocalOperations to extract SYSKEY from SYSTEM hive
        local_operations = LocalOperations(system_hive)
        boot_key = local_operations.getBootKey()  # SYSKEY

        # Initialize SAMHashes with the SAM hive and SYSKEY
        sam_hashes = SAMHashes(sam_hive, boot_key, isRemote=False)

        # Redirect stdout to capture dump output
        output = io.StringIO()
        sys.stdout = output
        sam_hashes.dump()

        # Clear secrets (good practice)
        sam_hashes.finish()

        # Reset stdout to default
        sys.stdout = sys.__stdout__

        # Get the captured output as a string
        hashes_output = output.getvalue()
        output.close()

        # Parse the output to extract usernames and hashes
        hash_dict = {}
        for line in hashes_output.splitlines():
            match = re.match(r"^(.+):([A-Fa-f0-9]{32})", line)
            if match:
                username = match.group(1).strip()
                ntlm_hash = match.group(2).strip()
                hash_dict[username] = ntlm_hash

        cleaned_hashes_dict = {}
        for username, ntlm_hash in hash_dict.items():
            clean_username = username.split(':')[0]
            cleaned_hashes_dict[clean_username] = ntlm_hash

        return cleaned_hashes_dict
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def parse_sam(reg, drive=None):
    sam_list = []

    # search names
    names_key = reg.open(r"SAM\Domains\Account\Users\Names")
    for user in names_key.subkeys():
        user_name = user.name()
        user_SID = int(user.value("").value_type())

        # get creation date and convert timezone
        creation_date = (user.timestamp()).replace(microsecond=0)  # creation date
        utc_creation_date = creation_date.replace(tzinfo=timezone.utc)  # make it UTC-aware
        creation_date = utc_creation_date.astimezone(pytz.timezone(config.timezone))  # convert to timezone

        # search through Users key
        hex_SID = f"{user_SID:08X}"
        user_key = reg.open(rf"SAM\Domains\Account\Users\{hex_SID}")

        # get name
        if key_value_exists(user_key, "GivenName"):
            name = (user_key.value("GivenName").value()).decode('utf-16')
        else:
            name = ""

        if key_value_exists(user_key, "Surname"):
            surname = (user_key.value("Surname").value()).decode('utf-16')
        else:
            surname = ""

        name = f"{name} {surname}"

        # get internet username
        if key_value_exists(user_key, "InternetUserName"):
            internet_username = (user_key.value("InternetUserName").value()).decode('utf-16')
        else:
            internet_username = ""

        # parse account data
        data = parse_account_data(user_key.value("F").value())
        last_login = data["Last Login Time"]
        last_password_change = data["Last Password Change"]
        last_incorrect_password = data["Last Incorrect Password Date"]
        invalid_login_count = data["Invalid Login Count"]
        total_login_count = data["Total Login Count"]

        # get NTLM hash
        if drive is not None:
            # copy SYSTEM file
            if not os.path.exists("SYSTEM_copy"):
                if drive == "C:\\":
                    config.copy_locked_reg("SYSTEM")
                elif drive != "C:\\" and len(drive) < 4:
                    config.copy_reg(drive, "SYSTEM")

            hashes_dict = extract_ntlm_hashes("SAM_copy", "SYSTEM_copy")
            user_ntlm_hash = ""
            for username, ntlm_hash in hashes_dict.items():
                if username == user_name:
                    user_ntlm_hash = ntlm_hash
        else:
            user_ntlm_hash = "Unavailable"

        sam_list.append(
            [user_name, str(user_SID), name, internet_username, str(creation_date), str(last_login),
             str(last_password_change), str(last_incorrect_password), str(invalid_login_count), str(total_login_count),
             str(user_ntlm_hash)])

    # delete copies
    if os.path.exists("SYSTEM_copy"):
        os.remove("SYSTEM_copy")

    # display values
    output = display_functions.eleven_values("Username", "SID", "Name", "Internet User Name",
                                             "Creation Date", "Last Login Time", "Last Password Change",
                                             "Last Incorrect Password Date", "Invalid Login Count",
                                             "Total Login Count", "NTLM Hash", sam_list)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output
