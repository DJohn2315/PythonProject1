import flet as ft

from pages.connect import ConnectionPage
from pages.interface import InterfacePage

def main(page: ft.Page):
    
    page.title = "IEEE Robot Interface"

    connection_page = ConnectionPage()
    interface_page = InterfacePage()

    page.add(connection_page)


ft.run(main)