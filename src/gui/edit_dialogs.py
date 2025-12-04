"""
Диалоговые окна для редактирования данных.
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime


class PersonnelEditDialog(QDialog):
    """Диалог для редактирования персонала"""

    def __init__(self, record_data=None, db_connection=None, parent=None):
        super().__init__(parent)
        self.record_data = record_data or {}
        self.db_connection = db_connection
        self.is_edit_mode = bool(record_data)
        self._setup_ui()

    def _setup_ui(self):
        """Настраивает интерфейс диалога"""
        title = "Редактирование персонала" if self.is_edit_mode else "Добавление персонала"
        self.setWindowTitle(title)
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Поля формы
        form_layout = QFormLayout()

        self.first_name_input = QLineEdit(self.record_data.get('first_name', ''))
        self.first_name_input.setPlaceholderText("Иван")
        form_layout.addRow("Имя*:", self.first_name_input)

        self.last_name_input = QLineEdit(self.record_data.get('last_name', ''))
        self.last_name_input.setPlaceholderText("Иванов")
        form_layout.addRow("Фамилия*:", self.last_name_input)

        self.father_name_input = QLineEdit(self.record_data.get('father_name', ''))
        self.father_name_input.setPlaceholderText("Иванович")
        form_layout.addRow("Отчество:", self.father_name_input)

        layout.addLayout(form_layout)

        # Кнопки
        button_box = QDialogButtonBox()

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self._validate_and_accept)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)

        button_box.addButton(self.save_button, QDialogButtonBox.AcceptRole)
        button_box.addButton(self.cancel_button, QDialogButtonBox.RejectRole)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def _validate_and_accept(self):
        """Проверяет данные и принимает диалог"""
        if not self.first_name_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Имя обязательно для заполнения")
            return

        if not self.last_name_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Фамилия обязательна для заполнения")
            return

        self.accept()

    def get_data(self):
        """Возвращает данные из формы"""
        return {
            'first_name': self.first_name_input.text().strip(),
            'last_name': self.last_name_input.text().strip(),
            'father_name': self.father_name_input.text().strip()
        }


class AutoEditDialog(QDialog):
    """Диалог для редактирования автомобилей"""

    def __init__(self, record_data=None, db_connection=None, parent=None):
        super().__init__(parent)
        self.record_data = record_data or {}
        self.db_connection = db_connection
        self.is_edit_mode = bool(record_data)
        self.drivers = []
        self._load_drivers()
        self._setup_ui()

    def _load_drivers(self):
        """Загружает список водителей из БД"""
        if self.db_connection:
            try:
                query = """
                    SELECT id, last_name || ' ' || first_name || ' ' || COALESCE(father_name, '') as full_name
                    FROM auto_personnel 
                    ORDER BY last_name, first_name
                """
                result = self.db_connection.execute_query(query)
                self.drivers = [(row['id'], row['full_name']) for row in result]
            except:
                self.drivers = []

    def _setup_ui(self):
        """Настраивает интерфейс диалога"""
        title = "Редактирование автомобиля" if self.is_edit_mode else "Добавление автомобиля"
        self.setWindowTitle(title)
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Поля формы
        form_layout = QFormLayout()

        self.num_input = QLineEdit(self.record_data.get('num', ''))
        self.num_input.setPlaceholderText("А123ВС77")
        form_layout.addRow("Номер*:", self.num_input)

        self.color_input = QLineEdit(self.record_data.get('color', ''))
        self.color_input.setPlaceholderText("Красный")
        form_layout.addRow("Цвет:", self.color_input)

        self.mark_input = QLineEdit(self.record_data.get('mark', ''))
        self.mark_input.setPlaceholderText("Газель")
        form_layout.addRow("Марка*:", self.mark_input)

        # Выбор водителя
        self.personnel_combo = QComboBox()
        self.personnel_combo.addItem("— Не назначен —", None)

        for driver_id, driver_name in self.drivers:
            self.personnel_combo.addItem(driver_name, driver_id)

        # Выбираем текущего водителя если есть
        current_personnel = self.record_data.get('personnel_id')
        if current_personnel:
            for i in range(self.personnel_combo.count()):
                if self.personnel_combo.itemData(i) == current_personnel:
                    self.personnel_combo.setCurrentIndex(i)
                    break

        form_layout.addRow("Водитель:", self.personnel_combo)

        layout.addLayout(form_layout)

        # Кнопки
        button_box = QDialogButtonBox()

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self._validate_and_accept)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)

        button_box.addButton(self.save_button, QDialogButtonBox.AcceptRole)
        button_box.addButton(self.cancel_button, QDialogButtonBox.RejectRole)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def _validate_and_accept(self):
        """Проверяет данные и принимает диалог"""
        if not self.num_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Номер автомобиля обязателен")
            return

        if not self.mark_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Марка автомобиля обязательна")
            return

        self.accept()

    def get_data(self):
        """Возвращает данные из формы"""
        return {
            'num': self.num_input.text().strip(),
            'color': self.color_input.text().strip(),
            'mark': self.mark_input.text().strip(),
            'personnel_id': self.personnel_combo.currentData()
        }


class RoutesEditDialog(QDialog):
    """Диалог для редактирования маршрутов"""

    def __init__(self, record_data=None, db_connection=None, parent=None):
        super().__init__(parent)
        self.record_data = record_data or {}
        self.db_connection = db_connection
        self.is_edit_mode = bool(record_data)
        self._setup_ui()

    def _setup_ui(self):
        """Настраивает интерфейс диалога"""
        title = "Редактирование маршрута" if self.is_edit_mode else "Добавление маршрута"
        self.setWindowTitle(title)
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Поля формы
        form_layout = QFormLayout()

        self.name_input = QLineEdit(self.record_data.get('name', ''))
        self.name_input.setPlaceholderText("Москва - Санкт-Петербург")
        form_layout.addRow("Название маршрута*:", self.name_input)

        layout.addLayout(form_layout)

        # Кнопки
        button_box = QDialogButtonBox()

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self._validate_and_accept)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)

        button_box.addButton(self.save_button, QDialogButtonBox.AcceptRole)
        button_box.addButton(self.cancel_button, QDialogButtonBox.RejectRole)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def _validate_and_accept(self):
        """Проверяет данные и принимает диалог"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Название маршрута обязательно")
            return

        self.accept()

    def get_data(self):
        """Возвращает данные из формы"""
        return {
            'name': self.name_input.text().strip()
        }


class JournalEditDialog(QDialog):
    """Диалог для работы с журналом (выпуск в рейс)"""

    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.vehicles = []
        self.routes = []
        self._load_data()
        self._setup_ui()

    def _load_data(self):
        """Загружает данные из БД"""
        try:
            # Загружаем автомобили без активных рейсов
            query = """
                SELECT a.id, a.num, a.mark, 
                       COALESCE(ap.last_name || ' ' || LEFT(ap.first_name, 1) || '.', 'Не назначен') as driver
                FROM auto a
                LEFT JOIN auto_personnel ap ON a.personnel_id = ap.id
                WHERE a.id NOT IN (
                    SELECT auto_id FROM journal WHERE time_in IS NULL
                )
                ORDER BY a.num
            """
            self.vehicles = self.db_connection.execute_query(query)

            # Загружаем маршруты
            query = "SELECT id, name FROM routes ORDER BY name"
            self.routes = self.db_connection.execute_query(query)

        except Exception as e:
            print(f"Ошибка загрузки данных для журнала: {e}")
            self.vehicles = []
            self.routes = []

    def _setup_ui(self):
        """Настраивает интерфейс диалога"""
        self.setWindowTitle("Выпуск автомобиля в рейс")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Информация
        info_label = QLabel("Выберите автомобиль и маршрут для выпуска в рейс")
        layout.addWidget(info_label)

        # Поля формы
        form_layout = QFormLayout()

        # Выбор автомобиля
        self.vehicle_combo = QComboBox()
        if self.vehicles:
            for vehicle in self.vehicles:
                display_text = f"{vehicle['num']} ({vehicle['mark']}) - {vehicle['driver']}"
                self.vehicle_combo.addItem(display_text, vehicle['id'])
        else:
            self.vehicle_combo.addItem("Нет доступных автомобилей", None)
            self.vehicle_combo.setEnabled(False)

        form_layout.addRow("Автомобиль*:", self.vehicle_combo)

        # Выбор маршрута
        self.route_combo = QComboBox()
        if self.routes:
            for route in self.routes:
                self.route_combo.addItem(route['name'], route['id'])
        else:
            self.route_combo.addItem("Нет маршрутов", None)
            self.route_combo.setEnabled(False)

        form_layout.addRow("Маршрут*:", self.route_combo)

        # Время отправления
        self.time_out_input = QDateTimeEdit()
        self.time_out_input.setDisplayFormat("dd.MM.yyyy HH:mm")
        self.time_out_input.setDateTime(QDateTime.currentDateTime())
        form_layout.addRow("Время отправления*:", self.time_out_input)

        layout.addLayout(form_layout)

        # Кнопки
        button_box = QDialogButtonBox()

        self.save_button = QPushButton("Выпустить в рейс")
        self.save_button.clicked.connect(self._validate_and_accept)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)

        button_box.addButton(self.save_button, QDialogButtonBox.AcceptRole)
        button_box.addButton(self.cancel_button, QDialogButtonBox.RejectRole)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def _validate_and_accept(self):
        """Проверяет данные и принимает диалог"""
        if not self.vehicle_combo.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите автомобиль")
            return

        if not self.route_combo.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите маршрут")
            return

        self.accept()

    def get_data(self):
        """Возвращает данные из формы"""
        return {
            'auto_id': self.vehicle_combo.currentData(),
            'route_id': self.route_combo.currentData(),
            'time_out': self.time_out_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        }


class ArrivalEditDialog(QDialog):
    """Диалог для регистрации прибытия"""

    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.active_trips = []
        self._load_active_trips()
        self._setup_ui()

    def _load_active_trips(self):
        """Загружает активные рейсы"""
        try:
            query = """
                SELECT j.id, a.num, a.mark, r.name, j.time_out,
                       COALESCE(ap.last_name || ' ' || LEFT(ap.first_name, 1) || '.', 'Не назначен') as driver
                FROM journal j
                JOIN auto a ON j.auto_id = a.id
                JOIN routes r ON j.route_id = r.id
                LEFT JOIN auto_personnel ap ON a.personnel_id = ap.id
                WHERE j.time_in IS NULL
                ORDER BY j.time_out
            """
            self.active_trips = self.db_connection.execute_query(query)
        except Exception as e:
            print(f"Ошибка загрузки активных рейсов: {e}")
            self.active_trips = []

    def _setup_ui(self):
        """Настраивает интерфейс диалога"""
        self.setWindowTitle("Регистрация прибытия автомобиля")
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        # Информация
        info_label = QLabel("Выберите активный рейс для регистрации прибытия")
        layout.addWidget(info_label)

        # Поля формы
        form_layout = QFormLayout()

        # Выбор активного рейса
        self.trip_combo = QComboBox()
        if self.active_trips:
            for trip in self.active_trips:
                display_text = f"Рейс #{trip['id']}: {trip['num']} ({trip['mark']}) - {trip['name']}"
                self.trip_combo.addItem(display_text, trip['id'])
        else:
            self.trip_combo.addItem("Нет активных рейсов", None)
            self.trip_combo.setEnabled(False)

        form_layout.addRow("Активный рейс*:", self.trip_combo)

        # Время прибытия
        self.time_in_input = QDateTimeEdit()
        self.time_in_input.setDisplayFormat("dd.MM.yyyy HH:mm")
        self.time_in_input.setDateTime(QDateTime.currentDateTime())
        form_layout.addRow("Время прибытия*:", self.time_in_input)

        layout.addLayout(form_layout)

        # Кнопки
        button_box = QDialogButtonBox()

        self.save_button = QPushButton("Зарегистрировать прибытие")
        self.save_button.clicked.connect(self._validate_and_accept)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)

        button_box.addButton(self.save_button, QDialogButtonBox.AcceptRole)
        button_box.addButton(self.cancel_button, QDialogButtonBox.RejectRole)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def _validate_and_accept(self):
        """Проверяет данные и принимает диалог"""
        if not self.trip_combo.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите активный рейс")
            return

        self.accept()

    def get_data(self):
        """Возвращает данные из формы"""
        return {
            'journal_id': self.trip_combo.currentData(),
            'time_in': self.time_in_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        }