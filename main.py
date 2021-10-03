from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import QFileDialog
import main_window
import progress_gui
import parser
from platform import system
from configparser import ConfigParser


PLATFORM_SEP = '\\' if system() == 'Windows' else '/'  # Устанавливаем раздлитель в зависимости от ОС


class Parse(QtWidgets.QDialog, progress_gui.Ui_Progress):

    def __init__(self, in_filename, output_dir):
        self.in_filename = in_filename
        self.output_dir = output_dir
        self.worker = None
        super(Parse, self).__init__()
        self.setupUi(self)
        self._thread = QtCore.QThread(self)
        self.worker = parser.NordTexParser(in_filename=self.in_filename,
                                           output_dir=self.output_dir,
                                           )
        self.progressBar.setRange(1, 100)
        self.progressBar.setValue(0)
        self.worker.progressBar.connect(self.update_progress)
        self.setWindowTitle('Парсинг...')
        self.worker.start()
        self.worker.moveToThread(self._thread)

    def update_progress(self, err_code, err_msg, i, msg):

        """
        изменение label и progressBar
        :param err_code:100  - value прогрессьбара
                        200     - удачное завершение
                        404     - ошибка
                        500     - не критическая ошибка, программа не прерывается
                        600     - дополнение к выводу, например, "Попытка подключения № 2"
                        700     - установка заголовка окна прогресса
        :param err_msg: Сообщение об ошибке из сигнала
        :param i:       счетчик для прогрессбара
        :param msg:     сообщение из потока
        :return:
        """
        if err_code == 200:
            QtWidgets.QMessageBox.information(None, self.tr('Парсинг.'),
                                              self.tr(err_msg),
                                              QtWidgets.QMessageBox.StandardButton.Ok)
            self.hide()
        elif err_code == 300:
            QtWidgets.QMessageBox.information(None, self.tr('Парсинг.'),
                                              self.tr(err_msg),
                                              QtWidgets.QMessageBox.StandardButton.Ok)

        elif err_code == 404:
            self.hide()
            QtWidgets.QMessageBox.critical(None, self.tr('Ошибка!'),
                                           self.tr(err_msg),
                                           QtWidgets.QMessageBox.StandardButton.Ok)
        elif err_code == 500:
            QtWidgets.QMessageBox.information(None, self.tr('Парсинг.'),
                                              self.tr(err_msg),
                                              QtWidgets.QMessageBox.StandardButton.Ok)
        elif err_code == 600:
            self.worker.progressBar.connect(self.error_label.setText(err_msg))
        elif err_code == 700:
            self.worker.progressBar.connect(self.error_label.setText(err_msg))
            self.setWindowTitle('Парсим данные с предыдущей сессии')
        else:
            self.worker.progressBar.connect(self.progressBar.setValue(i))
            self.error_label.setText(err_msg)
        self.label.setText(msg)

    @QtCore.Slot()
    def closeEvent(self, event):
        close = QtWidgets.QMessageBox()
        close.setText('Вы уверены, что хотите остановить парсинг?')
        close.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        close = close.exec()

        if close == QtWidgets.QMessageBox.Yes:
            event.accept()
            self.worker.stoped = True
        else:
            event.ignore()


class MainWindow(QtWidgets.QMainWindow, main_window.Ui_MainWindow):

    # TODO Сделать настройку разделов для сохранения в разных файлах.
    #  Например, чекбоксами установить названия разделов и выгрузить только эти разделы

    def open_parsing(self):
        self.w1 = Parse(self.input_filename_edit.text(), self.output_dir_edit.text())
        self.w1.show()
        self.save_config()

    def change_directory(self):
        dir_ = self.output_dir_edit.text()
        directory = QFileDialog.getExistingDirectory(self,
                                                     options=QFileDialog.ShowDirsOnly,
                                                     caption="Выбрать папку",
                                                     dir=dir_
                                                     )

        self.output_dir_edit.setText(directory if directory != '' else dir_)

    def open_file(self):
        filename = self.input_filename_edit.text()
        file = (QFileDialog.getOpenFileName(filter='MS Excel *.xls;; Все файлы *.*',
                                            dir=filename,
                                            caption='Выберите файл для обработки'))[0]
        self.input_filename_edit.setText(file if file != '' else filename)

    def __init__(self):
        self.w1, self.w2 = None, None
        super().__init__()
        self.setupUi(self)

        self.input_filename_button.pressed.connect(self.open_file)
        self.output_dir_button.pressed.connect(self.change_directory)
        self.start_button.pressed.connect(self.open_parsing)
        self.fill_field()

    def fill_field(self):
        config: ConfigParser = ConfigParser()
        try:
            config.read(f'config.cfg')

            self.input_filename_edit.setText(config.get('config', 'INFILE'))
            self.output_dir_edit.setText(config.get('config', 'OUTPUTDIR'))

            try:
                import os
                os.mkdir(config.get('config', 'OUTPUTDIR'))
            except FileExistsError:
                pass

        except Exception:
            QtWidgets.QMessageBox.critical(None, self.tr('Ошибка!'),
                                           self.tr('Файл настроек парсера не найден.\n'
                                                   'Создаю файл настроек по умолчанию.'),
                                           QtWidgets.QMessageBox.StandardButton.Ok)
            config['config'] = {
                'INFILE': '',
                'OUTPUTDIR': '',
            }

            with open(f'config.cfg', 'w') as configfile:
                config.write(configfile)
            pass

    def save_config(self):
        config = ConfigParser()
        config['config'] = {
            'INFILE': self.input_filename_edit.text(),
            'OUTPUTDIR': self.output_dir_edit.text(),
        }

        with open(f'config.cfg', 'w') as configfile:
            config.write(configfile)
        pass


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
