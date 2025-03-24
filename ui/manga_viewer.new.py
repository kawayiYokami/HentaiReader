from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter
from PyQt5.QtCore import Qt
from core.manga_manager import MangaManager
from styles.win_theme_color import Win11Style
from .components.index_panel import IndexPanel
from .components.content_panel import ContentPanel
from utils.manga_logger import log

class MangaViewer(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("漫画查看器")
        self.manga_manager = MangaManager()
        self.current_manga = None
        self.next_page_on_right = True  # 控制下一页显示位置
        self.is_single_page_mode = False  # 单双页模式控制
        self.current_style = 'default'  # 当前主题样式
        
        self.setup_ui()
        Win11Style.apply_style(self)
        log.info("MangaViewer初始化完成")

    def setup_ui(self):
        log.info("开始设置UI界面")
        self.setWindowTitle('漫画查看器')
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # 创建水平分割器
        h_splitter = QSplitter(Qt.Horizontal)
        
        # 创建索引面板和内容面板
        self.index_panel = IndexPanel()
        self.index_panel.set_manga_manager(self.manga_manager)
        self.index_panel.manga_list_view.clicked.connect(self.on_manga_selected)
        self.index_panel.manga_list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.index_panel.manga_list_view.customContextMenuRequested.connect(self.show_manga_context_menu)
        
        self.content_panel = ContentPanel()
        
        # 将面板添加到水平分割器
        h_splitter.addWidget(self.index_panel)
        h_splitter.addWidget(self.content_panel)
        
        # 设置水平分割器初始大小比例
        h_splitter.setSizes([300, 900])
        
        # 设置拉伸因子，使右侧面板获得所有额外空间
        h_splitter.setStretchFactor(0, 0)  # 左侧面板不拉伸
        h_splitter.setStretchFactor(1, 1)  # 右侧面板获得所有额外空间
        
        layout.addWidget(h_splitter)
        
        # 连接信号和槽
        self.connect_signals()
    
    def connect_signals(self):
        # 连接索引面板的信号
        self.index_panel.select_dir_btn.clicked.connect(self.select_directory)
        self.index_panel.search_input.textChanged.connect(self.on_search_text_changed)
        self.index_panel.search_timer.timeout.connect(self.perform_search)
        self.index_panel.tag_type_group.buttonClicked.connect(self.update_tag_buttons)
        
        # 连接内容面板的信号
        self.content_panel.page_slider.valueChanged.connect(self.on_slider_value_changed)
        self.content_panel.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        self.content_panel.prev_btn.clicked.connect(self.prev_page)
        self.content_panel.next_btn.clicked.connect(self.next_page)
        self.content_panel.single_page_btn.clicked.connect(self.toggle_page_mode)
        self.content_panel.style_btn.clicked.connect(self.toggle_style)