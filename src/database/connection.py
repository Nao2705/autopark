"""
Модуль для работы с базой данных PostgreSQL.
"""

import psycopg2
from psycopg2 import OperationalError, Error, DatabaseError
from psycopg2.extras import RealDictCursor
import time
from typing import Optional, Dict, List, Any
import logging
import sys
import os
import xml.etree.ElementTree as ET
import re
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Класс для управления подключением к PostgreSQL.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Инициализирует объект подключения к БД.

        Args:
            config (dict): Конфигурация подключения
        """
        self.config = config
        self.connection: Optional[psycopg2.extensions.connection] = None
        self.cursor: Optional[psycopg2.extensions.cursor] = None

        # Статистика
        self.stats = {
            'connection_attempts': 0,
            'queries_executed': 0,
            'errors': 0
        }

        logger.info(f"Инициализировано подключение к {config.get('dbname')}")

    def connect(self, max_retries: int = 3, retry_delay: int = 2) -> bool:
        """
        Устанавливает соединение с базой данных.

        Args:
            max_retries (int): Максимальное количество попыток
            retry_delay (int): Задержка между попытками

        Returns:
            bool: True если подключение успешно
        """
        for attempt in range(max_retries):
            self.stats['connection_attempts'] += 1

            try:
                logger.info(f"Попытка подключения {attempt + 1}/{max_retries} к БД {self.config['dbname']}")

                # Формируем параметры подключения
                conn_params = {
                    'host': self.config['host'],
                    'port': self.config['port'],
                    'dbname': self.config['dbname'],
                    'user': self.config['user'],
                    'password': self.config['password']
                }

                print(
                    f"Параметры подключения: {conn_params['user']}@{conn_params['host']}:{conn_params['port']}/{conn_params['dbname']}")

                # Устанавливаем соединение
                self.connection = psycopg2.connect(**conn_params)

                # Настройка параметров
                self.connection.autocommit = False

                # Создаем курсор
                self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)

                # Устанавливаем схему
                schema = self.config.get('schema', 'public')
                self.cursor.execute(f"SET search_path TO {schema}")
                self.connection.commit()

                logger.info(f"Успешно подключено к БД {self.config['dbname']}")
                print(f"Успешно подключено к БД {self.config['dbname']}")

                # Проверяем соединение
                if self._test_connection():
                    return True
                else:
                    self.disconnect()

            except OperationalError as e:
                error_msg = str(e)
                logger.error(f"Ошибка подключения (попытка {attempt + 1}): {error_msg}")
                print(f"Ошибка подключения: {error_msg}")

                if attempt < max_retries - 1:
                    logger.info(f"Повтор через {retry_delay} секунд...")
                    time.sleep(retry_delay)
                else:
                    self.stats['errors'] += 1

            except Exception as e:
                logger.error(f"Неожиданная ошибка при подключении: {e}")
                print(f"Неожиданная ошибка: {e}")
                self.stats['errors'] += 1
                return False

        logger.error(f"Не удалось подключиться после {max_retries} попыток")
        print(f"Не удалось подключиться после {max_retries} попыток")
        return False

    def _test_connection(self) -> bool:
        """
        Внутренний метод для проверки соединения.

        Returns:
            bool: True если соединение активно
        """
        try:
            self.cursor.execute("SELECT 1 as test_value")
            result = self.cursor.fetchone()
            return result['test_value'] == 1
        except Exception as e:
            logger.error(f"Ошибка тестирования соединения: {e}")
            return False

    def disconnect(self):
        """Закрывает соединение с БД"""
        try:
            if self.cursor:
                self.cursor.close()
                logger.debug("Курсор закрыт")

            if self.connection:
                self.connection.close()
                logger.info("Соединение с БД закрыто")

        except Exception as e:
            logger.error(f"Ошибка при закрытии соединения: {e}")
        finally:
            self.cursor = None
            self.connection = None

    def test_connection(self) -> bool:
        """
        Публичный метод для проверки соединения с БД.

        Returns:
            bool: True если соединение активно
        """
        if not self.connection or self.connection.closed:
            logger.warning("Соединение не активно или закрыто")
            return False

        return self._test_connection()

    def execute_query(self, query: str, params: tuple = None, fetch_all: bool = True) -> List[Dict]:
        """
        Выполняет SQL запрос.

        Args:
            query (str): SQL запрос
            params (tuple): Параметры для запроса
            fetch_all (bool): Возвращать все строки или только первую

        Returns:
            list: Результаты запроса
        """
        if not self.test_connection():
            raise ConnectionError("Нет активного соединения с БД")

        try:
            logger.debug(f"Выполнение запроса: {query[:100]}...")

            self.cursor.execute(query, params or ())
            self.stats['queries_executed'] += 1

            if query.strip().upper().startswith(('SELECT', 'WITH', 'SHOW', 'DESCRIBE')):
                if fetch_all:
                    result = self.cursor.fetchall()
                    logger.debug(f"Запрос вернул {len(result)} строк")
                    return result
                else:
                    result = self.cursor.fetchone()
                    logger.debug("Запрос вернул одну строку")
                    return [result] if result else []
            else:
                self.connection.commit()
                rows_affected = self.cursor.rowcount
                logger.debug(f"Запрос выполнен, затронуто строк: {rows_affected}")
                return [{'rows_affected': rows_affected}]

        except Error as e:
            if self.connection:
                self.connection.rollback()
            logger.error(f"Ошибка выполнения запроса: {e}")
            logger.debug(f"Запрос: {query}")
            self.stats['errors'] += 1
            raise

    def get_table_data(self, table_name: str, limit: int = None) -> List[Dict]:
        """
        Получает данные из таблицы.

        Args:
            table_name (str): Имя таблицы
            limit (int): Ограничение количества строк

        Returns:
            list: Данные таблицы
        """
        try:
            query = f"SELECT * FROM {table_name}"
            if limit:
                query += f" LIMIT {limit}"

            return self.execute_query(query)
        except Exception as e:
            logger.error(f"Ошибка получения данных из таблицы {table_name}: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику работы.

        Returns:
            dict: Статистика
        """
        return self.stats.copy()

    def __enter__(self):
        """Поддержка контекстного менеджера"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Поддержка контекстного менеджера"""
        self.disconnect()


def create_db_connection(config_path: str = 'config.xml') -> Optional[DatabaseConnection]:
    """
    Создает и возвращает подключение к БД.

    Args:
        config_path (str): Путь к файлу конфигурации

    Returns:
        DatabaseConnection: Объект подключения
    """
    try:
        # Загружаем .env
        load_dotenv()

        # Парсим XML
        tree = ET.parse(config_path)
        root = tree.getroot()

        # Функция замены переменных окружения
        def replace_env_vars(text):
            if not text:
                return text
            pattern = r'\$\{([^}]+)\}'

            def replace_match(match):
                var_name = match.group(1)
                return os.getenv(var_name, match.group(0))

            return re.sub(pattern, replace_match, text)

        # Получаем конфигурацию
        db_section = root.find('.//database')
        if db_section is None:
            print(" Не найден раздел database в config.xml")
            return None

        db_config = {
            'host': replace_env_vars(db_section.find('host').text),
            'port': int(replace_env_vars(db_section.find('port').text)),
            'dbname': replace_env_vars(db_section.find('dbname').text),
            'user': replace_env_vars(db_section.find('user').text),
            'password': replace_env_vars(db_section.find('password').text),
            'schema': replace_env_vars(
                db_section.find('schema').text if db_section.find('schema') is not None else 'public')
        }

        print("    Загруженная конфигурация БД:")
        print(f"   Хост: {db_config['host']}")
        print(f"   Порт: {db_config['port']}")
        print(f"   БД: {db_config['dbname']}")
        print(f"   Пользователь: {db_config['user']}")
        print(f"   Пароль: {'*' * len(db_config['password'])}")
        print(f"   Схема: {db_config['schema']}")

        # Создаем подключение
        connection = DatabaseConnection(db_config)

        # Устанавливаем соединение
        if connection.connect():
            return connection
        else:
            return None

    except Exception as e:
        print(f"Ошибка создания подключения: {e}")
        import traceback
        traceback.print_exc()
        return None


# Алиас для обратной совместимости
create_db_connection = create_db_connection

if __name__ == "__main__":
    print("Тестирование подключения к БД")
    print("-" * 50)

    conn = create_db_connection()

    if conn:
        print("Подключение создано успешно")

        # Проверяем соединение
        if conn.test_connection():
            print("Соединение активно")
        else:
            print("Соединение не активно")

        # Получаем список таблиц
        try:
            result = conn.execute_query("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)

            print(f"\n Таблицы в БД ({len(result)}):")
            for row in result:
                print(f"   • {row['table_name']}")

        except Exception as e:
            print(f"Ошибка получения таблиц: {e}")

        # Закрываем соединение
        conn.disconnect()
        print("\n   Тест завершен")
    else:
        print(" Не удалось создать подключение")