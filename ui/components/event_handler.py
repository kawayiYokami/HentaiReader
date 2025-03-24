from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from utils import manga_logger as log

class EventHandler:
    def __init__(self, viewer):
        self.viewer = viewer
        self.is_dragging = False
        self.last_pos = None
        self.drag_threshold = 5  # 拖动阈值，防止误触
        
    def handle_key_press(self, event):
        """处理键盘按键事件"""
        try:
            key = event.key()
            if key in [Qt.Key_Right, Qt.Key_Space, Qt.Key_Down]:
                self.viewer.next_page()
            elif key in [Qt.Key_Left, Qt.Key_Backspace, Qt.Key_Up]:
                self.viewer.prev_page()
            elif key == Qt.Key_Home:
                if self.viewer.current_manga:
                    self.viewer.current_manga.current_page = 0
                    self.viewer.show_current_page()
            elif key == Qt.Key_End:
                if self.viewer.current_manga:
                    self.viewer.current_manga.current_page = self.viewer.current_manga.total_pages - 1
                    self.viewer.show_current_page()
            elif key == Qt.Key_Plus or key == Qt.Key_Equal:
                current_zoom = self.viewer.zoom_slider.value()
                self.viewer.zoom_slider.setValue(min(current_zoom + 10, 200))
            elif key == Qt.Key_Minus:
                current_zoom = self.viewer.zoom_slider.value()
                self.viewer.zoom_slider.setValue(max(current_zoom - 10, 50))
            elif key == Qt.Key_S:
                self.viewer.toggle_page_mode()
            elif key == Qt.Key_D:
                self.viewer.next_page_on_right = not self.viewer.next_page_on_right
                self.viewer.show_current_page()
        except Exception as e:
            log.error(f"键盘事件处理错误: {str(e)}")
            QMessageBox.warning(self.viewer, '错误', f'键盘事件处理错误: {str(e)}')
    
    def handle_mouse_press(self, event):
        """处理鼠标按下事件"""
        try:
            if event.button() == Qt.LeftButton:
                self.is_dragging = True
                self.last_pos = event.pos()
        except Exception as e:
            log.error(f"鼠标按下事件处理错误: {str(e)}")
    
    def handle_mouse_release(self, event):
        """处理鼠标释放事件"""
        try:
            if event.button() == Qt.LeftButton:
                if self.is_dragging and self.last_pos:
                    dx = event.pos().x() - self.last_pos.x()
                    if abs(dx) > self.drag_threshold:
                        if dx > 0:
                            self.viewer.prev_page()
                        else:
                            self.viewer.next_page()
                self.is_dragging = False
                self.last_pos = None
        except Exception as e:
            log.error(f"鼠标释放事件处理错误: {str(e)}")
    
    def handle_mouse_move(self, event):
        """处理鼠标移动事件"""
        try:
            if self.is_dragging and self.last_pos:
                self.last_pos = event.pos()
        except Exception as e:
            log.error(f"鼠标移动事件处理错误: {str(e)}")
    
    def handle_wheel(self, event):
        """处理鼠标滚轮事件"""
        try:
            if event.modifiers() & Qt.ControlModifier:
                # Ctrl + 滚轮进行缩放
                delta = event.angleDelta().y()
                current_zoom = self.viewer.zoom_slider.value()
                if delta > 0:
                    self.viewer.zoom_slider.setValue(min(current_zoom + 10, 200))
                else:
                    self.viewer.zoom_slider.setValue(max(current_zoom - 10, 50))
            else:
                # 普通滚轮进行翻页
                delta = event.angleDelta().y()
                if delta > 0:
                    self.viewer.prev_page()
                else:
                    self.viewer.next_page()
        except Exception as e:
            log.error(f"鼠标滚轮事件处理错误: {str(e)}")
            QMessageBox.warning(self.viewer, '错误', f'鼠标滚轮事件处理错误: {str(e)}')