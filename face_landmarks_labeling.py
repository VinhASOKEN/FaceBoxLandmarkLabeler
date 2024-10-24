import os
import cv2
import glob
import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QProgressBar, QAction
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from copy import deepcopy

class ImageDisplay(FigureCanvas):
    def __init__(self, list_file, parent=None, width=5, height=4, dpi=100):
        self.start=0
        self.files = list_file
        self.IMAGE = cv2.cvtColor(cv2.imread(self.files[self.start]), cv2.COLOR_BGR2RGB)
        self.IMAGE_CLONE = self.IMAGE.copy()
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        self.axes.clear()
        self.axes.axis('off')
        plt.draw()
        super(ImageDisplay, self).__init__(self.fig)

    def nextImage(self):
        self.start += 1
        self.IMAGE = cv2.cvtColor(cv2.imread(self.files[self.start]), cv2.COLOR_BGR2RGB)
        self.IMAGE_CLONE = self.IMAGE.copy()
        self.ShowImage()

    def prevImage(self):
        self.start -= 1
        self.IMAGE = cv2.cvtColor(cv2.imread(self.files[self.start]), cv2.COLOR_BGR2RGB)
        self.IMAGE_CLONE = self.IMAGE.copy()
        self.ShowImage()

    def setImage(self, idx):
        self.start = idx
        self.IMAGE = cv2.cvtColor(cv2.imread(self.files[self.start]), cv2.COLOR_BGR2RGB)
        self.IMAGE_CLONE = self.IMAGE.copy()
        self.ShowImage()

    def draw_rectangle(self, rect):
        if rect[0] is not None and rect[1] is not None:
            clone = self.IMAGE_CLONE.copy()
            x1, y1 = int(rect[0][0]), int(rect[0][1])
            x2, y2 = int(rect[1][0]), int(rect[1][1])
            cv2.rectangle(clone, (x1, y1), (x2, y2), (0, 255, 0), 2)
            self.IMAGE = clone
            self.ShowImage()

    def draw_points(self, points):
        for point in points:
            x, y = int(point[0]), int(point[1])
            cv2.circle(self.IMAGE, (x, y), 1, (255, 0, 0), 3) 

        self.ShowImage()

    def ShowImage(self):
        self.axes.clear()
        self.axes.axis('off')
        self.axes.imshow(self.IMAGE)
        self.draw()



class App(QWidget):
    
    def __init__(self, image_folder):
        super().__init__()
        self.title = 'Face BOX WITH LANDMARKS LABELER'
        self.left = 50
        self.top = 50
        self.width = 800
        self.height = 640
        
        self.list_file = glob.glob(os.path.join(image_folder, '*.jpg'))
        self.list_file += glob.glob(os.path.join(image_folder, '*.png'))
        self.total_file = len(self.list_file)
        self.current_index = 0
        self.current_file = self.list_file[self.current_index]
        self.layout = QGridLayout()
        self.rect_coords = [None, None]
        self.list_points = []
        self.commit_rect_coords = None
        self.rect_clicked = False
        self.initUI()
    
    
    def press_clear(self):
        self.refresh()
        self.canvas.setImage(self.current_index)
        
    
    def press_clear_box(self):
        label_file = self.current_file.split('.')[0] + '.txt'
        with open(label_file, 'r') as file:
            lines = file.readlines()

        lines.pop(0)
        lines.insert(0, 'None\n')
        with open(label_file, 'w') as file:
            file.writelines(lines)

        self.commit_rect_coords = None
        self.rect_coords = [None, None]
        self.rect_clicked = False
        self.canvas.setImage(self.current_index)
        
    
    def press_clear_points(self):
        label_file = self.current_file.split('.')[0] + '.txt'
        with open(label_file, 'r') as file:
            lines = file.readlines()

        lines = lines[0]
        with open(label_file, 'w') as file:
            file.writelines(lines)

        self.list_points = []
        self.canvas.setImage(self.current_index)

    
    def press_next(self):
        if self.current_index < self.total_file - 1:
            # Update
            self.do_save()
            self.current_index += 1
            self.current_file = self.list_file[self.current_index]
            self.progress.setValue(self.current_index+1)
            # self.update()
            self.canvas.setImage(self.current_index)
            self.refresh()
            self.read_label_if_exists()


    def press_previous(self):
        if self.current_index > 0:
            self.do_save()
            self.current_index -= 1
            self.current_file = self.list_file[self.current_index]
            # Update
            self.progress.setValue(self.current_index+1)
            # self.update()
            self.canvas.setImage(self.current_index)
            self.refresh()
            self.read_label_if_exists()


    def do_save(self):
        if self.commit_rect_coords is not None:
            label_text = "{},{},{},{}\n".format(self.commit_rect_coords[0][0], self.commit_rect_coords[0][1], self.commit_rect_coords[1][0], self.commit_rect_coords[1][1])
            for point in self.list_points:
                print(point)
                label_text += "{},{}\n".format(point[0], point[1])
            label_file = self.current_file.split('.')[0] + '.txt'
            with open(label_file, 'w+', encoding="utf-8") as f:
                f.write(label_text)
        else:
            label_text = "None\n"
            for point in self.list_points:
                label_text += "{},{}\n".format(point[0], point[1])
            label_file = self.current_file.split('.')[0] + '.txt'
            with open(label_file, 'w+', encoding="utf-8") as f:
                f.write(label_text)

    def read_label_if_exists(self):
        label_file = self.current_file.split('.')[0] + '.txt'
        if os.path.exists(label_file):
            if os.path.getsize(label_file) > 0:
                lines = open(label_file).read().strip('\n').split('\n')
                print(lines[0])
                if lines[0] != "None":
                    rect = [float(x) for x in lines[0].split(',')]
                    self.rect_coords = [[rect[0], rect[1]], [rect[2], rect[3]]]
                    self.commit_rect_coords = deepcopy(self.rect_coords)
                self.list_points = []
                for line in lines[1:]:
                    point = [float(x) for x in line.split(',')]
                    self.list_points.append(point)
                print('Read label completed:')
                print('  - rect', self.rect_coords)
                print('  - points', self.list_points)
                self.canvas.draw_rectangle(self.rect_coords)
                self.canvas.draw_points(self.list_points)


    def get_size(self, width, height):
        max_width = 700
        if width > max_width:
            return (max_width, int(height/width*max_width))
        else:
            return (width, height)


    def refresh(self):
        self.commit_rect_coords = None
        self.rect_coords = [None, None]
        self.rect_clicked = False
        self.list_points = []


    def on_press_rect(self, event):
        if not self.rect_clicked:
            return
        self.rect_coords[0] = (int(event.xdata), int(event.ydata))


    def on_release_rect(self, event):
        if self.rect_clicked:
            if self.rect_coords[0] is not None and self.rect_coords[1] is not None:
                if self.rect_coords[0] != self.rect_coords[1]:
                    self.commit_rect_coords = deepcopy(self.rect_coords)
            self.rect_coords = [None, None]
            self.rect_clicked = False


    def on_move_rect(self, event):
        if event.xdata is not None and event.ydata is not None and self.rect_clicked:
            self.rect_coords[1] = (int(event.xdata), int(event.ydata))
            self.canvas.draw_rectangle(self.rect_coords)

    def draw_only_rect(self):
        self.rect_clicked = True
        self.canvas.mpl_disconnect(self.on_press_point)
        self.canvas.mpl_connect("button_press_event", self.on_press_rect)
        self.canvas.mpl_connect("button_release_event", self.on_release_rect)
        self.canvas.mpl_connect("motion_notify_event", self.on_move_rect)


    def on_press_point(self, event):
        if self.rect_clicked:
            return
        self.list_points.append((int(event.xdata), int(event.ydata)))
        self.canvas.draw_points(self.list_points)
            
            
    def draw_only_point(self):
        self.rect_clicked = False
        self.canvas.mpl_disconnect(self.on_press_rect)
        self.canvas.mpl_disconnect(self.on_release_rect)
        self.canvas.mpl_disconnect(self.on_move_rect)
        self.canvas.mpl_connect("button_press_event", self.on_press_point)
            

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.progress = QProgressBar()
        self.progress.setMaximum(self.total_file)
        self.canvas = ImageDisplay(self.list_file, dpi=100)
        self.canvas.ShowImage()
        self.read_label_if_exists()

        # Text box
        self.clear_button = QPushButton('CLEAR')
        self.clear_button.clicked.connect(self.press_clear)
        
        self.clear_button_box = QPushButton('CLEAR Rect')
        self.clear_button_box.clicked.connect(self.press_clear_box)
        
        self.clear_button_points = QPushButton('CLEAR Points')
        self.clear_button_points.clicked.connect(self.press_clear_points)
        
        # Button
        self.next_button = QPushButton('Next')
        self.next_button.clicked.connect(self.press_next)
        self.previous_button = QPushButton('Previous')
        self.previous_button.clicked.connect(self.press_previous)
        self.draw_rect_button = QPushButton('Draw Rect')
        self.draw_rect_button.clicked.connect(self.draw_only_rect)
        self.draw_point_button = QPushButton('Draw Points')
        self.draw_point_button.clicked.connect(self.draw_only_point)

        # Add all widgets
        self.layout.addWidget(self.canvas, 0, 0, 1, -1)
        self.layout.addWidget(self.clear_button, 1, 0, 1, 1)
        self.layout.addWidget(self.draw_rect_button, 1, 1, 1, 1)
        self.layout.addWidget(self.draw_point_button, 1, 2, 1, 1)
        self.layout.addWidget(self.clear_button_box, 1, 3, 1, 1)
        self.layout.addWidget(self.clear_button_points, 1, 4, 1, 1)
        self.layout.addWidget(self.next_button, 1, 5, 1, 1)
        self.layout.addWidget(self.progress, 2, 0, 1, 5)
        self.layout.addWidget(self.previous_button, 2, 5, 1, 1)
        
        # Add Keypress Event
        self.setEnterAction=QAction("Set Enter", self, shortcut=Qt.Key_Return, triggered=self.press_next)
        self.addAction(self.setEnterAction)
        self.layout.addWidget(QPushButton("Enter", self, clicked=self.setEnterAction.triggered))

        self.setLayout(self.layout)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App(r"C:\Users\vietl\OneDrive\Desktop\Gannhan\data_faces")
    sys.exit(app.exec_())