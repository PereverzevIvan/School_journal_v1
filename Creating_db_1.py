import os
import sqlite3

from PyQt5.QtGui import QIcon
from Designs import progres_window
from PyQt5.QtWidgets import QWidget, QMessageBox
import datetime as dt
from PyQt5.QtCore import QThread, QEvent
from modules.subjects_to_default import return_subjects_to_default
import json


# Функция удаления всех бд из папки "Базы данных"
def delete_files():
    files = os.listdir('Data_bases')
    for i in files:
        file = f'Data_bases/{i}'
        os.remove(file)


def find_db():
    try:
        db_count = (len([i for i in os.listdir('Data_bases') if '.db' in i]))
    except FileNotFoundError:
        os.mkdir('Data_bases')
        db_count = (len([i for i in os.listdir('Data_bases') if '.db' in i]))
    return db_count


# Функция для получения всех дней в учебном году
def get_dates_in_year():
    now_year = dt.datetime.now().year  # Текущий год (календарный)
    now_month = dt.datetime.now().month  # Текущий месяц
    # Уточняем текущий УЧЕБНЫЙ год
    now_year = now_year - 1 if now_month not in range(9, 13) else now_year
    # Дата начала текущего учебного года (начальная дата)
    start_date = dt.datetime(now_year, 9, 1)
    # Дата начала следующего учебного года (конечная дата)
    end_date = dt.datetime(now_year + 1, 5, 31)
    # Список всех дат, которые будут присутствовать в бд
    date_range = []
    while start_date <= end_date:
        # Проверяем, является ли текущий день выходным и не летний ли месяц
        if start_date.weekday() not in [5, 6] and start_date.month not in [6, 7, 8]:
            # Сохраняем дату в формате "ДД-ММ-ГГГГ"
            date_range.append(start_date.strftime('%d-%m-%Y'))
        # Увеличиваем текущую дату на 1 день
        start_date = start_date + dt.timedelta(days=1)
    return date_range


# Загружаем все предметы из json-файла
def get_subs():
    with open('subjects.json', mode='r', encoding='utf-8') as js_file:
        return json.load(js_file)


class CreateDBProcess(QThread):
    def __init__(self, wnd: QWidget):
        QThread.__init__(self)
        self.wnd = wnd

    def run(self):
        delete_files()  # Удаляем все существующие на данный момент бд
        if self.wnd.return_subjects_checkbox.isChecked():
            return_subjects_to_default()  # Возвращаем список предметов в исходное состояние, если нужно
        sub = get_subs()
        classes = tuple([i for i in sub.keys()])  # Ключи словаря с предметами (классы)
        date_range = tuple(get_dates_in_year())  # Даты
        for class_ in classes:
            if self.wnd.want_stop:
                break
            self.wnd.progressBar_2.setValue(0)
            self.wnd.class_2.setText(f'Класс: {int(class_)}')
            con = sqlite3.connect(f'Data_bases/Class_{class_}.db')
            cursor = con.cursor()
            now_subject_index = 0  # Индекс предмета, таблица которого создается в данный момент
            number_of_subjects = len(sub[class_])  # Общее кол-во предметов, преподаваемых в этом классе
            for subject in sub[class_]:
                if self.wnd.want_stop:
                    break
                self.wnd.subject.setText(f'Предмет: {subject}')
                cursor.execute(f"CREATE TABLE IF NOT EXISTS '{subject.lower()}' "
                               f"(id INTEGER PRIMARY KEY AUTOINCREMENT, 'ФИО' TEXT)")
                for date in date_range:
                    cursor.execute(f"ALTER TABLE '{subject.lower()}' ADD COLUMN '{date}' TEXT")
                now_subject_index += 1
                self.wnd.progressBar_2.setValue(round((now_subject_index / number_of_subjects) * 100))
            con.close()
            self.wnd.progressBar.setValue(round((int(class_) / 11) * 100))
        message = 'Базы данных успешно созданы'
        if self.wnd.want_stop:
            message = 'Создание баз данных успешно остановлено'
            delete_files()
        self.wnd.end_process(message)


class CreateDBWindow(QWidget, progres_window.Ui_DBCreateWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('static/icon.png'))
        self.setWindowTitle('Создание баз данных')
        self.setFixedSize(650, 350)
        self.class_2.hide()  # Прячем лэйбл для отображения класса
        self.subject.hide()  # Прячем лэйбл для отображения предмета
        self.btn_start.clicked.connect(self.get_ready)
        self.process = CreateDBProcess(self)
        self.process_was_start = False
        self.want_stop = False
        self.show()

    def start_process(self):
        self.setFixedSize(650, 400)
        self.process_was_start = True
        self.message.setText('Базы данных создаются\n' + 'Чтобы остановить процесс, закройте окно')
        self.progressBar.setValue(0)
        self.progressBar_2.setValue(0)
        self.class_2.show()
        self.subject.show()
        self.btn_start.setEnabled(False)
        self.return_subjects_checkbox.setEnabled(False)
        self.update()
        self.verticalLayout_2.update()
        self.process.start()

    def get_ready(self):
        db_count = find_db()
        if db_count != 0:
            message = 'Вы точно хотите создать базы данных?\n' + \
                      'Все созданные на данный момент базы данных, будут удалены.'
            valid = QMessageBox.question(self, 'Осторожно!', message,
                                         QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.No:
                return
        self.start_process()

    def end_process(self, mess):
        self.process_was_start = False
        self.want_stop = False
        self.message.setText(mess)
        self.class_2.hide()
        self.subject.hide()
        self.btn_start.setEnabled(True)
        self.return_subjects_checkbox.setEnabled(True)
        self.setFixedSize(650, 300)
        self.verticalLayout_2.update()

    def closeEvent(self, event: QEvent):
        if self.process_was_start:
            if not self.want_stop:
                message = 'Вы точно хотите остановить создание баз данных?'
                valid = QMessageBox.question(self, 'Внимание', message, QMessageBox.Yes, QMessageBox.No)
                if valid == QMessageBox.Yes:
                    self.want_stop = True
            event.ignore()
        else:
            event.accept()
