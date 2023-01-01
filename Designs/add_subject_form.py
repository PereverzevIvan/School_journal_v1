# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'add_subject_form.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AddSubjectForm(object):
    def setupUi(self, AddSubjectForm):
        AddSubjectForm.setObjectName("AddSubjectForm")
        AddSubjectForm.resize(770, 325)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AddSubjectForm.sizePolicy().hasHeightForWidth())
        AddSubjectForm.setSizePolicy(sizePolicy)
        AddSubjectForm.setMinimumSize(QtCore.QSize(770, 325))
        AddSubjectForm.setMaximumSize(QtCore.QSize(770, 325))
        AddSubjectForm.setStyleSheet("background-color: dodgerblue")
        self.horizontalLayout = QtWidgets.QHBoxLayout(AddSubjectForm)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget = QtWidgets.QWidget(AddSubjectForm)
        self.widget.setStyleSheet("background-color: white; border-radius: 10px")
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.class_line = QtWidgets.QLineEdit(self.widget)
        self.class_line.setMinimumSize(QtCore.QSize(0, 35))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.class_line.setFont(font)
        self.class_line.setStyleSheet("border-radius: 5px;\n"
"background-color: white;\n"
"border: 2px solid black;\n"
"color: black;")
        self.class_line.setObjectName("class_line")
        self.verticalLayout.addWidget(self.class_line)
        self.error_lab1 = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.error_lab1.setFont(font)
        self.error_lab1.setObjectName("error_lab1")
        self.verticalLayout.addWidget(self.error_lab1)
        self.label_2 = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.name_line = QtWidgets.QLineEdit(self.widget)
        self.name_line.setMinimumSize(QtCore.QSize(0, 35))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.name_line.setFont(font)
        self.name_line.setStyleSheet("border-radius: 5px;\n"
"background-color: white;\n"
"border: 2px solid black;\n"
"color: black;")
        self.name_line.setObjectName("name_line")
        self.verticalLayout.addWidget(self.name_line)
        self.error_lab2 = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.error_lab2.setFont(font)
        self.error_lab2.setObjectName("error_lab2")
        self.verticalLayout.addWidget(self.error_lab2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btn_ok = QtWidgets.QPushButton(self.widget)
        self.btn_ok.setMinimumSize(QtCore.QSize(35, 35))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.btn_ok.setFont(font)
        self.btn_ok.setStyleSheet("QPushButton {\n"
"    border: 2px solid black;\n"
"    border-radius: 5px;\n"
"    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                      stop: 0 #f6f7fa, stop: 1 #dadbde);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                      stop: 0 #dadbde, stop: 1 #f6f7fa);\n"
"}")
        self.btn_ok.setObjectName("btn_ok")
        self.horizontalLayout_2.addWidget(self.btn_ok)
        self.btn_delete = QtWidgets.QPushButton(self.widget)
        self.btn_delete.setMinimumSize(QtCore.QSize(35, 35))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.btn_delete.setFont(font)
        self.btn_delete.setStyleSheet("QPushButton {\n"
"    border: 2px solid black;\n"
"    border-radius: 5px;\n"
"    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                      stop: 0 #f6f7fa, stop: 1 #dadbde);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                      stop: 0 #dadbde, stop: 1 #f6f7fa);\n"
"}")
        self.btn_delete.setObjectName("btn_delete")
        self.horizontalLayout_2.addWidget(self.btn_delete)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout.addWidget(self.widget)

        self.retranslateUi(AddSubjectForm)
        QtCore.QMetaObject.connectSlotsByName(AddSubjectForm)

    def retranslateUi(self, AddSubjectForm):
        _translate = QtCore.QCoreApplication.translate
        AddSubjectForm.setWindowTitle(_translate("AddSubjectForm", "Form"))
        self.label.setText(_translate("AddSubjectForm", "Класс:"))
        self.error_lab1.setText(_translate("AddSubjectForm", "error"))
        self.label_2.setText(_translate("AddSubjectForm", "Название:"))
        self.error_lab2.setText(_translate("AddSubjectForm", "error"))
        self.btn_ok.setText(_translate("AddSubjectForm", "Добавить"))
        self.btn_delete.setText(_translate("AddSubjectForm", "Удалить"))
