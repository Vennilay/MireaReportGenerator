import os
from typing import List
from utils.logger import logger


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
        logger.log_operation("Поиск файлов с кодом", f"Директория: {directory}")
        found_files: List[str] = []

        try:
            file_count_by_ext = {}

            for root, dirs, files in os.walk(directory):
                logger.debug(f"Сканирование: {root}")
                for file in files:
                    if any(file.endswith(ext) for ext in cls.CODE_EXTENSIONS):
                        full_path = os.path.join(root, file)
                        found_files.append(full_path)

                        ext = os.path.splitext(file)[1]
                        file_count_by_ext[ext] = file_count_by_ext.get(ext, 0) + 1

                        logger.debug(f"  └─ Найден файл: {file}")

            logger.info(f"Поиск завершён: найдено {len(found_files)} файл(ов)")

            if file_count_by_ext:
                logger.info("Статистика по типам файлов:")
                for ext, count in sorted(file_count_by_ext.items()):
                    logger.info(f"  {ext}: {count} файл(ов)")

        except Exception as e:
            logger.log_exception("Поиск файлов", e)
            print(f"Ошибка при поиске файлов: {str(e)}")

        return found_files

    @staticmethod
    def read_file(file_path: str, encoding: str = "utf-8") -> str:
        logger.log_operation("Чтение файла", file_path)
        try:
            with open(file_path, "r", encoding=encoding, errors="ignore") as f:
                content = f.read()
                logger.log_file_operation("Чтение", file_path, f"успешно ({len(content)} байт)")
                return content
        except Exception as e:
            error_msg = (
                f"[Ошибка чтения файла: {os.path.basename(file_path)}\n"
                f"Причина: {str(e)}]"
            )
            logger.log_exception(f"Чтение файла {file_path}", e)
            return error_msg

    @staticmethod
    def file_exists(file_path: str) -> bool:
        exists = os.path.exists(file_path)
        logger.debug(f"Проверка существования файла {file_path}: {exists}")
        return exists

    @staticmethod
    def get_filename(file_path: str) -> str:
        return os.path.basename(file_path)

    @staticmethod
    def get_directory(file_path: str) -> str:
        return os.path.dirname(file_path)
