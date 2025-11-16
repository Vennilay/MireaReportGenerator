import flet as ft
from ui.app import MireaReportGenerator


def main(page: ft.Page):
    MireaReportGenerator(page)


if __name__ == "__main__":
    ft.app(target=main)
