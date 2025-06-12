# Manga Translator

现代化漫画翻译工具，集成OCR识别、多引擎翻译和文本替换功能。

## ✨ 核心功能
- **OCR文本识别**：精准识别漫画中的多语言文本
- **多引擎翻译**：支持Google翻译/智谱AI/本地模型
- **批量处理**：自动翻译整个漫画章节
- **字体保持**：智能处理文本布局保持原始美学
- **缓存系统**：显著提升重复处理效率

## 🚀 快速开始

### 环境要求

*   **Python**: `>=3.11,<3.12` (根据项目 [`pyproject.toml`](pyproject.toml:6) 定义)。建议使用 3.11.x 的最新修订版。您可以从 [Python官网](https://www.python.org/downloads/) 下载。
*   **Git**: 如果尚未安装，请从 [Git官网](https://git-scm.com/) 下载。
*   **uv**: 一个非常快的 Python 包管理器。如果尚未安装，请通过 `pip install uv` 或参考 [官方文档](https://github.com/astral-sh/uv) 安装。

### 安装与运行

1.  **克隆项目仓库**
    ```bash
    git clone https://github.com/kawayiYokami/MangaReader.git
    cd MangaReader
    ```

2.  **创建并激活虚拟环境**
    ```bash
    # 使用 uv 创建虚拟环境 (以 Python 3.11.12 为例)
    uv venv --python 3.11.12

    # 激活环境
    # Windows (CMD):
    .\.venv\Scripts\activate.bat
    # Windows (PowerShell):
    .\.venv\Scripts\Activate.ps1
    # Linux/macOS (bash/zsh):
    source .venv/bin/activate
    ```

3.  **安装依赖**
    ```bash
    # 使用 uv 同步依赖
    uv pip sync requirements.txt
    ```

4.  **运行程序**
    ```bash
    # 运行 Web UI
    python web_main.py
    ```
    启动后，请在浏览器中访问 `http://127.0.0.1:5000`。

### 使用流程
1. 选择漫画文件或文件夹
2. 设置翻译参数（语言/引擎）
3. 执行翻译（单页或批量）
4. 查看/保存结果

## 🙏 致谢
本项目的 OCR 功能依赖于优秀的 [OnnxOCR](https://github.com/jingsongliujing/OnnxOCR) 项目。
如果您觉得它对您有帮助，请给原作者 [jingsongliujing/OnnxOCR](https://github.com/jingsongliujing/OnnxOCR) 点个 Star ⭐ 支持一下！


## 📜 许可证
本项目采用 [GNU General Public License v3.0](LICENSE) 授权。