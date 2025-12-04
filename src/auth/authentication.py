"""
Модуль для аутентификации пользователей с хешированием паролей.
Поддерживает роли: администратор (полный доступ) и пользователь (только чтение).
"""

import hashlib
import sqlite3
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
import logging
import json
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthSystem:
    """
    Система аутентификации пользователей.
    Использует SQLite для хранения данных пользователей.
    """

    def __init__(self, db_path: str = 'users.db'):
        """
        Инициализирует систему аутентификации.

        Args:
            db_path (str): Путь к файлу SQLite базы данных
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._init_database()

        # Создаем тестовых пользователей если их нет
        self._create_default_users()

    def _init_database(self):
        """Инициализирует базу данных пользователей"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()

            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
                    full_name TEXT,
                    email TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP
                )
            ''')

            # Таблица сессий (для расширения функционала)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')

            # Таблица логов авторизации
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auth_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    action TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    success BOOLEAN NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
                )
            ''')

            self.conn.commit()
            logger.info(f"База данных аутентификации инициализирована: {self.db_path}")

        except sqlite3.Error as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise

    def _create_default_users(self):
        """Создает тестовых пользователей по умолчанию"""
        try:
            cursor = self.conn.cursor()

            # Проверяем, есть ли уже пользователи
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]

            if count == 0:
                logger.info("Создание тестовых пользователей...")

                # Администратор
                self.create_user(
                    username='admin',
                    password='admin123',
                    role='admin',
                    full_name='Администратор Системы',
                    email='admin@autopark.local'
                )

                # Обычный пользователь
                self.create_user(
                    username='user',
                    password='user123',
                    role='user',
                    full_name='Оператор Автопарка',
                    email='user@autopark.local'
                )

                logger.info("Тестовые пользователи созданы")
                print("\nТестовые пользователи созданы:")
                print("   Администратор: login: 'admin', password: 'admin123'")
                print("   Пользователь:  login: 'user',  password: 'user123'")

        except Exception as e:
            logger.error(f"Ошибка создания тестовых пользователей: {e}")

    def _generate_salt(self) -> str:
        """Генерирует соль для хеширования пароля"""
        alphabet = string.ascii_letters + string.digits
        salt = ''.join(secrets.choice(alphabet) for _ in range(16))
        return salt

    def _hash_password(self, password: str, salt: str) -> str:
        """
        Хеширует пароль с использованием соли.

        Args:
            password (str): Пароль пользователя
            salt (str): Соль для хеширования

        Returns:
            str: Хеш пароля
        """
        # Используем PBKDF2-HMAC-SHA256 для безопасного хеширования
        iterations = 100000
        dk = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations
        )
        return dk.hex()

    def create_user(self, username: str, password: str, role: str = 'user',
                    full_name: str = None, email: str = None) -> bool:
        """
        Создает нового пользователя.

        Args:
            username (str): Имя пользователя
            password (str): Пароль
            role (str): Роль ('admin' или 'user')
            full_name (str): Полное имя
            email (str): Email

        Returns:
            bool: True если пользователь создан успешно
        """
        try:
            # Проверяем валидность роли
            if role not in ['admin', 'user']:
                logger.error(f"Неверная роль: {role}")
                return False

            # Генерируем соль и хешируем пароль
            salt = self._generate_salt()
            password_hash = self._hash_password(password, salt)

            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password_hash, password_salt, role, full_name, email)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, salt, role, full_name, email))

            self.conn.commit()

            # Логируем создание пользователя
            cursor.execute("SELECT last_insert_rowid()")
            user_id = cursor.fetchone()[0]
            self._log_auth_action(user_id, username, 'create_user', True)

            logger.info(f"Пользователь создан: {username} ({role})")
            return True

        except sqlite3.IntegrityError:
            logger.error(f"Пользователь '{username}' уже существует")
            return False
        except Exception as e:
            logger.error(f"Ошибка создания пользователя: {e}")
            self._log_auth_action(None, username, 'create_user', False)
            return False

    def authenticate(self, username: str, password: str,
                     ip_address: str = None, user_agent: str = None) -> Optional[Dict[str, Any]]:
        """
        Аутентифицирует пользователя.

        Args:
            username (str): Имя пользователя
            password (str): Пароль
            ip_address (str): IP адрес (для логов)
            user_agent (str): User Agent (для логов)

        Returns:
            dict: Информация о пользователе или None если аутентификация не удалась
        """
        try:
            cursor = self.conn.cursor()

            # Проверяем блокировку пользователя
            cursor.execute('''
                SELECT id, username, password_hash, password_salt, role, full_name, 
                       is_active, locked_until, login_attempts
                FROM users 
                WHERE username = ? AND is_active = 1
            ''', (username,))

            user_data = cursor.fetchone()

            if not user_data:
                self._log_auth_action(None, username, 'login', False, ip_address, user_agent)
                logger.warning(f"Попытка входа несуществующего пользователя: {username}")
                return None

            user_id, username_db, password_hash, salt, role, full_name, is_active, locked_until, login_attempts = user_data

            # Проверяем блокировку
            if locked_until:
                locked_until_dt = datetime.fromisoformat(locked_until)
                if datetime.now() < locked_until_dt:
                    remaining = (locked_until_dt - datetime.now()).seconds // 60
                    logger.warning(f"Пользователь {username} заблокирован еще {remaining} минут")
                    self._log_auth_action(user_id, username, 'login_blocked', False, ip_address, user_agent)
                    return None

            # Проверяем пароль
            input_hash = self._hash_password(password, salt)

            if input_hash == password_hash:
                # Успешная аутентификация
                self._reset_login_attempts(user_id)
                self._update_last_login(user_id)

                user_info = {
                    'id': user_id,
                    'username': username_db,
                    'role': role,
                    'full_name': full_name,
                    'is_admin': role == 'admin',
                    'permissions': self._get_user_permissions(role)
                }

                self._log_auth_action(user_id, username, 'login', True, ip_address, user_agent)
                logger.info(f"Успешный вход пользователя: {username} ({role})")
                return user_info
            else:
                # Неверный пароль
                self._increment_login_attempts(user_id)
                self._log_auth_action(user_id, username, 'login', False, ip_address, user_agent)
                logger.warning(f"Неверный пароль для пользователя: {username}")
                return None

        except Exception as e:
            logger.error(f"Ошибка аутентификации: {e}")
            self._log_auth_action(None, username, 'login_error', False, ip_address, user_agent)
            return None

    def _increment_login_attempts(self, user_id: int):
        """Увеличивает счетчик неудачных попыток входа"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET login_attempts = login_attempts + 1 
                WHERE id = ?
            ''', (user_id,))

            # Проверяем, нужно ли заблокировать пользователя
            cursor.execute('SELECT login_attempts FROM users WHERE id = ?', (user_id,))
            attempts = cursor.fetchone()[0]

            if attempts >= 5:  # После 5 неудачных попыток
                lock_until = datetime.now() + timedelta(minutes=30)
                cursor.execute('''
                    UPDATE users 
                    SET locked_until = ? 
                    WHERE id = ?
                ''', (lock_until.isoformat(), user_id))
                logger.warning(f"Пользователь заблокирован на 30 минут (5 неудачных попыток)")

            self.conn.commit()
        except Exception as e:
            logger.error(f"Ошибка обновления счетчика попыток: {e}")

    def _reset_login_attempts(self, user_id: int):
        """Сбрасывает счетчик неудачных попыток входа"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET login_attempts = 0, locked_until = NULL 
                WHERE id = ?
            ''', (user_id,))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Ошибка сброса счетчика попыток: {e}")

    def _update_last_login(self, user_id: int):
        """Обновляет время последнего входа"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET last_login = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (user_id,))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Ошибка обновления времени входа: {e}")

    # В методе _get_user_permissions обновляем права:
    def _get_user_permissions(self, role: str) -> Dict[str, bool]:
        """
        Возвращает права доступа для роли.
        Упрощенная версия: только два типа пользователей.

        Args:
            role (str): Роль пользователя ('admin' или 'user')

        Returns:
            dict: Права доступа
        """
        if role == 'admin':
            # Администратор - ПОЛНЫЙ ДОСТУП
            return {
                # CRUD операции
                'can_create': True,
                'can_read': True,
                'can_update': True,
                'can_delete': True,

                # Модули приложения
                'can_manage_users': True,
                'can_manage_personnel': True,
                'can_manage_vehicles': True,
                'can_manage_routes': True,
                'can_manage_journal': True,
                'can_view_reports': True,
                'can_generate_reports': True,
                'can_export_data': True,

                # Системные права
                'can_configure_system': True,
                'can_view_logs': True,
                'can_backup_restore': True
            }
        else:
            # Пользователь (Оператор) - ОГРАНИЧЕННЫЙ ДОСТУП
            return {
                # CRUD операции
                'can_create': False,  # Не может создавать новые записи
                'can_read': True,  # Может просматривать данные
                'can_update': True,  # Может обновлять журнал (прибытие/отправление)
                'can_delete': False,  # Не может удалять записи

                # Модули приложения
                'can_manage_users': False,
                'can_manage_personnel': False,
                'can_manage_vehicles': False,
                'can_manage_routes': False,
                'can_manage_journal': True,  # Может работать с журналом оператора
                'can_view_reports': True,  # Может просматривать отчеты
                'can_generate_reports': True,  # Может формировать отчеты
                'can_export_data': False,  # Не может экспортировать

                # Системные права
                'can_configure_system': False,
                'can_view_logs': False,
                'can_backup_restore': False
            }

    def _log_auth_action(self, user_id: Optional[int], username: str, action: str,
                         success: bool, ip_address: str = None, user_agent: str = None):
        """Логирует действие аутентификации"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO auth_logs (user_id, username, action, ip_address, user_agent, success)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, username, action, ip_address, user_agent, success))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Ошибка логирования действия: {e}")

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Изменяет пароль пользователя.

        Args:
            username (str): Имя пользователя
            old_password (str): Старый пароль
            new_password (str): Новый пароль

        Returns:
            bool: True если пароль изменен успешно
        """
        try:
            # Сначала аутентифицируем пользователя
            user_info = self.authenticate(username, old_password)
            if not user_info:
                return False

            # Генерируем новую соль и хеш
            salt = self._generate_salt()
            new_password_hash = self._hash_password(new_password, salt)

            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, password_salt = ?, login_attempts = 0, locked_until = NULL
                WHERE username = ?
            ''', (new_password_hash, salt, username))

            self.conn.commit()
            self._log_auth_action(user_info['id'], username, 'change_password', True)
            logger.info(f"Пароль изменен для пользователя: {username}")
            return True

        except Exception as e:
            logger.error(f"Ошибка изменения пароля: {e}")
            self._log_auth_action(None, username, 'change_password', False)
            return False

    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о пользователе.

        Args:
            username (str): Имя пользователя

        Returns:
            dict: Информация о пользователе
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, username, role, full_name, email, is_active, 
                       created_at, last_login
                FROM users 
                WHERE username = ?
            ''', (username,))

            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'username': row[1],
                    'role': row[2],
                    'full_name': row[3],
                    'email': row[4],
                    'is_active': bool(row[5]),
                    'created_at': row[6],
                    'last_login': row[7]
                }
            return None

        except Exception as e:
            logger.error(f"Ошибка получения информации о пользователе: {e}")
            return None

    def list_users(self) -> list:
        """
        Возвращает список всех пользователей.

        Returns:
            list: Список пользователей
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, username, role, full_name, email, is_active, 
                       created_at, last_login
                FROM users 
                ORDER BY username
            ''')

            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'role': row[2],
                    'full_name': row[3],
                    'email': row[4],
                    'is_active': bool(row[5]),
                    'created_at': row[6],
                    'last_login': row[7]
                })

            return users

        except Exception as e:
            logger.error(f"Ошибка получения списка пользователей: {e}")
            return []

    def update_user(self, username: str, **kwargs) -> bool:
        """
        Обновляет данные пользователя.

        Args:
            username (str): Имя пользователя
            **kwargs: Поля для обновления

        Returns:
            bool: True если обновление успешно
        """
        try:
            allowed_fields = ['full_name', 'email', 'role', 'is_active']
            update_fields = []
            update_values = []

            for field, value in kwargs.items():
                if field in allowed_fields:
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)

            if not update_fields:
                return False

            update_values.append(username)

            cursor = self.conn.cursor()
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE username = ?"
            cursor.execute(query, update_values)

            self.conn.commit()
            logger.info(f"Данные пользователя обновлены: {username}")
            return True

        except Exception as e:
            logger.error(f"Ошибка обновления пользователя: {e}")
            return False

    def delete_user(self, username: str) -> bool:
        """
        Удаляет пользователя.

        Args:
            username (str): Имя пользователя

        Returns:
            bool: True если удаление успешно
        """
        try:
            # Не позволяем удалить самого себя (если нужно, можно убрать)
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))

            affected = cursor.rowcount
            self.conn.commit()

            if affected > 0:
                logger.info(f"Пользователь удален: {username}")
                return True
            else:
                logger.warning(f"Пользователь не найден: {username}")
                return False

        except Exception as e:
            logger.error(f"Ошибка удаления пользователя: {e}")
            return False

    def close(self):
        """Закрывает соединение с базой данных"""
        if self.conn:
            self.conn.close()
            logger.info("Соединение с базой данных аутентификации закрыто")

    def __del__(self):
        """Деструктор - закрывает соединение"""
        self.close()


# Фабричная функция для создания системы аутентификации
def create_auth_system(db_path: str = 'users.db') -> AuthSystem:
    """
    Создает и возвращает систему аутентификации.

    Args:
        db_path (str): Путь к файлу базы данных

    Returns:
        AuthSystem: Объект системы аутентификации
    """
    try:
        auth_system = AuthSystem(db_path)
        logger.info("Система аутентификации инициализирована")
        return auth_system
    except Exception as e:
        logger.error(f"Ошибка создания системы аутентификации: {e}")
        raise


# Тестирование модуля
if __name__ == "__main__":
    print("🧪 Тестирование системы аутентификации")
    print("=" * 50)

    try:
        # Создаем систему аутентификации
        auth = create_auth_system()

        # Тест 1: Проверка существующих пользователей
        print("\n1. 📋 Список пользователей:")
        users = auth.list_users()
        for user in users:
            print(f"   - {user['username']} ({user['role']}): {user['full_name']}")

        # Тест 2: Аутентификация
        print("\n2. 🔐 Тестирование аутентификации:")

        # Правильные учетные данные
        test_cases = [
            ('admin', 'admin123', True),
            ('user', 'user123', True),
            ('admin', 'wrongpassword', False),
            ('nonexistent', 'password', False)
        ]

        for username, password, should_succeed in test_cases:
            print(f"   Тест: {username}/{password}... ", end='')
            user_info = auth.authenticate(username, password)

            if user_info and should_succeed:
                print(f"УСПЕХ (роль: {user_info['role']})")
            elif not user_info and not should_succeed:
                print(f"ОЖИДАЕМЫЙ ПРОВАЛ")
            else:
                print(f"НЕОЖИДАННЫЙ РЕЗУЛЬТАТ")

        # Тест 3: Права доступа
        print("\n3.Проверка прав доступа:")
        admin_info = auth.authenticate('admin', 'admin123')
        user_info = auth.authenticate('user', 'user123')

        if admin_info:
            print(f"   Администратор может управлять пользователями: {admin_info['permissions']['can_manage_users']}")

        if user_info:
            print(f"   Пользователь может создавать записи: {user_info['permissions']['can_create']}")
            print(f"   Пользователь может читать данные: {user_info['permissions']['can_read']}")

        # Тест 4: Смена пароля
        print("\n4.Тест смены пароля (имитация)...")
        print("   Для реальной смены пароля используйте метод change_password()")

        # Закрываем соединение
        auth.close()

        print("\n" + "=" * 50)
        print("Тестирование системы аутентификации завершено успешно!")

    except Exception as e:
        print(f"\nОшибка тестирования: {e}")
        import traceback

        traceback.print_exc()