"""
Утилиты для работы с датами
"""

from datetime import datetime


def format_date_russian(date: datetime) -> str:
    """
    Форматирование даты в русский формат
    """
    months = {
        1: "января",
        2: "февраля",
        3: "марта",
        4: "апреля",
        5: "мая",
        6: "июня",
        7: "июля",
        8: "августа",
        9: "сентября",
        10: "октября",
        11: "ноября",
        12: "декабря",
    }
    return f"«{date.day}» {months[date.month]} {date.year}"


def get_current_date() -> datetime:
    """
    Получение текущей даты
    """
    return datetime.now()
