"""
Модуль для экспорта данных в Excel.
"""

import pandas as pd
from datetime import datetime
import os


class ExcelExporter:
    """Класс для экспорта данных в Excel"""

    @staticmethod
    def export_table_to_excel(table_widget, filename=None):
        """
        Экспортирует данные из QTableWidget в Excel.

        Args:
            table_widget: QTableWidget с данными
            filename: Имя файла для сохранения (если None - генерируется автоматически)

        Returns:
            str: Путь к сохраненному файлу или None в случае ошибки
        """
        try:
            # Получаем данные из таблицы
            data = []
            headers = []

            # Получаем заголовки
            for col in range(table_widget.columnCount()):
                header_item = table_widget.horizontalHeaderItem(col)
                headers.append(header_item.text() if header_item else f"Column {col}")

            # Получаем данные
            for row in range(table_widget.rowCount()):
                row_data = []
                for col in range(table_widget.columnCount()):
                    item = table_widget.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)

            # Создаем DataFrame
            df = pd.DataFrame(data, columns=headers)

            # Генерируем имя файла если не указано
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"report_{timestamp}.xlsx"

            # Сохраняем в Excel
            df.to_excel(filename, index=False)

            return os.path.abspath(filename)

        except Exception as e:
            print(f"Ошибка экспорта в Excel: {e}")
            return None

    @staticmethod
    def export_query_to_excel(db_connection, query, filename=None, params=None):
        """
        Экспортирует результаты SQL запроса в Excel.

        Args:
            db_connection: Подключение к БД
            query: SQL запрос
            filename: Имя файла для сохранения
            params: Параметры запроса

        Returns:
            str: Путь к сохраненному файлу или None в случае ошибки
        """
        try:
            # Выполняем запрос
            result = db_connection.execute_query(query, params)

            if not result:
                print("Нет данных для экспорта")
                return None

            # Создаем DataFrame
            df = pd.DataFrame(result)

            # Генерируем имя файла если не указано
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data_export_{timestamp}.xlsx"

            # Сохраняем в Excel
            df.to_excel(filename, index=False)

            return os.path.abspath(filename)

        except Exception as e:
            print(f"Ошибка экспорта запроса в Excel: {e}")
            return None