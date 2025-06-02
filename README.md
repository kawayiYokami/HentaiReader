# Manga Translator

现代化漫画翻译工具，集成OCR识别、多引擎翻译和文本替换功能。

## ✨ 核心功能
- **OCR文本识别**：精准识别漫画中的多语言文本
- **多引擎翻译**：支持Google翻译/智谱AI/本地模型
- **批量处理**：自动翻译整个漫画章节
- **字体保持**：智能处理文本布局保持原始美学
- **缓存系统**：显著提升重复处理效率

## 🚀 快速开始

### 安装

**Python 版本要求**: 3.11.x (具体为 `>=3.11, <3.12`，根据项目 [`pyproject.toml:6`](pyproject.toml:6) 定义)。
请从 [https://www.python.org/downloads/](https://www.python.org/downloads/) 下载并安装 Python 3.11 的最新修订版。确保在安装时将 Python 添加到系统 PATH。

**安装步骤**:

1.  **安装 Git**: 如果尚未安装，请从 [https://git-scm.com/](https://git-scm.com/) 下载并安装。
2.  **克隆项目并进入目录**:
    ```bash
    git clone https://github.com/kawayiYokami/MangaReader.git MangaReader
    cd MangaReader
    ```
3.  **获取 `OnnxOCR` 子项目**:
    ```bash
    update_ocr_font.bat
    ```
4.  **安装 `uv` (Python 包管理器)**:
    ```bash
    pip install uv
    ```
5.  **创建虚拟环境**:
    ```bash
    uv venv
    ```
6.  **激活虚拟环境**:
    *   Windows (CMD): `.\.venv\Scripts\activate.bat`
    *   Windows (PowerShell): `.\.venv\Scripts\Activate.ps1`
    *   Linux/macOS (bash/zsh): `source .venv/bin/activate`
7.  **安装依赖**:
    ```bash
    uv pip install -r requirements.txt
    ```

### 运行
```bash
python main.py
```

### 使用流程
1. 选择漫画文件或文件夹
2. 设置翻译参数（语言/引擎）
3. 执行翻译（单页或批量）
4. 查看/保存结果

### 业余娱乐项目