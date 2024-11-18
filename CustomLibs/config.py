import os
from CustomLibs import ShadowCopies
from CustomLibs import InputValidation as IV
import shutil

timezone = "America/New_York"

# set path
def set_path(artifact_path, drive):
    if "[root]" in os.listdir(drive):
        path = drive + f"[root]\\{artifact_path}"
    else:
        path = drive + artifact_path

    return path

# copy locked registry files
def copy_locked_reg(reg_file, user=None):
    # set path
    if not user:
        reg_path = f"Windows\\System32\\config\\{reg_file}"
    else:
        reg_path = f"Users\\{user}\\NTUSER.DAT"

    try:
        # create shadow copy
        ShadowCopies.create_shadow_copy()
        shadow_copy_path = ShadowCopies.get_latest_shadow_copy()
        reg_source = os.path.join(shadow_copy_path, reg_path)
        destination_path = os.path.join(os.getcwd(), f"{reg_file}_copy")

        # copy reg file from shadow copy
        shutil.copy(reg_source, destination_path)

        # delete shadow copy
        shadow_ID = ShadowCopies.get_latest_shadow_copy_id()
        ShadowCopies.delete_shadow_copy(shadow_ID)
    except Exception:
        print("Error: Make sure you are running as administrator.")

# copy registry files from mounted drive
def copy_reg(drive, reg_file, user=None):
    # set path
    if not user:
        reg_source = f"{drive}[root]\\Windows\\System32\\config\\{reg_file}"
    else:
        reg_source = f"{drive}[root]\\Users\\{user}\\NTUSER.DAT"
    destination_path = os.path.join(os.getcwd(), f"{reg_file}_copy")

    # copy reg file
    shutil.copy(reg_source, destination_path)

# ask to output to file
def file_ask(output, output_path):
    response = IV.yes_or_no("Save output to file? (y/n)\n")
    if response:
        with open(output_path, 'w') as file:
            for line in output:
                file.write(line + '\n')
