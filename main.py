import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QPushButton, QFileDialog, QLabel, QSlider, \
                             QHBoxLayout, QWidget, QListWidget, QListWidgetItem, QDialog, QMessageBox, QStyleFactory,
                             QGraphicsView, QGraphicsScene)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QPixmap, QPalette, QColor
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
import fitz  # PyMuPDF
import sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic



class FileDialog(QDialog):
    def __init__(self, parent, db_connection):
        super().__init__(parent)
        uic.loadUi('File.ui', self)

        self.db_connection = db_connection
        self.current_file_id = None

        self.layout = QVBoxLayout()
        self.update_file_list()

        self.prev_file_button.clicked.connect(self.prev_file)
        self.next_file_button.clicked.connect(self.next_file)
        self.delete_file_button.clicked.connect(self.delete_file)

        self.setLayout(self.layout)

    def update_file_list(self):
        # Обновление списка файлов из базы данных
        self.file_list.clear()
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT id, file_path FROM pdf_files")
        for row in cursor.fetchall():
            item = QListWidgetItem(row[1])
            item.setData(1, row[0])
            self.file_list.addItem(item)

    def prev_file(self):
        # Отображение предыдущего файла
        current_row = self.file_list.currentRow()
        if current_row > 0:
            item = self.file_list.item(current_row - 1)
            self.show_pdf(item.data(1))

    def next_file(self):
        # Отображение следующего файла
        current_row = self.file_list.currentRow()
        if current_row < self.file_list.count() - 1:
            item = self.file_list.item(current_row + 1)
            self.show_pdf(item.data(1))

    def show_pdf(self, file_id):
        # Отображение выбранного PDF-файла
        self.current_file_id = file_id
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT file_path FROM pdf_files WHERE id=?", (file_id,))
        file_path = cursor.fetchone()[0]
        self.parent().open_pdf(file_path)

    def delete_file(self):
        # Удаление выбранного файла из базы данных
        if self.current_file_id is not None:
            reply = QMessageBox.question(self, 'Delete File', 'Are you sure you want to delete this file?',
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                cursor = self.db_connection.cursor()
                cursor.execute("DELETE FROM pdf_files WHERE id=?", (self.current_file_id,))
                self.db_connection.commit()
                self.update_file_list()
                self.current_file_id = None


class PDFViewer(QMainWindow):
    dark_palette = None
    light_palette = None

    def __init__(self):
        super().__init__()
        uic.loadUi('Main.ui', self)

        self.scene = QGraphicsScene()

        self.set_light_theme()

        self.toggle_theme_button.clicked.connect(self.toggle_theme)
        self.page_slider.valueChanged.connect(self.update_page)
        self.prev_page_button.clicked.connect(self.prev_page)
        self.next_page_button.clicked.connect(self.next_page)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.open_file_button.clicked.connect(self.open_pdf_dialog)
        self.view_files_button.clicked.connect(self.view_loaded_files)

        self.current_page = 0
        self.current_zoom = 100
        self.document = None
        self.db_connection = self.setup_database()

    def setup_database(self):
        # Настройка базы данных SQLite для хранения информации о загруженных PDF-файлах
        conn = sqlite3.connect("pdf_viewer.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pdf_files (
                id INTEGER PRIMARY KEY,
                file_path TEXT
            )
        """)
        conn.commit()
        return conn

    def open_pdf_dialog(self):
        # Открытие диалогового окна для выбора PDF-файла
        pdf_path, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf)")
        if pdf_path:
            self.open_pdf(pdf_path)
            self.save_pdf_to_database(pdf_path)

    def view_loaded_files(self):
        # Открытие диалогового окна для просмотра списка загруженных PDF-файлов
        dialog = FileDialog(self, self.db_connection)
        dialog.exec()

    def open_pdf(self, pdf_path):
        # Открытие PDF-файла и отображение его содержимого
        self.document = fitz.open(pdf_path)
        self.page_slider.setRange(0, len(self.document) - 1)
        self.show_page(self.current_page)

    def show_page(self, page_num):
        # Отображение конкретной страницы PDF-файла
        if self.document is not None:
            page = self.document.load_page(page_num)
            pix = page.get_pixmap()
            qim = QImage(pix.samples,
                         pix.width,
                         pix.height,
                         pix.stride,
                         QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qim)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.view.setScene(self.scene)
            self.view.setSceneRect(0, 0, pixmap.width(), pixmap.height())
            self.page_slider.setValue(page_num)
            self.page_number_label.setText(f"Page: {page_num + 1}")

    def update_page(self):
        # Обработка изменения номера страницы
        self.show_page(self.page_slider.value())

    def prev_page(self):
        # Переключение на предыдущую страницу
        try:
            if self.current_page > 0:
                self.current_page -= 1
                self.show_page(self.current_page)
        except Exception:
            print('Open PDF file')

    def next_page(self):
        # Переключение на следующую страницу
        try:
            if self.current_page < len(self.document) - 1:
                self.current_page += 1
                self.show_page(self.current_page)
        except Exception:
            print('Open PDF file')

    def zoom_in(self):
        # Увеличение масштаба просмотра страницы
        if self.current_zoom < 200:
            self.current_zoom += 10
            self.update_view()

    def zoom_out(self):
        # Уменьшение масштаба просмотра страницы
        if self.current_zoom > 50:
            self.current_zoom -= 10
            self.update_view()

    def update_view(self):
        # Обновление отображения страницы с учетом текущего масштаба
        if self.document is not None:
            page = self.document.load_page(self.current_page)
            zoom = self.current_zoom / 100
            mediabox = page.mediabox
            width, height = mediabox[:2]
            img = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            qimg = QImage(img.samples, img.width, img.height, img.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.view.setScene(self.scene)
            self.view.setSceneRect(0, 0, width * zoom, height * zoom)

    def toggle_theme(self):
        # Переключение между темной и светлой темами
        current_palette = QApplication.palette()

        if current_palette.text().color() == QColor(0, 0, 0):
            self.set_dark_theme()
        else:
            self.set_light_theme()

    def set_dark_theme(self):
        # Установка темной темы приложения
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        QApplication.setPalette(dark_palette)

    def set_light_theme(self):
        # Установка светлой темы приложения
        light_palette = QPalette()
        light_palette.setColor(QPalette.Window, Qt.white)
        light_palette.setColor(QPalette.WindowText, Qt.black)
        light_palette.setColor(QPalette.Base, Qt.white)
        light_palette.setColor(QPalette.AlternateBase, Qt.white)
        light_palette.setColor(QPalette.ToolTipBase, Qt.white)
        light_palette.setColor(QPalette.ToolTipText, Qt.black)
        light_palette.setColor(QPalette.Text, Qt.black)
        light_palette.setColor(QPalette.Button, Qt.white)
        light_palette.setColor(QPalette.ButtonText, Qt.black)
        light_palette.setColor(QPalette.BrightText, Qt.red)
        light_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        light_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        light_palette.setColor(QPalette.HighlightedText, Qt.white)
        QApplication.setPalette(light_palette)

    def save_pdf_to_database(self, pdf_path):
        # Сохранение информации о загруженном PDF-файле в базу данных
        cursor = self.db_connection.cursor()
        cursor.execute("INSERT INTO pdf_files (file_path) VALUES (?)", (pdf_path,))
        self.db_connection.commit()


def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    viewer = PDFViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
