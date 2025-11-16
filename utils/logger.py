"""
Модуль для подробного логирования всех операций приложения
"""

import os
import logging
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler


class AppLogger:
    """
    Централизованная система логирования для MIREA Report Generator

    Поддерживает:
    - Включение/выключение логирования
    - Настраиваемый путь к файлам логов
    - Ротацию логов (автоматическое создание новых файлов)
    - Форматирование с временными метками
    - Разные уровни логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """

    _instance: Optional['AppLogger'] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls):
        """Singleton pattern - только один экземпляр логгера"""
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Инициализация логгера (вызывается только при первом создании)"""
        if self._logger is None:
            self._logger = logging.getLogger("MireaReportGenerator")
            self._logger.setLevel(logging.DEBUG)
            self._enabled = True
            self._log_path = "logs"
            self._initialized = False

    def configure(self, enabled: bool = True, log_path: str = "logs"):
        """
        Настройка параметров логирования

        Args:
            enabled: Включить/выключить логирование
            log_path: Путь к директории с логами
        """
        self._enabled = enabled
        self._log_path = log_path

        if self._initialized:
            self._logger.handlers.clear()
            self._initialized = False

        if self._enabled:
            self._setup_logger()

    def _setup_logger(self):
        """Настройка обработчиков логов и форматирования"""
        if self._initialized:
            return

        try:
            os.makedirs(self._log_path, exist_ok=True)
        except Exception as e:
            print(f"⚠️ Не удалось создать директорию для логов: {e}")
            self._enabled = False
            return

        log_formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        session_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = os.path.join(
            self._log_path,
            f"mirea_generator_{session_time}.log"
        )

        try:
            file_handler = RotatingFileHandler(
                log_filename,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(log_formatter)
            self._logger.addHandler(file_handler)

            # Также вывод в консоль для разработки
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(log_formatter)
            self._logger.addHandler(console_handler)

            self._initialized = True

            self.info("=" * 70)
            self.info("MIREA Report Generator - Новый сеанс")
            self.info(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.info(f"Файл лога: {log_filename}")
            self.info("=" * 70)

        except Exception as e:
            print(f"⚠️ Ошибка инициализации логгера: {e}")
            self._enabled = False

    def _log(self, level: int, message: str):
        """
        Внутренний метод для записи в лог

        Args:
            level: Уровень логирования
            message: Сообщение для записи
        """
        if self._enabled and self._initialized:
            self._logger.log(level, message)

    def debug(self, message: str):
        """Логирование отладочной информации"""
        self._log(logging.DEBUG, message)

    def info(self, message: str):
        """Логирование информационных сообщений"""
        self._log(logging.INFO, message)

    def warning(self, message: str):
        """Логирование предупреждений"""
        self._log(logging.WARNING, message)

    def error(self, message: str):
        """Логирование ошибок"""
        self._log(logging.ERROR, message)

    def critical(self, message: str):
        """Логирование критических ошибок"""
        self._log(logging.CRITICAL, message)

    def log_operation(self, operation: str, details: str = ""):
        """
        Логирование операции с деталями

        Args:
            operation: Название операции
            details: Дополнительные детали
        """
        if details:
            self.info(f"[ОПЕРАЦИЯ] {operation}: {details}")
        else:
            self.info(f"[ОПЕРАЦИЯ] {operation}")

    def log_exception(self, operation: str, exception: Exception):
        """
        Логирование исключения с контекстом

        Args:
            operation: Название операции где произошла ошибка
            exception: Объект исключения
        """
        self.error(f"[ИСКЛЮЧЕНИЕ] {operation}: {type(exception).__name__}: {str(exception)}")

    def log_file_operation(self, operation: str, filepath: str, status: str = "успешно"):
        """
        Логирование файловых операций

        Args:
            operation: Тип операции (чтение, запись, создание и т.д.)
            filepath: Путь к файлу
            status: Статус операции
        """
        self.info(f"[ФАЙЛ] {operation} | {os.path.basename(filepath)} | {status}")
        self.debug(f"  └─ Полный путь: {filepath}")

    def is_enabled(self) -> bool:
        """Проверка, включено ли логирование"""
        return self._enabled


logger = AppLogger()
