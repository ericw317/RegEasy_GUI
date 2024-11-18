import flet as ft
from user_controls.routes import router
from user_controls.app_bar import NavBar
import views.software_page as direct_page
import views.system_page as system_page
import views.sam_page as sam_page
import views.NTUSER_page as NTUSER_page

def main(page: ft.Page):
    page.title = "RegEasy"
    page.window_width = 1350
    page.window_height = 800
    page.theme_mode = "dark"
    page.appbar = NavBar(page)
    page.on_route_change = router.route_change
    router.page = page
    page.add(
        ft.Column([
            router.body
        ],
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
        ), ft.Container(padding=50.5)
    )

    direct_page.get_page(page)
    system_page.get_page(page)
    sam_page.get_page(page)
    NTUSER_page.get_page(page)
    page.go('/')

ft.app(target=main)
