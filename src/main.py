import flet as ft

from pages.connect import ConnectionPage
from pages.interface import InterfacePage

def main(page: ft.Page):
    
    page.title = "IEEE Robot Interface"

    connection_page = ConnectionPage()
    interface_page = InterfacePage()

    page.add(ft.Text(f"{page.route}"))
    page.add(connection_page)

    def route_change(e: ft.RouteChangeEvent):
        page.add(ft.Text(f"{e.route}"))
    
    page.on_route_change = route_change
    page.update()


ft.run(main)