import sys
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QImage
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QSlider,
                             QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QColorDialog)

class PaintCanvas(QWidget):
    """Холст для рисования, поддерживающий Кисть, Линию, Прямоугольник, Круг и Заливку."""
    def __init__(self):
        super().__init__()
        self.init_canvas()

    def init_canvas(self):
        self.tool_mode = "Кисть"
        self.pen_width = 12
        
        self.pen_color = QColor(50, 50, 50)       
        self.brush_color = QColor(100, 150, 250)   
        
        self.last_pos = QPoint()
        self.start_pos = QPoint()
        self.end_pos = QPoint()
        self.is_drawing = False

        self.pixmap = QPixmap(1200, 800)
        self.pixmap.fill(Qt.GlobalColor.white)
        self.setMinimumSize(700, 500)

    def clear_canvas(self):
        self.pixmap.fill(Qt.GlobalColor.white)
        self.update() 

    def set_tool_mode(self, mode):
        self.tool_mode = mode

    def set_pen_width(self, width):
        self.pen_width = width

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)

        if self.is_drawing and self.tool_mode in ["Линия", "Прямоугольник", "Круг"]:
            self.apply_shapes_styles(painter)
            
            if self.tool_mode == "Линия":
                painter.drawLine(self.start_pos, self.end_pos)
            elif self.tool_mode == "Прямоугольник":
                rect = QRect(self.start_pos, self.end_pos)
                painter.drawRect(rect.normalized())
            elif self.tool_mode == "Круг":
                rect = QRect(self.start_pos, self.end_pos)
                painter.drawEllipse(rect.normalized())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            target_point = event.position().toPoint()
            
            if self.tool_mode == "Заливщик (Ведро)":
                self.flood_fill(target_point, self.brush_color)
                self.update()
            else:
                self.is_drawing = True
                if self.tool_mode == "Кисть":
                    self.last_pos = target_point
                    pixmap_painter = QPainter(self.pixmap)
                    self.apply_brush_styles(pixmap_painter)
                    pixmap_painter.drawPoint(self.last_pos)
                    pixmap_painter.end()
                else:
                    self.start_pos = target_point
                    self.end_pos = self.start_pos
                self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.is_drawing:
            current_pos = event.position().toPoint()
            
            if self.tool_mode == "Кисть":
                pixmap_painter = QPainter(self.pixmap)
                self.apply_brush_styles(pixmap_painter)
                pixmap_painter.drawLine(self.last_pos, current_pos)
                pixmap_painter.end()
                self.last_pos = current_pos
                self.update()
            else:
                self.end_pos = current_pos
                self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.is_drawing = False
            current_pos = event.position().toPoint()
            
            if self.tool_mode in ["Линия", "Прямоугольник", "Круг"]:
                self.end_pos = current_pos
                pixmap_painter = QPainter(self.pixmap)
                self.apply_shapes_styles(pixmap_painter)
                
                if self.tool_mode == "Линия":
                    pixmap_painter.drawLine(self.start_pos, self.end_pos)
                elif self.tool_mode == "Прямоугольник":
                    rect = QRect(self.start_pos, self.end_pos)
                    pixmap_painter.drawRect(rect.normalized())
                elif self.tool_mode == "Круг":
                    rect = QRect(self.start_pos, self.end_pos)
                    pixmap_painter.drawEllipse(rect.normalized())
                    
                pixmap_painter.end()
                self.update()

    def apply_brush_styles(self, painter):
        pen = QPen(self.pen_color, self.pen_width, Qt.PenStyle.SolidLine)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

    def apply_shapes_styles(self, painter):
        pen = QPen(self.pen_color, self.pen_width, Qt.PenStyle.SolidLine)
        pen.setCapStyle(Qt.PenCapStyle.SquareCap)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)  
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)      

    def flood_fill(self, start_point, fill_color):
        """Безопасный попиксельный алгоритм заливки через QRgb."""
        image = self.pixmap.toImage()
        width, height = image.width(), image.height()
        x_start, y_start = start_point.x(), start_point.y()
        
        if x_start < 0 or x_start >= width or y_start < 0 or y_start >= height:
            return
            
        target_rgb = image.pixel(x_start, y_start)
        fill_rgb = fill_color.rgb()
        
        if target_rgb == fill_rgb:
            return

        queue = [(x_start, y_start)]
        while queue:
            x, y = queue.pop()
            if image.pixel(x, y) == target_rgb:
                image.setPixel(x, y, fill_rgb)
                if x > 0: queue.append((x - 1, y))
                if x < width - 1: queue.append((x + 1, y))
                if y > 0: queue.append((x, y - 1))
                if y < height - 1: queue.append((x, y + 1))
                
        self.pixmap = QPixmap.fromImage(image)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Paint — Классический режим")
        self.resize(1200, 750)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        toolbar_layout = QHBoxLayout()

        toolbar_layout.addWidget(QLabel("<b>Инструмент:</b>"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Кисть", "Линия", "Прямоугольник", "Круг", "Заливщик (Ведро)"])
        self.mode_combo.currentTextChanged.connect(self.change_mode)
        toolbar_layout.addWidget(self.mode_combo)

        toolbar_layout.addSpacing(20)

        self.btn_pen_color = QPushButton("Цвет Инструмента")
        self.btn_pen_color.setStyleSheet("background-color: rgb(50,50,50); color: white; font-weight: bold;")
        self.btn_pen_color.clicked.connect(self.choose_pen_color)
        toolbar_layout.addWidget(self.btn_pen_color)

        toolbar_layout.addSpacing(10)

        self.btn_brush_color = QPushButton("Цвет Ведра (Заливки)")
        self.btn_brush_color.setStyleSheet("background-color: rgb(100,150,250); color: black; font-weight: bold;")
        self.btn_brush_color.clicked.connect(self.choose_brush_color)
        toolbar_layout.addWidget(self.btn_brush_color)

        toolbar_layout.addSpacing(20)

        toolbar_layout.addWidget(QLabel("Толщина:"))
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setMinimum(1)
        self.width_slider.setMaximum(50)
        self.width_slider.setValue(12)
        self.width_slider.setFixedWidth(130)
        self.width_slider.valueChanged.connect(self.change_width)
        toolbar_layout.addWidget(self.width_slider)

        self.width_label = QLabel("12 px")
        self.width_label.setFixedWidth(45) 
        toolbar_layout.addWidget(self.width_label)

        toolbar_layout.addSpacing(20)

        self.btn_reset = QPushButton("🗑 Сбросить")
        self.btn_reset.setStyleSheet("background-color: #ff4d4d; color: white; font-weight: bold; padding: 5px 12px;")
        self.btn_reset.clicked.connect(self.reset_canvas_clicked)
        toolbar_layout.addWidget(self.btn_reset)

        toolbar_layout.addSpacing(10)
        
        self.btn_exit = QPushButton("❌ Выйти")
        self.btn_exit.setStyleSheet("background-color: #555555; color: white; font-weight: bold; padding: 5px 12px;")
        self.btn_exit.clicked.connect(self.close) 
        toolbar_layout.addWidget(self.btn_exit)

        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)

        self.canvas = PaintCanvas()
        main_layout.addWidget(self.canvas)

    def change_mode(self, text):
        self.canvas.set_tool_mode(text)

    def change_width(self, value):
        self.canvas.set_pen_width(value)
        self.width_label.setText(f"{value} px")

    def choose_pen_color(self):
        color = QColorDialog.getColor(self.canvas.pen_color, self, "Выберите цвет инструмента")
        if color.isValid():
            self.canvas.pen_color = color
            self.btn_pen_color.setStyleSheet(f"background-color: {color.name()}; color: white; font-weight: bold;")

    def choose_brush_color(self):
        color = QColorDialog.getColor(self.canvas.brush_color, self, "Выберите цвет заливки")
        if color.isValid():
            self.canvas.brush_color = color
            self.btn_brush_color.setStyleSheet(f"background-color: {color.name()}; color: black; font-weight: bold;")

    def reset_canvas_clicked(self):
        self.canvas.clear_canvas()

if __name__ == "__main__":
    app = QApplication([])  
    window = MainWindow()
    window.show()
    app.exec()             