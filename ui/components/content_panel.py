from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QScrollArea)
from PyQt5.QtCore import Qt
from .image_label import ImageLabel
from .page_slider import PageSlider
from .zoom_slider import ZoomSlider

class ContentPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_manga = None
        self.is_single_page_mode = False
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 图片查看区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.image_label = ImageLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        scroll_area.setWidget(self.image_label)
        layout.addWidget(scroll_area)
        
        # 导航按钮布局
        nav_layout = QHBoxLayout()
        nav_layout.addStretch()
        
        # 创建导航按钮组
        nav_button_widget = QWidget()
        nav_button_layout = QHBoxLayout(nav_button_widget)
        nav_button_layout.setContentsMargins(0, 0, 0, 0)
        nav_button_layout.setSpacing(5)
        
        self.page_slider = PageSlider()
        
        self.zoom_slider = ZoomSlider()
        
        self.prev_btn = QPushButton('←')
        self.prev_btn.setFixedWidth(30)
        
        self.single_page_btn = QPushButton('双页')
        self.single_page_btn.setFixedWidth(50)
        self.single_page_btn.setCheckable(True)
        
        self.next_btn = QPushButton('→')
        self.next_btn.setFixedWidth(30)
        
        nav_button_layout.addWidget(self.page_slider)
        nav_button_layout.addWidget(self.prev_btn)
        nav_button_layout.addWidget(self.single_page_btn)
        nav_button_layout.addWidget(self.next_btn)
        nav_button_layout.addWidget(self.zoom_slider)
        
        # 添加风格切换按钮
        self.style_btn = QPushButton('默认')
        self.style_btn.setFixedWidth(50)
        nav_button_layout.addWidget(self.style_btn)
        
        nav_layout.addWidget(nav_button_widget)
        nav_layout.addStretch()
        
        layout.addLayout(nav_layout)
        
        # 确保图像显示控件可以接收键盘焦点
        self.image_label.setFocusPolicy(Qt.StrongFocus)
        # 启用鼠标追踪
        self.image_label.setMouseTracking(True)

    def set_current_manga(self, manga):
        self.current_manga = manga
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        enabled = self.current_manga is not None
        self.prev_btn.setEnabled(enabled)
        self.next_btn.setEnabled(enabled)
        self.page_slider.setEnabled(enabled)
        self.single_page_btn.setEnabled(enabled)
        self.zoom_slider.setEnabled(enabled)

    def toggle_page_mode(self):
        self.is_single_page_mode = not self.is_single_page_mode
        self.single_page_btn.setText('单页' if self.is_single_page_mode else '双页')
        if self.current_manga:
            self.show_current_page()

    def show_current_page(self):
        if not self.current_manga:
            return
        # 实现显示当前页面的逻辑
        pass

    def prev_page(self):
        self.change_page(-1)

    def next_page(self):
        self.change_page(1)

    def change_page(self, direction):
        if not self.current_manga:
            return
            
        step = 1 if self.is_single_page_mode else 2
        current_page = self.current_manga.current_page
        total_pages = self.current_manga.total_pages
        
        if direction > 0:  # 向后翻页
            if current_page < total_pages - step:
                self.current_manga.current_page += step
                self.show_current_page()
        else:  # 向前翻页
            if current_page >= step:
                self.current_manga.current_page -= step
                self.show_current_page()