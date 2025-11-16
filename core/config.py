"""
Модуль для работы с конфигурацией приложения
"""
import json
import os
from typing import Any, Dict


class ConfigManager:
    """
    Менеджер конфигурации приложения
    """

    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load()

    def load(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                    if "logging_enabled" not in config_data:
                        config_data["logging_enabled"] = True
                    if "log_directory" not in config_data:
                        config_data["log_directory"] = "logs"
                    return config_data
        except Exception as e:
            print(f"Ошибка загрузки конфига: {str(e)}")
        return self._get_default_config()

    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        return {
            "group": "",
            "student_name": "",
            "teacher_name": "",
            "work_number": "",
            "last_directory": "",
            "template_path": "template.docx",
            "save_directory": "",
            "save_nearby": True,
            "logging_enabled": True,
            "log_directory": "logs",
        }

    def save(self, config_data: Dict[str, Any]) -> bool:
        try:
            # Убедимся, что настройки логирования сохранены
            if "logging_enabled" not in config_data:
                config_data["logging_enabled"] = self.config.get("logging_enabled", True)
            if "log_directory" not in config_data:
                config_data["log_directory"] = self.config.get("log_directory", "logs")

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            self.config = config_data
            return True
        except Exception as e:
            print(f"Ошибка сохранения конфига: {str(e)}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def update(self, key: str, value: Any):
        self.config[key] = value
        self.save(self.config)
