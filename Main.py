import os
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTableWidgetItem, QMessageBox, QCalendarWidget, \
    QScrollBar
from Designs import Pupil_form, Main_window, add_subject_form, about_us
from Creating_db_1 import CreateDBWindow
import sqlite3
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtGui import QPixmap, QIcon
from modules.Errors import PupilNotFoundError
import json


def question_valid(wnd, message):
    mes_box = QMessageBox().question(wnd, 'Подтверждение', message, QMessageBox.Yes, QMessageBox.No)
    return mes_box


# Загружаем все предметы из json-файла
def get_subs():
    with open('subjects.json', mode='r', encoding='utf-8') as js_file:
        return json.load(js_file)


# Функция для предотвращения ошибки деления на ноль при вычислении среднего балла ученика
def get_len_for_sort(lenth):
    return lenth if lenth else 1


# Функция для сдвига желаемого периода на месяц вперед или назад
def month_move(move, date):
    months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    date_str = [int(i) for i in date.split('-')][::-1]
    date = dt.datetime(*date_str)
    if (date.year % 400 == 0) or (date.year % 4 == 0 and date.year % 100 != 0):
        months[1] = 29
    if move == 'ago':
        date -= dt.timedelta(days=months[(date.month - 2) % 12])
    else:
        date += dt.timedelta(days=months[(date.month - 1) % 12])
    return date


# Функция для определения следующего учебного года
def now_education_year():
    now_year = dt.datetime.now().year
    now_month = dt.datetime.now().month
    now_year = now_year - 1 if now_month not in range(9, 13) else now_year
    need_date = dt.datetime(now_year, 9, 1)
    next_date = dt.datetime(now_year + 1, 5, 31)
    return need_date, next_date


def too_many_days(frt_date, scd_date):
    st_dt = [int(i) for i in frt_date.split('-')]
    fn_dt = [int(i) for i in scd_date.split('-')]
    start_date = dt.datetime(st_dt[2], st_dt[1], st_dt[0])
    finish_date = dt.datetime(fn_dt[2], fn_dt[1], fn_dt[0])
    if finish_date - start_date > dt.timedelta(days=366):
        return True
    return False


# Функция нахождения промежуточных дат между двумя введёнными
def between_dates(frt_date, scd_date):
    all_date = []
    st_dt = [int(i) for i in frt_date.split('-')]
    fn_dt = [int(i) for i in scd_date.split('-')]
    start_date = dt.datetime(st_dt[2], st_dt[1], st_dt[0])
    finish_date = dt.datetime(fn_dt[2], fn_dt[1], fn_dt[0])
    while start_date <= finish_date:
        if start_date.weekday() not in [5, 6] and start_date.month not in [6, 7, 8]:
            all_date.append(start_date.strftime('%d-%m-%Y'))
        start_date += dt.timedelta(days=1)
    if not all_date:
        all_date = [start_date + dt.timedelta(days=1)]
    return all_date


def find_db():
    try:
        db_count = len([i for i in os.listdir('Data_bases') if '.db' in i])
    except FileNotFoundError:
        db_count = 0
    return db_count


# Класс с логикой главного окна
class MainWindow(QMainWindow, Main_window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Школьный журнал')
        self.setWindowIcon(QIcon('static/icon.png'))
        self.class_box.addItems([str(i) for i in range(1, 12)])  # Список классов
        self.error_lab.hide()
        self.btn_open_pupil.clicked.connect(self.open_pupil_form)  # Кнопка для открытия профиля ученика

        sub = get_subs()
        self.class_box.currentTextChanged.connect(self.subject_box_update)  # Список предметов
        self.subject_box.addItems(sub[self.class_box.currentText()])

        self.check_class.clicked.connect(self.show_pupils)  # Кнопка для загрузки бд
        self.table_puplis.itemChanged.connect(self.update_elem)  # Событие изменения содержимого ячейки
        self.btn_delete_pupil.clicked.connect(self.delete_elem)  # Кнопка для удаления ученика
        self.btn_add_pupil.clicked.connect(self.insert_elem)  # Кнопка для добавления ученика
        self.btn_find_pupil.clicked.connect(self.find_pupils)  # Кнопка для поиска ученика
        self.btn_sort.clicked.connect(self.sort_pupil)  # Кнопка для сортировки учеников
        self.sort_order.clicked.connect(self.change_sort_order)  # Кнопка смены порядка сортировки
        self.create_bd_action.triggered.connect(self.create_data_bases)  # Кнопка для создания бд
        self.about_action.triggered.connect(self.open_about_us)
        self.add_subject_action.triggered.connect(self.open_add_subject_form)  # Кнопка для управления предметами
        self.month_ago.clicked.connect(lambda ch, x='ago': self.month_fast_move(x))
        self.month_later.clicked.connect(lambda ch, x='later': self.month_fast_move(x))

        start_calendar = QCalendarWidget()
        start_calendar.setStyleSheet('background-color: white; padding-right: 10px; color: black')
        start_calendar.setGridVisible(True)
        start_calendar.setVerticalHeaderFormat(0)
        finish_calendar = QCalendarWidget()
        finish_calendar.setStyleSheet('background-color: white; padding-right: 10px; color: black')
        finish_calendar.setGridVisible(True)
        finish_calendar.setVerticalHeaderFormat(0)

        start, finish = now_education_year()  # Период за который будут показаны оценки (по умолчанию)
        self.start_date.setDate(start)
        self.finish_date.setDate(start + dt.timedelta(days=30))
        self.start_date.setCalendarWidget(start_calendar)
        self.finish_date.setCalendarWidget(finish_calendar)

        scroll_1 = QScrollBar()
        scroll_1.setStyleSheet('background-color: lightgray')
        scroll_2 = QScrollBar()
        scroll_2.setStyleSheet('background-color: lightgray')

        self.table_puplis.setVerticalScrollBar(scroll_1)
        self.table_puplis.setHorizontalScrollBar(scroll_2)

        # События смены периода, за который нужно показать оценки
        self.start_date.dateChanged.connect(self.change_now_between_dates)
        self.finish_date.dateChanged.connect(self.change_now_between_dates)

        self.table_class = ''  # Номер класса, который мы хотим открыть
        self.table_name = ''  # Название предмета, который мы хотим вывести

        self.window_for_create = None  # Окно для создания баз данных
        self.window_about_us = None  # Окно "О нас"
        self.add_subject_wnd = None  # Окно управления учебными предметами
        self.open_pupil_profiles = []  # Открытые окна профилей учеников

        self.con = None  # Соединение с бд
        self.all_titles = []  # Список всех заголовков столбцов в базе данных
        self.variability = False  # Изменчивость таблицы
        self.find_process = False  # Процесс поиска
        self.sort_process = False  # Процесс сортировки
        self.loading_between_dates = ''  # Период, даты в котором уже найдены (текущий)
        # Период, даты в котором предстоит найти (будущий)
        self.now_between_dates = f'{self.start_date.text()} {self.finish_date.text()}'
        self.between_date = []  # Все даты в указанном периоде

        self.month_ago.setToolTip('Передвинуть период на месяц назад')
        self.month_later.setToolTip('Передвинуть период на месяц вперед')

        self.sort_direction = '🠗'
        self.sort_order.setText('🠗')
        self.sort_order.setToolTip('По возрастанию')
        self.sort_order.setIcon(QIcon('static/sort-icon_1.png'))

    def month_fast_move(self, move):
        self.start_date.setDate(month_move(move, self.start_date.text()))
        self.finish_date.setDate(month_move(move, self.finish_date.text()))

    # Метод смены порядка сортировки (по убыванию или по возрастанию)
    def change_sort_order(self):
        if self.sort_direction == '🠕':
            self.sort_direction = '🠗'
            self.sort_order.setToolTip('По возрастанию')
            self.sort_order.setIcon(QIcon('static/sort-icon_1.png'))
        else:
            self.sort_direction = '🠕'
            self.sort_order.setToolTip('По убыванию')
            self.sort_order.setIcon(QIcon('static/sort-icon.png'))

    # Метод закрытия окна
    def closeEvent(self, event):
        event.accept()  # Закрываем окно
        exit()

    # Метод смены периода, за который нужно поставить оценки
    def change_now_between_dates(self):
        self.now_between_dates = f'{self.start_date.text()} {self.finish_date.text()}'

    # Метод простого показа таблицы в её изначальном виде
    def show_pupils(self):
        # Проверка наличия бд
        if find_db() == 11:
            self.find_process = False
            self.sort_process = False
            self.pupil_name_for_find.setText('')  # Очищаем поле для поиска учеников
            self.table_puplis.clear()  # Очищаем таблицу
            self.error_lab.hide()
            self.table_class = self.class_box.currentText()  # Класс
            self.table_name = self.subject_box.currentText()  # Предмет

            # Устанавливаем связь с бд
            self.con = sqlite3.connect(f"Data_bases/Class_{self.table_class}.db")
            cur = self.con.cursor()
            try:
                rows_in_table = cur.execute(f"SELECT * FROM '{self.table_name.lower()}'").fetchall()
            except sqlite3.OperationalError:
                self.error_lab.setText('Предмет не найден')
                self.error_lab.show()
                return
            # Получаем все заголовки колонок в бд
            self.all_titles = [description[0] for description in cur.description]
            self.load_table(rows_in_table)  # Загружаем полученную информацию в таблицу

        else:
            self.error_lab.setText('К сожалению, базы данных отсутствуют (их можно создать во вкладке'
                                   ' "Дополнительный функционал")')
            self.error_lab.show()

    # Метод, который загружает в QTableWidget данные, полученные в качестве аргумента
    def load_table(self, rows_in_table):
        self.variability = False
        # Если текущий период не совпадает с будущим находим новые даты в заданном периоде
        if self.loading_between_dates != self.now_between_dates:
            if not too_many_days(self.start_date.text(), self.finish_date.text()):
                self.between_date = [i for i in self.all_titles if i in
                                     between_dates(self.start_date.text(), self.finish_date.text())]
                if self.between_date == []:
                    self.error_lab.setText('Данный период не содержит никакой информации')
                    self.error_lab.show()
            else:
                self.error_lab.setText('Вы выбрали слишком большой промежуток времени')
                self.error_lab.show()
                self.between_date = []
            self.loading_between_dates = self.now_between_dates
        # Список дат, оценки за которые будут отображены
        used_titles = self.all_titles[:2] + self.between_date
        # Список индексов нужных дат в списке всех дат
        used_titles_indexes = [self.all_titles.index(i) for i in used_titles]
        self.table_puplis.setColumnCount(len(used_titles))  # Кол-во колонок в таблице
        self.table_puplis.setRowCount(len(rows_in_table) + 1)  # Кол-во строк в таблице
        # Заполняем первую строку таблицы заголовками колонок
        for i, row in enumerate(used_titles):
            self.table_puplis.setItem(0, i, QTableWidgetItem(str(row)))
        # Загружаем в таблицу остальную информацию
        for i, row in enumerate(rows_in_table):
            column_set = 0
            for j in used_titles_indexes:
                elem = row[j]
                elem = '' if elem is None else elem
                self.table_puplis.setItem(i + 1, column_set, QTableWidgetItem(str(elem)))
                column_set += 1
        self.table_puplis.setColumnWidth(0, 50)
        self.table_puplis.setColumnWidth(1, 250)
        [self.table_puplis.setColumnWidth(i, 85) for i in range(2, self.table_puplis.columnCount())]
        self.variability = True
        self.update()

    # Метод для сортировки учеников
    def sort_pupil(self):
        self.error_lab.hide()
        # Если таблицу можно изменить
        if self.variability:
            sort_key = self.sort_key_box.currentText()  # Ключ сортировки
            cur = self.con.cursor()  # Курсор
            request_1 = f"SELECT * FROM '{self.table_name.lower()}'\n"
            request_2 = f"ORDER BY {sort_key}"
            if sort_key == 'Среднему баллу':
                rows_in_table = cur.execute(request_1).fetchall()
                pupils = {}
                [pupils.__setitem__(x[0], tuple(int(j) for j in x[2:] if j is not None and j.isdigit())) for x in
                 rows_in_table]
                new_list = sorted([[key, round(sum(pupils[key]) / get_len_for_sort(len(pupils[key])), 2)]
                                   for key in pupils.keys()], key=lambda x: x[1])
                rows_in_table = [rows_in_table[i[0] - 1] for i in new_list]
            else:
                rows_in_table = cur.execute(request_1 + request_2).fetchall()
            if self.sort_direction == '🠕':
                rows_in_table = rows_in_table[::-1]
            self.load_table(rows_in_table)
            self.sort_process = True
            self.find_process = False
        else:
            self.error_lab.setText('Сначала загрузите таблицу, нажав на кнопку "Показать"')
            self.error_lab.show()

    # Метод поиска ученика(ов)
    def find_pupils(self):
        self.error_lab.hide()
        if self.variability:
            # Подстрока, по которой будет производиться поиск
            desire_pupil = self.pupil_name_for_find.text()
            if desire_pupil:
                cur = self.con.cursor()  # Курсор
                rows_in_table = cur.execute(f"SELECT * FROM '{self.table_name.lower()}'").fetchall()
                if rows_in_table:
                    rows_in_table = [i for i in rows_in_table if i[1] is not None]
                    rows_in_table = [i for i in rows_in_table if desire_pupil.lower() in i[1].lower()]
                    if rows_in_table:
                        self.load_table(rows_in_table)
                        self.find_process = True
                        self.sort_process = False
                    else:
                        self.error_lab.setText('Ученик не найден')
                        self.error_lab.show()
            else:
                self.error_lab.setText('Поле для ввода ФИО ученика пустое')
                self.error_lab.show()
        else:
            self.error_lab.setText('Сначала загрузите таблицу, нажав на кнопку "Показать"')
            self.error_lab.show()

    # Метод, изменяющий таблицу базы данных в соответствии с QTableWidget
    def update_elem(self, tb_item):
        if self.variability:
            change = False  # Прошло ли изменение все проверки
            # Получаем заголовок колонки
            column_name = self.table_puplis.item(0, tb_item.column()).text()
            # Получаем id ученика
            pupil_id = self.table_puplis.item(tb_item.row(), 0).text()
            # Получаем текст, который фигурирует в изменении
            item_content = self.table_puplis.item(tb_item.row(), tb_item.column()).text()
            request_2 = ''
            request_3 = f"WHERE id = {pupil_id}"
            if tb_item.row() != 0:
                if tb_item.column() == 1:
                    # Если ячейка не содержит цифр
                    if all(el not in ''.join(item_content.split()) for el in '123456790!@#$%^&*()?/"№:,./|\\'):
                        change = True
                        request_2 = f"SET '{column_name}' = '{item_content}'\n"
                    elif item_content == '':
                        item_content = 'NULL'
                        request_2 = f"SET '{column_name}' = {item_content}\n"
                        change = True
                elif tb_item.column() > 1:
                    # Если ячейка содержит только цифры
                    if item_content.isdigit():
                        # Если попадает в диапазон от [2;5]
                        if int(item_content) in range(2, 6):
                            request_2 = f"SET '{column_name}' = {item_content}\n"
                            change = True
                    else:
                        if item_content.lower() == 'н':
                            item_content = 'н'
                            request_2 = f"SET '{column_name}' = '{item_content}'\n"
                            change = True
                    if item_content == '':
                        item_content = 'NULL'
                        request_2 = f"SET '{column_name}' = {item_content}\n"
                        change = True
            if change:
                cur = self.con.cursor()
                if tb_item.column() == 1:
                    # Проводим изменения во всех таблицах бд
                    sub = get_subs()
                    for subject in sub[self.table_class]:
                        request_1 = f"UPDATE '{subject.lower()}'\n"
                        request = request_1 + request_2 + request_3
                        cur.execute(request)
                else:
                    request_1 = f"UPDATE '{self.table_name.lower()}'\n"
                    request = request_1 + request_2 + request_3
                    cur.execute(request)
                self.con.commit()
            # Обновляем таблицу в том режиме, в котором она была до внесения изменения
            if self.find_process:
                self.find_pupils()
            elif self.sort_process:
                self.sort_pupil()
            else:
                self.show_pupils()

    # Метод нумерации всех оставшихся после удаления учеников
    def numerate_pupils(self, cur, subject):
        cur_id = 1
        all_ids = cur.execute(f"SELECT id FROM '{subject.lower()}'").fetchall()
        for i in all_ids:
            request_1 = f"UPDATE '{subject.lower()}'\n"
            request_2 = f"SET 'id' = {cur_id}\n"
            request_3 = f"WHERE id = {i[0]}"
            request = request_1 + request_2 + request_3
            cur.execute(request)
            cur_id += 1

    # Метод для удаления строк из таблицы
    def delete_elem(self):
        self.error_lab.hide()
        if self.variability:
            # Получаем индексы выделенных строк таблицы
            select_rows = list(set([i.row() for i in self.table_puplis.selectedItems()]))
            if select_rows and 0 not in select_rows:
                # Просим подтверждения
                mes = 'Вы действительно хотите удалить эти строки?\n' \
                      'Восстановить их уже не получится'
                valid = question_valid(self, mes)
                if valid == QMessageBox.Yes:
                    cur = self.con.cursor()
                    # Получаем id учеников, которых хотим удалить
                    ids = [self.table_puplis.item(i, 0).text() for i in select_rows]
                    # Удаляем этого ученика во всех таблицах бд
                    sub = get_subs()
                    for subject in sub[self.table_class]:
                        # Удаляем
                        for i in ids:
                            request = f"DELETE FROM '{subject.lower()}' WHERE id = {i}"
                            cur.execute(request)
                        # Номируем оставшихся
                        self.numerate_pupils(cur, subject)
                        self.con.commit()
                    # Обновляем таблицу в том режиме, в котором она была до удаления
                    if self.find_process:
                        self.find_pupils()
                    elif self.sort_process:
                        self.sort_pupil()
                    else:
                        self.show_pupils()
            else:
                self.error_lab.setText('Сначала выделите строки, которые хотите удалить')
                self.error_lab.show()
        else:
            self.error_lab.setText('Сначала загрузите таблицу, нажав на кнопку "Показать"')
            self.error_lab.show()

    # Метод для добавления ученика в бд
    def insert_elem(self):
        self.error_lab.hide()
        if self.variability and not self.find_process:
            cur = self.con.cursor()
            # Добавляем ученика во все таблицы бд
            sub = get_subs()
            for subject in sub[self.table_class]:
                ids = [int(self.table_puplis.item(i, 0).text()) for i in range(1, self.table_puplis.rowCount())]
                if len(ids):
                    request = f"INSERT INTO '{subject.lower()}'(ФИО, id) VALUES('', {max(ids) + 1})"
                else:
                    request = f"INSERT INTO '{subject.lower()}'(ФИО, id) VALUES('', 1)"
                cur.execute(request)
                self.con.commit()
            # Обновляем таблицу в том режиме, в котором она была до добавления
            if self.find_process:
                self.find_pupils()
            elif self.sort_process:
                self.sort_pupil()
            else:
                self.show_pupils()
        else:
            if self.find_process:
                self.error_lab.setText('Во время поиска нельзя добавить ученика')
            else:
                self.error_lab.setText('Сначала загрузите таблицу, нажав на кнопку "Показать"')
            self.error_lab.show()

    # Метод для смены учебных предметов в выпадающем списке
    def subject_box_update(self):
        self.error_lab.hide()
        sub = get_subs()
        self.subject_box.clear()
        self.subject_box.addItems(sub[self.class_box.currentText()])

    def clear_pupil_table_widget(self):
        self.table_puplis.clear()
        self.table_puplis.setRowCount(0)
        self.table_puplis.setColumnCount(0)

    # Метод открытия профиля выбранного ученика
    def open_pupil_form(self):
        self.error_lab.hide()
        if self.variability:
            selected_rows = list(set([i.row() for i in self.table_puplis.selectedItems()]))
            if len(selected_rows) == 1 and selected_rows != [0]:
                name = self.table_puplis.item(selected_rows[0], 1).text()  # ФИО
                class_num = self.class_box.currentText()  # Класс
                subject = self.subject_box.currentText()  # Предмет
                p_id = self.table_puplis.item(selected_rows[0], 0).text()  # id ученика
                pupil_form = PupilForm(name, class_num, subject, p_id)  # Окно профиля ученика
                self.open_pupil_profiles.append(pupil_form)  # Добавляем его в общий список
            elif len(selected_rows) > 1:
                self.error_lab.setText('Вы не можете открыть профили двух или более учеников сразу (только поочерёдно)')
                self.error_lab.show()
            elif len(selected_rows) == 0:
                self.error_lab.setText('Чтобы открыть профиль ученика, нужно выделить его строку')
                self.error_lab.show()
        else:
            self.error_lab.setText('Сначала загрузите таблицу, нажав на кнопку "Показать"')
            self.error_lab.show()

    # Метод для открытия окна управления предметами
    def open_add_subject_form(self):
        self.error_lab.hide()
        if find_db() == 11:
            self.add_subject_wnd = AddSubjectForm(self)
        else:
            self.error_lab.setText('К сожалению, базы данных отсутствуют (их можно создать во вкладке'
                                   ' "Дополнительный функционал")')
            self.error_lab.show()

    def open_about_us(self):
        self.error_lab.hide()
        self.window_about_us = AboutUsWindow()

    # Метод открытия окна для создания бд
    def create_data_bases(self):
        self.error_lab.hide()
        if self.window_for_create is not None:
            if not self.window_for_create.process_was_start:
                self.window_for_create.close()
                self.window_for_create = None
                self.create_data_bases()
            else:
                self.error_lab.setText('Базы данных уже создаются')
                self.error_lab.show()
        else:
            self.window_for_create = CreateDBWindow()


# Класс с логикой окна профиля ученика
class PupilForm(QWidget, Pupil_form.Ui_Form):
    def __init__(self, pupil_name, class_num, subject, pupil_id):
        super(PupilForm, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('static/icon_profile.png'))

        sub = get_subs()
        self.objects_box.addItems(sub[class_num])  # Список предметов
        self.objects_box.setCurrentText(subject)

        self.objects_box.currentTextChanged.connect(self.load_info)  # Событие смены предмета
        self.month_ago.clicked.connect(lambda ch, x='ago': self.month_fast_move(x))
        self.month_later.clicked.connect(lambda ch, x='later': self.month_fast_move(x))
        self.pupil_name_line.setText(pupil_name)  # Поле с ФИО ученика
        self.pupil_class.setText(str(class_num))  # Поле с классом ученика
        self.setWindowTitle(f'Профиль {pupil_name}')
        start, finish = now_education_year()  # Период, за который будет показан средний балл
        self.start_date.setDate(start)
        self.finish_date.setDate(start + dt.timedelta(days=30))
        # События смены периода
        self.start_date.dateChanged.connect(self.change_period_event)
        self.finish_date.dateChanged.connect(self.change_period_event)

        self.pupil_id = pupil_id  # id ученика
        self.con = sqlite3.connect(f'Data_bases/Class_{class_num}.db')  # Связь с бд
        self.all_titles = None  # Заголовки колонок
        self.pupil_info = None  # Информация об ученике
        self.pixmap = None  # Изображение

        self.month_ago.setToolTip('Передвинуть период на месяц назад')
        self.month_later.setToolTip('Передвинуть период на месяц вперед')

        start_calendar = QCalendarWidget()
        start_calendar.setStyleSheet('background-color: white; padding-right: 10px; color: black')
        start_calendar.setGridVisible(True)
        start_calendar.setVerticalHeaderFormat(0)
        finish_calendar = QCalendarWidget()
        finish_calendar.setStyleSheet('background-color: white; padding-right: 10px; color: black')
        finish_calendar.setGridVisible(True)
        finish_calendar.setVerticalHeaderFormat(0)

        self.start_date.setCalendarWidget(start_calendar)
        self.finish_date.setCalendarWidget(finish_calendar)

        self.load_info()
        self.show()

    # Метод для быстрой смены месяцев
    def month_fast_move(self, move):
        self.start_date.setDate(month_move(move, self.start_date.text()))
        self.finish_date.setDate(month_move(move, self.finish_date.text()))

    # Метод для загрузки информации об ученике
    def load_info(self):
        try:
            self.label_3.setText('График среднего балла ученика за каждый месяц')
            cur = self.con.cursor()
            subject = self.objects_box.currentText().lower()
            self.pupil_info = cur.execute(f"SELECT * FROM '{subject}' WHERE id = {self.pupil_id}").fetchone()[2:]
            # Получаем заголовки колонок
            self.all_titles = [description[0] for description in cur.description][2:]
            if self.pupil_info is None:
                raise PupilNotFoundError
            # Считаем кол-во пропусков
            leaves = len([i for i in self.pupil_info if i == 'н'])
            self.leaves_l.setText(str(leaves))
            self.create_histogramm()  # Строим график успеваемости
            self.change_period_event()
        # Если по какой-то причине ученик не найден, вызываем соответствующее сообщение
        except PupilNotFoundError:
            self.label_3.setText('К сожалению, этот ученик не зарегистрирован в данном предмете')
            self.graphics.clear()

    # Метод изменяющий содержимое некоторых полей, если период был изменен
    def change_period_event(self):
        btwn_dates = between_dates(self.start_date.text(), self.finish_date.text())
        # Получаем даты в заданном периоде и преобразуем их в индексы нужных колонок
        between_date = [self.all_titles.index(i) for i in btwn_dates if i in self.all_titles]
        self.set_average_score(between_date)
        self.set_leaves_count(between_date)

    # Метод для подсчета количества пропусков за указанный период
    def set_leaves_count(self, between_date):
        leaves = 0
        if between_date:
            leaves = len([self.pupil_info[i] for i in between_date if self.pupil_info[i] == 'н'])
        self.leaves_l.setText(str(leaves))

    # Метод для вычисления среднего балла за определенный период
    def set_average_score(self, between_date):
        average_score = 'Нет'
        if between_date:
            scores = [int(self.pupil_info[i]) for i in between_date
                      if self.pupil_info[i] and self.pupil_info[i].isdigit()]
            if scores:
                average_score = round(sum(scores) / len(scores), 2)
        self.average_score_line.setText(str(average_score))

    # Метод создания графика среднего балла ученика
    def create_histogramm(self):
        plt.close()
        # Словарь, где ключи - месяцы, а значения - оценки, полученные в эти месяцы
        score_month = {'09': [], '10': [], '11': [], '12': [], '01': [], '02': [], '03': [],
                       '04': [], '05': []}
        # Из информации об ученике берем все его оценки
        [score_month[self.all_titles[i][3:5]].append(int(self.pupil_info[i]))
         for i in range(len(self.all_titles)) if self.pupil_info[i] and self.pupil_info[i] in '2345']
        values = []
        for key in score_month.keys():
            scores = score_month[key]
            if len(scores) == 0:
                values += [0]
            else:
                values += [round(sum(scores) / len(scores), 2)]
        # Кол-во колонок в гистограмме
        index = np.arange(9)
        indexes = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        # Формируем саму гистограмму
        plt.bar(indexes, values, color='orange', bottom=0)
        # Выставляем мин. и макс. значения
        plt.ylim(0, 5)
        # Подписываем колонки
        plt.xticks(index, ['сен', 'окт', 'нояб', 'дек', 'янв', 'фев', 'март', 'апр', 'май'])
        # Над каждой колонкой выписываем её точное значение
        for x, y in zip(index, values):
            plt.text(x, y + 0.05, y, ha='center', va='bottom')
        plt.savefig('static/Graphics.png')  # Сохраняем график
        self.pixmap = QPixmap('static/Graphics.png')
        self.graphics.setPixmap(self.pixmap)  # Загружаем его в окно профиля


# Класс, содержащий логику окна для управления предметами
class AddSubjectForm(QWidget, add_subject_form.Ui_AddSubjectForm):
    def __init__(self, wnd):
        super(AddSubjectForm, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Управление предметами')
        self.error_lab1.setText('')
        self.error_lab2.setText('')
        self.setWindowIcon(QIcon('static/icon.png'))
        self.class_line.textChanged.connect(self.class_test)
        self.name_line.textChanged.connect(self.name_test)
        self.btn_ok.clicked.connect(self.enter)
        self.btn_delete.clicked.connect(self.delete)
        self.wnd = wnd
        self.clas = False  # Класс введен корректно
        self.name = False  # Название предмета введено корректно
        self.show()

    # Метод для проверки и показа ошибки в строке ввода класса
    def class_test(self):
        text = self.class_line.text()
        if not text:
            self.clas = False
            self.error_lab1.setText('')
            return
        if not text.isdigit():
            self.clas = False
            self.error_lab1.setText('Введите класс, в котором изучается предмет')
            return
        else:
            if int(text) not in range(1, 12):
                self.clas = False
                self.error_lab1.setText('Введите число от 1 до 11')
                return
        self.clas = True
        self.error_lab1.setText('')
        return

    # Метод для проверки и показа ошибок в строке ввода имени предмета
    def name_test(self):
        text = self.name_line.text()
        if not text:
            self.error_lab2.setText('')
            self.name = False
            return
        if any([str(i) in text for i in range(10)]):
            self.name = False
            self.error_lab2.setText('Название предмета не должно содержать чисел')
            return
        self.name = True
        self.error_lab2.setText('')
        return

    # Метод для добавления предмета в общий список
    def enter(self):
        if self.clas and self.name:
            clas, name = self.class_line.text(), self.name_line.text()
            con = sqlite3.connect(f"Data_bases/Class_{clas}.db")
            cur = con.cursor()
            tables = cur.execute('SELECT name from sqlite_master where type = "table"').fetchall()
            if any([name.lower() == i[0] for i in tables]):
                self.error_lab2.setText('Такой предмет уже есть')
                return
            self.btn_ok.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.error_lab2.setText('Предмет добавляется')
            first_sub = self.wnd.subject_box.itemText(1).lower()
            all_pupils = cur.execute(f"SELECT id, ФИО FROM '{first_sub}'").fetchall()
            cur.execute(f'SELECT * FROM "{first_sub}"')
            all_titles = [description[0] for description in cur.description][2:]
            cur.execute(
                f"CREATE TABLE IF NOT EXISTS '{name.lower()}' (id INTEGER PRIMARY KEY AUTOINCREMENT, 'ФИО' TEXT)")
            for j in all_titles:
                cur.execute(f"ALTER TABLE '{name.lower()}' ADD COLUMN '{j}' TEXT")
            for i in all_pupils:
                cur.execute(f"INSERT INTO '{name.lower()}' (id, ФИО) VALUES({i[0]}, '{i[1]}')")
            con.commit()
            con.close()
            file = get_subs()
            file[clas].append(name.lower().capitalize())
            with open('subjects.json', mode='w', encoding='utf-8') as js_file:
                json.dump(file, js_file, indent=4, ensure_ascii=False)
            self.btn_ok.setEnabled(True)
            self.btn_delete.setEnabled(True)
            self.error_lab2.setText('Добавление предмета прошло успешно')
            self.wnd.subject_box_update()

    def delete(self):
        if self.clas and self.name:
            valid = question_valid(self, 'Вы точно хотите удалить этот предмет?')
            if valid == QMessageBox.No:
                return
            clas, name = self.class_line.text(), self.name_line.text()
            con = sqlite3.connect(f"Data_bases/Class_{clas}.db")
            cur = con.cursor()
            tables = cur.execute('SELECT name from sqlite_master where type= "table"').fetchall()
            if not any([name.lower() == i[0] for i in tables]):
                self.error_lab2.setText('Такого предмета нет')
                return
            else:
                self.btn_ok.setEnabled(False)
                self.btn_delete.setEnabled(False)
                cur.execute(f'DROP TABLE "{name.lower()}"')
                file = get_subs()
                del file[clas][file[clas].index(name.lower().capitalize())]
                with open('subjects.json', mode='w', encoding='utf-8') as js_file:
                    json.dump(file, js_file, indent=4, ensure_ascii=False)
                self.btn_ok.setEnabled(True)
                self.btn_delete.setEnabled(True)
                self.error_lab2.setText('Удаление предмета прошло успешно')
                self.wnd.subject_box_update()
                self.wnd.clear_pupil_table_widget()
                # self.wnd.show_pupils()


class AboutUsWindow(QWidget, about_us.Ui_Form):
    def __init__(self):
        super(AboutUsWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('О нас')
        self.label.setText('Научный руководитель:')
        self.about_author.setText('Никишина Ирина Николаевна')
        self.about_idea_author.setText('Переверзев Иван Дмитриевич')
        self.setWindowIcon(QIcon('static/icon.png'))
        self.pixmap = QPixmap('static/hello.png')
        self.hello_img.setPixmap(self.pixmap)

        scroll = QScrollBar()
        scroll.setStyleSheet('background-color: lightgray')

        self.textBrowser.setVerticalScrollBar(scroll)

        self.show()


def exit():
    sys.exit()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = MainWindow()
    wnd.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
