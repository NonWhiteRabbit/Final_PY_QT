import sys
import os
import sqlite3
from PySide2.QtCore import Qt, Slot, QModelIndex
from PySide2.QtWidgets import QApplication, QWidget, QTableView, QMainWindow, QFileDialog, QToolBar, \
    QVBoxLayout, QMessageBox, QWidgetAction, QInputDialog, QAction
from PySide2.QtGui import QIcon
from PySide2.QtSql import QSqlDatabase, QSqlTableModel, QSqlRecord
from ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow, QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.sql = None
        self.filter = [["Файлы баз данных (*.db *.sdb *.sqlite *.db3 *.s3db *.sqlite3 *.sl3 *.db2 *.s2db *.sqlite2 "
                        "*.sl2)"], ["Все файлы (*)"]]
        self.action_widgets = []
        self.filename = None

        self.action_4 = QAction("Выход")
        icon_000 = QIcon('ico/exit_closethesession_close_6317.ico')
        self.action_4.setIcon(icon_000)
        self.ui.menuFile.addAction(self.action_4)
        self.action_4.triggered.connect(self.exit)
        self.ui.action.triggered.connect(self.openFile)
        self.ui.action_2.triggered.connect(self.newFile)
        self.ui.action_3.triggered.connect(self.saveFile)
        self.action_widgets.append(self.ui.action_3)

        self.ui.menuFile.setTitle('Файл')
        toolbar = QToolBar()
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        toolbar.setMovable(False)

        self.open_new_file = QWidgetAction(self.ui.menubar)
        icon01 = QIcon('ico/catalog_open.ico')
        self.open_new_file.setIcon(icon01)
        self.open_new_file.setToolTip('Открыть каталог')
        toolbar.addAction(self.open_new_file)
        self.open_new_file.triggered.connect(self.openFile)

        self.create_catalog = QWidgetAction(self.ui.menubar)
        icon03 = QIcon('ico/new-file_40454.ico')
        self.create_catalog.setIcon(icon03)
        self.create_catalog.setToolTip('Создать каталог')
        toolbar.addAction(self.create_catalog)
        self.create_catalog.triggered.connect(self.newFile)

        self.save_file = QWidgetAction(self.ui.menubar)
        icon02 = QIcon('ico/save_14949.ico')
        self.save_file.setIcon(icon02)
        self.save_file.setToolTip('Сохранить изменения')
        toolbar.addAction(self.save_file)
        self.save_file.triggered.connect(self.saveFile)
        self.action_widgets.append(self.save_file)

        self.search = QWidgetAction(self.ui.menubar)
        icon1 = QIcon('ico/android-search_icon-icons.com_50501.ico')
        self.search.setIcon(icon1)
        self.search.setToolTip('Найти запись')
        toolbar.addAction(self.search)
        self.search.triggered.connect(self.bookSearch)
        self.action_widgets.append(self.search)

        self.add_table_row = QWidgetAction(self.ui.menubar)
        icon2 = QIcon('ico/add-book_icon-icons.com_71795.ico')
        self.add_table_row.setIcon(icon2)
        self.add_table_row.setToolTip('Добавить запись')
        toolbar.addAction(self.add_table_row)
        self.add_table_row.triggered.connect(self.addRecord)
        self.action_widgets.append(self.add_table_row)

        self.del_table_row = QWidgetAction(self.ui.menubar)
        icon3 = QIcon('ico/open-book-with-minus-sign_icon-icons.com_70432.ico')
        self.del_table_row.setIcon(icon3)
        self.del_table_row.setToolTip('Удалить запись')
        toolbar.addAction(self.del_table_row)
        self.del_table_row.triggered.connect(self.removeRecord)
        self.action_widgets.append(self.del_table_row)

        self.clean_catalog = QWidgetAction(self.ui.menubar)
        icon4 = QIcon('ico/delete_4219.ico')
        self.clean_catalog.setIcon(icon4)
        self.clean_catalog.setToolTip('Очистить каталог')
        toolbar.addAction(self.clean_catalog)
        self.clean_catalog.triggered.connect(self.cleanCatalog)
        self.action_widgets.append(self.clean_catalog)

        self.undo_action = QWidgetAction(self.ui.menubar)  # TODO: Не отменяет добавление, удаление и очистку записей
        icon5 = QIcon('ico/undolinear_106178.ico')
        self.undo_action.setIcon(icon5)
        self.undo_action.setToolTip('Отмена действия')
        toolbar.addAction(self.undo_action)
        self.undo_action.triggered.connect(self.undoAction)
        self.action_widgets.append(self.undo_action)

        self.refresh_catalog = QWidgetAction(self.ui.menubar)
        icon6 = QIcon('ico/vcsupdaterequired_93493.ico')
        self.refresh_catalog.setIcon(icon6)
        self.refresh_catalog.setToolTip('Обновить')
        toolbar.addAction(self.refresh_catalog)
        self.refresh_catalog.triggered.connect(self.refresh)
        self.action_widgets.append(self.refresh_catalog)

        self.close_catalog = QWidgetAction(self.ui.menubar)
        icon7 = QIcon('ico/action_exit_close_remove_13915.ico')
        self.close_catalog.setIcon(icon7)
        self.close_catalog.setToolTip('Закрыть каталог')
        toolbar.addAction(self.close_catalog)
        self.close_catalog.triggered.connect(self.catalogClose)
        self.action_widgets.append(self.close_catalog)

        self.actionwidgetsOff()

    @classmethod
    def empty_widget(cls):
        """
        Метод для создания пустого Виджета
        :return: empty_widget
        """
        empty_widget = QWidget()
        return empty_widget

    def actionwidgetsOn(self):
        """
        Метод для активации Action-виджетов
        :return: None
        """
        for i in self.action_widgets:
            i.setEnabled(True)

    def actionwidgetsOff(self):
        """
        Метод для деактивации Action-виджетов
        :return: None
        """
        for i in self.action_widgets:
            i.setEnabled(False)

    def confirmAction(self):
        """
        Метод для подтверждения выбранного действия
        :return: str(result)
        """
        result = QMessageBox.question(None, "Подтверждение выбора",
                                      "Вы действительно хотите вьполнить действие?",
                                      buttons=QMessageBox.Yes | QMessageBox.No,
                                      defaultButton=QMessageBox.Yes)
        return str(result)

    @Slot()
    def openFile(self):
        """
        Слот для подключения каталога
        :return: None
        """
        dialog = QFileDialog.getOpenFileName(caption="Открыть каталог",
                                             dir=str(os.path.abspath("main.py")),
                                             filter=f"{self.filter[0]};;{self.filter[1]}",
                                             selectedFilter=f"{self.filter[0]}")
        if len(str(dialog[0])) != 0:
            if str(dialog[0]).split(".")[1] not in ('db', 'sdb', 'sqlite', 'db3', 's3db', 'sqlite3', 'sl3', 'db2',
                                                    's2db', 'sqlite2', 'sl2'):
                QMessageBox.information(None, "Предупреждение", "Данный тип файлов не поддерживается",
                                        buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)
            else:
                self.filename = str(dialog[0])
                self.sql = SQLite(self.filename)
                widget = self.sql.on()
                self.setCentralWidget(widget)
                self.resize(widget.width(), widget.height())
                self.actionwidgetsOn()

    @Slot()
    def newFile(self):
        """
        Слот для создания нового каталога
        :return: None
        """
        dialog = QFileDialog.getSaveFileName(caption="Создать каталог",
                                             dir=str(os.path.abspath("main.py")),
                                             filter=f"Data base(*.db);;{self.filter[1]}",
                                             selectedFilter=f"Data base(*.db)")
        if len(str(dialog[0])) == 0:
            QMessageBox.information(None, "Предупреждение", "Введите название файла",
                                    buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)
        else:
            conn = sqlite3.connect(str(dialog[0]))
            cursor = conn.cursor()
            cursor.execute("""CREATE TABLE books (Название_книги text, Автор  text, Год_выпуска text, Жанр text, Статус text)""")
            conn.commit()
            conn.close()
            self.filename = str(dialog[0])
            self.sql = SQLite(self.filename)
            widget = self.sql.on()
            self.setCentralWidget(widget)
            self.resize(widget.width(), widget.height())
            self.actionwidgetsOn()

    @staticmethod
    def lower_func(string: str):
        return string.lower()

    @Slot()
    def bookSearch(self):  # TODO: не работает поиск, если не совпадает регистр
        """
        Слот для поиска информации в каталоге
        :return: None
        """
        valid = False
        tip_text = None
        while not valid:
            s, ok = QInputDialog.getText(None, "Окно поиска", "Найти", text=tip_text)
            tip_text = s
            if ok:
                # self.sql.conn.create_function("mylower", 1, MainWindow.lower_func)
                # s = s.lower()
                self.sql.model.setFilter(f"Название_книги LIKE '%{s}%' "
                                         f"OR Автор LIKE '%{s}%' "
                                         f"OR Год_выпуска LIKE '%{s}%' "
                                         f"OR Жанр LIKE '%{s}%' "
                                         f"OR Статус LIKE '%{s}%'")
                self.sql.model.select()
            else:
                self.refresh()
                valid = True

    @Slot()
    def addRecord(self):
        """
        Слот для добавления записи в каталог
        :return: None
        """
        self.sql.model.insertRow(self.sql.model.rowCount())
        self.sql.model.submitAll()

    @Slot()
    def removeRecord(self):
        """
        Слот для удаления записи из каталога
        :return: None
        """
        result = self.confirmAction()
        if result.split(".")[-1] == "Yes":
            if not self.sql.tableView.selectedIndexes():
                QMessageBox.information(None, "Предупреждение", "Выберите запись для удаления",
                                        buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)
            else:
                self.sql.model.removeRow(self.sql.tableView.currentIndex().row())
                self.sql.model.submitAll()
                self.sql.model.select()

    @Slot()
    def catalogClose(self):
        """
        Слот для закрытия каталога
        :return: None
        """
        result = self.confirmAction()
        if result.split(".")[-1] == "Yes":
            self.sql.db.close()
            self.setCentralWidget(MainWindow.empty_widget())
            self.actionwidgetsOff()

    @Slot()
    def undoAction(self):
        """
        Слот для отмены выполненных изменений
        :return: None
        """
        self.sql.model.revertAll()


    @Slot()
    def refresh(self):
        """
        Слот для обновления вывода на экран содержимого каталога
        :return: None
        """
        self.sql.model.submitAll()
        self.sql.db.close()
        self.sql = SQLite(self.filename)
        widget = self.sql.on()
        self.setCentralWidget(widget)
        self.resize(widget.width(), widget.height())

    @Slot()
    def cleanCatalog(self):
        """
        Слот для очистки каталога от записей
        :return: None
        """
        datas = None
        result = self.confirmAction()
        if result.split(".")[-1] == "Yes":
            for i in range(self.sql.model.rowCount()-1, -1, -1):
                datas = self.sql.model.removeRow(i)
        self.sql.model.submitAll()
        self.sql.model.select()
        if datas is True:
            QMessageBox.information(None, "Информационное сообщение", "Каталог успешно очищен",
                                    buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)

    @Slot()
    def saveFile(self):
        """
        Слот для сохранения изменений в каталоге
        :return: None
        """
        self.sql.model.submitAll()

    @Slot()
    def exit(self):
        QApplication.quit()


class SQLite(QSqlDatabase):
    """
    Класс для инициализации и открытия базы данных каталога, полученный из Slot'а (openFile)
    """
    def __init__(self, path=None):
        """
        Инициализация экземпляра класса
        :param path: путь до каталога, полученный изиз Slot'а (openFile)
        """
        super().__init__()
        self.path = path
        self.width = 0
        self.heigh = 0
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(self.path)
        self.db.open()
        self.window = QWidget()
        self.window.setWindowTitle("Каталог книг")
        self.conn = sqlite3.connect(self.path)
        cursor = self.conn.cursor()
        sql = f'select * from sqlite_master where type = "table"'  # получение имени таблицы(первая в списке), к которой будет
                                                                    # осуществлено подключение
        cursor.execute(sql)
        self.search_result = cursor.fetchall()[0][1]
        self.model = QSqlTableModel(parent=self.window, db=self.db)
        self.model.setTable(self.search_result)
        self.db_record = QSqlRecord(self.db.record(self.search_result))
        self.tableView = QTableView()

    def on(self):
        """
        Метод для подключения и отображения подключенного каталога
        :return: виджет self.window
        """
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model.select()
        self.model.setHeaderData(-1, Qt.Horizontal, self.db_record.fieldName(0))
        vbox = QVBoxLayout()
        self.tableView.setModel(self.model)
        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()
        for i in range(self.model.columnCount() + 2):
            self.width += self.tableView.columnWidth(i)
        for j in range(self.model.rowCount() + 1):
            self.heigh += self.tableView.rowHeight(j)
        self.tableView.resize(self.width + 50, self.heigh + 50)
        vbox.addWidget(self.tableView)
        self.window.setLayout(vbox)
        self.window.resize(self.tableView.width()+30, self.tableView.height()+120)
        return self.window


def main(argv):
    app = QApplication(argv)

    main_window = MainWindow()
    main_window.show()

    return app.exec_()


if __name__ == '__main__':
    if not 'QT_QPA_PLATFORM_PLUGIN_PATH' in os.environ:
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = './platforms'

    exit_status = main(sys.argv)
    sys.exit(exit_status)
