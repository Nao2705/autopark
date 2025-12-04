"""
Главный файл приложения "Система управления автопарком".
"""

import sys
import os

# Добавляем путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox
        from src.auth.authentication import create_auth_system
        from src.database.connection import create_db_connection
        from src.gui.widgets import LoginDialog
        from src.gui.main_window import MainWindow

        print("Запуск системы управления автопарком")
        print("=" * 60)

        # Создаем приложение
        app = QApplication(sys.argv)
        app.setApplicationName("Автопарк - Система управления")


        print("Инициализация системы аутентификации...")
        auth_system = create_auth_system()

        print("Подключение к базе данных...")
        db_connection = create_db_connection()

        if not db_connection:
            print("Не удалось подключиться к базе данных")
            QMessageBox.critical(None, "Ошибка - Не удалось подключиться к базе данных.\n")
            return 1

        print("База данных подключена")

        print("\nАвторизация пользователя...")
        login_dialog = LoginDialog(auth_system)

        if login_dialog.exec_() == LoginDialog.Accepted:
            user_info = login_dialog.user_info
            print(f"Пользователь авторизован: {user_info['username']} ({user_info['role']})")

            print("Запуск главного окна приложения...")
            main_window = MainWindow(user_info, db_connection, auth_system)
            main_window.show()

            print("\n" + "=" * 60)
            print("Приложение успешно запущено!")
            print(f"Пользователь: {user_info['full_name']}")
            print(f"Роль: {user_info['role']}")
            print("=" * 60)

            return app.exec_()
        else:
            print("Авторизация отменена")
            db_connection.disconnect()
            auth_system.close()
            return 0

    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        print("Проверьте структуру проекта и наличие всех модулей")
        return 1
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())