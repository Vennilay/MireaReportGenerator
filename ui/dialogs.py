"""
Модуль для работы с диалоговыми окнами
"""

import os
from typing import List

import flet as ft


class DialogManager:
    """
    Менеджер диалоговых окон
    """

    def __init__(self, page: ft.Page):
        self.page = page

    def show_snackbar(self, message: str, color: str = ft.Colors.BLUE_700):
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE, size=14),
            bgcolor=color,
            duration=3000,
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.margin.only(top=10, left=20, right=20),
        )
        self.page.overlay.insert(0, snackbar)
        snackbar.open = True
        self.page.update()

    def show_alert(self, title: str, message: str):
        def close_dialog(_e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, weight=ft.FontWeight.BOLD),
            content=ft.Text(message),
            actions=[
                ft.TextButton("ОК", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def show_files_list(self, files: List[str]):
        def close_dialog(_e):
            dialog.open = False
            self.page.update()

        files_list_view = ft.ListView(
            spacing=5,
            padding=10,
            height=400,
            width=600,
        )

        if files:
            files_list_view.controls.append(
                ft.Container(
                    content=ft.Text(
                        f"📁 Найдено файлов: {len(files)}",
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                        size=16,
                    ),
                    bgcolor=ft.Colors.BLUE_700,
                    padding=12,
                    border_radius=8,
                )
            )

            for idx, file_path in enumerate(files, 1):
                files_list_view.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(
                                    f"{idx}.",
                                    size=14,
                                    color=ft.Colors.BLUE_400,
                                    weight=ft.FontWeight.BOLD,
                                    width=40,
                                ),
                                ft.Icon(
                                    ft.Icons.CODE,
                                    size=20,
                                    color=ft.Colors.BLUE_300,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            os.path.basename(file_path),
                                            size=14,
                                            color=ft.Colors.WHITE,
                                            weight=ft.FontWeight.W_500,
                                        ),
                                        ft.Text(
                                            os.path.dirname(file_path),
                                            size=11,
                                            color=ft.Colors.GREY_400,
                                            italic=True,
                                        ),
                                    ],
                                    spacing=2,
                                    tight=True,
                                ),
                            ],
                            spacing=10,
                        ),
                        padding=12,
                        border_radius=6,
                        bgcolor=ft.Colors.GREY_800,
                        border=ft.border.all(1, ft.Colors.GREY_700),
                    )
                )
        else:
            files_list_view.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.WARNING_AMBER,
                                color=ft.Colors.ORANGE_400,
                                size=28,
                            ),
                            ft.Text(
                                "Файлы с кодом не найдены",
                                color=ft.Colors.ORANGE_300,
                                weight=ft.FontWeight.W_500,
                                size=14,
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=20,
                    bgcolor=ft.Colors.GREY_800,
                    border_radius=8,
                )
            )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Список найденных файлов",
                weight=ft.FontWeight.BOLD,
                size=20,
            ),
            content=ft.Container(
                content=files_list_view,
                bgcolor=ft.Colors.GREY_900,
                border_radius=8,
                padding=10,
            ),
            actions=[
                ft.TextButton("Закрыть", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def show_about(self, avatar_url: str, repo_url: str):
        def close_dialog(_e):
            dialog.open = False
            self.page.update()

        def open_github(_e):
            self.page.launch_url("https://github.com/Vennilay")

        def open_repo(_e):
            self.page.launch_url(repo_url)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "О создателе 👨‍💻",
                weight=ft.FontWeight.BOLD,
                size=20,
            ),
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.CircleAvatar(
                            foreground_image_src=avatar_url,
                            radius=50,
                            bgcolor=ft.Colors.BLUE_700,
                        ),
                        alignment=ft.alignment.center,
                        padding=ft.padding.only(bottom=15),
                    ),
                    ft.Text(
                        "MIREA Report Generator",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(height=10),
                    ft.Text(
                        "Генератор отчётов для студентов РТУ МИРЭА",
                        size=14,
                        color=ft.Colors.GREY_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        "Разработчик: Vennilay",
                        size=14,
                        weight=ft.FontWeight.W_500,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=10),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "GitHub Profile",
                                icon=ft.Icons.PERSON,
                                on_click=open_github,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.GREY_800,
                                    color=ft.Colors.WHITE,
                                ),
                            ),
                            ft.ElevatedButton(
                                "Repository",
                                icon=ft.Icons.CODE,
                                on_click=open_repo,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.BLUE_700,
                                    color=ft.Colors.WHITE,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        "© 2025 Vennilay",
                        size=12,
                        color=ft.Colors.GREY_500,
                        italic=True,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                tight=True,
                spacing=5,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            actions=[
                ft.TextButton("Закрыть", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
