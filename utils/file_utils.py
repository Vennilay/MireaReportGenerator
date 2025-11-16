"""
Утилиты для работы с файлами
"""

import os
from typing import List


class FileManager:
    """
    Менеджер для работы с файлами
    """

    CODE_EXTENSIONS = [
        ".py",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".java",
        ".js",
        ".kt",
        ".go",
        ".rs",
    ]

    @classmethod
    def find_code_files(cls, directory: str) -> List[str]:
        found_files: List[str] = []

        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if any(file.endswith(ext) for ext in cls.CODE_EXTENSIONS):
                        full_path = os.path.join(root, file)
                        found_files.append(full_path)
        except Exception as e:
            print(f"Ошибка при поиске файлов: {str(e)}")

        return found_files

    @staticmethod
    def read_file(file_path: str, encoding: str = "utf-8") -> str:
        try:
            with open(file_path, "r", encoding=encoding, errors="ignore") as f:
                return f.read()
        except Exception as e:
            return (
                f"[Ошибка чтения файла: {os.path.basename(file_path)}\n"
                f"Причина: {str(e)}]"
            )

    @staticmethod
    def file_exists(file_path: str) -> bool:
        return os.path.exists(file_path)

    @staticmethod
    def get_filename(file_path: str) -> str:
        return os.path.basename(file_path)

    @staticmethod
    def get_directory(file_path: str) -> str:
        return os.path.dirname(file_path)
