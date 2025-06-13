# 主题功能重构计划 (简化版)

## 目标

实现桌面版和网页版应用在主题切换功能上的行为区分，并修复桌面版启动时主题不固定的问题。

*   **桌面版**: 切换主题时，更新后端的 `config.json` 文件。应用启动时，直接从 `config.json` 读取主题设置。
*   **网页版**: 切换主题时，仅更新浏览器的 `localStorage`，不影响后端配置文件。

## 核心思路

利用前端已有的桌面环境检测能力 (`runningInDesktopApp` 或 `window.pywebview`)，在前端层面控制主题的保存逻辑，并通过后端向前端注入初始主题状态，保证桌面版启动时状态的正确性。

## 实施步骤

### 第一步：修改前端保存逻辑

**目的**: 只在桌面环境下，才向后端发送保存主题的API请求。

1.  **定位文件**: 找到处理主题切换的 Vue 组件方法 `onThemeChange` (可能在 `web/static/js/manga-browser.js` 或相关JS文件中)。
2.  **修改逻辑**:
    *   保留 `window.themeManager.setTheme(newTheme)` 的调用，以保证UI即时响应。
    *   使用 `if (this.runningInDesktopApp)` 条件判断，将调用后端API的 `fetch` 请求包裹起来，确保只有在桌面版时才执行。

**代码示例 (Vue Component):**
```javascript
async onThemeChange(newTheme) {
    // 1. 立即应用主题到UI (所有环境都需要)
    window.themeManager.setTheme(newTheme);

    // 2. 检查是否为桌面版
    if (this.runningInDesktopApp) {
        // 3. 只有桌面版才向服务器发送保存请求
        try {
            await fetch('/api/settings/themeMode', { 
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    key: 'themeMode',
                    value: newTheme.charAt(0).toUpperCase() + newTheme.slice(1)
                })
             });
            console.log('桌面版主题已保存。');
        } catch (error) {
            console.error('保存主题到服务器失败:', error);
        }
    } else {
        // 网页版不执行任何操作，仅依赖localStorage
        console.log('网页版主题已切换，仅保存在浏览器本地。');
    }
}
```

### 第二步：修复桌面版加载主题的问题

**目的**: 让桌面版启动时能正确加载 `config.json` 中的主题，而不是回退到默认值。

1.  **后端修改**:
    *   **文件**: `web/app.py`
    *   **操作**: 在返回 `index.html` 的路由处理函数 (`read_root`) 中，从 `config` 对象读取主题，并将其作为变量 `initial_theme` 传递给模板。

    **代码示例 (`web/app.py`):**
    ```python
    from core.config import config

    @router.get("/", response_class=HTMLResponse)
    async def read_root(request: Request):
        initial_theme = config.themeMode.value.value if hasattr(config.themeMode.value, 'value') else str(config.themeMode.value)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "initial_theme": initial_theme,
        })
    ```

2.  **前端模板修改**:
    *   **文件**: `web/templates/index.html`
    *   **操作**: 在 `<script>` 标签中，将后端传来的 `initial_theme` 存储到全局 `window` 对象上。

    **代码示例 (`index.html`):**
    ```html
    <script>
        window.initialTheme = '{{ initial_theme | default('auto') }}';
    </script>
    ```

3.  **前端JS初始化逻辑修改**:
    *   **文件**: `web/static/js/theme-manager.js`
    *   **操作**: 修改 `init` 方法，使其优先使用 `window.initialTheme` 作为初始主题。

    **代码示例 (`theme-manager.js`):**
    ```javascript
    init() {
        // 优先使用后端注入的初始主题
        let themeToApply = window.initialTheme;

        // 如果后端没有注入，再从localStorage读取
        if (!themeToApply) {
            themeToApply = localStorage.getItem('manga-translator-theme');
        }
        
        // 如果依然没有，则设置一个最终默认值
        if (!themeToApply) {
            themeToApply = 'auto';
        }
        
        this.currentTheme = themeToApply;
        
        // 确保桌面端的localStorage与config文件同步
        if (!!window.pywebview) {
             localStorage.setItem('manga-translator-theme', this.currentTheme);
        }

        this.applyTheme();
        this.watchSystemTheme();
    }