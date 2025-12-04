import xml.etree.ElementTree as ET
import os
import re
from dotenv import load_dotenv


class ConfigLoader:
    """
    Класс для загрузки конфигурации из XML файла с поддержкой переменных окружения.
    Поддерживает замену ${VAR_NAME} на значения из .env файла.
    """

    def __init__(self, config_path='config.xml'):
        """
        Инициализирует загрузчик конфигурации.

        Args:
            config_path (str): Путь к файлу конфигурации XML
        """
        self.config_path = config_path
        self.config = {}
        self.env_vars = {}

        # Загружаем переменные окружения из .env
        load_dotenv()
        self._load_env_vars()

    def _load_env_vars(self):
        """Загружает все переменные окружения из .env файла"""
        self.env_vars = dict(os.environ)
        print(f"Загружено {len(self.env_vars)} переменных окружения")

    def _replace_env_vars(self, text):
        """
        Заменяет ${VAR_NAME} в тексте на значения из переменных окружения.

        Args:
            text (str): Текст с переменными

        Returns:
            str: Текст с замененными переменными
        """
        if not text:
            return text

        # Регулярное выражение для поиска ${VAR_NAME}
        pattern = r'\$\{([^}]+)\}'

        def replace_match(match):
            var_name = match.group(1)
            value = self.env_vars.get(var_name)
            if value is None:
                print(f" Предупреждение: Переменная окружения '{var_name}' не найдена")
                return match.group(0)  # Возвращаем оригинал, если переменная не найдена
            return value

        return re.sub(pattern, replace_match, text)

    def load(self):
        """
        Загружает и парсит конфигурацию из XML файла.

        Returns:
            dict: Словарь с конфигурацией или None в случае ошибки
        """
        try:
            # Проверяем существование файла
            if not os.path.exists(self.config_path):
                print(f" Файл конфигурации '{self.config_path}' не найден")
                return None

            # Парсим XML
            tree = ET.parse(self.config_path)
            root = tree.getroot()

            # Инициализируем конфигурацию
            self.config = {
                'database': {},
                'app': {}
            }

            # Обрабатываем раздел database
            db_section = root.find('.//database')
            if db_section is not None:
                self.config['database'] = {
                    'host': self._replace_env_vars(db_section.find('host').text),
                    'port': int(self._replace_env_vars(db_section.find('port').text)),
                    'dbname': self._replace_env_vars(db_section.find('dbname').text),
                    'user': self._replace_env_vars(db_section.find('user').text),
                    'password': self._replace_env_vars(db_section.find('password').text),
                    'schema': self._replace_env_vars(
                        db_section.find('schema').text if db_section.find('schema') is not None else 'public')
                }

            # Обрабатываем раздел app
            app_section = root.find('.//app')
            if app_section is not None:
                self.config['app'] = {
                    'title': self._replace_env_vars(app_section.find('title').text),
                    'version': self._replace_env_vars(app_section.find('version').text)
                }

            # Логируем успешную загрузку (без пароля)
            print(" Конфигурация успешно загружена")
            safe_config = self.config.copy()
            safe_config['database'] = safe_config['database'].copy()
            safe_config['database']['password'] = '***'  # Маскируем пароль
            print(f"   База данных: {safe_config['database']['dbname']}@{safe_config['database']['host']}")
            print(f"   Приложение: {safe_config['app']['title']} v{safe_config['app']['version']}")

            return self.config

        except ET.ParseError as e:
            print(f" Ошибка парсинга XML: {e}")
            return None
        except AttributeError as e:
            print(f" Отсутствует обязательный элемент в конфигурации: {e}")
            return None
        except ValueError as e:
            print(f" Ошибка преобразования типа данных: {e}")
            return None
        except Exception as e:
            print(f" Неожиданная ошибка при загрузке конфигурации: {e}")
            return None

    def get_db_config(self):
        """
        Возвращает только конфигурацию базы данных.

        Returns:
            dict: Конфигурация базы данных
        """
        if not self.config:
            print(" Конфигурация еще не загружена, загружаю...")
            self.load()
        return self.config.get('database', {})

    def get_app_config(self):
        """
        Возвращает только конфигурацию приложения.

        Returns:
            dict: Конфигурация приложения
        """
        if not self.config:
            print(" Конфигурация еще не загружена, загружаю...")
            self.load()
        return self.config.get('app', {})

    def print_config_summary(self):
        """Выводит краткую информацию о конфигурации"""
        if not self.config:
            print("Конфигурация не загружена")
            return

        print("\n Сводка конфигурации:")
        print("-" * 40)

        db_config = self.config.get('database', {})
        print(f"База данных:")
        print(f"  Хост: {db_config.get('host')}")
        print(f"  Порт: {db_config.get('port')}")
        print(f"  Имя БД: {db_config.get('dbname')}")
        print(f"  Пользователь: {db_config.get('user')}")
        print(f"  Пароль: {'*' * len(db_config.get('password', ''))}")
        print(f"  Схема: {db_config.get('schema')}")

        app_config = self.config.get('app', {})
        print(f"\nПриложение:")
        print(f"  Название: {app_config.get('title')}")
        print(f"  Версия: {app_config.get('version')}")
        print("-" * 40)


# Для тестирования
if __name__ == "__main__":
    print(" Тестирование загрузчика конфигурации...")
    loader = ConfigLoader()
    config = loader.load()

    if config:
        loader.print_config_summary()
        print("\n   Тест пройден успешно!")
    else:
        print("\n   Тест не пройден!")