from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel
from ui.components.event_handler import EventHandler

class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.event_handler = EventHandler(parent)

    def keyPressEvent(self, event):
        self.event_handler.handle_key_press(event)

    def mousePressEvent(self, event):
        self.event_handler.handle_mouse_press(event)

    def mouseReleaseEvent(self, event):
        self.event_handler.handle_mouse_release(event)

    def mouseMoveEvent(self, event):
        self.event_handler.handle_mouse_move(event)

    def wheelEvent(self, event):
        self.event_handler.handle_wheel(event)