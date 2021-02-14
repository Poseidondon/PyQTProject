import sys
from os import listdir, remove
from os.path import isfile, join
import sqlite3
import datetime
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QSlider, QColorDialog
from PyQt5.QtWidgets import QFileDialog, QLabel, QMessageBox, QGraphicsOpacityEffect, QWidget
from PyQt5.QtWidgets import QInputDialog, QPushButton, QTableWidgetItem, QTableWidget, QListWidget
from PyQt5.QtGui import QPixmap, QIcon, QCursor, QTransform, QPainter, QPen, QImage
from PyQt5.QtCore import Qt, QSize


class Project(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def file_menuInit(self):
        self.open_action = QAction('Открыть', self)
        self.open_action.setShortcut('Ctrl+O')
        self.open_action.setStatusTip('Открыть изображение')
        self.open_action.triggered.connect(self.open)

        self.save_action = QAction('Сохранить', self)
        self.save_action.setShortcut('Ctrl+S')
        self.save_action.setStatusTip('Сохранить изображение')
        self.save_action.triggered.connect(self.save)

        self.save_as_action = QAction('Сохранить как', self)
        self.save_as_action.setStatusTip('Сохранить изображение как')
        self.save_as_action.triggered.connect(self.save_as)

        self.delete_action = QAction('Удалить', self)
        self.delete_action.setShortcut('Del')
        self.delete_action.setStatusTip('Удалить изображение')
        self.delete_action.triggered.connect(self.delete)

        self.edit_action = QAction('Редактирование', self)
        self.edit_action.setShortcut('Ctrl+E')
        self.edit_action.setStatusTip('Разрешить редактирование')
        self.edit_action.triggered.connect(self.edit)

        self.editCopy_action = QAction('Редактирование копии', self)
        self.editCopy_action.setStatusTip('Создать копию изображения и редактировать её')
        self.editCopy_action.triggered.connect(self.editCopy)

        self.exit_action = QAction('Выход', self)
        self.exit_action.setStatusTip('Закрыть приложение')
        self.exit_action.triggered.connect(qApp.quit)

        self.file_menu = self.menubar.addMenu('Файл')
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addAction(self.delete_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.edit_action)
        self.file_menu.addAction(self.editCopy_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        self.delete_action.setEnabled(False)
        self.edit_action.setEnabled(False)
        self.editCopy_action.setEnabled(False)
        self.save_action.setEnabled(False)
        self.save_as_action.setEnabled(False)

    def edit_menuInit(self):
        self.undo_action = QAction('Отмена', self)
        self.undo_action.setShortcut('Ctrl+Z')
        self.undo_action.setStatusTip('Отменить действие')
        self.undo_action.triggered.connect(self.undo)

        self.history_action = QAction('История действий', self)
        self.history_action.setStatusTip('Открыть истрию действий с данным файлом')
        self.history_action.triggered.connect(self.history)

        self.edit_menu = self.menubar.addMenu('Редактирование')
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.history_action)

        self.edit_menu.setEnabled(False)

    def arrowsInit(self):
        self.op_right = QGraphicsOpacityEffect(self)
        self.op_right.setOpacity(0)
        self.op_left = QGraphicsOpacityEffect(self)
        self.op_left.setOpacity(0)

        self.arrow_right = QLabel(self)
        self.arrow_right.setPixmap(QPixmap('arrow_right.png'))
        self.arrow_right.setGraphicsEffect(self.op_right)
        self.arrow_right.setStyleSheet("background-color:#ECF0F1;")

        self.arrow_left = QLabel(self)
        self.arrow_left.setPixmap(QPixmap('arrow_left.png'))
        self.arrow_left.setGraphicsEffect(self.op_left)
        self.arrow_left.setStyleSheet("background-color:#ECF0F1;")

    def sliderInit(self):
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setGeometry(self.width() - 150, 32, 140, 16)
        self.slider.setMinimum(100)
        self.slider.setMaximum(800)
        self.slider.setValue(100)
        self.slider.valueChanged.connect(self.scaleChange)
        self.slider_text = QLabel('Размер: 100%', self)
        self.slider_text.setGeometry(self.width() - 230, 30, 75, 20)

    def toolbarInit(self):
        self.rotateLeft_action = QAction(QIcon('rotate_left.png'), 'Повернуть на 90 против часовой', self)
        self.rotateLeft_action.triggered.connect(self.rotate)

        self.rotateRight_action = QAction(QIcon('rotate_right.png'), 'Повернуть на 90 по часовой', self)
        self.rotateRight_action.triggered.connect(self.rotate)

        self.moveCursor_action = QAction(QIcon('move_icon.png'), 'Выбрать инструмент: курсор', self)
        self.moveCursor_action.triggered.connect(self.choose_cursor)
        self.moveCursor_action.setCheckable(True)
        self.moveCursor_action.setChecked(True)

        self.brush_action = QAction(QIcon('brush_icon.png'), 'Выбрать инструмент: кисть', self)
        self.brush_action.triggered.connect(self.choose_brush)
        self.brush_action.setCheckable(True)

        pixmap = QPixmap(QSize(32, 32))
        pixmap.fill(self.color)
        self.selectColor_action = QAction(QIcon(pixmap), 'Выбрать цвет', self)
        self.selectColor_action.triggered.connect(self.select_color)

        self.selectThickness_action = QAction(QIcon('thickness_icon.png'), 'Выбрать толщину', self)
        self.selectThickness_action.triggered.connect(self.select_thickness)

        self.toolbar = self.addToolBar('Edit')
        self.toolbar.setMovable(False)
        self.toolbar.addAction(self.rotateLeft_action)
        self.toolbar.addAction(self.rotateRight_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.moveCursor_action)
        self.toolbar.addAction(self.brush_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.selectColor_action)
        self.toolbar.addAction(self.selectThickness_action)

        self.toolbar.setEnabled(False)

    def initUI(self):
        self.fname = ''
        self.cur_dir = ''
        self.color = Qt.red
        self.thickness = 3

        self.setWindowTitle('Просмотр фотографий')
        self.setGeometry(0, 0, 800, 600)
        self.setMinimumWidth(500)
        self.setMinimumHeight(200)

        self.image = QLabel(self)
        self.arrowsInit()
        self.showMaximized()
        self.setMouseTracking(True)

        self.statusBar()
        self.menubar = self.menuBar()
        self.file_menuInit()
        self.edit_menuInit()
        self.toolbarInit()
        self.sliderInit()

    def mouseMoveEvent(self, event):
        if self.fname:
            if event.x() > self.width() // 2:
                self.op_right.setOpacity(0.8 - (self.width() - event.x()) / (self.width() / 2))
                self.op_left.setOpacity(0)
            else:
                self.op_left.setOpacity((self.width() / 2 - event.x()) / (self.width() / 2) - 0.2)
                self.op_right.setOpacity(0)

            if self.dragging:
                if not self.brush_action.isChecked():
                    x_shift = event.x() - self.prev_x
                    y_shift = event.y() - self.prev_y
                    self.prev_x, self.prev_y = event.x(), event.y()
                    if self.image.width() > self.width():
                        if x_shift < 0 and self.image.x() + self.image.width() + x_shift > self.width():
                            self.image.move(self.image.x() + x_shift, self.image.y())
                            self.total_x_shift += x_shift
                        elif x_shift > 0 and self.image.x() + x_shift < 0:
                            self.image.move(self.image.x() + x_shift, self.image.y())
                            self.total_x_shift += x_shift
                    if self.image.height() > self.height():
                        if y_shift < 0 and self.image.y() + self.image.height() + y_shift > self.height() + 25:
                            self.image.move(self.image.x(), self.image.y() + y_shift)
                            self.total_y_shift += y_shift
                        elif y_shift > 0 and self.image.y() + y_shift < 29:
                            self.image.move(self.image.x(), self.image.y() + y_shift)
                            self.total_y_shift += y_shift
                else:
                    painter = QPainter(self.new_pixmap)
                    painter.setPen(QPen(self.color, self.thickness, Qt.SolidLine))
                    mult = self.slider.value() * 0.01
                    shift_x = (self.width() - self.new_pixmap.width() * mult) // 2 + self.total_x_shift
                    shift_y = (self.height() - self.new_pixmap.height() * mult) // 2 + 29 + self.total_y_shift
                    x0, y0 = int((self.prev_x - shift_x) // mult), int((self.prev_y - shift_y) // mult)
                    x1, y1 = int((event.x() - shift_x) // mult), int((event.y() - shift_y) // mult)
                    painter.drawLine(x0, y0, x1, y1)

                    if not self.save_pixels:
                        if x0 > x1:
                            self.min_x, self.max_x = x1 - self.thickness // 2 - 1, x0 + self.thickness // 2
                        else:
                            self.min_x, self.max_x = x0 - self.thickness // 2 - 1, x1 + self.thickness // 2
                        if y0 > y1:
                            self.min_y, self.max_y = y1 - self.thickness // 2 - 1, y0 + self.thickness // 2
                        else:
                            self.min_y, self.max_y = y0 - self.thickness // 2 - 1, y1 + self.thickness // 2
                        self.save_pixels = True
                    else:
                        self.min_y = min(y0 - self.thickness // 2 - 1, y1 - self.thickness // 2, self.min_y)
                        self.min_x = min(x0 - self.thickness // 2 - 1, x1 - self.thickness // 2, self.min_x)
                        self.max_y = max(y0 + self.thickness // 2, y1 + self.thickness // 2, self.max_y)
                        self.max_x = max(x0 + self.thickness // 2, x1 + self.thickness // 2, self.max_x)

                    self.prev_x, self.prev_y = event.x(), event.y()
                    self.image.setPixmap(self.new_pixmap.scaledToWidth(self.new_pixmap.width() * mult))
                    self.pixmap = self.new_pixmap.scaledToWidth(self.pixmap.width())

    def mousePressEvent(self, event):
        if self.fname:
            if event.x() >= self.width() - 51 and event.y() > 54:
                self.open_next()
            elif event.x() <= 51 and event.y() > 54:
                self.open_prev()
            elif event.y() > 54:
                self.dragging = True
                self.prev_x = event.x()
                self.prev_y = event.y()
                if not self.brush_action.isChecked():
                    self.setCursor(QCursor(QPixmap('move_icon.png').scaledToWidth(26)))
                else:
                    self.save_pixels = False
                    self.save_image = QImage(self.new_pixmap)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        if not self.brush_action.isChecked():
            self.unsetCursor()
        else:
            pixels = []
            for i in range(self.min_x, self.max_x + 1):
                for j in range(self.min_y, self.max_y + 1):
                    pixels.append((i, j, self.save_image.pixel(i, j)))
            currentDT = str(datetime.datetime.now())
            con = sqlite3.connect('data.db')
            cur = con.cursor()
            cur.execute("""INSERT into history
                                   VALUES(?, ?, ?)""",
                        (currentDT, self.cur_dir + '/' + self.fname, 'draw_' + str(pixels)))
            con.commit()
            con.close()

    def resizeEvent(self, event):
        if self.fname:
            self.resize_pixmap()
            self.scaleChange()

    def resize_pixmap(self):
        width = self.width()
        height = self.height() - 54
        self.new_pixmap = self.pixmap
        if self.pixmap.width() > width or self.pixmap.height() > height:
            self.new_pixmap = self.pixmap.scaled(width, height, Qt.KeepAspectRatio)
        self.image.setGeometry(width // 2 - self.new_pixmap.width() // 2,
                               height // 2 - self.new_pixmap.height() // 2 + 54,
                               self.new_pixmap.width(), self.new_pixmap.height())
        self.image.setPixmap(self.new_pixmap)

        self.arrow_left.setGeometry(0, 54, 51, height)
        self.arrow_right.setGeometry(width - 51, 54, 51, height)
        self.image.setMouseTracking(True)
        self.arrow_left.setMouseTracking(True)
        self.arrow_right.setMouseTracking(True)
        self.total_x_shift = 0
        self.total_y_shift = 0

        self.slider.move(self.width() - 150, 32)
        self.slider_text.move(self.width() - 230, 30)

    def open(self, dir=None):
        if not dir:
            dir = QFileDialog.getOpenFileName(self, 'Выбрать картинку', self.cur_dir, "Картинка(*.png *.bmp *.jpg)")[0]
        if dir:
            self.fname = dir.split('/')[-1]
            self.cur_dir = '/'.join(dir.split('/')[:-1])
            self.images_list = [f for f in listdir(self.cur_dir)
                                if isfile(join(self.cur_dir, f)) and f.split('.')[1].lower() in {'png', 'bmp', 'jpg'}]
            self.setWindowTitle(self.fname)

            self.delete_action.setEnabled(True)
            self.save_action.setEnabled(True)
            self.save_as_action.setEnabled(True)
            self.edit_action.setEnabled(True)
            self.editCopy_action.setEnabled(True)
            self.edit_menu.setEnabled(False)
            self.toolbar.setEnabled(False)
            self.moveCursor_action.setChecked(True)
            self.brush_action.setChecked(False)


            self.image.setEnabled(True)
            self.dragging = False
            self.pixmap = QPixmap(dir)
            self.resize_pixmap()

            self.slider.show()
            self.slider_text.show()
            self.slider.setValue(100)

    def open_next(self):
        if self.images_list[-1] == self.fname:
            self.open(self.cur_dir + '/' + self.images_list[0])
        else:
            self.open(self.cur_dir + '/' + self.images_list[self.images_list.index(self.fname) + 1])

    def open_prev(self):
        if self.images_list[0] == self.fname:
            self.open(self.cur_dir + '/' + self.images_list[-1])
        else:
            self.open(self.cur_dir + '/' + self.images_list[self.images_list.index(self.fname) - 1])

    def save(self):
        self.pixmap.save(self.cur_dir + '/' + self.fname, self.fname.split('.')[1].upper())

    def save_as(self):
        dir = QFileDialog.getSaveFileName(self, 'Сохранить как', self.cur_dir)[0]
        if dir:
            if '.' in dir:
                self.pixmap.save(dir, dir.split('.')[1].upper())
            else:
                self.pixmap.save(dir + '.' + self.fname.split('.')[1], self.fname.split('.')[1].upper())

    def delete(self):
        answer = QMessageBox.question(self, "Подтверждение", "Удалить '%s'?" % self.fname,
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer == QMessageBox.Yes:
            remove(self.cur_dir + '/' + self.fname)
            if len(self.images_list) == 1:
                self.image.setEnabled(False)
                self.slider.close()
                self.slider_text.close()
            else:
                self.open_next()

    def edit(self):
        answer = QMessageBox.question(self, "Подтверждение", "Разрешить редактирование %s?" % self.fname,
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer == QMessageBox.Yes:
            self.edit_menu.setEnabled(True)
            self.toolbar.setEnabled(True)

    def editCopy(self):
        count = 1
        while True:
            name = self.fname.split('.')[0] + '(%s)' % str(count) + '.' + self.fname.split('.')[1]
            if name in self.images_list:
                count += 1
            else:
                f = open(self.cur_dir + '/' + self.fname, 'rb')
                data = f.read()
                f.close()
                new_f = open(self.cur_dir + '/' + name, 'wb')
                new_f.write(data)
                new_f.close()

                self.fname = name
                self.images_list.append(name)
                self.setWindowTitle(self.fname)
                break
        self.edit()

    def scaleChange(self):
        self.slider_text.setText('Размер: ' + str(self.slider.value()) + '%')
        new_pixmap = self.pixmap.scaledToWidth(int(self.new_pixmap.width() * self.slider.value() * 0.01))
        self.image.setPixmap(new_pixmap)
        self.image.setGeometry(self.width() // 2 - new_pixmap.width() // 2,
                               self.height() // 2 - new_pixmap.height() // 2,
                               new_pixmap.width(), new_pixmap.height() + 54)
        self.total_x_shift = 0
        self.total_y_shift = 0

    def undo(self):
        history = HistoryForm(self.cur_dir + '/' + self.fname).history()
        if history:
            if history[0][1].split('_')[0] == 'rotate':
                self.pixmap = self.pixmap.transformed(QTransform().rotate(-int(history[0][1].split('_')[1])))
                self.image.setPixmap(self.pixmap)
                self.resize_pixmap()
                self.scaleChange()
                con = sqlite3.connect('data.db')
                cur = con.cursor()
                cur.execute("""DELETE FROM history WHERE time=?""", (history[0][0],))
                con.commit()
                con.close()
            elif history[0][1].split('_')[0] == 'draw':
                image = QImage(self.new_pixmap)
                pixels = eval(history[0][1].split('_')[1])
                for pix in pixels:
                    image.setPixel(pix[0], pix[1], pix[2])
                self.pixmap = QPixmap(image)
                self.resize_pixmap()
                self.scaleChange()
                con = sqlite3.connect('data.db')
                cur = con.cursor()
                cur.execute("""DELETE FROM history WHERE time=?""", (history[0][0],))
                con.commit()
                con.close()

    def history(self):
        self.open_history = HistoryForm(self.cur_dir + '/' + self.fname)
        self.open_history.show()

    def rotate(self, angle=None):
        if not angle:
            if self.sender() == self.rotateLeft_action:
                angle = -90
            else:
                angle = 90
        self.pixmap = self.pixmap.transformed(QTransform().rotate(angle))
        self.image.setPixmap(self.pixmap)
        self.resize_pixmap()
        currentDT = str(datetime.datetime.now())
        con = sqlite3.connect('data.db')
        cur = con.cursor()
        cur.execute("""INSERT into history
                       VALUES(?, ?, ?)""",
                    (currentDT, self.cur_dir + '/' + self.fname, 'rotate_' + str(angle)))
        con.commit()
        con.close()

    def choose_cursor(self):
        if not self.moveCursor_action.isChecked():
            self.moveCursor_action.setChecked(True)
        else:
            self.brush_action.setChecked(False)

    def choose_brush(self):
        if not self.brush_action.isChecked():
            self.brush_action.setChecked(True)
        else:
            self.moveCursor_action.setChecked(False)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = color
            pixmap = QPixmap(QSize(32, 32))
            pixmap.fill(self.color)
            self.selectColor_action.setIcon(QIcon(pixmap))

    def select_thickness(self):
        i, okBtnPressed = QInputDialog.getInt(self, "Введите толщину", "Введите толщину",
                                              self.thickness, 1, 999, 1)
        if okBtnPressed:
            self.thickness = i


class HistoryForm(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI(args[-1])

    def initUI(self, file):
        self.setGeometry(100, 100, 400, 600)
        self.setWindowTitle('История действий')
        self.file = file

        self.table = QTableWidget(self)
        self.table.setGeometry(5, 5, 390, 560)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnCount(2)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(['Время', 'Операция'])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 235)
        con = sqlite3.connect('data.db')
        cur = con.cursor()
        self.data = cur.execute("""SELECT * FROM history
                              WHERE image=?""", (file,)).fetchall()[::-1]
        con.close()
        self.data = [(i[0], i[2]) for i in self.data]
        table_data = []
        for i in self.data:
            if i[1].split('_')[0] == 'rotate':
                if i[1].split('_')[1] == '90':
                    operation = 'Поворот на 90 по часовой'
                else:
                    operation = 'Поворот на 90 против часовой'
            elif i[1].split('_')[0] == 'draw':
                operation = 'Рисование'
            table_data.append((i[0][:-7], operation))
        if table_data:
            for i, row in enumerate(table_data):
                self.table.setRowCount(self.table.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(elem))
        else:
            self.table.setRowCount(1)
            self.table.setItem(0, 1, QTableWidgetItem('История пуста'))

        self.clear_btn = QPushButton('Очистить историю этого файла', self)
        self.clear_btn.setGeometry(5, 570, 190, 25)
        self.clear_btn.clicked.connect(self.clear)
        self.clearAll_btn = QPushButton('Очистить всю историю', self)
        self.clearAll_btn.setGeometry(200, 570, 190, 25)
        self.clearAll_btn.clicked.connect(self.clear)

    def clear(self):
        answer = QMessageBox.question(self, "Подтверждение", "Очистить историю?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer == QMessageBox.Yes:
            con = sqlite3.connect('data.db')
            cur = con.cursor()
            if self.sender() == self.clear_btn:
                cur.execute("""DELETE FROM history WHERE image=?""", (self.file,))
            else:
                cur.execute("""DELETE FROM history""")
            con.commit()
            con.close()
            self.table.setRowCount(0)
            self.table.setRowCount(1)
            self.table.setItem(0, 1, QTableWidgetItem('История пуста'))

    def history(self):
        return self.data


if __name__ == '__main__':
    if 'data.db' not in listdir():
        con = sqlite3.connect('data.db')
        cur = con.cursor()
        cur.execute("""CREATE TABLE history (
                       time DATETIME PRIMARY KEY UNIQUE,
                       image STRING,
                       operation STRING
                       );""")
        con.commit()
        con.close()

    app = QApplication(sys.argv)
    ex = Project()
    sys.exit(app.exec_())
