"""
Переиспользуемые UI компоненты
"""

from typing import Callable, Optional

import flet as ft


class UIComponents:
    """
    Класс для создания переиспользуемых UI компонентов
    """

    @staticmethod
    def create_header(about_callback: Callable) -> ft.Row:
        return ft.Row(
            [
                ft.Text(
                    "MIREA Report Generator",
                    size=26,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700,
                ),
                ft.IconButton(
                    icon=ft.Icons.INFO_OUTLINED,
                    tooltip="О создателе",
                    on_click=about_callback,
                    icon_color=ft.Colors.BLUE_600,
                    icon_size=28,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    @staticmethod
    def create_text_field(
        label: str,
        value: str,
        icon: str,
        on_change: Optional[Callable] = None,
        hint: Optional[str] = None,
        width: int = 400,
    ) -> ft.TextField:
        return ft.TextField(
            label=label,
            value=value,
            width=width,
            border_color=ft.Colors.BLUE_400,
            prefix_icon=icon,
            on_change=on_change,
            hint_text=hint,
        )

    @staticmethod
    def create_number_field(
        label: str,
        value: str,
        on_change: Optional[Callable] = None,
        width: int = 200,
    ) -> ft.TextField:
        return ft.TextField(
            label=label,
            value=value,
            width=width,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.BLUE_400,
            prefix_icon=ft.Icons.NUMBERS,
            on_change=on_change,
        )

    @staticmethod
    def create_button(
        text: str,
        icon: str,
        on_click: Callable,
        color: str,
        tooltip: Optional[str] = None,
    ) -> ft.ElevatedButton:
        return ft.ElevatedButton(
            text,
            icon=icon,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor=color,
                color=ft.Colors.WHITE,
            ),
            tooltip=tooltip,
        )

    @staticmethod
    def create_generate_button(on_click: Callable) -> ft.ElevatedButton:
        return ft.ElevatedButton(
            "Создать DOCX документ",
            icon=ft.Icons.DESCRIPTION,
            on_click=on_click,
            disabled=True,
            bgcolor=ft.Colors.GREY_400,
            color=ft.Colors.GREY_700,
            width=300,
            height=50,
            opacity=0.6,
            animate_opacity=300,
        )

    @staticmethod
    def create_footer(
        avatar_url: str,
        repo_url: str,
        page: ft.Page,
    ) -> ft.Container:
        def open_repo(_e):
            page.launch_url(repo_url)

        return ft.Container(
            content=ft.Row(
                [
                    ft.CircleAvatar(
                        foreground_image_src=avatar_url,
                        radius=12,
                        bgcolor=ft.Colors.BLUE_700,
                    ),
                    ft.Text(
                        "Made with ❤️ by Vennilay",
                        size=12,
                        color=ft.Colors.GREY_600,
                        italic=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=ft.padding.only(top=20, bottom=10),
            on_click=open_repo,
            tooltip="Открыть репозиторий на GitHub",
        )
