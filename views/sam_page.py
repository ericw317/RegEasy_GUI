import flet as ft
from CustomLibs import general
from CustomLibs import config
from Registry import Registry
from CustomLibs import SAM_functions as SF
import os

# functions
def clear_fields():
    dd_drives.value = None
    t_registry_file.value = None

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

def parse_SAM():
    full_output = ""
    if dd_drives.value is not None and dd_drives.value != "":
        try:
            open_dlg_loading()
            # copy SYSTEM file
            if dd_drives.value == "C:\\" and not os.path.exists("SAM_copy"):
                config.copy_locked_reg("SAM")
            elif dd_drives.value != "C:\\" and len(dd_drives.value) < 4:
                config.copy_reg(dd_drives.value, "SAM")

            # initialize registry object
            reg = Registry.Registry("SAM_copy")

            # parse output
            full_output = SF.parse_sam(reg, dd_drives.value)

            # export data
            export_data(full_output)
            if os.path.exists("SAM_copy"):
                os.remove("SAM_copy")

            dlg_loading.open = False
            page_var.update()
        except Exception as e:
            dlg_loading.open = False
            page_var.update()
            open_error(f"Unable to parse drive: {e}")
    elif t_registry_file.value is not None and t_registry_file.value != "":
        if general.identify_registry_hive(t_registry_file.value) == "SAM":
            open_dlg_loading()

            # initialize registry object
            reg = Registry.Registry(t_registry_file.value)

            # parse output
            full_output = SF.parse_sam(reg)

            # export data
            export_data(full_output)
            if os.path.exists("SAM_copy"):
                os.remove("SAM_copy")
            dlg_loading.open = False
            page_var.update()
        else:
            open_error("Invalid SAM File.")
    else:
        open_error("No drive or registry file selected.")

def export_data(data):
    with open("SAM Data.txt", 'w') as file:
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
    "Parse SAM",
    height=50, width=250,
    on_click=lambda _: parse_SAM()
)

# dialogues
dlg_pick_file = ft.FilePicker(on_result=lambda e: get_file(e))
dlg_loading = ft.AlertDialog(
    title=ft.Text("Extracting Data"),
    content=ft.ProgressRing(width=16, height=16, stroke_width=2)
)
dlg_error = ft.AlertDialog(title=ft.Text("Error"))


def sam_page(router):
    content = ft.Column([
        ft.Row([
            ft.Text("SAM", size=40)
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            dd_drives, t_registry_file, b_registry_file
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            b_parse
        ], alignment=ft.MainAxisAlignment.CENTER),
    ], alignment=ft.MainAxisAlignment.START)

    return content
