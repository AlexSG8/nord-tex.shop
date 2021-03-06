# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide2 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(520, 150)
        MainWindow.setMinimumSize(QtCore.QSize(520, 150))
        MainWindow.setMaximumSize(QtCore.QSize(520, 150))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 40, 260, 28))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 10, 260, 28))
        self.label_2.setObjectName("label_2")
        self.output_dir_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.output_dir_edit.setGeometry(QtCore.QRect(280, 40, 200, 28))
        self.output_dir_edit.setObjectName("output_dir_edit")
        self.input_filename_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.input_filename_edit.setGeometry(QtCore.QRect(280, 10, 200, 28))
        self.input_filename_edit.setObjectName("input_filename_edit")
        self.input_filename_button = QtWidgets.QToolButton(self.centralwidget)
        self.input_filename_button.setGeometry(QtCore.QRect(480, 10, 28, 28))
        self.input_filename_button.setObjectName("input_filename_button")
        self.output_dir_button = QtWidgets.QToolButton(self.centralwidget)
        self.output_dir_button.setGeometry(QtCore.QRect(480, 40, 28, 28))
        self.output_dir_button.setObjectName("output_dir_button")
        self.start_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_button.setGeometry(QtCore.QRect(165, 71, 191, 50))
        self.start_button.setObjectName("start_button")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 520, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        self.input_filename_edit.setFocus()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "???????????? \"nord-tex.shop\""))
        self.label.setText(_translate("MainWindow", "???????????????? ?????????? ?????? ???????????????????? ????????????????????"))
        self.label_2.setText(_translate("MainWindow", "???????????????? ???????? ?????? ??????????????????"))
        self.input_filename_button.setText(_translate("MainWindow", "..."))
        self.output_dir_button.setText(_translate("MainWindow", "..."))
        self.start_button.setText(_translate("MainWindow", "??????????????????"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
