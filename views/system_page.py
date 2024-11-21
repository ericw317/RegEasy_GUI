import flet as ft
from CustomLibs import general
from CustomLibs import config
from Registry import Registry
from CustomLibs import SYSTEM_functions as SF
import os

# functions
def clear_fields():
    dd_drives.value = None
    t_registry_file.value = None
    c_computer_name.value = False
    c_timezone_info.value = False
    c_USB_devices.value = False
    c_USB_storage.value = False
    c_last_shutdown.value = False

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
        t_registry_file.update()
        dd_drives.update()
    else:
        "Cancelled"

def drive_change(e):
    t_registry_file.value = None
    t_registry_file.update()

def parse_SYSTEM():
    full_output = ""
    if dd_drives.value is not None and dd_drives.value != "":
        try:
            open_dlg_loading()
            # copy SYSTEM file
            if dd_drives.value == "C:\\" and not os.path.exists("SYSTEM_copy"):
                config.copy_locked_reg("SYSTEM")
            elif dd_drives.value != "C:\\" and len(dd_drives.value) < 4:
                config.copy_reg(dd_drives.value, "SYSTEM")

            # initialize registry object
            reg = Registry.Registry("SYSTEM_copy")

            # parse output
            if c_computer_name.value:
                full_output += SF.parse_computer_name(reg)
            if c_timezone_info.value:
                full_output += SF.parse_timezone(reg)
            if c_USB_devices.value:
                full_output += SF.parse_USB_devices(reg)
            if c_USB_storage.value:
                full_output += SF.parse_USB_storage(reg)
            if c_last_shutdown.value:
                full_output += SF.parse_last_shutdown(reg)

            # export data
            export_data(full_output)
            if os.path.exists("SYSTEM_copy"):
                os.remove("SYSTEM_copy")
            dlg_loading.open = False
            page_var.update()
        except Exception as e:
            dlg_loading.open = False
            page_var.update()
            open_error(f"Unable to parse drive: {e}")
    elif t_registry_file.value is not None and t_registry_file.value != "":
        if general.identify_registry_hive(t_registry_file.value) == "SYSTEM":
            open_dlg_loading()

            # initialize registry object
            reg = Registry.Registry(t_registry_file.value)

            # parse output
            if c_computer_name.value:
                full_output += SF.parse_computer_name(reg)
            if c_timezone_info.value:
                full_output += SF.parse_timezone(reg)
            if c_USB_devices.value:
                full_output += SF.parse_USB_devices(reg)
            if c_USB_storage.value:
                full_output += SF.parse_USB_storage(reg)
            if c_last_shutdown.value:
                full_output += SF.parse_last_shutdown(reg)

            # export data
            export_data(full_output)
            if os.path.exists("SYSTEM_copy"):
                os.remove("SYSTEM_copy")
            dlg_loading.open = False
            page_var.update()
        else:
            open_error("Invalid SYSTEM File.")
    else:
        open_error("No drive or registry file selected.")

def export_data(data):
    output_path = os.path.join(config.output_path, "SYSTEM Data.txt")
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


# variables
drives = general.list_drives()

# dropdowns
dd_drives = ft.Dropdown(
    label="Drives",
    options=[],
    on_change=drive_change
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
    "Parse System",
    height=50, width=250,
    on_click=lambda _: parse_SYSTEM()
)

# checkboxes
c_computer_name = ft.Checkbox(label="Computer Name")
c_timezone_info = ft.Checkbox(label="Timezone Info")
c_USB_devices = ft.Checkbox(label="USB Devices")
c_USB_storage = ft.Checkbox(label="USB Storage")
c_last_shutdown = ft.Checkbox(label="Last Shutdown")

# dialogues
dlg_pick_file = ft.FilePicker(on_result=lambda e: get_file(e))
dlg_loading = ft.AlertDialog(
    title=ft.Text("Extracting Data"),
    content=ft.ProgressRing(width=16, height=16, stroke_width=2)
)
dlg_error = ft.AlertDialog(title=ft.Text("Error"))


def system_page(router):
    content = ft.Column([
        ft.Row([
            ft.Text("SYSTEM", size=40)
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            dd_drives, t_registry_file, b_registry_file
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            c_computer_name, c_timezone_info, c_USB_devices, c_USB_storage, c_last_shutdown
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            b_parse
        ], alignment=ft.MainAxisAlignment.CENTER),
    ], alignment=ft.MainAxisAlignment.START)


    return content
