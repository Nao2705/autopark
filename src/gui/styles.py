"""
Стили для PyQt5 приложения.
"""

STYLES = {
    # Основные стили
    'main_window': """
        QMainWindow {
            background-color: #f0f0f0;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
    """,

    # Стили для меню
    'menu_bar': """
        QMenuBar {
            background-color: #2c3e50;
            color: white;
            padding: 4px;
            font-size: 13px;
        }
        QMenuBar::item {
            background-color: transparent;
            padding: 5px 10px;
        }
        QMenuBar::item:selected {
            background-color: #34495e;
            border-radius: 3px;
        }
        QMenuBar::item:pressed {
            background-color: #1a252f;
        }
    """,

    # Стили для кнопок
    'button_primary': """
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #1c6ea4;
        }
        QPushButton:disabled {
            background-color: #95a5a6;
            color: #7f8c8d;
        }
    """,

    'button_danger': """
        QPushButton {
            background-color: #e74c3c;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #c0392b;
        }
        QPushButton:pressed {
            background-color: #a93226;
        }
    """,

    'button_success': """
        QPushButton {
            background-color: #27ae60;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #229954;
        }
        QPushButton:pressed {
            background-color: #1e8449;
        }
    """,

    # Стили для таблиц
    'table_widget': """
        QTableWidget {
            background-color: white;
            alternate-background-color: #f8f9fa;
            selection-background-color: #3498db;
            selection-color: white;
            gridline-color: #dee2e6;
            border: 1px solid #ced4da;
            border-radius: 4px;
        }
        QTableWidget::item {
            padding: 6px;
        }
        QTableWidget::item:selected {
            background-color: #3498db;
            color: white;
        }
        QHeaderView::section {
            background-color: #2c3e50;
            color: white;
            padding: 8px;
            border: none;
            font-weight: bold;
        }
        QHeaderView::section:checked {
            background-color: #34495e;
        }
    """,

    # Стили для полей ввода
    'line_edit': """
        QLineEdit {
            padding: 8px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            background-color: white;
            font-size: 13px;
        }
        QLineEdit:focus {
            border: 2px solid #3498db;
            padding: 7px;
        }
        QLineEdit:disabled {
            background-color: #e9ecef;
            color: #6c757d;
        }
    """,

    # Стили для вкладок
    'tab_widget': """
        QTabWidget::pane {
            border: 1px solid #dee2e6;
            background-color: white;
            border-radius: 4px;
        }
        QTabBar::tab {
            background-color: #f8f9fa;
            padding: 8px 16px;
            margin-right: 2px;
            border: 1px solid #dee2e6;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #3498db;
            font-weight: bold;
        }
        QTabBar::tab:hover:!selected {
            background-color: #e9ecef;
        }
    """,

    # Стили для статус бара
    'status_bar': """
        QStatusBar {
            background-color: #2c3e50;
            color: white;
            padding: 4px;
            font-size: 12px;
        }
    """,

    # Стили для диалоговых окон
    'dialog': """
        QDialog {
            background-color: #f8f9fa;
        }
        QLabel {
            color: #2c3e50;
            font-size: 13px;
        }
    """,

    # Стили для групповых рамок
    'group_box': """
        QGroupBox {
            font-weight: bold;
            border: 2px solid #dee2e6;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: white;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
    """,

    # Стили для комбобоксов
    'combo_box': """
        QComboBox {
            padding: 6px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            background-color: white;
        }
        QComboBox:editable {
            background-color: white;
        }
        QComboBox:!editable, QComboBox::drop-down:editable {
            background-color: white;
        }
        QComboBox:!editable:on, QComboBox::drop-down:editable:on {
            background-color: white;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #ced4da;
        }
        QComboBox::down-arrow {
            image: url(down_arrow.png);
        }
    """
}


def apply_styles(widget):
    """
    Применяет все стили к виджету и его дочерним элементам.

    Args:
        widget: PyQt виджет
    """
    widget.setStyleSheet(STYLES['main_window'])