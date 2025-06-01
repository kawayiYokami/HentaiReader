# Manga Translator

现代化漫画翻译工具，集成 OCR 识别、多引擎翻译和文本替换功能，提供高效的漫画本地化解决方案。

## ✨ 功能特性

- **OCR 文本识别**：精准识别漫画中的文本区域，支持多语言字符集
- **多引擎翻译**：集成智谱AI、Google翻译引擎，支持自定义API和批量处理
- **批量处理**：全自动批量翻译整个漫画章节
- **字体保持**：内置 12+ 精选字体库，确保翻译文本风格统一
- **文本替换系统**：智能处理气泡文本布局，保持原始漫画美学
- **直观界面**：基于 PySide6 和 qfluentwidgets 构建的操作界面

## 🚀 快速开始

### 📦 安装

1. **克隆仓库**:
   ```bash
   git clone https://github.com/your-username/manga.git
   cd manga
   ```

2. **安装依赖**:
   ```bash
   pip install uv
   uv venv
   uv pip install -r requirements.txt
   ```

3. **初始化子项目 (OCR 引擎)**:
   ```bash
   update_ocr_font.bat
   ```
   > 此脚本会自动克隆 [OnnxOCR](https://github.com/jingsongliujing/OnnxOCR) 子项目

### 🏃 运行

启动应用程序：
```bash
python main.py
```

### 使用指南
1. 主界面选择漫画文件/目录
2. 在 OCR 翻译窗口（`Ctrl+T`）配置：
   - 选择源语言/目标语言
   - 设置翻译引擎和 API 密钥
   - 调整文本检测参数
3. 点击"开始翻译"进行单页处理
4. 使用批处理工作器进行全集翻译

## 🛠️ 项目结构

```
manga/
├── main.py                    # 应用入口
├── pyproject.toml             # 项目配置
├── README.md                  # 项目文档
├── update_ocr_font.bat        # 字体更新脚本
├── uv.toml                    # uv 配置
├── core/                      # 核心逻辑
│   ├── batch_translation_worker.py  # 批量翻译工作器
│   ├── config.py              # 应用配置
│   ├── image_translator.py    # 图像翻译器
│   ├── manga_cache.py         # 漫画缓存
│   ├── manga_manager.py       # 漫画管理
│   ├── manga_model.py         # 数据模型
│   ├── manga_text_replacer.py # 文本替换引擎
│   ├── ocr_manager.py         # OCR 管理器
│   └── translator.py          # 翻译器
├── font/                      # 字体库（12+ 精选字体）
│   ├── 杨任东竹石体-Heavy.ttf
│   ├── Alibaba-PuHuiTi-Bold.ttf
│   └── ...（其他字体文件）
├── OnnxOCR/                   # OCR 子项目 [MIT]
│   └── ...（OCR 引擎实现）
├── ui/                        # 用户界面
│   ├── new_interface/         # 主界面组件
│   │   ├── control_panel.py   # 控制面板
│   │   ├── manga_browser.py   # 漫画浏览器
│   │   ├── manga_list.py      # 漫画列表
│   │   ├── manga_viewer.py    # 漫画查看器
│   │   └── tag_filter.py      # 标签过滤器
│   └── ocr_translation/       # OCR 翻译界面
│       ├── ocr_translation_window.py     # 主窗口
│       └── translation_settings_window.py # 设置窗口
├── utils/                     # 工具模块
│   ├── color_utils.py         # 颜色处理
│   └── manga_logger.py        # 日志系统
└── views/                     # 视图接口
    ├── manga_browser_interface.py
    ├── manga_translation_interface.py
    └── settings_interface.py
```

## ⚙️ 配置

关键配置文件：

1. **翻译设置** [`ui/ocr_translation/translation_settings_window.py`]：
   - 设置默认翻译引擎 (ChatGPT/DeepL)
   - 配置 API 密钥和端点
   - 调整翻译参数（温度、最大 token 等）

2. **OCR 配置** [`core/ocr_manager.py`]：
   - 文本检测置信度阈值
   - 文本区域合并参数
   - 语言识别模型选择

3. **字体设置** [`core/manga_text_replacer.py`]：
   - 默认替换字体（从 `font/` 目录选择）
   - 字体大小自适应规则
   - 文本描边和阴影配置

## 🤝 贡献指南

欢迎贡献！请遵循以下流程：
1. 提交 issue 描述问题/建议
2. 创建特性分支 (`feat/your-feature`)
3. 提交 PR 并关联对应 issue
4. 确保通过核心功能测试：
   ```bash
   python -m core.test.test_manga_batch_translate
   ```

## 📄 许可证

- 主项目: [MIT License](LICENSE)
- OnnxOCR 子项目: [MIT License](https://github.com/jingsongliujing/OnnxOCR/blob/main/LICENSE)