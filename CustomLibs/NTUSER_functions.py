from CustomLibs import time_conversion as TC
from CustomLibs import InputValidation as IV
from CustomLibs import display_functions
import re
from CustomLibs import config
import codecs
import pytz
from datetime import timezone
import string

def decode_rot13(string):
    return codecs.decode(string, 'rot13')

def decode_data(data):
    if len(data) >= 12:
        last_executed_filetime = int.from_bytes(data[60:68], byteorder="little")
        return last_executed_filetime
    return None

def sanitize_name(name):
    if "{0139D44E-6AFE-49F2-8690-3DAFCAE6FFB8}" in name:
        return name.replace("{0139D44E-6AFE-49F2-8690-3DAFCAE6FFB8}", "{Common Programs}")
    elif "{9E3995AB-1F9C-4F13-B827-48B24B6C7174}" in name:
        return name.replace("{9E3995AB-1F9C-4F13-B827-48B24B6C7174}", "{User Pinned}")
    elif "{A77F5D77-2E2B-44C3-A6A2-ABA601054A51}" in name:
        return name.replace("{A77F5D77-2E2B-44C3-A6A2-ABA601054A51}", "{Programs}")
    else:
        return name

def find_lnk_guid_path(user_assist_key):
    # Search for the GUID containing LNK files (".yax" in ROT13)
    for GUID in user_assist_key.subkeys():
        for Count in GUID.subkeys():
            for value in Count.values():
                if value.name().endswith(".yax"):
                    clean_path = (user_assist_key.path()).split("Software", 1)[-1]
                    return f"Software{clean_path}\\{GUID.name()}\\Count"
    return None

def filter_printable_characters(s):
    # Filter and return only printable characters from the string
    return ''.join(c for c in s if c in string.printable)

def valid_first_character(s):
    # Check if the string is empty or if the first character is not printable
    return bool(s) and s[0] in string.ascii_letters + string.digits + string.punctuation


def split_paths(line):
    # Regex pattern to find the start of a drive letter (e.g., C:\, D:\)
    drive_pattern = r"([A-Z]:\\)"

    # Find all matches for the drive pattern in the line
    matches = list(re.finditer(drive_pattern, line))

    if len(matches) > 1:
        # If there are two drive letter matches, split at the start of the second one
        path1 = line[:matches[1].start()].strip()
        path2 = line[matches[1].start():].strip()
    else:
        # If only one path is present, set path1 and leave path2 empty
        path1 = line.strip()
        path2 = ""

    return path1, path2


def split_paths_run(input_string):
    # Regex to capture text within quotes and the remaining part
    match = re.match(r'"([^"]+)"\s*(.*)', input_string)

    if match:
        string1 = match.group(1)  # The path inside the quotes
        string2 = match.group(2)  # The remaining part
        return [string1, string2]
    else:
        return None, None  # If the format doesn't match

def is_ip_address(s):
    # Check if the string matches an IP address pattern
    parts = s.split('.')
    if len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
        return True
    return False

def clean_file_name(file_name):
    # List of valid file extensions
    valid_extensions = ['exe', 'lnk', 'txt', 'pdf', 'jpg', 'png', 'docx', 'xlsx', 'mp4', 'mp3', 'zip', '001',
                        '002', '7z', 'aax', 'aep', 'aes', 'appinstaller', 'App', 'asc', 'automaticDestinations-ms',
                        'avif', 'avi', 'bak', 'bin', 'bmp', 'cap', 'chr', 'com', 'conf', 'copy0', 'cpp', 'cryptomator',
                        'css', 'csv', 'dat', 'dcr', 'dd', 'djvu', 'dotx', 'E01', 'E02', 'E03', 'E04', 'E05', 'eps',
                        'epub', 'evtx', 'fb2', 'FBX', 'gif', 'gz', 'hccr', 'html', 'htm', 'hve', 'img', 'ini', 'iso',
                        'jar', 'jpeg', 'json', 'js', 'kdbx', 'LOG1', 'LOG2', 'log', 'm4a', 'm4b', 'm4v', 'md', 'mem',
                        'mht', 'mhtml', 'minecraft', 'mkv', 'mov', 'mpg', 'msix', 'netxml', 'NEW', 'obj', 'odt', 'ogg',
                        'org', 'ova', 'ovpn', 'pcap', 'pm', 'pot', 'pptx', 'ppt', 'ps1', 'psd', 'PWL', 'py', 'rar',
                        'raw', 'rtf', 'sav', 'sfap0', 'sfk', 'sfv', 'sh', 'sqlite', 'srt', 'tmp', 'torrent', 'ttf',
                        'ui', 'var', 'vbox', 'veg', 'VirtualBox', 'wav', 'webm', 'webp', 'WidgetsApp', 'wmv', 'xml',
                        'yaml', 'zim', 'zsh', '1', '0', '2', '8']

    # Split the filename by the first period
    parts = file_name.split('.', 1)  # Split into [filename, rest of the string]

    # Check if there is a second part and if it starts with a valid extension
    if len(parts) > 1:
        # Loop through valid extensions and see if any match the start of the second part
        for ext in valid_extensions:
            if parts[1].startswith(ext):
                return f"{parts[0]}.{ext}"  # Return only the filename with the valid extension
    return parts[0]  # Return the filename without extension if no valid extension found

# parse recent docs
def parse_recent_docs(reg, all=False):
    key = reg.open(r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs")
    recent_docs_list = []

    # collect file names and extensions
    for extension in key.subkeys():
        for file in extension.values():
            file_extension = extension.name()
            file_name = (file.value()).decode('utf-16')
            if valid_first_character(file_name):
                file_name = filter_printable_characters(file_name)

                if not is_ip_address(file_name.split('/')[0]):
                    # Split by "." and rejoin only the first two parts
                    parts = file_name.split('.')
                    if len(parts) > 1:
                        file_name = '.'.join(parts[:2])  # Keeps everything up to the second period
                    else:
                        file_name = parts[0]  # In case there's only one part

                    file_name = clean_file_name(file_name)
                else:
                    file_name = file_name.split('/')[0]
                recent_docs_list.append([file_extension, file_name])

    # display data
    output = ["RECENT DOCS"]
    output += display_functions.two_values("Extension", "File", recent_docs_list)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output

# parse ComDlg32
def parse_comdlg32(reg, all=False):
    CID_success = False
    first_folder_success = False
    try:
        # parse CIDSizeMRU
        key = reg.open(r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\CIDSizeMRU")
        CID_program_list = []
        CIDSizeMRU_list = []
        # add CIDSizeMRU programs to list
        for program in key.values():
            program_name = (program.value()).decode('utf-16')
            if valid_first_character(program_name):
                program_name = filter_printable_characters(program_name)
                CID_program_list.append(program_name)

        # reverse list
        CID_program_list.reverse()

        # add values to full list
        for position, program in enumerate(CID_program_list):
            CIDSizeMRU_list.append([program, str(position)])

        # display output
        CID_output = ["CID SIZE MRU"]
        CID_output += display_functions.two_values("Executable", "MRU Position", CIDSizeMRU_list)

        CID_success = True
    except Exception:
        pass

    try:
        # parse FirstFolder
        key = reg.open(r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\FirstFolder")
        program_list = []
        first_folder_list = []
        for program in key.values():
            program_name = (program.value()).decode('utf-16')

            # get filtered names
            if valid_first_character(program_name):
                program_name = filter_printable_characters(program_name)
                program_list.append(program_name)

        # reverse program list
        program_list.reverse()

        # split paths for each entry
        for position, program in enumerate(program_list):
            path1, path2 = split_paths(program)
            first_folder_list.append([path1, path2, str(position)])

        # display output
        first_folder_output = ["FIRST FOLDER"]
        first_folder_output += display_functions.three_values("Executable", "Folder Name", "MRU Position",
                                                              first_folder_list)

        first_folder_success = True
    except Exception:
        pass

    if CID_success and first_folder_success:
        outputs = CID_output + first_folder_output
    elif CID_success and not first_folder_success:
        outputs = CID_output
    elif not CID_success and first_folder_success:
        outputs = first_folder_output
    else:
        outputs = []

    formatted_output = "\n".join(outputs) + "\n"
    return formatted_output

# parse user assist
def parse_user_assist(reg, all=False):
    key = reg.open(r"Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist")
    user_assist_list = []

    # get path with lnk files
    lnk_guid = find_lnk_guid_path(key)
    if lnk_guid is None:
        return 0

    # collect contents of LNK GUID folder
    lnk_guid = reg.open(lnk_guid)
    for value in lnk_guid.values():
        if (value.name()).endswith(".yax"):
            # name full path of program
            path = decode_rot13(value.name())

            # sanitize names
            path = sanitize_name(path)

            last_execution = TC.filetime_convert(decode_data(value.value()))  # last execution date

            # add data to list
            if path.endswith(".lnk"):
                path = path[:-4]
            user_assist_list.append([path, str(last_execution)])

    # display data
    output = ["USER ASSIST"]
    output += display_functions.two_values("File Path", "Last Executed", user_assist_list)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output

# parse typed paths
def parse_typed_paths(reg, all=False):
    key = reg.open(r"Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths")
    typed_paths_list = []

    for value in key.values():
        typed_paths_list.append(value.value())

    # display data
    output = display_functions.one_value("TYPED PATHS", typed_paths_list)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output

# parse mount points
def parse_mount_points(reg, all=False):
    key = reg.open(r"Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2")
    mount_list = []

    for subkey in key.subkeys():
        if not (subkey.name()).startswith("{"):
            # get mount point
            mount_point = subkey.name()

            # get timestamp and convert
            timestamp = (subkey.timestamp()).replace(microsecond=0)
            utc_timestamp = timestamp.replace(tzinfo=timezone.utc)  # make it UTC-aware
            timestamp = utc_timestamp.astimezone(pytz.timezone(config.timezone))  # convert to timezone

            # add to list
            mount_list.append([mount_point, str(timestamp)])

    # display values
    output = ["MOUNT POINTS"]
    output += display_functions.two_values("Mount Point", "Timestamp", mount_list)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output

# parse run
def parse_run(reg, all=False):
    key = reg.open(r"Software\Microsoft\Windows\CurrentVersion\Run")
    run_list = []

    for application in key.values():
        # get app name and data
        app_name = application.name()
        app_data = application.value()

        # if mode is available, get mode
        if app_data.startswith('"'):
            app_path, run_mode = split_paths_run(app_data)
        else:
            app_path = app_data
            run_mode = ""

        run_list.append([app_name, app_path, run_mode])

    # display data
    output = ["RUN"]
    output += display_functions.three_values("App Name", "Path", "Run Mode", run_list)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output

# parse IE URLs
def parse_IE_urls(reg, all=False):
    try:
        key = reg.open(r"Software\Microsoft\Internet Explorer\TypedURLs")
        urls = []

        for URL in key.values():
            urls.append(URL.value())

        # display data
        output = display_functions.one_value("INTERNET EXPLORER TYPED URLs", urls)
    except:
        output = []

    formatted_output = "\n".join(output) + "\n"
    return formatted_output
