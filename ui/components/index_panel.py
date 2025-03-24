from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QButtonGroup, QScrollArea, QFrame,
                             QTreeView)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QStandardItemModel
from ..layouts.flow_layout import FlowLayout

class IndexPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manga_manager = None
        self.tag_buttons = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 目录选择和搜索布局
        dir_layout = QHBoxLayout()
        self.select_dir_btn = QPushButton('📂')
        self.select_dir_btn.setMaximumWidth(30)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('搜索漫画...')
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        
        dir_layout.addWidget(self.select_dir_btn)
        dir_layout.addWidget(self.search_input)
        layout.addLayout(dir_layout)
        
        # 标签分类按钮组
        self.tag_type_group = QButtonGroup(self)
        tag_type_layout = QHBoxLayout()
        layout.addLayout(tag_type_layout)
        
        # 创建垂直分割器
        v_splitter = QSplitter(Qt.Vertical)
        
        # 标签过滤区域
        tag_scroll_area = QScrollArea()
        tag_scroll_area.setWidgetResizable(True)
        tag_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tag_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.tag_frame = QFrame()
        self.tag_layout = FlowLayout(self.tag_frame)
        self.tag_layout.setSpacing(5)
        tag_scroll_area.setWidget(self.tag_frame)
        
        # 过滤按钮组
        self.filter_button_group = QButtonGroup(self)
        self.filter_button_group.setExclusive(False)
        
        # 漫画列表
        self.manga_list_view = QTreeView()
        self.manga_model = QStandardItemModel()
        self.manga_list_view.setModel(self.manga_model)
        
        # 将组件添加到垂直分割器
        v_splitter.addWidget(tag_scroll_area)
        v_splitter.addWidget(self.manga_list_view)
        
        # 设置垂直分割器初始大小
        v_splitter.setSizes([200, 400])
        layout.addWidget(v_splitter)
        
        # 设置最小宽度
        self.setMinimumWidth(300)

    def set_manga_manager(self, manga_manager):
        self.manga_manager = manga_manager

    def create_tag_type_buttons(self):
        if not self.manga_manager:
            return
        # 清除现有按钮
        for button in self.tag_type_group.buttons():
            self.tag_type_group.removeButton(button)
            button.deleteLater()

        # 创建新按钮
        for tag_type in self.manga_manager.get_tag_types():
            btn = QPushButton(tag_type)
            btn.setCheckable(True)
            self.tag_type_group.addButton(btn)
            self.tag_layout.addWidget(btn)

    def update_tag_buttons(self):
        if not self.manga_manager:
            return
        # 实现标签按钮更新逻辑
        pass

    def update_manga_list(self):
        if not self.manga_manager:
            return
        # 实现漫画列表更新逻辑
        pass

    def perform_search(self):
        # 实现搜索逻辑
        pass