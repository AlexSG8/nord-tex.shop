import json
import re
# from datetime import datetime
import xlrd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import selenium.common.exceptions as sel_ex
from time import time
from PySide2 import QtCore
# from export_json_to_excel import export_to_xlsx
from platform import system
from save_sections import save_section

PLATFORM_SEP = '\\' if system() == 'Windows' else '/'  # Устанавливаем раздлитель в зависимости от ОС


class NordTexParser(QtCore.QThread):
    progressBar: QtCore.SignalInstance = QtCore.Signal(object, object, object, object)
    """
         progressBar: QtCore.SignalInstance = QtCore.Signal(err_code, err_msg, iterator, msg)
    """

    @QtCore.Slot()
    def xls_parse(self, filename):
        """
        Parse excel source file

        :param filename: input excel file
        :return: output json file
        """
        try:
            book = xlrd.open_workbook(filename, formatting_info=True)
            sheet = book.sheet_by_index(0)

            headers_index = sheet.col_values(0).index('Артикул')
            headers_name = sheet.row_values(headers_index)  # Строка заголовков
            row_dict = []
            for i in range(headers_index+1, sheet.nrows-1):
                row_dict.append(dict(zip(headers_name, sheet.row_values(i))))

            # Наименование	Цена	Описание	Артикул	Размер	Материал	Фото
            output_json = []
            article = ''
            for c, i in enumerate(row_dict):
                if self.stoped:
                    print('Excel parsing stoped')
                    return
                new_dict = {}

                if str(i['Артикул']) == '':
                    continue
                elif type(i['Артикул']) == str:
                    article = str(i['Артикул'])
                    continue

                new_dict['Наименование'] = i['Название']
                new_dict['Цена'] = str(i['Цена']).replace('.', ',')
                new_dict['Акция'] = str(i['Акция']).replace('.', ',')
                new_dict['Артикул'] = str(int(i['Артикул']))
                new_dict['Материал'] = i['Исходный материал']
                new_dict['Размер'] = i['Размер ']
                new_dict['Size_temp'] = i['Название']
                new_dict['Раздел'] = article
                new_dict['Trade Mark'] = i['Торговая марка']
                output_json.append(new_dict)

            return output_json
        except FileNotFoundError:
            self.progressBar.emit(404, 'Файл не найден!', 0, f'')
            return []
        except Exception as ex:
            print(f'parser.xls_parse: {str(ex)}')
            self.progressBar.emit(404, str(ex), 0, '')

    def get_webdriver(self):
        try:
            options = Options()
            options.headless = True
            options.set_preference("dom.webdriver.enabled", False)  # Отключаем режим драйвера, маскируемся под человека
            options.set_preference("toolkit.cosmeticAnimations.enabled", False)  # Отключаем анимацию
            options.set_preference("permissions.default.image", 2)  # Отключаем картинки
            driver_platform = 'geckodriver.exe' if system() == 'Windows' else 'geckodriver'
            driver = webdriver.Firefox(options=options, executable_path=f'./{driver_platform}')

            return driver
        except Exception as ex:
            print(f'parser.get_webdriver: {str(ex)}')
            self.progressBar.emit(404, str(ex), 0, '')

    def parse_product_selenium(self, article, driver):
        """
        :param driver: web driver
        :param article: product article
        :return: description, photo_urls_lst
        """
        try:
            # Ищем товар по артикулу на странице поиска и забираем его url
            driver.get(f'https://nord-tex.shop/catalog/?q={article}')
            product_url = driver.find_element_by_class_name('dark_link').get_attribute('href')
            driver.get(product_url)

            # Забираем описание товара
            description = driver.find_element_by_class_name('detail_text').text
            # Забираем ссылки на фото
            photo_urls = driver.find_element_by_class_name('wrapp_thumbs').find_element_by_class_name('thumbs') \
                .find_element_by_class_name('flex-viewport').find_element_by_class_name('slides_block') \
                .find_elements_by_tag_name('li')
            photo_urls_lst = []
            for i in range(len(photo_urls)):
                photo_urls_lst.append(f"https://nord-tex.shop{photo_urls[i].get_attribute('data-big')}")

            return description, photo_urls_lst
        except sel_ex.NoSuchElementException:
            return 'Page not found', 'Page not found'
        except sel_ex.WebDriverException:
            driver.close()
            return 'Network Error', 'Website unreachable'
        except Exception as ex:
            print(f'parser.parse_product_selenium: {str(ex)}')
            self.progressBar.emit(404, str(ex), 0, '')

    @QtCore.Slot()
    def run(self):
        try:
            data = self.xls_parse(self.in_filename)  # json после парсинга входного excel файла
            len_data = len(data)

            driver = self.get_webdriver()

            for c, i in enumerate(data):
                if self.stoped:
                    print('Website parsing stoped')
                    driver.close()
                    driver.quit()
                    return

                description, photo_urls = self.parse_product_selenium(i['Артикул'], driver)
                if description == 'Network Error' and photo_urls == 'Website unreachable':
                    print('Website unreachable')
                    return
                i['Описание'] = str(i['Размер']) + '\n\n' + str(description) + \
                                   ('\n#постельное белье #комплект постельного белья'
                                    if 'КПБ' in i['Наименование'] else '')
                i['Фото'] = photo_urls
                i['Размер'] = self.get_size(i['Size_temp'])
                self.progressBar.emit(100,
                                      '',
                                      (c + 1) * 100 / len_data,
                                      f'Товар {str(c+1)} из {str(len_data)} загружен.'
                                      )

                print(f'Выполнено {c+1} из {len_data}\t', i)

            driver.close()
            driver.quit()

            # Очистка json от мусора
            out_data = []
            for d in data:
                if d['Цена'] == '0,0':
                    d['Цена'] = 'Акция'
                d['Фото'] = str(d['Фото']).replace(',', ';').replace("'", "").replace(']', '').replace('[', '')
                if d['Фото'] == 'Page not found' and 'Page not found' in d['Описание']:
                    d['Фото'] = ''
                    d['Описание'] = ''
                out_data.append(d)
            # Запись конечного json
            try:
                with open(f'{self.output_dir}{PLATFORM_SEP}output.json', 'w') as outfile:
                    json.dump(out_data, outfile, indent=2, ensure_ascii=False)
            except PermissionError as ex:
                self.progressBar.emit(404, str(ex), 0, f'')

            # export_to_xlsx(in_data=f'{self.output_dir}{PLATFORM_SEP}output.json',
            #                filename=f'{self.output_dir}{PLATFORM_SEP}catalog_export_'
            #                f'{datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")}.xlsx')
            save_section(directory=f'{self.output_dir}{PLATFORM_SEP}',
                         in_file=f'{self.output_dir}{PLATFORM_SEP}output.json')

            self.progressBar.emit(200, 'Завершено.', 0, f'')
        except Exception as ex:
            print(f'parser.run: {ex}')
            self.progressBar.emit(404, str(ex), 0, '')

    @staticmethod
    def get_size(size_temp):
        """
        Преобразует размеры в необходимые
        :param size_temp:
        :return:
        """

        re_nums = re.compile(r'\d+/\d+')
        size = re_nums.search(size_temp)

        if '1,5СП' in size_temp:
            return 'Полутораспальное'
        elif '2,0СП' in size_temp:
            return 'Двуспальное'
        elif 'Евро' in size_temp:
            return 'Евро'
        elif 'Семейный' in size_temp:
            return 'Семейный'
        elif 'Ясли' in size_temp:
            return 'Ясли'
        elif size:
            ssize = str(size_temp[size.start():size.end()])
            if len(ssize.split('/')[0]) <= 1 or len(ssize.split('/')[1]) <= 1 or \
                    len(ssize.split('/')[0]) >= 4 or len(ssize.split('/')[1]) >= 4:
                return ''
            return ssize
        else:
            return ''

    def get_section(self):
        """
        Разделения на разделы
        :return:
        """

        pass

    def __init__(self, in_filename, output_dir, parent=None):
        self.stoped = False
        self.in_filename = in_filename
        self.output_dir = output_dir
        QtCore.QThread.__init__(self, parent)


if __name__ == '__main__':
    start_time = time()
    NordTexParser('infile.xls', 'output.json')
    print(f'Выполнено за {time()-start_time} сек.')
