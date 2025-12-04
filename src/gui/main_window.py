"""
Главное окно приложения управления автопарком.
Полностью рабочая версия без эмодзи.
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os

# Импорты для модулей приложения
try:
    from src.gui.edit_dialogs import (
        PersonnelEditDialog, AutoEditDialog, RoutesEditDialog,
        JournalEditDialog, ArrivalEditDialog
    )
except ImportError:
    # Альтернативный путь импорта
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class MainWindow(QMainWindow):
    """
    Главное окно приложения управления автопарком.
    """

    def __init__(self, user_info, db_connection, auth_system):
        super().__init__()
        self.user_info = user_info
        self.db_connection = db_connection
        self.auth_system = auth_system
        self.current_table = None
        self.current_data = []
        self._setup_ui()
        self._load_initial_data()

    def _setup_ui(self):
        """Настраивает интерфейс главного окна"""
        role_display = "Администратор" if self.user_info['is_admin'] else "Оператор"
        self.setWindowTitle(f"Автопарк - Система управления [{role_display}]")
        self.setGeometry(100, 100, 1400, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        header_layout = QHBoxLayout()
        title_label = QLabel("АВТОПАРК - Система управления")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50;")
        user_role_text = "АДМИНИСТРАТОР" if self.user_info['is_admin'] else "ОПЕРАТОР"
        user_label = QLabel(f"{user_role_text}: {self.user_info['full_name']}")
        user_label.setObjectName("user_label")  # Добавляем имя объекта для поиска
        if self.user_info['is_admin']:
            user_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            permissions_text = "Полный доступ ко всем функциям"
        else:
            user_label.setStyleSheet("color: #3498db; font-weight: bold;")
            permissions_text = "Доступ: просмотр данных, работа с журналом"
        permissions_label = QLabel(permissions_text)
        permissions_label.setObjectName("permissions_label")  # Добавляем имя объекта для поиска
        permissions_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        user_info_layout = QVBoxLayout()
        user_info_layout.addWidget(user_label)
        user_info_layout.addWidget(permissions_label)
        header_layout.addLayout(user_info_layout)

        # Добавляем кнопку смены пользователя
        self.change_user_button = QPushButton("Сменить пользователя")
        self.change_user_button.clicked.connect(self._change_user)
        self.change_user_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.change_user_button)

        main_layout.addLayout(header_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #dee2e6;")
        main_layout.addWidget(line)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabBar::tab {
                min-width: 150px;
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid #dee2e6;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                text-align: center;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 3px solid #3498db;
            }
        """)

        self.references_tab = QWidget()
        self._setup_references_tab()
        self.tab_widget.addTab(self.references_tab, "СПРАВОЧНИКИ")

        self.journals_tab = QWidget()
        self._setup_journals_tab()
        self.tab_widget.addTab(self.journals_tab, "ЖУРНАЛЫ")

        self.reports_tab = QWidget()
        self._setup_reports_tab()
        self.tab_widget.addTab(self.reports_tab, "ОТЧЕТЫ")

        main_layout.addWidget(self.tab_widget)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        if self.user_info['is_admin']:
            status_text = f"АДМИНИСТРАТОР | Полный доступ | Пользователь: {self.user_info['username']}"
        else:
            status_text = f"ОПЕРАТОР | Ограниченный доступ | Пользователь: {self.user_info['username']}"
        self.status_bar.showMessage(status_text)

        self._apply_styles()

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background-color: white;
                border-radius: 4px;
            }
            QStatusBar {
                background-color: #2c3e50;
                color: white;
                padding: 4px;
                font-size: 11px;
                font-weight: bold;
            }
        """)

    def _setup_references_tab(self):
        layout = QVBoxLayout(self.references_tab)
        info_label = QLabel()
        if self.user_info['is_admin']:
            info_label.setText("Управление справочниками (добавление, редактирование, удаление доступно)")
            info_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px; background-color: #eafaf1; border-radius: 3px;")
        else:
            info_label.setText("Просмотр справочников (только чтение)")
            info_label.setStyleSheet("color: #3498db; font-weight: bold; padding: 5px; background-color: #ebf5fb; border-radius: 3px;")
        layout.addWidget(info_label)

        toolbar = QHBoxLayout()
        self.table_combo = QComboBox()
        self.table_combo.addItems(["Персонал", "Автомобили", "Маршруты"])
        self.table_combo.currentTextChanged.connect(self._load_table_data)
        toolbar.addWidget(QLabel("Таблица:"))
        toolbar.addWidget(self.table_combo)
        toolbar.addStretch()

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self._load_table_data)
        toolbar.addWidget(self.refresh_button)

        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self._add_record)
        toolbar.addWidget(self.add_button)

        self.edit_button = QPushButton("Изменить")
        self.edit_button.clicked.connect(self._edit_record)
        toolbar.addWidget(self.edit_button)

        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self._delete_record)
        toolbar.addWidget(self.delete_button)

        # === Права доступа ===
        can_edit = self.user_info['permissions']['can_create']
        self.add_button.setEnabled(can_edit)
        self.edit_button.setEnabled(can_edit)
        self.delete_button.setEnabled(can_edit)

        layout.addLayout(toolbar)

        self.table_view = QTableWidget()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table_view)

        self.table_status = QLabel("Выберите таблицу для отображения данных")
        layout.addWidget(self.table_status)

    def _setup_journals_tab(self):
        layout = QVBoxLayout(self.journals_tab)
        info_label = QLabel()
        if self.user_info['permissions']['can_manage_journal']:
            info_label.setText("Журнал оператора (выпуск и прием автомобилей доступен)")
            info_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px; background-color: #eafaf1; border-radius: 3px;")
        else:
            info_label.setText("Журнал оператора (только просмотр)")
            info_label.setStyleSheet("color: #3498db; font-weight: bold; padding: 5px; background-color: #ebf5fb; border-radius: 3px;")
        layout.addWidget(info_label)

        title_label = QLabel("ЖУРНАЛ ОПЕРАТОРА")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)

        control_layout = QHBoxLayout()
        release_group = QGroupBox("Выпуск автомобиля в рейс")
        release_layout = QVBoxLayout()
        self.release_button = QPushButton("Выпустить в рейс")
        self.release_button.clicked.connect(self._release_auto)
        release_layout.addWidget(self.release_button)
        release_group.setLayout(release_layout)
        control_layout.addWidget(release_group)

        arrival_group = QGroupBox("Прибытие автомобиля из рейса")
        arrival_layout = QVBoxLayout()
        arrival_form = QFormLayout()
        self.arrival_combo = QComboBox()
        arrival_form.addRow("Активный рейс:", self.arrival_combo)
        self.arrival_button = QPushButton("Зарегистрировать прибытие")
        self.arrival_button.clicked.connect(self._register_arrival)
        arrival_layout.addLayout(arrival_form)
        arrival_layout.addWidget(self.arrival_button)
        arrival_group.setLayout(arrival_layout)
        control_layout.addWidget(arrival_group)

        layout.addLayout(control_layout)

        # Права на выпуск/прибытие
        can_manage = self.user_info['permissions']['can_manage_journal']
        self.release_button.setEnabled(can_manage)
        self.arrival_button.setEnabled(can_manage)

        active_label = QLabel("Активные рейсы:")
        layout.addWidget(active_label)
        self.active_journal_table = QTableWidget()
        self.active_journal_table.setColumnCount(3)
        self.active_journal_table.setHorizontalHeaderLabels(["ID", "Автомобиль", "Маршрут"])
        layout.addWidget(self.active_journal_table)

        history_label = QLabel("История рейсов:")
        layout.addWidget(history_label)
        self.history_journal_table = QTableWidget()
        self.history_journal_table.setColumnCount(6)
        self.history_journal_table.setHorizontalHeaderLabels(["ID", "Автомобиль", "Маршрут", "Отправление", "Прибытие", "Длительность"])
        layout.addWidget(self.history_journal_table)

    def _setup_reports_tab(self):
        layout = QVBoxLayout(self.reports_tab)
        info_label = QLabel()
        if self.user_info['permissions']['can_generate_reports']:
            info_label.setText("Формирование отчетов (доступно)")
            info_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px; background-color: #eafaf1; border-radius: 3px;")
        else:
            info_label.setText("Просмотр отчеты (только просмотр)")
            info_label.setStyleSheet("color: #3498db; font-weight: bold; padding: 5px; background-color: #ebf5fb; border-radius: 3px;")
        layout.addWidget(info_label)

        title_label = QLabel("ОТЧЕТЫ")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title_label)

        report1_group = QGroupBox("Отчет: Рекорды маршрутов")
        report1_layout = QVBoxLayout()
        report1_description = QLabel("Минимальное время проезда по каждому маршруту")
        report1_description.setWordWrap(True)
        report1_layout.addWidget(report1_description)
        self.report1_button = QPushButton("Сформировать отчет")
        self.report1_button.clicked.connect(self._generate_report1)
        report1_layout.addWidget(self.report1_button)
        self.report1_table = QTableWidget()
        report1_layout.addWidget(self.report1_table)
        report1_group.setLayout(report1_layout)
        layout.addWidget(report1_group)

        report2_group = QGroupBox("Отчет: Среднее время проезда")
        report2_layout = QVBoxLayout()
        report2_description = QLabel("Среднее время проезда по каждому маршруту (в минутах)")
        report2_description.setWordWrap(True)
        report2_layout.addWidget(report2_description)
        self.report2_button = QPushButton("Сформировать отчет")
        self.report2_button.clicked.connect(self._generate_report2)
        report2_layout.addWidget(self.report2_button)
        self.report2_table = QTableWidget()
        report2_layout.addWidget(self.report2_table)
        report2_group.setLayout(report2_layout)
        layout.addWidget(report2_group)

        if self.user_info['permissions']['can_export_data']:
            export_layout = QHBoxLayout()
            self.export_report_button = QPushButton("Экспортировать все отчеты в Excel")
            self.export_report_button.clicked.connect(self._export_all_reports)
            export_layout.addWidget(self.export_report_button)
            export_layout.addStretch()
            layout.addLayout(export_layout)

        # Права на отчёты
        can_view = self.user_info['permissions']['can_view_reports']
        self.report1_button.setEnabled(can_view)
        self.report2_button.setEnabled(can_view)
        if hasattr(self, 'export_report_button'):
            self.export_report_button.setEnabled(self.user_info['permissions']['can_export_data'])

    def _load_initial_data(self):
        self._load_table_data()
        self._update_journal_data()
        self._load_reports()

    def _load_table_data(self):
        table_name = self.table_combo.currentText()
        if table_name == "Персонал":
            self._load_personnel_data()
        elif table_name == "Автомобили":
            self._load_auto_data()
        elif table_name == "Маршруты":
            self._load_routes_data()

    def _load_personnel_data(self):
        try:
            query = "SELECT id, first_name, last_name, father_name FROM auto_personnel ORDER BY last_name, first_name"
            result = self.db_connection.execute_query(query)
            if result:
                self.current_table = 'auto_personnel'
                self.current_data = result
                headers = ["ID", "Имя", "Фамилия", "Отчество"]
                data = [[row['id'], row['first_name'], row['last_name'], row['father_name']] for row in result]
                self._display_table_data(headers, data)
                self.table_status.setText(f"Загружено записей: {len(result)}")
            else:
                self.table_status.setText("Нет данных")
        except Exception as e:
            self.table_status.setText(f"Ошибка загрузки: {str(e)}")
            print(f"Ошибка загрузки персонала: {e}")

    def _load_auto_data(self):
        try:
            query = """
                SELECT a.id, a.num, a.color, a.mark,
                       ap.last_name || ' ' || LEFT(ap.first_name, 1) || '.' as driver
                FROM auto a
                LEFT JOIN auto_personnel ap ON a.personnel_id = ap.id
                ORDER BY a.num
            """
            result = self.db_connection.execute_query(query)
            if result:
                self.current_table = 'auto'
                self.current_data = result
                headers = ["ID", "Номер", "Цвет", "Марка", "Водитель"]
                data = [[row['id'], row['num'], row['color'], row['mark'], row['driver']] for row in result]
                self._display_table_data(headers, data)
                self.table_status.setText(f"Загружено записей: {len(result)}")
            else:
                self.table_status.setText("Нет данных")
        except Exception as e:
            self.table_status.setText(f"Ошибка загрузки: {str(e)}")
            print(f"Ошибка загрузки автомобилей: {e}")

    def _load_routes_data(self):
        try:
            query = "SELECT id, name FROM routes ORDER BY name"
            result = self.db_connection.execute_query(query)
            if result:
                self.current_table = 'routes'
                self.current_data = result
                headers = ["ID", "Название маршрута"]
                data = [[row['id'], row['name']] for row in result]
                self._display_table_data(headers, data)
                self.table_status.setText(f"Загружено записей: {len(result)}")
            else:
                self.table_status.setText("Нет данных")
        except Exception as e:
            self.table_status.setText(f"Ошибка загрузки: {str(e)}")
            print(f"Ошибка загрузки маршрутов: {e}")

    def _display_table_data(self, headers, data):
        self.table_view.setRowCount(len(data))
        self.table_view.setColumnCount(len(headers))
        self.table_view.setHorizontalHeaderLabels(headers)
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data) if cell_data is not None else "")
                self.table_view.setItem(row_idx, col_idx, item)
        self.table_view.resizeColumnsToContents()

    def _add_record(self):
        if not self.user_info['permissions']['can_create']:
            QMessageBox.warning(self, "Доступ запрещен", "Недостаточно прав для добавления записей")
            return
        self._perform_record_action(action='add')

    def _edit_record(self):
        if not self.user_info['permissions']['can_update']:
            QMessageBox.warning(self, "Доступ запрещен", "Недостаточно прав для редактирования записей")
            return
        self._perform_record_action(action='edit')

    def _delete_record(self):
        if not self.user_info['permissions']['can_delete']:
            QMessageBox.warning(self, "Доступ запрещен", "Недостаточно прав для удаления записей")
            return
        self._perform_record_action(action='delete')

    def _perform_record_action(self, action):
        if not self.current_table:
            QMessageBox.warning(self, "Ошибка", "Выберите таблицу")
            return

        try:
            if action == 'add':
                if self.current_table == 'auto_personnel':
                    dialog = PersonnelEditDialog(db_connection=self.db_connection, parent=self)
                elif self.current_table == 'auto':
                    dialog = AutoEditDialog(db_connection=self.db_connection, parent=self)
                elif self.current_table == 'routes':
                    dialog = RoutesEditDialog(db_connection=self.db_connection, parent=self)
                else:
                    raise ValueError("Неизвестная таблица")
                if dialog.exec_() == QDialog.Accepted:
                    self._execute_insert(dialog.get_data())
                    self.status_bar.showMessage(f"Запись добавлена в таблицу {self.current_table}")

            elif action == 'edit':
                selected = self.table_view.selectedItems()
                if not selected:
                    QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования")
                    return
                row = selected[0].row()
                record_id = int(self.table_view.item(row, 0).text())
                query = f"SELECT * FROM {self.current_table} WHERE id = %s"
                result = self.db_connection.execute_query(query, (record_id,), fetch_all=False)
                if not result:
                    QMessageBox.warning(self, "Ошибка", "Запись не найдена")
                    return
                record_data = result[0]
                if self.current_table == 'auto_personnel':
                    dialog = PersonnelEditDialog(record_data=record_data, db_connection=self.db_connection, parent=self)
                elif self.current_table == 'auto':
                    dialog = AutoEditDialog(record_data=record_data, db_connection=self.db_connection, parent=self)
                elif self.current_table == 'routes':
                    dialog = RoutesEditDialog(record_data=record_data, db_connection=self.db_connection, parent=self)
                else:
                    raise ValueError("Неизвестная таблица")
                if dialog.exec_() == QDialog.Accepted:
                    self._execute_update(record_id, dialog.get_data())
                    self.status_bar.showMessage(f"Запись #{record_id} обновлена")

            elif action == 'delete':
                selected = self.table_view.selectedItems()
                if not selected:
                    QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления")
                    return
                row = selected[0].row()
                record_id = int(self.table_view.item(row, 0).text())
                reply = QMessageBox.question(
                    self, "Подтверждение удаления",
                    f"Вы уверены, что хотите удалить запись #{record_id}?\nЭто действие нельзя отменить.",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self._execute_delete(record_id)
                    self.status_bar.showMessage(f"Запись #{record_id} удалена")

            self._load_table_data()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить операцию: {str(e)}")
            print(f"Ошибка при выполнении операции: {e}")

    def _execute_insert(self, data):
        if self.current_table == 'auto_personnel':
            query = "INSERT INTO auto_personnel (first_name, last_name, father_name) VALUES (%s, %s, %s)"
            params = (data['first_name'], data['last_name'], data['father_name'])
        elif self.current_table == 'auto':
            query = "INSERT INTO auto (num, color, mark, personnel_id) VALUES (%s, %s, %s, %s)"
            params = (data['num'], data['color'], data['mark'], data['personnel_id'])
        elif self.current_table == 'routes':
            query = "INSERT INTO routes (name) VALUES (%s)"
            params = (data['name'],)
        self.db_connection.execute_query(query, params)

    def _execute_update(self, record_id, data):
        if self.current_table == 'auto_personnel':
            query = "UPDATE auto_personnel SET first_name = %s, last_name = %s, father_name = %s WHERE id = %s"
            params = (data['first_name'], data['last_name'], data['father_name'], record_id)
        elif self.current_table == 'auto':
            query = "UPDATE auto SET num = %s, color = %s, mark = %s, personnel_id = %s WHERE id = %s"
            params = (data['num'], data['color'], data['mark'], data['personnel_id'], record_id)
        elif self.current_table == 'routes':
            query = "UPDATE routes SET name = %s WHERE id = %s"
            params = (data['name'], record_id)
        self.db_connection.execute_query(query, params)

    def _execute_delete(self, record_id):
        query = f"DELETE FROM {self.current_table} WHERE id = %s"
        try:
            self.db_connection.execute_query(query, (record_id,))
        except Exception as e:
            error_msg = str(e)
            if "foreign key constraint" in error_msg.lower():
                QMessageBox.critical(
                    self, "Ошибка удаления",
                    f"Не удалось удалить запись #{record_id}.\n"
                    "Запись связана с другими данными в системе.\n"
                    "Сначала удалите связанные записи."
                )
            else:
                raise

    def _update_journal_data(self):
        try:
            self.arrival_combo.clear()
            query = """
                SELECT j.id, a.num, r.name
                FROM journal j
                JOIN auto a ON j.auto_id = a.id
                JOIN routes r ON j.route_id = r.id
                WHERE j.time_in IS NULL
                ORDER BY j.time_out
            """
            active_trips = self.db_connection.execute_query(query)
            if active_trips:
                for trip in active_trips:
                    display_text = f"Рейс #{trip['id']}: {trip['num']} - {trip['name']}"
                    self.arrival_combo.addItem(display_text, trip['id'])
            else:
                self.arrival_combo.addItem("Нет активных рейсов")
                self.arrival_button.setEnabled(False)

            if active_trips:
                headers = ["ID", "Автомобиль", "Маршрут"]
                data = [[trip['id'], trip['num'], trip['name']] for trip in active_trips]
                self._fill_table(self.active_journal_table, data, headers)
            else:
                self.active_journal_table.setRowCount(0)

            query = """
                SELECT j.id, a.num, r.name, j.time_out, j.time_in,
                       (j.time_in - j.time_out) as duration
                FROM journal j
                JOIN auto a ON j.auto_id = a.id
                JOIN routes r ON j.route_id = r.id
                WHERE j.time_in IS NOT NULL
                ORDER BY j.time_out DESC
                LIMIT 20
            """
            history = self.db_connection.execute_query(query)
            if history:
                headers = ["ID", "Автомобиль", "Маршрут", "Отправление", "Прибытие", "Длительность"]
                data = [
                    [
                        record['id'],
                        record['num'],
                        record['name'],
                        str(record['time_out']),
                        str(record['time_in']),
                        str(record['duration'])
                    ] for record in history
                ]
                self._fill_table(self.history_journal_table, data, headers)
            else:
                self.history_journal_table.setRowCount(0)

        except Exception as e:
            print(f"Ошибка обновления журнала: {e}")

    def _fill_table(self, table, data, headers=None):
        table.setRowCount(len(data))
        table.setColumnCount(len(data[0]) if data else 0)
        if headers:
            table.setHorizontalHeaderLabels(headers)
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data) if cell_data is not None else "")
                table.setItem(row_idx, col_idx, item)
        table.resizeColumnsToContents()

    def _load_reports(self):
        self._generate_report1()
        self._generate_report2()

    def _release_auto(self):
        if not self.user_info['permissions']['can_manage_journal']:
            QMessageBox.warning(self, "Доступ запрещен", "Недостаточно прав для выпуска автомобилей")
            return
        try:
            dialog = JournalEditDialog(self.db_connection, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                query = "INSERT INTO journal (auto_id, route_id, time_out) VALUES (%s, %s, %s)"
                self.db_connection.execute_query(query, (data['auto_id'], data['route_id'], data['time_out']))
                self._update_journal_data()
                self.status_bar.showMessage("Автомобиль выпущен в рейс")
        except Exception as e:
            error_msg = str(e)
            if "автомобиль еще не вернулся" in error_msg.lower():
                QMessageBox.warning(self, "Ошибка",
                                    "Этот автомобиль еще не вернулся из предыдущего рейса.\n"
                                    "Дождитесь его прибытия или выберите другой автомобиль.")
            else:
                QMessageBox.critical(self, "Ошибка", f"Не удалось выпустить автомобиль: {error_msg}")
            print(f"Ошибка выпуска автомобиля: {e}")

    def _register_arrival(self):
        try:
            dialog = ArrivalEditDialog(self.db_connection, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                query = "UPDATE journal SET time_in = %s WHERE id = %s"
                self.db_connection.execute_query(query, (data['time_in'], data['journal_id']))
                self._update_journal_data()
                self.status_bar.showMessage("Прибытие автомобиля зарегистрировано")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось зарегистрировать прибытие: {str(e)}")
            print(f"Ошибка регистрации прибытия: {e}")

    def _generate_report1(self):
        try:
            query = """
                SELECT 
                    r.name as Маршрут,
                    MIN(j.time_in - j.time_out) as Минимальное_время,
                    a.num as Номер_автомобиля,
                    CONCAT(ap.last_name, ' ', LEFT(ap.first_name, 1), '.') as Водитель
                FROM routes r
                JOIN journal j ON r.id = j.route_id
                JOIN auto a ON j.auto_id = a.id
                JOIN auto_personnel ap ON a.personnel_id = ap.id
                WHERE j.time_in IS NOT NULL
                GROUP BY r.name, a.num, ap.last_name, ap.first_name
                ORDER BY Минимальное_время
                LIMIT 10
            """
            result = self.db_connection.execute_query(query)
            if result:
                headers = ["Маршрут", "Минимальное время", "Номер автомобиля", "Водитель"]
                data = [[row['Маршрут'], str(row['Минимальное_время']), row['Номер_автомобиля'], row['Водитель']] for row in result]
                self._fill_table(self.report1_table, data, headers)
                self.status_bar.showMessage(f"Отчет 'Рекорды маршрутов' сформирован: {len(result)} записей")
            else:
                self.report1_table.setRowCount(0)
                self.status_bar.showMessage("Нет данных для отчета")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сформировать отчет: {str(e)}")
            print(f"Ошибка формирования отчета 1: {e}")

    def _generate_report2(self):
        try:
            query = """
                SELECT 
                    r.name as Маршрут,
                    ROUND(AVG(EXTRACT(EPOCH FROM (j.time_in - j.time_out)) / 60), 2) as Среднее_время_в_минутах
                FROM routes r
                JOIN journal j ON r.id = j.route_id
                WHERE j.time_in IS NOT NULL AND j.time_out IS NOT NULL
                GROUP BY r.name
                ORDER BY Среднее_время_в_минутах DESC
            """
            result = self.db_connection.execute_query(query)
            if result:
                headers = ["Маршрут", "Среднее время в минутах"]
                data = [[row['Маршрут'], str(row['Среднее_время_в_минутах'])] for row in result]
                self._fill_table(self.report2_table, data, headers)
                self.status_bar.showMessage(f"Отчет 'Среднее время проезда' сформирован: {len(result)} записей")
            else:
                self.report2_table.setRowCount(0)
                self.status_bar.showMessage("Нет данных для отчета")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сформировать отчет: {str(e)}")
            print(f"Ошибка формирования отчета 2: {e}")

    def _export_all_reports(self):
        try:
            from src.utils.exporter import ExcelExporter
            if self.report1_table.rowCount() > 0:
                ExcelExporter.export_table_to_excel(self.report1_table, "report_records.xlsx")
            if self.report2_table.rowCount() > 0:
                ExcelExporter.export_table_to_excel(self.report2_table, "report_avg_time.xlsx")
            QMessageBox.information(
                self, "Экспорт завершен",
                "Отчеты успешно экспортированы в Excel файлы.\n"
                "Файлы сохранены в текущей директории."
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать отчеты: {str(e)}")
            print(f"Ошибка экспорта: {e}")

    def _change_user(self):
        """
        Открывает окно аутентификации для смены пользователя.
        Простая реализация - перезапуск приложения.
        """
        reply = QMessageBox.question(
            self, "Смена пользователя",
            "Вы уверены, что хотите сменить пользователя?\n"
            "Приложение будет перезапущено.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Импортируем здесь, чтобы избежать циклических импортов
            from src.gui.widgets import LoginDialog
            import subprocess
            import sys
            import os

            # Получаем путь к текущему исполняемому файлу
            if getattr(sys, 'frozen', False):
                # Если приложение собрано в exe
                application_path = sys.executable
            else:
                # Если запуск из Python
                application_path = sys.argv[0]

            # Закрываем текущее окно
            self.close()

            # Закрываем соединения
            if self.db_connection:
                self.db_connection.disconnect()

            if self.auth_system:
                self.auth_system.close()

            # Перезапускаем приложение
            QApplication.quit()

            # Ждем немного перед перезапуском
            QTimer.singleShot(500, lambda: subprocess.Popen([sys.executable] + sys.argv))

    def closeEvent(self, event):
        if self.db_connection:
            self.db_connection.disconnect()
        if self.auth_system:
            self.auth_system.close()
        event.accept()