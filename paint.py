from PyQt5.QtGui import *  # Импорт всех классов и функций из модуля PyQt5.QtGui
from PyQt5.QtWidgets import *  # Импорт всех классов и функций из модуля PyQt5.QtWidgets
from PyQt5.QtCore import *  # Импорт всех классов и функций из модуля PyQt5.QtCore

from PyQt5 import QtGui  # Импорт модуля QtGui из PyQt5

from PyQt5.QtGui import QPainter, QBitmap, QPolygon, QPen, QBrush, QColor  # Импорт конкретных классов из PyQt5.QtGui
from PyQt5.QtCore import Qt  # Импорт конкретного класса Qt из PyQt5.QtCore

from MainWindow import Ui_MainWindow  # Импорт класса Ui_MainWindow из модуля MainWindow

import sys  # Импорт модуля sys для работы с системными параметрами и функциями
import random  # Импорт модуля random для работы со случайными числами
import types  # Импорт модуля types для работы с типами данных

try:
    # Включение в блок try/except для обработки исключения при использовании в Mac/Linux
    from PyQt5.QtWinExtras import QtWin  # Импорт класса QtWin из PyQt5.QtWinExtras

    myappid = 'com.learnpyqt.minute-apps.paint'  # Уникальный идентификатор приложения
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)  # Установка идентификатора приложения
except ImportError:
    pass  # Игнорирование ошибки ImportError, если модуль не найден

BRUSH_MULT = 3  # Константа для множителя размера кисти
SPRAY_PAINT_MULT = 5  # Константа для множителя параметров распыления краски
SPRAY_PAINT_N = 100  # Константа для числа распыляемых точек

# Список шестнадцатеричных значений цветов
COLORS = [
    '#000000', '#82817f', '#820300', '#868417', '#007e03', '#037e7b', '#040079',
    '#81067a', '#7f7e45', '#05403c', '#0a7cf6', '#093c7e', '#7e07f9', '#7c4002',

    '#ffffff', '#c1c1c1', '#f70406', '#fffd00', '#08fb01', '#0bf8ee', '#0000fa',
    '#b92fc2', '#fffc91', '#00fd83', '#87f9f9', '#8481c4', '#dc137d', '#fb803c',
]

# Список размеров шрифтов
FONT_SIZES = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]

# Список режимов рисования
MODES = [
    'selectpoly', 'selectrect',
    'eraser', 'fill',
    'dropper', 'stamp',
    'pen', 'brush',
    'spray', 'text',
    'line', 'polyline',
    'rect', 'polygon',
    'ellipse', 'roundrect'
]

# Размеры холста
CANVAS_DIMENSIONS = 600, 400

# Список штампов для отображения
STAMPS = [
    ':/stamps/pie-apple.png',
    ':/stamps/pie-cherry.png',
    ':/stamps/pie-cherry2.png',
    ':/stamps/pie-lemon.png',
    ':/stamps/pie-moon.png',
    ':/stamps/pie-pork.png',
    ':/stamps/pie-pumpkin.png',
    ':/stamps/pie-walnut.png',
]
# Создание пера для выделения с определенными параметрами
SELECTION_PEN = QPen(QColor(0xff, 0xff, 0xff), 1, Qt.DashLine)
# Создание пера для предварительного просмотра с определенными параметрами
PREVIEW_PEN = QPen(QColor(0xff, 0xff, 0xff), 1, Qt.SolidLine)


def build_font(config):
    """
    Создание полного шрифта из опций конфигурации
    :param self: ссылка на объект класса
    :param config: словарь с настройками шрифта
    :return: QFont - объект шрифта
    """
    font = config['font']  # Получение шрифта из конфигурации
    font.setPointSize(config['fontsize'])  # Установка размера шрифта
    font.setBold(config['bold'])  # Установка жирности
    font.setItalic(config['italic'])  # Установка курсива
    font.setUnderline(config['underline'])  # Установка подчеркивания
    return font  # Возврат созданного шрифта


class Canvas(QLabel):  # Определение класса Canvas, который наследует QLabel

    mode = 'rectangle'  # Установка начального значения режима рисования

    primary_color = QColor(Qt.black)  # Установка начального значения основного цвета на черный
    secondary_color = None  # Установка начального значения вторичного цвета на None

    primary_color_updated = pyqtSignal(str)  # Создание сигнала обновления основного цвета
    secondary_color_updated = pyqtSignal(str)  # Создание сигнала обновления вторичного цвета

    # Хранение настроек, включая ширину пера, шрифты и т.д.
    config = {
        # Опции рисования.
        'size': 1,
        'fill': True,
        # Опции шрифта.
        'font': QFont('Times'),
        'fontsize': 12,
        'bold': False,
        'italic': False,
        'underline': False,
    }

    active_color = None  # Инициализация переменной для активного цвета
    preview_pen = None  # Инициализация переменной для предварительного пера

    timer_event = None  # Инициализация переменной для события таймера

    current_stamp = None  # Инициализация переменной для текущего штампа

    def initialize(self):  # Определение метода initialize
        # Установка цвета фона в зависимости от вторичного цвета, если он существует, иначе - белый
        self.background_color = QColor(self.secondary_color) if self.secondary_color else QColor(Qt.white)
        self.eraser_color = QColor(self.secondary_color) if self.secondary_color else QColor(Qt.white)
        self.eraser_color.setAlpha(100)  # Установка прозрачности цвета ластиковки
        self.reset()  # Вызов метода reset

    def reset(self):
        # Создание pixmap для отображения.
        self.setPixmap(QPixmap(*CANVAS_DIMENSIONS))

        # Очистка холста.
        self.pixmap().fill(self.background_color)

    def set_primary_color(self, hex):  # Определение метода для установки основного цвета
        self.primary_color = QColor(hex)  # Установка основного цвета из шестнадцатеричного значения

    def set_secondary_color(self, hex):  # Определение метода для установки вторичного цвета
        self.secondary_color = QColor(hex)  # Установка вторичного цвета из шестнадцатеричного значения

    def set_config(self, key, value):  # Определение метода для установки конфигурации
        self.config[key] = value  # Установка значения конфигурации по ключу

    def set_mode(self, mode):  # Определение метода для установки режима
        # Очистка активных анимаций по таймеру.
        self.timer_cleanup()  # Вызов метода для очистки активных анимаций по таймеру
        # Сброс переменных, специфичных для режима (всех)
        self.active_shape_fn = None  # Сброс переменной функции активной формы на None
        self.active_shape_args = ()  # Сброс переменной аргументов активной формы на пустой кортеж

        self.origin_pos = None  # Сброс переменной начальной позиции на None

        self.current_pos = None  # Сброс переменной текущей позиции на None
        self.last_pos = None  # Сброс переменной последней позиции на None

        self.history_pos = None  # Сброс переменной истории позиций на None
        self.last_history = []  # Сброс переменной последней истории на пустой список

        self.current_text = ""  # Сброс переменной текущего текста на пустую строку
        self.last_text = ""  # Сброс переменной последнего текста на пустую строку

        self.last_config = {}  # Сброс переменной последней конфигурации на пустой словарь

        self.dash_offset = 0  # Сброс переменной смещения штриха на 0
        self.locked = False  # Установка переменной заблокированного состояния в False
        # Применение режима
        self.mode = mode  # Установка режима рисования в переданное значение

    def reset_mode(self):
        self.set_mode(self.mode)  # Сброс режима до его текущего значения

    def on_timer(self):
        if self.timer_event:
            self.timer_event()  # Если есть событие таймера, вызываем его

    def timer_cleanup(self):
        if self.timer_event:
            # Остановить таймер, затем выполнить очистку.
            timer_event = self.timer_event  # Сохраняем текущее таймерное событие
            self.timer_event = None  # Сбрасываем таймерное событие
            timer_event(final=True)  # Вызываем сохраненное таймерное событие с параметром final=True

    # События мыши.

    def mousePressEvent(self, e):
        fn = getattr(self, "%s_mousePressEvent" % self.mode,
                     None)  # Получаем метод для обработки события нажатия мыши в соответствии с текущим режимом
        if fn:
            return fn(e)  # Если метод для данного события существует, вызываем его, передавая событие

    def mouseMoveEvent(self, e):
        fn = getattr(self, "%s_mouseMoveEvent" % self.mode,
                     None)  # Получаем метод для обработки события перемещения мыши в соответствии с текущим режимом
        if fn:
            return fn(e)  # Если метод для данного события существует, вызываем его, передавая событие

    def mouseReleaseEvent(self, e):
        fn = getattr(self, "%s_mouseReleaseEvent" % self.mode,
                     None)  # Получаем метод для обработки события отпускания кнопки мыши в соответствии с текущим режимом
        if fn:
            return fn(e)  # Если метод для данного события существует, вызываем его, передавая событие

    def mouseDoubleClickEvent(self, e):
        fn = getattr(self, "%s_mouseDoubleClickEvent" % self.mode,
                     None)  # Получаем метод для обработки двойного щелчка мыши в соответствии с текущим режимом
        if fn:
            return fn(e)  # Если метод для данного события существует, вызываем его, передавая событие

    # Общие события (общие для инструментов, похожих на кисти)

    def generic_mousePressEvent(self, e):
        self.last_pos = e.pos()  # Сохраняем последнюю позицию мыши

        if e.button() == Qt.LeftButton:
            self.active_color = self.primary_color  # Устанавливаем активный цвет в основной цвет при нажатии левой кнопки мыши
        else:
            self.active_color = self.secondary_color  # Иначе устанавливаем активный цвет во вторичный цвет

    def generic_mouseReleaseEvent(self, e):
        self.last_pos = None  # Сбрасываем последнюю позицию мыши в None при отпускании кнопки мыши

    # События, зависящие от режима.

    # Выберите события полигона

    def selectpoly_mousePressEvent(self, e):
        if not self.locked or e.button == Qt.RightButton:  # Если не заблокировано или нажата правая кнопка мыши
            self.active_shape_fn = 'drawPolygon'  # Устанавливаем функцию активной формы на 'drawPolygon'
            self.preview_pen = SELECTION_PEN  # Устанавливаем предварительное перо для выделения на SELECTION_PEN
            self.generic_poly_mousePressEvent(e)  # Вызываем обобщенный метод для обработки события нажатия мыши

    def selectpoly_timerEvent(self, final=False):
        self.generic_poly_timerEvent(final)  # Вызываем обобщенный метод для обработки события по таймеру

    def selectpoly_mouseMoveEvent(self, e):
        if not self.locked:  # Если не заблокировано
            self.generic_poly_mouseMoveEvent(e)  # Вызываем обобщенный метод для обработки события перемещения мыши

    def selectpoly_mouseDoubleClickEvent(self, e):
        self.current_pos = e.pos()  # Устанавливаем текущую позицию мыши по двойному щелчку
        self.locked = True  # Блокируем возможность изменения текущего состояния

    def selectpoly_copy(self):
        """
        Копирование полигональной области из текущего изображения и возврат ее.

        Создаем маску для выделенной области и используем ее для удаления
        невыбранных областей. Затем получаем прямоугольник,
        ограничивающий выделение, и обрезаем его, чтобы получить изображение минимального размера.

        :return: QPixmap скопированной области.
        """
        self.timer_cleanup()  # Очищаем таймерные события

        pixmap = self.pixmap().copy()  # Создаем копию текущего изображения
        bitmap = QBitmap(*CANVAS_DIMENSIONS)  # Создаем битовую карту с размерами CANVAS_DIMENSIONS
        bitmap.clear()  # Начальное состояние с видимыми случайными данными

        p = QPainter(bitmap)
        # Создаем маску, где выделенная пользователем область будет сохранена,
        # а остальная часть изображения будет удалена и станет прозрачной.
        userpoly = QPolygon(self.history_pos + [self.current_pos])  # Создаем полигон из истории и текущей позиции
        p.setPen(QPen(Qt.color1))  # Устанавливаем перо для маски
        p.setBrush(QBrush(Qt.color1))  # Устанавливаем кисть для маски (Qt.color1 == включенный бит)
        p.drawPolygon(userpoly)  # Рисуем полигон
        p.end()  # Завершаем рисование

        # Устанавливаем созданную маску на изображение.
        pixmap.setMask(bitmap)

        # Рассчитываем ограничивающий прямоугольник и возвращаем его копию.
        return pixmap.copy(userpoly.boundingRect())

    # Выберите события прямоугольника

    def selectrect_mousePressEvent(self, e):
        # Установка функции рисования прямоугольника и предварительной кисти для выделения
        self.active_shape_fn = 'drawRect'
        self.preview_pen = SELECTION_PEN
        self.generic_shape_mousePressEvent(e)

    def selectrect_timerEvent(self, final=False):
        # Вызов общего таймерного события для формы прямоугольника
        self.generic_shape_timerEvent(final)

    def selectrect_mouseMoveEvent(self, e):
        if not self.locked:
            self.current_pos = e.pos()  # Обновление текущей позиции при перемещении мыши

    def selectrect_mouseReleaseEvent(self, e):
        self.current_pos = e.pos()  # Захват финальной позиции при отпускании кнопки мыши
        self.locked = True  # Блокировка для завершения выделения

    def selectrect_copy(self):
        """
        Копирование прямоугольной области текущего изображения.

        :return: QPixmap скопированной области.
        """
        self.timer_cleanup()  # Очистка таймерных событий
        return self.pixmap().copy(QRect(self.origin_pos, self.current_pos))  # Копирование прямоугольной области

    # События стирания

    def eraser_mousePressEvent(self, e):
        self.generic_mousePressEvent(e)  # Обработка события нажатия мыши для ластика

    def eraser_mouseMoveEvent(self, e):
        if self.last_pos:
            p = QPainter(self.pixmap())  # Создание объекта QPainter для рисования на изображении
            p.setPen(
                QPen(self.eraser_color, 30, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))  # Настройка параметров ластика
            p.drawLine(self.last_pos, e.pos())  # Рисование линии на изображении от предыдущей позиции до текущей

            self.last_pos = e.pos()  # Обновление последней позиции мыши
            self.update()  # Обновление изображения

    def eraser_mouseReleaseEvent(self, e):
        self.generic_mouseReleaseEvent(e)  # Обработка события отпускания кнопки мыши для ластика

    # События Stamp (pie)

    def stamp_mousePressEvent(self, e):
        p = QPainter(self.pixmap())  # Создание объекта QPainter для рисования на изображении
        stamp = self.current_stamp  # Получение текущего "печати" (stamp)
        # Отрисовка "печати" по координатам нажатия мыши с учетом размера "печати"
        p.drawPixmap(e.x() - stamp.width() // 2, e.y() - stamp.height() // 2, stamp)
        self.update()  # Обновление изображения

    # События пера

    def pen_mousePressEvent(self, e):
        self.generic_mousePressEvent(e)  # Обработка события нажатия мыши для пера

    def pen_mouseMoveEvent(self, e):
        if self.last_pos:
            p = QPainter(self.pixmap())  # Создание объекта QPainter для рисования на изображении
            # Настройка параметров пера и отрисовка линии от предыдущей позиции до текущей
            p.setPen(QPen(self.active_color, self.config['size'], Qt.SolidLine, Qt.SquareCap, Qt.RoundJoin))
            p.drawLine(self.last_pos, e.pos())

            self.last_pos = e.pos()  # Обновление последней позиции мыши
            self.update()  # Обновление изображения

    def pen_mouseReleaseEvent(self, e):
        self.generic_mouseReleaseEvent(e)  # Обработка события отпускания кнопки мыши для пера

    # События кисти

    def brush_mousePressEvent(self, e):
        self.generic_mousePressEvent(e)  # Обработка события нажатия мыши для кисти

    def brush_mouseMoveEvent(self, e):
        if self.last_pos:
            p = QPainter(self.pixmap())  # Создание объекта QPainter для рисования на изображении
            # Настройка параметров кисти и отрисовка линии от предыдущей позиции до текущей
            p.setPen(QPen(self.active_color, self.config['size'] * BRUSH_MULT, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawLine(self.last_pos, e.pos())

            self.last_pos = e.pos()  # Обновление последней позиции мыши
            self.update()  # Обновление изображения

    def brush_mouseReleaseEvent(self, e):
        self.generic_mouseReleaseEvent(e)  # Обработка события отпускания кнопки мыши для кисти

    # Мероприятия по распылению

    def spray_mousePressEvent(self, e):
        self.generic_mousePressEvent(e)  # Обработка события нажатия мыши для распыления краски

    def spray_mouseMoveEvent(self, e):
        if self.last_pos:
            p = QPainter(self.pixmap())  # Создание объекта QPainter для рисования на изображении
            p.setPen(QPen(self.active_color, 1))  # Настройка параметров для распыления краски

            # Создание случайных точек вокруг текущей позиции мыши для эффекта распыления краски
            for n in range(self.config['size'] * SPRAY_PAINT_N):
                xo = random.gauss(0, self.config['size'] * SPRAY_PAINT_MULT)
                yo = random.gauss(0, self.config['size'] * SPRAY_PAINT_MULT)
                p.drawPoint(e.x() + xo, e.y() + yo)

        self.update()  # Обновление изображения

    def spray_mouseReleaseEvent(self, e):
        self.generic_mouseReleaseEvent(e)  # Обработка события отпускания кнопки мыши для распыления краски

    # Текстовые события

    def keyPressEvent(self, e):
        if self.mode == 'text':  # Проверка, что текущий режим - ввод текста
            if e.key() == Qt.Key_Backspace:  # Если нажата клавиша Backspace, удалить последний символ
                self.current_text = self.current_text[:-1]
            else:  # Иначе добавить введенный символ в текст
                self.current_text = self.current_text + e.text()

    def text_mousePressEvent(self, e):
        # Если нажата левая кнопка мыши и текущая позиция пуста
        if e.button() == Qt.LeftButton and self.current_pos is None:
            self.current_pos = e.pos()  # Устанавливаем текущую позицию
            self.current_text = ""  # Очищаем текст
            self.timer_event = self.text_timerEvent  # Устанавливаем событие таймера для текста

        elif e.button() == Qt.LeftButton:

            self.timer_cleanup()  # Очищаем таймер
            # Рисуем текст на изображении
            p = QPainter(self.pixmap())
            p.setRenderHints(QPainter.Antialiasing)
            font = build_font(self.config)  # Создаем шрифт
            p.setFont(font)
            pen = QPen(self.primary_color, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            p.setPen(pen)
            p.drawText(self.current_pos, self.current_text)  # Рисуем текст на холсте
            self.update()  # Обновляем изображение

            self.reset_mode()  # Сбрасываем режим

        elif e.button() == Qt.RightButton and self.current_pos:
            self.reset_mode()  # Сбрасываем режим

    def text_timerEvent(self, final=False):
        p = QPainter(self.pixmap())  # Создаем QPainter для рисования на изображении
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = PREVIEW_PEN
        p.setPen(pen)
        if self.last_text:
            font = build_font(self.last_config)
            p.setFont(font)
            p.drawText(self.current_pos, self.last_text)

        if not final:
            font = build_font(self.config)
            p.setFont(font)
            p.drawText(self.current_pos, self.current_text)

        self.last_text = self.current_text
        self.last_config = self.config.copy()
        self.update()  # Обновляем изображение

    # Заполнять события

    def fill_mousePressEvent(self, e):
        # При нажатии левой кнопки мыши задаем активный цвет
        if e.button() == Qt.LeftButton:
            self.active_color = self.primary_color
        else:
            self.active_color = self.secondary_color

        image = self.pixmap().toImage()  # Получаем изображение из pixmap
        w, h = image.width(), image.height()  # Получаем ширину и высоту изображения
        x, y = e.x(), e.y()  # Получаем координаты щелчка мыши

        # Получаем целевой цвет из начальной позиции.
        target_color = image.pixel(x, y)

        have_seen = set()
        queue = [(x, y)]  # Инициализируем очередь с начальной позицией

        # Функция для получения координат соседних точек
        def get_cardinal_points(have_seen, center_pos):
            points = []
            cx, cy = center_pos
            # Проверяем соседние точки на валидность
            for x, y in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                xx, yy = cx + x, cy + y
                if (xx >= 0 and xx < w and
                        yy >= 0 and yy < h and
                        (xx, yy) not in have_seen):
                    points.append((xx, yy))
                    have_seen.add((xx, yy))  # Добавляем точку во множество уже просмотренных

            return points

        # Производим заполнение области.
        p = QPainter(self.pixmap())  # Создаем QPainter для рисования на pixmap
        p.setPen(QPen(self.active_color))  # Устанавливаем активный цвет

        while queue:  # Пока очередь не пуста
            x, y = queue.pop()
            # Если цвет пикселя соответствует целевому цвету, рисуем точку и добавляем соседние точки в очередь
            if image.pixel(x, y) == target_color:
                p.drawPoint(QPoint(x, y))
                queue.extend(get_cardinal_points(have_seen, (x, y)))

        self.update()  # Обновляем изображение

    # События капельницы

    def dropper_mousePressEvent(self, e):
        # Получаем цвет изображения в позиции, на которую было произведено нажатие мыши
        c = self.pixmap().toImage().pixel(e.pos())
        # Переводим цвет в строковый формат hex
        hex = QColor(c).name()

        if e.button() == Qt.LeftButton:
            # Устанавливаем полученный цвет как основной цвет
            self.set_primary_color(hex)
            self.primary_color_updated.emit(hex)  # Обновляем интерфейс пользователя.

        elif e.button() == Qt.RightButton:
            # Устанавливаем полученный цвет как вторичный цвет
            self.set_secondary_color(hex)
            self.secondary_color_updated.emit(hex)  # Обновляем интерфейс пользователя.

    # Общие события для фигур: прямоугольник, эллипс, закругленный прямоугольник

    def generic_shape_mousePressEvent(self, e):
        # Устанавливаем начальную позицию и текущую позицию при нажатии мыши
        self.origin_pos = e.pos()  # Начальная позиция
        self.current_pos = e.pos()  # Текущая позиция
        self.timer_event = self.generic_shape_timerEvent  # Устанавливаем таймерное событие для фигур

    def generic_shape_timerEvent(self, final=False):
        p = QPainter(self.pixmap())  # Создаем QPainter для рисования на холсте
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)  # Устанавливаем режим композиции для рисования
        pen = self.preview_pen  # Используемая кисть
        pen.setDashOffset(self.dash_offset)  # Устанавливаем смещение для эффекта прерывистой линии
        p.setPen(pen)  # Устанавливаем кисть для рисования

        # Рисуем предварительный эскиз фигуры
        if self.last_pos:
            getattr(p, self.active_shape_fn)(QRect(self.origin_pos, self.last_pos), *self.active_shape_args)

        if not final:
            # Обновляем смещение для эффекта прерывистой линии
            self.dash_offset -= 1
            pen.setDashOffset(self.dash_offset)
            p.setPen(pen)
            # Рисуем фигуру в текущей позиции
            getattr(p, self.active_shape_fn)(QRect(self.origin_pos, self.current_pos), *self.active_shape_args)

        self.update()  # Обновляем холст
        self.last_pos = self.current_pos  # Запоминаем последнюю позицию

    def generic_shape_mouseMoveEvent(self, e):
        # Устанавливаем текущую позицию
        self.current_pos = e.pos()

    def generic_shape_mouseReleaseEvent(self, e):
        if self.last_pos:
            # Очищаем индикатор.
            self.timer_cleanup()

            p = QPainter(self.pixmap())
            # Устанавливаем параметры рисования линии
            p.setPen(QPen(self.primary_color, self.config['size'], Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))

            if self.config['fill']:
                # Устанавливаем заливку, если задано
                p.setBrush(QBrush(self.secondary_color))
            # Рисуем выбранную фигуру (прямоугольник, эллипс и т.д.)
            getattr(p, self.active_shape_fn)(QRect(self.origin_pos, e.pos()), *self.active_shape_args)
            self.update()

        self.reset_mode()

    # События для рисования линии

    def line_mousePressEvent(self, e):
        # Устанавливаем начальную и текущую позиции для рисования линии
        self.origin_pos = e.pos()
        self.current_pos = e.pos()
        self.preview_pen = PREVIEW_PEN
        self.timer_event = self.line_timerEvent

    def line_timerEvent(self, final=False):
        p = QPainter(self.pixmap())
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = self.preview_pen
        p.setPen(pen)
        if self.last_pos:
            # Рисуем предварительный эскиз линии
            p.drawLine(self.origin_pos, self.last_pos)

        if not final:
            # Рисуем линию от начальной позиции к текущей
            p.drawLine(self.origin_pos, self.current_pos)

        self.update()
        self.last_pos = self.current_pos

    def line_mouseMoveEvent(self, e):
        # Устанавливаем текущую позицию для рисования линии
        self.current_pos = e.pos()

    def line_mouseReleaseEvent(self, e):
        if self.last_pos:
            # Очищаем индикатор.
            self.timer_cleanup()

            p = QPainter(self.pixmap())
            # Устанавливаем параметры рисования линии
            p.setPen(QPen(self.primary_color, self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

            # Рисуем линию от начальной позиции до текущей позиции мыши
            p.drawLine(self.origin_pos, e.pos())
            self.update()

        self.reset_mode()

    # Общие события для многоугольников
    def generic_poly_mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.history_pos:
                self.history_pos.append(e.pos())
            else:
                # Начало нового многоугольника
                self.history_pos = [e.pos()]
                self.current_pos = e.pos()
                self.timer_event = self.generic_poly_timerEvent

        elif e.button() == Qt.RightButton and self.history_pos:
            # Очистка, если мы не рисуем многоугольник
            self.timer_cleanup()
            self.reset_mode()

    def generic_poly_timerEvent(self, final=False):
        p = QPainter(self.pixmap())
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = self.preview_pen
        pen.setDashOffset(self.dash_offset)
        p.setPen(pen)
        if self.last_history:
            # Рисуем предыдущий контур, используя индикатор превью
            getattr(p, self.active_shape_fn)(*self.last_history)

        if not final:
            # Обновляем параметры для создания индикатора превью
            self.dash_offset -= 1
            pen.setDashOffset(self.dash_offset)
            p.setPen(pen)
            getattr(p, self.active_shape_fn)(*self.history_pos + [self.current_pos])

        self.update()
        self.last_pos = self.current_pos
        self.last_history = self.history_pos + [self.current_pos]

    def generic_poly_mouseMoveEvent(self, e):
        # Обновляем текущую позицию для создания многоугольника
        self.current_pos = e.pos()

    def generic_poly_mouseDoubleClickEvent(self, e):
        # Очистка предыдущих анимаций, если есть
        self.timer_cleanup()
        p = QPainter(self.pixmap())
        # Установка параметров рисования для полигона
        p.setPen(QPen(self.primary_color, self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        # Применение цвета заливки, игнорируя кисть для полилиний
        if self.secondary_color:
            p.setBrush(QBrush(self.secondary_color))

        # Начало рисования полигона
        getattr(p, self.active_shape_fn)(*self.history_pos + [e.pos()])
        self.update()
        self.reset_mode()

    # События для полилиний

    def polyline_mousePressEvent(self, e):
        # Установка формы активной фигуры в полилинию
        self.active_shape_fn = 'drawPolyline'  # Устанавливает тип текущей фигуры на полилинию
        self.preview_pen = PREVIEW_PEN  # Устанавливает предварительную кисть для предварительного просмотра
        self.generic_poly_mousePressEvent(
            e)  # Вызывает универсальную функцию для обработки нажатия кнопки мыши для полилиний

    def polyline_timerEvent(self, final=False):
        self.generic_poly_timerEvent(
            final)  # Выполняет универсальную функцию для таймера, связанного с рисованием полилиний

    def polyline_mouseMoveEvent(self, e):
        self.generic_poly_mouseMoveEvent(
            e)  # Выполняет универсальную функцию для обработки движения мыши при рисовании полилиний

    def polyline_mouseDoubleClickEvent(self, e):
        self.generic_poly_mouseDoubleClickEvent(
            e)  # Выполняет универсальную функцию для обработки двойного щелчка мыши при рисовании полилиний

    def rect_mousePressEvent(self, e):
        # Установка формы активной фигуры в прямоугольник
        self.active_shape_fn = 'drawRect'  # Устанавливает тип текущей фигуры на прямоугольник
        self.active_shape_args = ()  # Устанавливает аргументы для прямоугольника (в данном случае пусто)
        self.preview_pen = PREVIEW_PEN  # Устанавливает предварительную кисть для предварительного просмотра
        self.generic_shape_mousePressEvent(
            e)  # Вызывает универсальную функцию для обработки нажатия кнопки мыши для прямоугольников

    def rect_timerEvent(self, final=False):
        self.generic_shape_timerEvent(
            final)  # Выполняет универсальную функцию для таймера, связанного с рисованием прямоугольников

    def rect_mouseMoveEvent(self, e):
        self.generic_shape_mouseMoveEvent(
            e)  # Выполняет универсальную функцию для обработки движения мыши при рисовании прямоугольников

    def rect_mouseReleaseEvent(self, e):
        self.generic_shape_mouseReleaseEvent(
            e)  # Выполняет универсальную функцию для обработки отпускания кнопки мыши при рисовании прямоугольников

    # События для многоугольника

    def polygon_mousePressEvent(self, e):
        # Установка формы активной фигуры в многоугольник
        self.active_shape_fn = 'drawPolygon'  # Устанавливает тип текущей фигуры на многоугольник
        self.preview_pen = PREVIEW_PEN  # Устанавливает предварительную кисть для предварительного просмотра
        self.generic_poly_mousePressEvent(
            e)  # Вызывает универсальную функцию для обработки нажатия кнопки мыши для многоугольников

    def polygon_timerEvent(self, final=False):
        self.generic_poly_timerEvent(
            final)  # Выполняет универсальную функцию для таймера, связанного с рисованием многоугольников

    def polygon_mouseMoveEvent(self, e):
        self.generic_poly_mouseMoveEvent(
            e)  # Выполняет универсальную функцию для обработки движения мыши при рисовании многоугольников

    def polygon_mouseDoubleClickEvent(self, e):
        self.generic_poly_mouseDoubleClickEvent(
            e)  # Выполняет универсальную функцию для обработки двойного щелчка мыши при рисовании многоугольников

    # События для эллипса

    def ellipse_mousePressEvent(self, e):
        # Установка формы активной фигуры в эллипс
        self.active_shape_fn = 'drawEllipse'  # Устанавливает тип текущей фигуры на эллипс
        self.active_shape_args = ()  # Задает аргументы для эллипса (в данном случае - пустые)
        self.preview_pen = PREVIEW_PEN  # Устанавливает предварительную кисть для предварительного просмотра
        self.generic_shape_mousePressEvent(
            e)  # Вызывает универсальную функцию для обработки нажатия кнопки мыши для эллипса

    def ellipse_timerEvent(self, final=False):
        self.generic_shape_timerEvent(
            final)  # Выполняет универсальную функцию для таймера, связанного с рисованием эллипса

    def ellipse_mouseMoveEvent(self, e):
        self.generic_shape_mouseMoveEvent(
            e)  # Выполняет универсальную функцию для обработки движения мыши при рисовании эллипса

    def ellipse_mouseReleaseEvent(self, e):
        self.generic_shape_mouseReleaseEvent(
            e)  # Выполняет универсальную функцию для обработки отпускания кнопки мыши при рисовании эллипса

    # События для прямоугольника с закругленными углами

    def roundrect_mousePressEvent(self, e):
        # Установка формы активной фигуры в прямоугольник с закругленными углами
        self.active_shape_fn = 'drawRoundedRect'  # Устанавливает тип текущей фигуры на прямоугольник с закругленными углами
        self.active_shape_args = (25, 25)  # Параметры: ширина и высота закругления
        self.preview_pen = PREVIEW_PEN  # Устанавливает предварительную кисть для предварительного просмотра
        self.generic_shape_mousePressEvent(
            e)  # Вызывает универсальную функцию для обработки нажатия кнопки мыши для прямоугольника с закругленными углами

    def roundrect_timerEvent(self, final=False):
        self.generic_shape_timerEvent(
            final)  # Выполняет универсальную функцию для таймера, связанного с рисованием прямоугольника с закругленными углами

    def roundrect_mouseMoveEvent(self, e):
        self.generic_shape_mouseMoveEvent(
            e)  # Выполняет универсальную функцию для обработки движения мыши при рисовании прямоугольника с закругленными углами

    def roundrect_mouseReleaseEvent(self, e):
        self.generic_shape_mouseReleaseEvent(
            e)  # Выполняет универсальную функцию для обработки отпускания кнопки мыши при рисовании прямоугольника с закругленными углами


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Замена заполнителя холста из QtDesigner.
        self.horizontalLayout.removeWidget(self.canvas)
        self.canvas = Canvas()  # Создание экземпляра класса Canvas
        self.canvas.initialize()  # Инициализация холста
        # Необходимо включить отслеживание мыши для следования за ней без нажатой кнопки.
        self.canvas.setMouseTracking(True)
        # Включение фокуса для перехвата клавиатурных вводов.
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.horizontalLayout.addWidget(self.canvas)  # Добавление холста в макет

        # Настройка кнопок режима
        mode_group = QButtonGroup(self)
        mode_group.setExclusive(True)

        for mode in MODES:
            btn = getattr(self, '%sButton' % mode)  # Получение кнопки по имени режима
            btn.pressed.connect(
                lambda mode=mode: self.canvas.set_mode(mode))  # Назначение обработчика на нажатие кнопки режима
            mode_group.addButton(btn)  # Добавление кнопки в группу

        # Настройка кнопок выбора цвета.
        self.primaryButton.pressed.connect(lambda: self.choose_color(self.set_primary_color))
        self.secondaryButton.pressed.connect(lambda: self.choose_color(self.set_secondary_color))

        # Инициализация цветов кнопок.
        for n, hex in enumerate(COLORS, 1):
            btn = getattr(self, 'colorButton_%d' % n)  # Получение кнопки по индексу
            btn.setStyleSheet('QPushButton { background-color: %s; }' % hex)  # Установка стиля кнопки с цветом
            btn.hex = hex  # Для использования в событии ниже

            def patch_mousePressEvent(self_, e):
                # Переопределение метода mousePressEvent для обработки события нажатия мыши на кнопке цвета.
                if e.button() == Qt.LeftButton:
                    self.set_primary_color(self_.hex)  # Установка первичного цвета по нажатию левой кнопкой мыши.

                elif e.button() == Qt.RightButton:
                    self.set_secondary_color(self_.hex)  # Установка вторичного цвета по нажатию правой кнопкой мыши.

            btn.mousePressEvent = types.MethodType(patch_mousePressEvent, btn)  # Привязка переопределенной функции
            # к событию mousePressEvent кнопки.

        # Настройка сигналов действий
        self.actionCopy.triggered.connect(
            self.copy_to_clipboard)  # Привязка сигнала действия "Копировать" к функции copy_to_clipboard.

        # Инициализация таймера анимации.
        self.timer = QTimer()  # Создание таймера
        self.timer.timeout.connect(self.canvas.on_timer)  # Подключение сигнала таймера к методу on_timer холста.
        self.timer.setInterval(100)  # Установка интервала таймера в 100 миллисекунд.
        self.timer.start()  # Запуск таймера.

        # Настройка для согласования с холстом.
        self.set_primary_color('#000000')  # Установка первичного цвета по умолчанию черным.
        self.set_secondary_color('#ffffff')  # Установка вторичного цвета по умолчанию белым.

        # Сигналы для изменения цвета, инициированные холстом (пипеткой).
        self.canvas.primary_color_updated.connect(
            self.set_primary_color)  # Привязка сигнала изменения первичного цвета к функции set_primary_color.
        self.canvas.secondary_color_updated.connect(
            self.set_secondary_color)  # Привязка сигнала изменения вторичного цвета к функции set_secondary_color.

        # Настройка состояния штампа.
        self.current_stamp_n = -1  # Начальное значение индекса штампа.
        self.next_stamp()  # Выбор следующего штампа.
        self.stampnextButton.pressed.connect(
            self.next_stamp)  # Привязка события нажатия кнопки "Следующий" к функции next_stamp.

        # Опции меню
        self.actionNewImage.triggered.connect(
            self.canvas.initialize)  # Привязка события "Новое изображение" к функции initialize холста.
        self.actionOpenImage.triggered.connect(
            self.open_file)  # Привязка события "Открыть изображение" к функции open_file.
        self.actionSaveImage.triggered.connect(
            self.save_file)  # Привязка события "Сохранить изображение" к функции save_file.
        self.actionClearImage.triggered.connect(
            self.canvas.reset)  # Привязка события "Очистить изображение" к функции reset холста.
        self.actionInvertColors.triggered.connect(
            self.invert)  # Привязка события "Инвертировать цвета" к функции invert.
        self.actionFlipHorizontal.triggered.connect(
            self.flip_horizontal)  # Привязка события "Отразить по горизонтали" к функции flip_horizontal.
        self.actionFlipVertical.triggered.connect(
            self.flip_vertical)  # Привязка события "Отразить по вертикали" к функции flip_vertical.

        # Настройка панели инструментов для рисования.
        self.fontselect = QFontComboBox()  # Выбор шрифта
        self.fontToolbar.addWidget(self.fontselect)  # Добавление выбора шрифта в панель инструментов
        self.fontselect.currentFontChanged.connect(lambda f: self.canvas.set_config('font',
                                                                                    f))  # Привязка события смены шрифта к функции set_config холста для шрифта.
        self.fontselect.setCurrentFont(QFont('Times'))  # Установка шрифта по умолчанию

        self.fontsize = QComboBox()  # Выбор размера шрифта
        self.fontsize.addItems([str(s) for s in FONT_SIZES])  # Добавление вариантов размеров шрифта в выпадающий список
        self.fontsize.currentTextChanged.connect(lambda f: self.canvas.set_config('fontsize',
                                                                                  int(f)))  # Привязка события смены размера шрифта к функции set_config холста.

        # Подключитесь к сигналу, генерирующему текст текущего выделения. Преобразуйте строку в float
        # и установить в качестве pointsize. Мы могли бы также использовать index + retrieve из FONT_SIZES.
        self.fontToolbar.addWidget(self.fontsize)

        self.fontToolbar.addAction(self.actionBold)  # Кнопка для жирного шрифта
        self.actionBold.triggered.connect(lambda s: self.canvas.set_config('bold',
                                                                           s))  # Привязка события изменения состояния кнопки "Жирный" к функции set_config холста.
        self.fontToolbar.addAction(self.actionItalic)  # Кнопка для курсива
        self.actionItalic.triggered.connect(lambda s: self.canvas.set_config('italic',
                                                                             s))  # Привязка события изменения состояния кнопки "Курсив" к функции set_config холста.
        self.fontToolbar.addAction(self.actionUnderline)  # Кнопка для подчеркивания
        self.actionUnderline.triggered.connect(lambda s: self.canvas.set_config('underline',
                                                                                s))  # Привязка события изменения состояния кнопки "Подчеркнутый" к функции set_config холста.

        sizeicon = QLabel()  # Иконка для размера шрифта
        sizeicon.setPixmap(QPixmap(':/icons/border-weight.png'))  # Установка изображения для иконки размера шрифта
        self.drawingToolbar.addWidget(sizeicon)  # Добавление иконки в панель инструментов
        self.sizeselect = QSlider()  # Ползунок для выбора размера
        self.sizeselect.setRange(1, 20)  # Установка диапазона значений для ползунка
        self.sizeselect.setOrientation(Qt.Horizontal)  # Установка горизонтальной ориентации ползунка
        self.sizeselect.valueChanged.connect(lambda s: self.canvas.set_config('size',
                                                                              s))  # Привязка события изменения значения ползунка к функции set_config холста.
        self.drawingToolbar.addWidget(self.sizeselect)  # Добавление ползунка в панель инструментов

        self.actionFillShapes.triggered.connect(lambda s: self.canvas.set_config('fill',
                                                                                 s))  # Привязка события изменения состояния кнопки "Заливка фигур" к функции set_config холста.
        self.drawingToolbar.addAction(self.actionFillShapes)  # Добавление кнопки "Заливка фигур" в панель инструментов
        self.actionFillShapes.setChecked(True)  # Установка состояния "включено" по умолчанию для кнопки "Заливка фигур"

        self.show()  # Отображение окна приложения

    def choose_color(self, callback):
        # Функция для выбора цвета с помощью диалогового окна QColorDialog
        dlg = QColorDialog()  # Создание диалогового окна для выбора цвета
        if dlg.exec():  # Если пользователь выбрал цвет и нажал "ОК" в диалоговом окне
            callback(dlg.selectedColor().name())  # Вызов колбэка с шестнадцатеричным значением выбранного цвета

    def set_primary_color(self, hex):
        # Установка основного цвета и стиля кнопки для отображения цвета
        self.canvas.set_primary_color(hex)  # Установка основного цвета холста
        self.primaryButton.setStyleSheet('QPushButton { background-color: %s; }' % hex)  # Установка цвета кнопки

    def set_secondary_color(self, hex):
        # Установка вторичного цвета и стиля кнопки для отображения цвета
        try:
            self.canvas.set_secondary_color(hex)  # Установка вторичного цвета холста
            self.secondaryButton.setStyleSheet('QPushButton { background-color: %s; }' % hex)  # Установка цвета кнопки
        except Exception as e:
            print(f"An error occurred: {e}")

    def next_stamp(self):
        # Переключение на следующий штамп (изображение)
        try:
            self.current_stamp_n += 1  # Увеличение индекса текущего штампа
            if self.current_stamp_n >= len(STAMPS):  # Если индекс выходит за пределы списка штампов
                self.current_stamp_n = 0  # Возвращаемся к началу списка

            pixmap = QPixmap(STAMPS[self.current_stamp_n])  # Загрузка изображения штампа
            self.stampnextButton.setIcon(QIcon(pixmap))  # Установка изображения на кнопку для следующего штампа

            self.canvas.current_stamp = pixmap  # Установка текущего штампа на холсте
        except Exception as e:
            print(f"An error occurred: {e}")

    def copy_to_clipboard(self):
        """
        Копирование изображения на холсте в буфер обмена.
        """
        try:
            clipboard = QApplication.clipboard()  # Получение объекта буфера обмена приложения

            # Проверка режима и блокировки области, затем копирование выбранной области в буфер обмена.
            if self.canvas.mode == 'selectrect' and self.canvas.locked:
                clipboard.setPixmap(self.canvas.selectrect_copy())

            # Проверка режима и блокировки области, затем копирование выбранной области в буфер обмена.
            elif self.canvas.mode == 'selectpoly' and self.canvas.locked:
                clipboard.setPixmap(self.canvas.selectpoly_copy())

            else:
                clipboard.setPixmap(self.canvas.pixmap())  # Копирование всего изображения на холсте в буфер обмена

        except Exception as e:
            print(
                f"An error occurred: {e}")  # Обработка и вывод сообщения об ошибке, если возникла исключительная ситуация

    def open_file(self):
        """
        Открытие изображения для редактирования, масштабирование меньшей из сторон и обрезка остатка.
        :return:
        """
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                              "PNG image files (*.png); JPEG image files (*jpg); All files (*.*)")

        if path:
            pixmap = QPixmap()
            pixmap.load(path)

            # Необходимо обрезать изображение до размеров нашего холста. Получаем размер загруженного изображения.
            iw = pixmap.width()
            ih = pixmap.height()

            # Получаем размер области, которую мы заполняем.
            cw, ch = CANVAS_DIMENSIONS

            if iw / cw < ih / ch:  # Высота относительно больше, чем ширина.
                pixmap = pixmap.scaledToWidth(cw)
                hoff = (pixmap.height() - ch) // 2
                pixmap = pixmap.copy(
                    QRect(QPoint(0, hoff), QPoint(cw, pixmap.height() - hoff))
                )

            elif iw / cw > ih / ch:  # Ширина относительно больше, чем высота.
                pixmap = pixmap.scaledToHeight(ch)
                woff = (pixmap.width() - cw) // 2
                pixmap = pixmap.copy(
                    QRect(QPoint(woff, 0), QPoint(pixmap.width() - woff, ch))
                )

            self.canvas.setPixmap(pixmap)

    def save_file(self):
        """
        Сохранение активного холста в файл изображения.
        :return:
        """
        try:
            path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "PNG Image file (*.png)")

            if path:
                pixmap = self.canvas.pixmap()
                pixmap.save(path, "PNG")
        except Exception as e:
            print(f"An error occurred: {e}")

    def invert(self):
        # Инвертирование цветов на холсте
        try:
            img = QImage(self.canvas.pixmap())  # Создание изображения на основе текущего изображения на холсте
            img.invertPixels()  # Инвертирование цветов пикселей изображения
            pixmap = QPixmap()
            pixmap.convertFromImage(img)  # Преобразование изображения обратно в формат QPixmap
            self.canvas.setPixmap(pixmap)  # Установка инвертированного изображения на холсте
        except Exception as e:
            print(f"An error occurred: {e}")

    def flip_horizontal(self):
        # Отражение изображения по горизонтали
        try:
            pixmap = self.canvas.pixmap()  # Получение текущего изображения на холсте
            self.canvas.setPixmap(
                pixmap.transformed(QTransform().scale(-1, 1)))  # Отражение по горизонтали и установка на холсте
        except Exception as e:
            print(f"An error occurred: {e}")

    def flip_vertical(self):
        # Отражение изображения по вертикали
        try:
            pixmap = self.canvas.pixmap()  # Получение текущего изображения на холсте
            self.canvas.setPixmap(
                pixmap.transformed(QTransform().scale(1, -1)))  # Отражение по вертикали и установка на холсте
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == '__main__':
    # Основная часть программы, инициализация приложения и его запуск
    app = QApplication(sys.argv)  # Создание объекта приложения
    app.setWindowIcon(QtGui.QIcon(':/icons/piecasso.ico'))  # Установка иконки окна приложения
    window = MainWindow()  # Создание экземпляра основного окна
    app.exec_()  # Запуск основного цикла обработки событий приложения
