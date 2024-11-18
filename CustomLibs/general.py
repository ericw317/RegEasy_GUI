from CustomLibs import InputValidation as IV
import psutil
from Registry import Registry

def list_drives():
    partitions = psutil.disk_partitions()
    drives = []

    # add each drive to a dictionary and enumerate each entry
    for partition in partitions:
        drives.append(partition.device)

    return drives

# identify hive
def identify_registry_hive(filepath):
    try:
        reg = Registry.Registry(filepath)
        root_keys = [key.name() for key in reg.root().subkeys()]

        if "ControlSet001" in root_keys:
            return "SYSTEM"
        elif "Microsoft" in root_keys:
            return "SOFTWARE"
        elif "Policy" in root_keys and "SAM" in root_keys:
            return "SECURITY"
        elif "SAM" in root_keys:
            return "SAM"
        elif "Software" in root_keys:
            return "NTUSER.DAT"
        else:
            return "Unknown registry hive"
    except Exception as e:
        return "Not a registry file"
