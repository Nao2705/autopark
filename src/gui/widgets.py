"""
Кастомные виджеты для приложения.
Упрощенная версия с LoginDialog.
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os


class LoginDialog(QDialog):
    """
    Диалоговое окно для входа в систему.
    Упрощенная версия без "Запомнить меня".
    """

    def __init__(self, auth_system, parent=None, change_user_mode=False):
        super().__init__(parent)
        self.auth_system = auth_system
        self.user_info = None
        self.change_user_mode = change_user_mode  # Флаг режима смены пользователя
        self._setup_ui()

    def _setup_ui(self):
        """Настраивает интерфейс окна входа"""
        # Изменяем заголовок в зависимости от режима
        if self.change_user_mode:
            self.setWindowTitle("Смена пользователя")
        else:
            self.setWindowTitle("Вход в систему")

        self.setFixedSize(500, 250)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel("АВТОПАРК - Система управления")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title_label)

        # Поля ввода
        form_layout = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите имя пользователя")
        self.username_input.setMaxLength(50)
        form_layout.addRow("Логин:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMaxLength(100)
        form_layout.addRow("Пароль:", self.password_input)

        layout.addLayout(form_layout)

        # Кнопки
        button_layout = QHBoxLayout()

        self.login_button = QPushButton("Войти")
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self._login)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # Статус
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #e74c3c;")
        layout.addWidget(self.status_label)

        # Подсказка (показываем всегда)
        hint_label = QLabel("Тестовые пользователи: admin/admin123 или user/user123")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("color: #7f8c8d; font-size: 10px; margin-top: 10px;")
        layout.addWidget(hint_label)

        # Подключаем клавишу Enter
        self.username_input.returnPressed.connect(self._login)
        self.password_input.returnPressed.connect(self._login)

        self.setLayout(layout)

    def _login(self):
        """Обрабатывает попытку входа"""
        username = self.username_input.text().strip()
        password = self.password_input.text()  # Пароль не обрезаем, так как могут быть пробелы в начале/конце

        if not username or not password:
            self.status_label.setText("Заполните все поля")
            return

        # Показываем индикатор загрузки
        self.login_button.setEnabled(False)
        self.login_button.setText("Вход...")
        QApplication.processEvents()

        # Аутентификация
        self.user_info = self.auth_system.authenticate(username, password)

        if self.user_info:
            self.accept()
        else:
            self.status_label.setText("Неверный логин или пароль")
            self.password_input.clear()
            self.login_button.setEnabled(True)
            self.login_button.setText("Войти")


# Простые вспомогательные классы
class CustomTableView(QTableWidget):
    """
    Таблица для отображения данных.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        self.horizontalHeader().setStretchLastSection(True)
        self.setEditTriggers(QTableView.NoEditTriggers)


class DataEditDialog(QDialog):
    """
    Простой диалог для редактирования данных.
    Базовый класс.
    """

    def __init__(self, table_name, record_data=None, parent=None):
        super().__init__(parent)
        self.table_name = table_name
        self.record_data = record_data or {}
        self.is_edit_mode = bool(record_data)
        self._setup_ui()

    def _setup_ui(self):
        """Базовый UI"""
        title = f"Редактирование - {self.table_name}" if self.is_edit_mode else f"Добавление - {self.table_name}"
        self.setWindowTitle(title)
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Поля формы будут добавляться в дочерних классах
        self.form_widget = QWidget()
        self.form_layout = QFormLayout()
        self.form_widget.setLayout(self.form_layout)
        layout.addWidget(self.form_widget)

        # Кнопки
        button_box = QDialogButtonBox()

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.accept)

        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)

        button_box.addButton(save_button, QDialogButtonBox.AcceptRole)
        button_box.addButton(cancel_button, QDialogButtonBox.RejectRole)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_data(self):
        """Возвращает данные из формы (переопределяется в дочерних классах)"""
        return {}