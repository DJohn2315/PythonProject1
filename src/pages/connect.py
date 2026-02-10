import flet as ft
from client import connect_client

class ConnectionPage(ft.Column):
    def init(self):

        self.error_text = ft.Text(
            value="",
            color=ft.Colors.RED
        )

        self.ip_input = ft.TextField(
                hint_text="10.227.93.XXX"
            )

        self.controls=[
            ft.Text("Connect to IP Address"),
            self.ip_input,
            self.error_text,
            ft.Button(
                content="Connect",
                on_click=lambda e: self.connect_client_to_server(self.ip_input.value)
            )
        ]
    
    def connect_client_to_server(self, ip):
        print(f"Attempting Connection to {ip}")
        connection = connect_client(ip)
        if "Error" in connection:
            self.error_text.value = connection
        else:
            self.error_text.value = ""
            if connection == "Connection established":
                self._page.route = "/interface"
            