import flet as ft
from CustomLibs import general
from CustomLibs import config
from Registry import Registry
from CustomLibs import NTUSER_functions as NF
import os

# functions
def clear_fields():
    dd_drives.value = None
    t_registry_file.value = None
    dd_users.value = None
    c_recent_docs.value = None
    c_comdlg32.value = None
    c_user_assist.value = None
    c_typed_paths.value = None
    c_mount_points.value = None
    c_run.value = None
    c_IE_typed_URLs.value = None
    dd_users.options = []

def get_page(page):
    global page_var
    page_var = page
    page_var.overlay.append(dlg_pick_file)
    page_var.overlay.append(dlg_loading)
    page_var.overlay.append(dlg_error)

def get_file(e: ft.FilePickerResultEvent):
    if e.files:
        file_path = e.files[0].path
        t_registry_file.value = file_path
        dd_drives.value = None
        dd_users.value = None
        dd_users.options = []
        t_registry_file.update()
        dd_drives.update()
        dd_users.update()
    else:
        "Cancelled"

def drive_change(e):
    # set registry file to None
    t_registry_file.value = None
    t_registry_file.update()

    # populate user list
    users = get_users(dd_drives.value)
    for user in users:
        dd_users.options.append(ft.dropdown.Option(user))
    dd_users.update()

def parse_NTUSER():
    full_output = ""
    if dd_drives.value is not None and dd_drives.value != "" and dd_users.value is not None and dd_users.value != "":
        try:
            open_dlg_loading()
            # copy NTUSER file
            if dd_drives.value == "C:\\" and not os.path.exists("NTUSER_copy"):
                config.copy_locked_reg("NTUSER", dd_users.value)
            elif dd_drives.value != "C:\\":
                config.copy_reg(dd_drives.value, "NTUSER", dd_users.value)

            # initialize registry object
            reg = Registry.Registry("NTUSER_copy")

            # parse output
            if c_recent_docs.value:
                full_output += NF.parse_recent_docs(reg)
            if c_comdlg32.value:
                full_output += NF.parse_comdlg32(reg)
            if c_user_assist.value:
                full_output += NF.parse_user_assist(reg)
            if c_typed_paths.value:
                full_output += NF.parse_typed_paths(reg)
            if c_mount_points.value:
                full_output += NF.parse_mount_points(reg)
            if c_run.value:
                full_output += NF.parse_run(reg)
            if c_IE_typed_URLs.value:
                full_output += NF.parse_IE_urls(reg)

            # export data
            export_data(full_output)
            if os.path.exists("NTUSER_copy"):
                os.remove("NTUSER_copy")

            dlg_loading.open = False
            page_var.update()
        except Exception as e:
            dlg_loading.open = False
            page_var.update()
            open_error(f"Unable to parse drive: {e}")
    elif t_registry_file.value is not None and t_registry_file.value != "":
        if general.identify_registry_hive(t_registry_file.value) == "NTUSER.DAT":
            open_dlg_loading()

            # initialize registry object
            reg = Registry.Registry(t_registry_file.value)

            # parse output
            if c_recent_docs.value:
                full_output += NF.parse_recent_docs(reg)
            if c_comdlg32.value:
                full_output += NF.parse_comdlg32(reg)
            if c_user_assist.value:
                full_output += NF.parse_user_assist(reg)
            if c_typed_paths.value:
                full_output += NF.parse_typed_paths(reg)
            if c_mount_points.value:
                full_output += NF.parse_mount_points(reg)
            if c_run.value:
                full_output += NF.parse_run(reg)
            if c_IE_typed_URLs.value:
                full_output += NF.parse_IE_urls(reg)

            # export data
            export_data(full_output)
            dlg_loading.open = False
            page_var.update()
        else:
            open_error("Invalid NTUSER.DAT File.")
    else:
        open_error("Invalid input. Select a drive AND user, or select a registry file.")

def export_data(data):
    output_path = os.path.join(config.output_path, "NTUSER Data.txt")
    with open(output_path, 'w') as file:
        file.write(data)

def open_dlg_loading(e=None):
    page_var.dialogue = dlg_loading
    dlg_loading.open = True
    page_var.update()

def open_error(error_message, e=None):
    dlg_error.content = ft.Text(error_message)
    page_var.dialog = dlg_error
    dlg_error.open = True
    page_var.update()

def get_users(drive):
    dd_users.options = []
    user_list = []
    exclusion_list = ["All Users", "Default", "Default User", "Public"]
    try:
        if drive == "C:\\":
            users_path = f"{drive}Users"
        else:
            users_path = f"{drive}[root]\\Users"

        for user in os.listdir(users_path):
            full_path = os.path.join(users_path, user)
            if os.path.isdir(full_path) and user not in exclusion_list:
                user_list.append(user)
    except Exception:
        user_list = []

    return user_list


# variables
drives = general.list_drives()

# dropdowns
dd_drives = ft.Dropdown(
    label="Drives",
    options=[],
    on_change=drive_change
)
dd_users = ft.Dropdown(
    label="Users",
    options=[]
)
# populate dd_drives
for drive in drives:
    dd_drives.options.append(ft.dropdown.Option(drive))

# text fields
t_registry_file = ft.TextField(label="Registry File", read_only=True)

# buttons
b_registry_file = ft.ElevatedButton(
    "Select Registry File",
    height=50,
    on_click=lambda _: dlg_pick_file.pick_files()
)
b_parse = ft.ElevatedButton(
    "Parse NTUSER.DAT",
    height=50, width=250,
    on_click=lambda _: parse_NTUSER()
)

# checkboxes
c_recent_docs = ft.Checkbox(label="Recent Docs")
c_comdlg32 = ft.Checkbox(label="ComDlg32")
c_user_assist = ft.Checkbox(label="User Assist")
c_typed_paths = ft.Checkbox(label="Typed Paths")
c_mount_points = ft.Checkbox(label="Mount Points")
c_run = ft.Checkbox(label="Run")
c_IE_typed_URLs = ft.Checkbox(label="IE Typed URLs")


# dialogues
dlg_pick_file = ft.FilePicker(on_result=lambda e: get_file(e))
dlg_loading = ft.AlertDialog(
    title=ft.Text("Extracting Data"),
    content=ft.ProgressRing(width=16, height=16, stroke_width=2)
)
dlg_error = ft.AlertDialog(title=ft.Text("Error"))


def ntuser_page(router):
    content = ft.Column([
        ft.Row([
            ft.Text("NTUSER.DAT", size=40)
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            dd_drives, t_registry_file, b_registry_file
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            ft.Text(" " * int(61.75)), dd_users
        ], alignment=ft.MainAxisAlignment.START),
        ft.Row([
            c_recent_docs, c_comdlg32, c_user_assist, c_typed_paths, c_mount_points, c_run, c_IE_typed_URLs
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            b_parse
        ], alignment=ft.MainAxisAlignment.CENTER),
    ], alignment=ft.MainAxisAlignment.START)

    return content
