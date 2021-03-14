import json
import re
import xlsxwriter
import xlwt


def open_json(filename):
    try:
        with open(filename, "r") as read_file:
            data = json.load(read_file)
            return data
    except Exception as ex:
        print(f'def open_json({filename})\nException: {ex}')
        return f'def open_json({filename})\nException: {ex}'


def get_sections(data):
    sections = []
    for i in data:
        if i['Trade Mark'] == 'Disney' or \
                i['Trade Mark'] == 'Marvel' or \
                i['Trade Mark'] == 'Облачко' or \
                i['Trade Mark'] == 'Absolut':
            continue
        else:
            sections.append(i['Раздел'])
    return list(set(sections))


def get_sizes(directory, data, section):
    sizes = list(set([i['Размер'] for i in data]))
    for s in sizes:
        kpbs = []
        for d in data:
            if s in d['Размер'] and d['Цена'] != 'Акция':
                kpbs.append(d)
            else:
                continue
        save_file(directory, section + ' ' + s + '', kpbs)
    return list(set(sizes))


def save_file(directory, filename, data):
    export_to_xls(directory+(filename.replace('"', '')), data)


def export_to_xlsx(filename, in_data):
    """
    Записывает данные в файл Excel

    :param  filename:       имя файла для записи.
    :param  in_data:         данные для записи.
    :return:                None, если данных для записи нет.
    """

    with xlsxwriter.Workbook(f'{filename}.xlsx') as workbook:
        ws = workbook.add_worksheet()
        cell_format_bottom = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'left',
            'font_size': 10
        })
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'font_size': 10,
            'text_wrap': True  # Перенос строки
        })
        # Установка ширины столбцов
        ws.set_column(0, 0, 15)     # Наименование
        ws.set_column(1, 1, 6)      # Цена
        ws.set_column(2, 2, 80)     # Описание
        ws.set_column(3, 3, 6)      # Артикул
        ws.set_column(4, 4, 20)     # Размер
        ws.set_column(5, 5, 10)     # Материал
        ws.set_column(6, 6, 65)     # Фото

        for col, h in enumerate(['Наименование', 'Цена', 'Описание',
                                 'Артикул', 'Размер', 'Материал', 'Фото']):
            ws.write_string(0, col, h, cell_format=cell_format_bottom)

        for row, item in enumerate(in_data, start=1):

            ws.write_string(row, 0, item['Наименование'], cell_format=cell_format)
            ws.write_string(row, 1, item['Цена'], cell_format=cell_format)
            ws.write_string(row, 2, item['Описание'], cell_format=cell_format)
            ws.write_string(row, 3, item['Артикул'], cell_format=cell_format)
            ws.write_string(row, 4, item['Размер'], cell_format=cell_format)
            ws.write_string(row, 5, item['Материал'], cell_format=cell_format)
            ws.write_string(row, 6, str(item['Фото']).replace('[', '').replace(']', '').replace("'", ""),
                            cell_format=cell_format)


def export_to_xls(filename, in_data):
    # Создать таблицу, кодировка символов по умолчанию ascii
    workbook = xlwt.Workbook(encoding='utf-8', style_compression=0)
    ws = workbook.add_sheet('Каталог', cell_overwrite_ok=False)

    # Ширина столбцов
    ws.col(0).width = 150 * 36     # Наименование
    ws.col(1).width = 60 * 36     # Цена
    ws.col(2).width = 800 * 36    # Описание
    ws.col(3).width = 80 * 36     # Артикул
    ws.col(4).width = 200 * 36    # Размер
    ws.col(5).width = 100 * 36    # Материал
    ws.col(6).width = 650 * 36    # Фото

    # Стиль заголовка
    style_header = xlwt.XFStyle()
    style_header.alignment.wrap = 1
    style_header.borders.left = 1
    style_header.borders.right = 1
    style_header.borders.top = 1
    style_header.borders.bottom = 1
    style_header.font.bold = 1
    style_header.font.name = 'Calibri'
    style_header.font.height = 240

    # Стиль ячеек
    style = xlwt.XFStyle()
    style.alignment.wrap = 1
    style.borders.left = 1
    style.borders.right = 1
    style.borders.top = 1
    style.borders.bottom = 1
    style.font.bold = 0
    style.font.name = 'Calibri'
    style.font.height = 240

    # Формируем заголовки
    for col, h in enumerate(['Наименование', 'Цена', 'Описание',
                             'Артикул', 'Размер', 'Материал', 'Фото']):
        ws.write(0, col, label=h, style=style_header)

    # Заполняем таблицу
    for row, item in enumerate(in_data, start=1):
        ws.write(row, 0, item['Наименование'], style=style)
        ws.write(row, 1, item['Цена'], style=style)
        ws.write(row, 2, item['Описание'], style=style)
        ws.write(row, 3, item['Артикул'], style=style)
        ws.write(row, 4, item['Размер'], style=style)
        ws.write(row, 5, item['Материал'], style=style)
        ws.write(row, 6, str(item['Фото']).replace('[', '').replace(']', '').replace("'", ""), style=style)

    workbook.save(f'{filename}.xls')


def save_section(directory, in_file):
    try:
        data = open_json(in_file)
        kpb = list(set('КПБ '+''.join(re.findall(r'"[^..]+"', i)) for i in get_sections(data) if 'КПБ' in i))

        # Выборка по КПБ (кроме детских)
        for k in kpb:
            kpbs = []
            for d in data:
                if k in d['Раздел']:
                    kpbs.append(d)
                else:
                    continue
            get_sizes(directory, kpbs, k)

        # Выборка детских КПБ
        kpb = []
        for i in data:
            if i['Цена'] != 'Акция' and 'КПБ' in i['Раздел'] and ('Marvel' in i['Trade Mark'] or
                                                                  'Disney' in i['Trade Mark'] or
                                                                  'Облачко' in i['Trade Mark']):
                kpb.append(i)
        save_file(directory, 'КПБ Детские - Disney, Marvel, Облачко', kpb)

        # Выборка "Простыни, наволочки, пододеяльники, наматрасники"
        kpb = []
        for i in data:
            if i['Цена'] != 'Акция' and ('простыня ' in i['Наименование'].lower() or
                                         'наволочка ' in i['Наименование'].lower() or
                                         'набор наволоч' in i['Наименование'].lower() or
                                         'пододеяльник ' in i['Наименование'].lower() or
                                         'наматрасник ' in i['Наименование'].lower()):
                kpb.append(i)
        save_file(directory, 'Простыни, наволочки, пододеяльники, наматрасники', kpb)

        # Выборка "Подушки, одеяла"
        kpb = []
        for i in data:
            if i['Цена'] != 'Акция' and ('подушка ' in i['Наименование'].lower() or
                                         'одеяло ' in i['Наименование'].lower()):
                kpb.append(i)
        save_file(directory, 'Подушки, одеяла', kpb)

        # Выборка "Пледы, покрывала"
        kpb = []
        for i in data:
            if i['Цена'] != 'Акция' and ('плед ' in i['Наименование'].lower() or
                                         'покрывало ' in i['Наименование'].lower()):
                kpb.append(i)
        save_file(directory, 'Пледы, покрывала', kpb)

        # Выборка "Полотенца"
        kpb = []
        for i in data:
            if i['Цена'] != 'Акция' and ('полотенце ' in i['Наименование'].lower() or
                                         'набор полотен' in i['Наименование'].lower()):
                kpb.append(i)
        save_file(directory, 'Полотенца', kpb)

        # Выборка "Шторы"
        kpb = []
        for i in data:
            if i['Цена'] != 'Акция' and ('штор' in i['Наименование'].lower()):
                kpb.append(i)
        save_file(directory, 'Шторы', kpb)

        # Выборка "Текстиль для кухни"
        kpb = []
        for i in data:
            if i['Цена'] != 'Акция' and ('скатер' in i['Наименование'].lower() or
                                         'кухн' in i['Наименование'].lower()):
                kpb.append(i)
        save_file(directory, 'Текстиль для кухни, скатерти', kpb)

        # Выборка "Декоративные подушки"
        kpb = []
        for i in data:
            if i['Цена'] != 'Акция' and ('декор' in i['Наименование'].lower() and
                                         'подушк' in i['Наименование'].lower()):
                kpb.append(i)
        save_file(directory, 'Декоративные подушки', kpb)

        # Выборка "КПБ 'Absolut'"
        kpb = []
        for i in data:
            if i['Цена'] != 'Акция' and ('кпб' in i['Наименование'].lower() and
                                         'absolut' in i['Наименование'].lower()):
                kpb.append(i)
        save_file(directory, 'КПБ Absolut', kpb)

        # Выборка "Акции"
        kpb = []
        for i in data:
            if i['Цена'] == 'Акция':
                i['Цена'] = f'Акция\n{i["Акция"]}'
                kpb.append(i)
        save_file(directory, 'Акции', kpb)

        return 'Done'
    except Exception as ex:
        print(f'def save_section({directory, in_file})\nException: {ex}')
        return f'def save_section({directory, in_file})\nException: {ex}'


if __name__ == '__main__':
    save_section('OUTPUT/', 'OUTPUT/output.json')
