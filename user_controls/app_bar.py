import flet as ft
import views.software_page as directory_page


def NavBar(page):
    NavBar = ft.Dropdown(
        label="Registry",
        width=150,
        value="SYSTEM",
        on_change=lambda _: change(),
        options=[
            ft.dropdown.Option("SYSTEM"),
            ft.dropdown.Option("SOFTWARE"),
            ft.dropdown.Option("SAM"),
            ft.dropdown.Option("NTUSER.DAT"),
            ft.dropdown.Option("Settings")
        ]
    )

    def change():
        directory_page.clear_fields()
        if NavBar.value == "SYSTEM":
            navigation = "/"
        elif NavBar.value == "SOFTWARE":
            navigation = "/software_page"
        elif NavBar.value == "SAM":
            navigation = "/sam_page"
        elif NavBar.value == "NTUSER.DAT":
            navigation = "/ntuser_page"
        elif NavBar.value == "Settings":
            navigation = "/settings"
        page.go(navigation)

    return NavBar