"""
Главный класс приложения с UI
"""

import os
import platform
from datetime import datetime
from typing import List, Optional
import flet as ft
import urllib.request
from core.config import ConfigManager
from core.document_generator import DocumentGenerator
from ui.components import UIComponents
from ui.dialogs import DialogManager
from utils.file_utils import FileManager
from utils.date_utils import format_date_russian


def _create_macos_warning() -> ft.Container:
    """
    Создание предупреждающего баннера для пользователей macOS.

    Returns:
        Контейнер с предупреждением о проблемах с диалогами выбора файлов
    """
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(
                    ft.Icons.INFO,
                    color=ft.Colors.ORANGE_400,
                    size=24,
                ),
                ft.Text(
                    "macOS: Диалоги выбора файлов могут работать "
                    "некорректно. Используйте ручной ввод путей.",
                    color=ft.Colors.ORANGE_700,
                    size=13,
                    weight=ft.FontWeight.W_500,
                ),
            ],
            spacing=10,
        ),
        bgcolor=ft.Colors.ORANGE_50,
        padding=15,
        border_radius=8,
        border=ft.border.all(1, ft.Colors.ORANGE_300),
    )


class MireaReportGenerator:
    """
    Главный класс приложения генератора отчётов для РТУ МИРЭА.

    Управляет всем пользовательским интерфейсом, обрабатывает события,
    координирует работу с файлами, конфигурацией и генерацией документов.
    """

    TEMPLATE_URL = (
        "https://raw.githubusercontent.com/"
        "Vennilay/MireaReportGenerator/main/template.docx"
    )
    AVATAR_URL = "https://avatars.githubusercontent.com/Vennilay"
    REPO_URL = "https://github.com/Vennilay/MireaReportGenerator"

    def __init__(self, page: ft.Page):
        """
        Инициализация приложения.

        Args:
            page: Объект страницы Flet для отрисовки интерфейса
        """
        self.page = page
        self._setup_page()

        self.is_macos = platform.system() == "Darwin"

        self.config_manager = ConfigManager()
        self.file_manager = FileManager()
        self.dialog_manager = DialogManager(page)
        self.ui = UIComponents()

        self.selected_directory: Optional[str] = None
        self.selected_save_directory: Optional[str] = None
        self.found_files: List[str] = []
        self.selected_date: datetime = datetime.now()

        self.group_field: Optional[ft.TextField] = None
        self.student_field: Optional[ft.TextField] = None
        self.teacher_field: Optional[ft.TextField] = None
        self.work_number_field: Optional[ft.TextField] = None

        self.template_path_field: Optional[ft.TextField] = None
        self.template_input_field: Optional[ft.TextField] = None
        self.template_path_display: Optional[ft.Text] = None

        self.date_picker: Optional[ft.DatePicker] = None
        self.date_display: Optional[ft.Text] = None

        self.directory_text: Optional[ft.Text] = None
        self.directory_input_field: Optional[ft.TextField] = None

        self.save_directory_text: Optional[ft.Text] = None
        self.save_directory_input_field: Optional[ft.TextField] = None

        self.save_nearby_checkbox: Optional[ft.Checkbox] = None
        self.files_count_text: Optional[ft.Text] = None
        self.show_files_btn: Optional[ft.ElevatedButton] = None
        self.generate_btn: Optional[ft.ElevatedButton] = None
        self.select_save_dir_btn: Optional[ft.ElevatedButton] = None
        self.apply_save_btn: Optional[ft.ElevatedButton] = None

        self.dir_picker = ft.FilePicker(on_result=self.on_directory_selected)
        self.template_picker = ft.FilePicker(on_result=self.on_template_selected)
        self.save_dir_picker = ft.FilePicker(on_result=self.on_save_directory_selected)

        self.page.overlay.extend(
            [self.dir_picker, self.template_picker, self.save_dir_picker]
        )

        self.create_ui()

    def _setup_page(self) -> None:
        """
        Настройка базовых параметров окна приложения:
        заголовок, размеры, прокрутка, локализация.
        """
        self.page.title = (
            "MIREA Report Generator - Генератор отчётов РТУ МИРЭА"
        )
        self.page.window.width = 900
        self.page.window.height = 800
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.ADAPTIVE
        self.page.locale_configuration = ft.LocaleConfiguration(
            supported_locales=[ft.Locale("ru", "RU")],
            current_locale=ft.Locale("ru", "RU"),
        )

    def create_ui(self) -> None:
        """
        Создание всего пользовательского интерфейса приложения.

        Формирует все секции: заголовок, поля ввода, кнопки,
        собирает их в единый макет и добавляет на страницу.
        """
        config = self.config_manager.config

        header = self.ui.create_header(self.show_about_dialog)

        macos_warning = _create_macos_warning() if self.is_macos else None

        self._create_form_fields(config)

        template_section = self._create_template_section(config)
        date_section = self._create_date_section()
        files_section = self._create_files_section(config)
        save_section = self._create_save_section(config)

        self.generate_btn = self.ui.create_generate_button(
            self.generate_document
        )

        footer = self.ui.create_footer(
            self.AVATAR_URL, self.REPO_URL, self.page
        )

        controls: List[ft.Control] = [header]

        if macos_warning:
            controls.append(macos_warning)

        controls.extend(
            [
                ft.Divider(height=20, color=ft.Colors.BLUE_200),
                ft.Text(
                    "Данные титульного листа:",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                self.group_field,
                self.student_field,
                self.teacher_field,
                self.work_number_field,
                ft.Divider(height=20, color=ft.Colors.BLUE_200),
                template_section,
                ft.Divider(height=20, color=ft.Colors.BLUE_200),
                date_section,
                ft.Divider(height=20, color=ft.Colors.BLUE_200),
                files_section,
                ft.Divider(height=20, color=ft.Colors.BLUE_200),
                save_section,
                ft.Divider(height=20, color=ft.Colors.BLUE_200),
                self.generate_btn,
                footer,
            ]
        )

        main_column = ft.Column(controls, spacing=10)
        self.page.add(ft.Container(content=main_column, padding=20))
        self.validate_form()

    def _create_form_fields(self, config) -> None:
        """
        Создание полей ввода для данных титульного листа.

        Args:
            config: Словарь с сохранённой конфигурацией
        """
        self.group_field = self.ui.create_text_field(
            "Группа (например: ИКБО-47-52)",
            config.get("group", ""),
            ft.Icons.GROUP,
            on_change=lambda _: self.validate_form(),
        )

        self.student_field = self.ui.create_text_field(
            "ФИО студента (например: Иванов И.И.)",
            config.get("student_name", ""),
            ft.Icons.PERSON,
            on_change=lambda _: self.validate_form(),
        )

        self.teacher_field = self.ui.create_text_field(
            "ФИО преподавателя (например: Кодабашян Л.С.)",
            config.get("teacher_name", ""),
            ft.Icons.SCHOOL,
            on_change=lambda _: self.validate_form(),
        )

        self.work_number_field = self.ui.create_number_field(
            "Номер работы",
            config.get("work_number", ""),
            on_change=lambda _: self.validate_form(),
        )

    def _create_template_section(self, config) -> ft.Column:
        """
        Создание секции настройки шаблона документа.

        Включает поля ввода пути, кнопки выбора и скачивания.
        На macOS кнопка выбора файла отключена и окрашена серым.

        Args:
            config: Словарь с сохранённой конфигурацией

        Returns:
            Колонка с элементами управления шаблоном
        """
        self.template_path_field = self.ui.create_text_field(
            "Путь к файлу шаблона (например: template.docx)",
            config.get("template_path", "template.docx"),
            ft.Icons.DESCRIPTION,
            hint="Укажите путь или имя файла шаблона",
        )

        self.template_input_field = ft.TextField(
            label="Или введите полный путь к шаблону",
            hint_text="/Users/username/Documents/template.docx",
            width=400,
            border_color=ft.Colors.PURPLE_400,
            prefix_icon=ft.Icons.EDIT,
            on_change=self.on_template_manual_input,
        )

        select_btn = self._create_file_picker_button(
            "Выбрать файл",
            ft.Icons.FILE_OPEN,
            self.select_template_flet,
            ft.Colors.PURPLE_600,
            "Выбрать файл через диалог",
        )

        download_btn = self.ui.create_button(
            "Скачать с GitHub",
            ft.Icons.DOWNLOAD,
            self.download_template,
            ft.Colors.GREEN_600,
            tooltip="Скачать шаблон template.docx с GitHub",
        )

        self.template_path_display = ft.Text(
            value=f"Текущий шаблон: {config.get('template_path', 'template.docx')}",
            color=ft.Colors.GREY_700,
            size=12,
        )

        buttons_row = ft.Row([select_btn, download_btn], spacing=10)

        if self.is_macos:
            buttons_row.controls.insert(0, self._create_block_icon())

        return ft.Column(
            [
                ft.Text(
                    "Настройки шаблона:",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                self.template_path_field,
                self.template_input_field,
                buttons_row,
                self.template_path_display,
            ],
            spacing=10,
        )

    def _create_date_section(self) -> ft.Column:
        """
        Создание секции выбора даты документа.

        Returns:
            Колонка с календарём и отображением выбранной даты
        """
        self.date_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
            on_change=self.on_date_changed,
            on_dismiss=self.on_date_dismissed,
            help_text="Выберите дату",
            cancel_text="Отмена",
            confirm_text="ОК",
        )
        self.page.overlay.append(self.date_picker)

        self.date_display = ft.Text(
            value=self._format_date(self.selected_date),
            size=16,
            color=ft.Colors.GREEN_700,
            weight=ft.FontWeight.BOLD,
        )

        date_btn = self.ui.create_button(
            "Выбрать дату",
            ft.Icons.CALENDAR_MONTH,
            self.open_date_picker,
            ft.Colors.BLUE_600,
        )

        return ft.Column(
            [
                ft.Text(
                    "Дата документа:",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Row([date_btn, self.date_display], spacing=20),
            ],
            spacing=10,
        )

    def _create_files_section(self, config) -> ft.Column:
        """
        Создание секции выбора директории с файлами кода.

        Поддерживает ручной ввод пути и выбор через диалог (кроме macOS).

        Args:
            config: Словарь с сохранённой конфигурацией

        Returns:
            Колонка с элементами выбора директории
        """
        self.directory_text = ft.Text(
            value="Директория не выбрана",
            color=ft.Colors.GREY_700,
        )

        self.directory_input_field = ft.TextField(
            label="Введите путь к папке с файлами кода",
            hint_text=(
                "/Users/username/Documents/code"
                if self.is_macos
                else "C:\\Users\\username\\code"
            ),
            value=config.get("last_directory", ""),
            width=500,
            border_color=ft.Colors.BLUE_400,
            prefix_icon=ft.Icons.EDIT_LOCATION,
            on_submit=self.on_directory_manual_input,
            on_blur=self.on_directory_manual_input,
        )

        select_btn = self._create_file_picker_button(
            "Выбрать через диалог",
            ft.Icons.FOLDER_OPEN,
            self.select_directory_flet,
            ft.Colors.BLUE_600,
            "Выбрать папку через диалог",
        )

        apply_btn = ft.ElevatedButton(
            "Применить путь",
            icon=ft.Icons.CHECK,
            on_click=self.on_directory_manual_input,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE,
            ),
        )

        self.files_count_text = ft.Text(
            value="Файлы не найдены",
            color=ft.Colors.GREY_600,
            size=14,
        )

        self.show_files_btn = self.ui.create_button(
            "Показать список файлов",
            ft.Icons.LIST,
            self.show_files_dialog,
            ft.Colors.INDIGO_600,
        )
        self.show_files_btn.visible = False

        buttons_row = ft.Row([select_btn, apply_btn], spacing=10)

        if self.is_macos:
            buttons_row.controls.insert(0, self._create_block_icon())

        return ft.Column(
            [
                ft.Text(
                    "Выбор файлов с кодом:",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                self.directory_input_field,
                buttons_row,
                self.directory_text,
                self.files_count_text,
                self.show_files_btn,
            ],
            spacing=10,
        )

    def _create_save_section(self, config) -> ft.Column:
        """
        Создание секции настроек сохранения документа.

        Позволяет выбрать сохранение рядом с программой или в указанной папке.

        Args:
            config: Словарь с сохранённой конфигурацией

        Returns:
            Колонка с элементами настройки места сохранения
        """
        self.save_nearby_checkbox = ft.Checkbox(
            label="Сохранить рядом с программой",
            value=config.get("save_nearby", True),
            on_change=self.on_save_nearby_changed,
            fill_color=ft.Colors.BLUE_600,
        )

        self.save_directory_input_field = ft.TextField(
            label="Или введите путь к папке для сохранения",
            hint_text=(
                "/Users/username/Documents"
                if self.is_macos
                else "C:\\Users\\username\\Documents"
            ),
            value=config.get("save_directory", ""),
            width=500,
            border_color=ft.Colors.TEAL_400,
            prefix_icon=ft.Icons.EDIT_LOCATION,
            on_submit=self.on_save_directory_manual_input,
            on_blur=self.on_save_directory_manual_input,
            disabled=config.get("save_nearby", True),
        )

        is_save_disabled = config.get("save_nearby", True) or self.is_macos
        base_bg = (
            ft.Colors.GREY_400 if self.is_macos else ft.Colors.TEAL_600
        )

        self.select_save_dir_btn = ft.ElevatedButton(
            "Выбрать через диалог"
            + (" (недоступно)" if self.is_macos else ""),
            icon=(
                ft.Icons.FOLDER_SPECIAL
                if not self.is_macos
                else ft.Icons.BLOCK
            ),
            on_click=self.select_save_directory_flet,
            disabled=is_save_disabled,
            style=ft.ButtonStyle(
                bgcolor=(
                    ft.Colors.GREY_300
                    if config.get("save_nearby", True)
                    else base_bg
                ),
                color=(
                    ft.Colors.WHITE
                    if (not self.is_macos and not config.get("save_nearby", True))
                    else ft.Colors.GREY_700
                ),
            ),
            tooltip=(
                "⚠️ На macOS не работает — используйте ручной ввод пути"
                if self.is_macos
                else "Выбрать папку через диалог"
            ),
        )

        self.apply_save_btn = ft.ElevatedButton(
            "Применить путь",
            icon=ft.Icons.CHECK,
            on_click=self.on_save_directory_manual_input,
            disabled=config.get("save_nearby", True),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE,
            ),
        )

        if config.get("save_nearby", True):
            initial_text = "Файл будет сохранён рядом с программой"
            initial_color = ft.Colors.GREY_600
        elif config.get("save_directory", ""):
            self.selected_save_directory = config.get("save_directory", "")
            initial_text = f"Папка сохранения: {self.selected_save_directory}"
            initial_color = ft.Colors.GREEN_700
        else:
            initial_text = "Выберите папку для сохранения"
            initial_color = ft.Colors.ORANGE_700

        self.save_directory_text = ft.Text(
            value=initial_text,
            color=initial_color,
        )

        buttons_row = ft.Row(
            [self.select_save_dir_btn, self.apply_save_btn], spacing=10
        )

        if self.is_macos and not config.get("save_nearby", True):
            buttons_row.controls.insert(0, self._create_block_icon())

        return ft.Column(
            [
                ft.Text(
                    "Место сохранения документа:",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Row([self.save_nearby_checkbox], spacing=10),
                self.save_directory_input_field,
                buttons_row,
                self.save_directory_text,
            ],
            spacing=10,
        )

    def _create_file_picker_button(
        self,
        text: str,
        icon: str,
        on_click,
        color: str,
        tooltip_text: str,
    ) -> ft.ElevatedButton:
        """
        Создание кнопки выбора файла/папки с учётом платформы.

        На macOS кнопка автоматически становится серой и неактивной.

        Args:
            text: Текст кнопки
            icon: Иконка кнопки
            on_click: Обработчик клика
            color: Цвет кнопки (для не-macOS)
            tooltip_text: Текст подсказки

        Returns:
            Кнопка с правильным стилем для текущей платформы
        """
        btn_color = ft.Colors.GREY_400 if self.is_macos else color
        btn_text = text + (" (недоступно)" if self.is_macos else "")
        btn_icon = ft.Icons.BLOCK if self.is_macos else icon

        return ft.ElevatedButton(
            btn_text,
            icon=btn_icon,
            on_click=on_click,
            disabled=self.is_macos,
            style=ft.ButtonStyle(
                bgcolor=btn_color,
                color=(
                    ft.Colors.WHITE
                    if not self.is_macos
                    else ft.Colors.GREY_700
                ),
            ),
            tooltip=(
                "⚠️ На macOS не работает — используйте ручной ввод"
                if self.is_macos
                else tooltip_text
            ),
        )

    @staticmethod
    def _create_block_icon() -> ft.Icon:
        """
        Создание иконки блокировки для macOS.

        Returns:
            Иконка с символом блокировки
        """
        return ft.Icon(
            ft.Icons.BLOCK,
            color=ft.Colors.GREY_500,
            size=20,
            tooltip="Диалоги выбора файлов не работают на macOS",
        )

    def on_directory_manual_input(self, _e) -> None:
        """
        Обработчик ручного ввода пути к директории с кодом.

        Проверяет существование и корректность пути,
        запускает поиск файлов при успешной валидации.
        """
        path = (self.directory_input_field.value or "").strip()
        if not path:
            return

        if not os.path.exists(path):
            self._handle_invalid_directory_path(path, "не существует")
            return

        if not os.path.isdir(path):
            self._handle_invalid_directory_path(path, "не директория")
            return

        self.selected_directory = path
        self.directory_text.value = f"✅ Выбрана: {path}"
        self.directory_text.color = ft.Colors.GREEN_700
        self.find_code_files()
        self.page.update()

        if self.found_files:
            self.dialog_manager.show_snackbar(
                f"✅ Найдено файлов: {len(self.found_files)}",
                ft.Colors.GREEN_700,
            )

    def _handle_invalid_directory_path(self, path: str, reason: str) -> None:
        """
        Обработка некорректного пути к директории.

        Args:
            path: Введённый путь
            reason: Причина ошибки
        """
        self.selected_directory = None
        self.found_files = []
        self.directory_text.value = f"❌ Путь {reason}: {path}"
        self.directory_text.color = ft.Colors.RED_700
        self.files_count_text.value = "❌ Неверный путь"
        self.files_count_text.color = ft.Colors.RED_700
        self.show_files_btn.visible = False
        self.page.update()
        self.validate_form()

    def on_template_manual_input(self, _e) -> None:
        """
        Обработчик ручного ввода пути к файлу шаблона.

        Проверяет существование файла и обновляет отображение.
        """
        path = (self.template_input_field.value or "").strip()
        if not path:
            return

        if not os.path.exists(path):
            self.template_path_display.value = f"❌ Файл не найден: {path}"
            self.template_path_display.color = ft.Colors.RED_700
            self.page.update()
            return

        self.template_path_field.value = path
        self.template_path_display.value = (
            f"✅ Текущий шаблон: {os.path.basename(path)}"
        )
        self.template_path_display.color = ft.Colors.GREEN_700
        self.page.update()
        self.dialog_manager.show_snackbar(
            f"✅ Выбран шаблон: {os.path.basename(path)}",
            ft.Colors.GREEN_700,
        )

    def on_save_directory_manual_input(self, _e) -> None:
        """
        Обработчик ручного ввода пути для сохранения документа.

        Игнорируется если включена опция "Сохранить рядом с программой".
        """
        if self.save_nearby_checkbox.value:
            return

        path = (self.save_directory_input_field.value or "").strip()
        if not path:
            return

        if not os.path.exists(path):
            self._handle_invalid_save_path(path, "не существует")
            return

        if not os.path.isdir(path):
            self._handle_invalid_save_path(path, "не директория")
            return

        self.selected_save_directory = path
        self.save_directory_text.value = f"✅ Папка сохранения: {path}"
        self.save_directory_text.color = ft.Colors.GREEN_700
        self.page.update()
        self.dialog_manager.show_snackbar(
            f"✅ Выбрана папка: {path}",
            ft.Colors.GREEN_700,
        )

    def _handle_invalid_save_path(self, path: str, reason: str) -> None:
        """
        Обработка некорректного пути для сохранения.

        Args:
            path: Введённый путь
            reason: Причина ошибки
        """
        self.selected_save_directory = None
        self.save_directory_text.value = f"❌ Путь {reason}: {path}"
        self.save_directory_text.color = ft.Colors.RED_700
        self.page.update()

    def validate_form(self) -> None:
        """
        Валидация всей формы для активации кнопки генерации.

        Проверяет заполненность всех обязательных полей и наличие файлов.
        Обновляет визуальное состояние кнопки генерации документа.
        """
        if not self.generate_btn:
            return

        is_valid = (
            bool(self.group_field.value and self.group_field.value.strip())
            and bool(
                self.student_field.value and self.student_field.value.strip()
            )
            and bool(
                self.teacher_field.value and self.teacher_field.value.strip()
            )
            and bool(
                self.work_number_field.value
                and self.work_number_field.value.strip()
            )
            and bool(self.found_files)
        )

        self.generate_btn.disabled = not is_valid

        if is_valid:
            self.generate_btn.bgcolor = ft.Colors.GREEN_700
            self.generate_btn.color = ft.Colors.WHITE
            self.generate_btn.opacity = 1.0
        else:
            self.generate_btn.bgcolor = ft.Colors.GREY_400
            self.generate_btn.color = ft.Colors.GREY_700
            self.generate_btn.opacity = 0.6

        self.generate_btn.update()

    def on_save_nearby_changed(self, _e) -> None:
        """
        Обработчик изменения чекбокса "Сохранить рядом с программой".

        Управляет доступностью полей ввода пути и кнопок выбора директории.
        """
        is_nearby = self.save_nearby_checkbox.value

        self.select_save_dir_btn.disabled = is_nearby or self.is_macos
        self.save_directory_input_field.disabled = is_nearby
        self.apply_save_btn.disabled = is_nearby

        if is_nearby:
            self.select_save_dir_btn.style.bgcolor = ft.Colors.GREY_300
            self.select_save_dir_btn.style.color = ft.Colors.GREY_700
            self.save_directory_text.value = (
                "Файл будет сохранён рядом с программой"
            )
            self.save_directory_text.color = ft.Colors.GREY_600
        else:
            if self.is_macos:
                self.select_save_dir_btn.style.bgcolor = ft.Colors.GREY_400
                self.select_save_dir_btn.style.color = ft.Colors.GREY_700
            else:
                self.select_save_dir_btn.style.bgcolor = ft.Colors.TEAL_600
                self.select_save_dir_btn.style.color = ft.Colors.WHITE

            if self.selected_save_directory:
                self.save_directory_text.value = (
                    f"Папка сохранения: {self.selected_save_directory}"
                )
                self.save_directory_text.color = ft.Colors.GREEN_700
            else:
                self.save_directory_text.value = (
                    "Введите путь к папке для сохранения"
                )
                self.save_directory_text.color = ft.Colors.ORANGE_700

        self.page.update()

    def select_directory_flet(self, _e) -> None:
        """
        Открытие диалога выбора директории с кодом.

        На macOS показывает предупреждение вместо диалога.
        """
        if self.is_macos:
            self.dialog_manager.show_alert(
                "Ограничение платформы",
                "На macOS диалоги выбора файлов могут работать некорректно.\n\n"
                "Пожалуйста, используйте ручной ввод пути в текстовое поле.",
            )
            return
        self.dir_picker.get_directory_path(
            dialog_title="Выберите папку с файлами кода"
        )

    def on_directory_selected(self, e: ft.FilePickerResultEvent) -> None:
        """
        Обработчик выбора директории через системный диалог.

        Args:
            e: Событие с результатом выбора пути
        """
        if e.path:
            self.selected_directory = e.path
            self.directory_input_field.value = e.path
            self.directory_text.value = f"Выбрана: {self.selected_directory}"
            self.directory_text.color = ft.Colors.GREEN_700
            self.find_code_files()
            self.page.update()
            self.dialog_manager.show_snackbar(
                f"✅ Найдено файлов: {len(self.found_files)}",
                ft.Colors.GREEN_700,
            )

    def select_template_flet(self, _e) -> None:
        """
        Открытие диалога выбора файла шаблона.

        На macOS показывает предупреждение вместо диалога.
        """
        if self.is_macos:
            self.dialog_manager.show_alert(
                "Ограничение платформы",
                "На macOS диалоги выбора файлов могут работать некорректно.\n\n"
                "Пожалуйста, используйте ручной ввод пути в текстовое поле.",
            )
            return
        self.template_picker.pick_files(
            dialog_title="Выберите файл шаблона DOCX",
            allowed_extensions=["docx"],
            allow_multiple=False,
        )

    def on_template_selected(self, e: ft.FilePickerResultEvent) -> None:
        """
        Обработчик выбора файла шаблона через системный диалог.

        Args:
            e: Событие с результатом выбора файла
        """
        if e.files:
            template_path = e.files[0].path
            self.template_path_field.value = template_path
            self.template_input_field.value = template_path
            self.template_path_display.value = (
                f"Текущий шаблон: {os.path.basename(template_path)}"
            )
            self.template_path_display.color = ft.Colors.GREEN_700
            self.page.update()
            self.dialog_manager.show_snackbar(
                f"✅ Выбран шаблон: {os.path.basename(template_path)}",
                ft.Colors.GREEN_700,
            )

    def select_save_directory_flet(self, _e) -> None:
        """
        Открытие диалога выбора директории для сохранения.

        На macOS показывает предупреждение вместо диалога.
        """
        if self.is_macos:
            self.dialog_manager.show_alert(
                "Ограничение платформы",
                "На macOS диалоги выбора файлов могут работать некорректно.\n\n"
                "Пожалуйста, используйте ручной ввод пути в текстовое поле.",
            )
            return
        self.save_dir_picker.get_directory_path(
            dialog_title="Выберите папку для сохранения документа"
        )

    def on_save_directory_selected(self, e: ft.FilePickerResultEvent) -> None:
        """
        Обработчик выбора директории сохранения через системный диалог.

        Args:
            e: Событие с результатом выбора пути
        """
        if e.path:
            self.selected_save_directory = e.path
            self.save_directory_input_field.value = e.path
            self.save_directory_text.value = (
                f"Папка сохранения: {self.selected_save_directory}"
            )
            self.save_directory_text.color = ft.Colors.GREEN_700
            self.page.update()
            self.dialog_manager.show_snackbar(
                f"✅ Выбрана папка: {self.selected_save_directory}",
                ft.Colors.GREEN_700,
            )

    def download_template(self, _e) -> None:
        """
        Скачивание файла шаблона с GitHub.

        Загружает template.docx из репозитория и сохраняет локально.
        """
        try:
            self.dialog_manager.show_snackbar(
                "⏳ Скачивание шаблона с GitHub...", ft.Colors.BLUE_700
            )

            output_path = "template.docx"
            urllib.request.urlretrieve(self.TEMPLATE_URL, output_path)

            self.template_path_field.value = output_path
            self.template_path_display.value = (
                f"Текущий шаблон: {output_path}"
            )
            self.template_path_display.color = ft.Colors.GREEN_700

            self.page.update()
            self.dialog_manager.show_snackbar(
                "✅ Шаблон успешно скачан с GitHub!", ft.Colors.GREEN_700
            )
            self.dialog_manager.show_alert(
                "Успех! 🎉",
                "Шаблон успешно скачан!\n\n"
                f"Файл сохранён как: {output_path}\n\n"
                "Теперь вы можете использовать его для создания документов.",
            )

        except Exception as e:
            error_message = (
                "Не удалось скачать шаблон:\n\n"
                f"{str(e)}\n\n"
                "Проверьте подключение к интернету."
            )
            self.dialog_manager.show_alert("Ошибка", error_message)
            self.dialog_manager.show_snackbar(
                f"❌ Ошибка скачивания: {str(e)}", ft.Colors.RED_700
            )

    def open_date_picker(self, _e) -> None:
        """Открытие календаря для выбора даты документа."""
        self.page.open(self.date_picker)

    def on_date_changed(self, event) -> None:
        """
        Обработчик изменения даты в календаре.

        Args:
            event: Событие выбора даты
        """
        if event.control.value:
            self.selected_date = event.control.value
            self.date_display.value = self._format_date(self.selected_date)
            self.page.update()
            self.dialog_manager.show_snackbar(
                f"✅ Дата выбрана: {self._format_date(self.selected_date)}",
                ft.Colors.GREEN_700,
            )

    def on_date_dismissed(self, _e) -> None:
        """Обработчик закрытия календаря без выбора даты."""
        pass

    def find_code_files(self) -> None:
        """
        Поиск файлов с кодом в выбранной директории.

        Использует FileManager для рекурсивного поиска файлов
        с поддерживаемыми расширениями (.py, .cpp, .java и т.д.).
        Обновляет счётчик и видимость кнопки списка файлов.
        """
        if not self.selected_directory:
            return

        self.found_files = self.file_manager.find_code_files(
            self.selected_directory
        )

        if self.found_files:
            self.files_count_text.value = (
                f"📁 Найдено файлов: {len(self.found_files)}"
            )
            self.files_count_text.color = ft.Colors.GREEN_700
            self.files_count_text.weight = ft.FontWeight.BOLD
            self.show_files_btn.visible = True
        else:
            self.files_count_text.value = "❌ Файлы с кодом не найдены"
            self.files_count_text.color = ft.Colors.ORANGE_700
            self.show_files_btn.visible = False

        self.validate_form()

    def show_files_dialog(self, _e) -> None:
        """Открытие диалогового окна со списком найденных файлов."""
        self.dialog_manager.show_files_list(self.found_files)

    def show_about_dialog(self, _e) -> None:
        """Открытие диалогового окна "О создателе"."""
        self.dialog_manager.show_about(self.AVATAR_URL, self.REPO_URL)

    def generate_document(self, _e) -> None:
        """
        Основной метод генерации итогового DOCX документа.

        Выполняет:
        1. Валидацию всех полей
        2. Проверку наличия шаблона
        3. Генерацию документа через DocumentGenerator
        4. Сохранение конфигурации
        5. Вывод результата пользователю
        """
        if not self._validate_generation_inputs():
            return

        template_path = (self.template_path_field.value or "").strip() or (
            "template.docx"
        )

        if not os.path.exists(template_path):
            self.dialog_manager.show_alert(
                "Ошибка",
                "Файл шаблона не найден: "
                f"{template_path}\n\n"
                "Убедитесь, что файл существует или укажите правильный путь.",
            )
            return

        self.dialog_manager.show_snackbar(
            "⏳ Создание документа...", ft.Colors.BLUE_700
        )

        try:
            doc_generator = DocumentGenerator(template_path)

            output_filename = doc_generator.generate_filename(
                self.work_number_field.value,
                self.student_field.value,
            )

            output_path = self._determine_output_path(output_filename)
            if not output_path:
                return

            success = doc_generator.generate(
                group=self.group_field.value,
                student_name=self.student_field.value,
                teacher_name=self.teacher_field.value,
                work_number=self.work_number_field.value,
                date=self.selected_date,
                code_files=self.found_files,
                output_path=output_path,
            )

            if success:
                self._save_current_config()
                self._show_success_message(output_path)
            else:
                self.dialog_manager.show_alert(
                    "Ошибка",
                    "Не удалось создать документ. Проверьте логи.",
                )

        except Exception as ex:
            error_message = (
                "Произошла ошибка при создании документа:\n\n" f"{str(ex)}"
            )
            self.dialog_manager.show_alert("Ошибка", error_message)
            self.dialog_manager.show_snackbar(
                f"❌ Ошибка: {str(ex)}", ft.Colors.RED_700
            )

    def _validate_generation_inputs(self) -> bool:
        """
        Валидация всех обязательных полей перед генерацией.

        Returns:
            True если все поля заполнены, False иначе
        """
        validations = [
            (self.group_field.value, "Группа"),
            (self.student_field.value, "ФИО студента"),
            (self.teacher_field.value, "ФИО преподавателя"),
            (self.work_number_field.value, "Номер работы"),
        ]

        for value, field_name in validations:
            if not value:
                self.dialog_manager.show_alert(
                    "Ошибка", f"Заполните поле '{field_name}'!"
                )
                return False

        if not self.found_files:
            self.dialog_manager.show_alert(
                "Ошибка",
                "Не выбраны файлы с кодом! Выберите директорию с файлами.",
            )
            return False

        return True

    def _determine_output_path(self, filename: str) -> Optional[str]:
        """
        Определение финального пути для сохранения документа.

        Args:
            filename: Имя выходного файла

        Returns:
            Полный путь для сохранения или None при ошибке
        """
        if self.save_nearby_checkbox.value:
            return filename

        if not self.selected_save_directory:
            self.dialog_manager.show_alert(
                "Ошибка",
                "Не выбрана папка для сохранения!\n\n"
                "Выберите папку или включите опцию "
                "'Сохранить рядом с программой'.",
            )
            return None

        return os.path.join(self.selected_save_directory, filename)

    def _show_success_message(self, output_path: str) -> None:
        """
        Отображение сообщения об успешной генерации документа.

        Args:
            output_path: Путь к созданному документу
        """
        absolute_path = os.path.abspath(output_path)
        self.dialog_manager.show_alert(
            "Успех! 🎉",
            "Документ успешно создан!\n\n"
            f"Имя файла: {os.path.basename(output_path)}\n\n"
            f"Путь: {absolute_path}",
        )
        self.dialog_manager.show_snackbar(
            f"✅ Документ создан: {os.path.basename(output_path)}",
            ft.Colors.GREEN_700,
        )

    def _save_current_config(self) -> None:
        """
        Сохранение текущих настроек в конфигурационный файл.

        Записывает все введённые данные для автоматического
        заполнения при следующем запуске приложения.
        """
        config_data = {
            "group": self.group_field.value,
            "student_name": self.student_field.value,
            "teacher_name": self.teacher_field.value,
            "work_number": self.work_number_field.value,
            "last_directory": self.selected_directory or "",
            "template_path": self.template_path_field.value,
            "save_directory": self.selected_save_directory or "",
            "save_nearby": self.save_nearby_checkbox.value,
        }
        self.config_manager.save(config_data)

    @staticmethod
    def _format_date(date: datetime) -> str:
        """
        Форматирование даты в русском формате для отображения.

        Args:
            date: Объект datetime

        Returns:
            Строка вида: «13» ноября 2025
        """
        return format_date_russian(date)