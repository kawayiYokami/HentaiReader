# Web架构框架 - 翻译工厂架构

## 🏗️ 整体架构

### 技术栈
- **后端**: FastAPI + Python 3.8+
- **前端**: 原生JavaScript + Element Plus + Vue 3 (CDN)
- **数据库**: SQLite (缓存和配置)
- **WebSocket**: 实时通信
- **静态文件**: FastAPI StaticFiles
- **架构模式**: 翻译工厂架构 + 会话管理

### 核心设计理念
- **翻译工厂**: 全局单例翻译服务，封装所有翻译复杂逻辑
- **会话管理**: 会话级别的查看器控制，独立的缓存和状态管理
- **分层架构**: 严格的web层/core层分离，单向依赖
- **统一接口**: 通过统一的缓存键生成器确保一致性

## 🧩 组件化架构设计

### 🎯 组件化设计原则
- **单一职责**: 每个组件只负责一个明确的功能
- **高度复用**: 组件可在多个页面中重复使用
- **松耦合**: 组件间完全独立，无依赖关系
- **易扩展**: 新功能通过新增组件实现，不修改现有组件

### 📋 五层组件架构

#### 1. Layout 布局组件 (4个)
```
components/layout/
├── html-head.html          # HTML头部和依赖管理
├── app-container.html      # 应用容器和路由逻辑
├── sidebar.html           # 侧边栏导航
└── hidden-elements.html   # 隐藏的表单元素
```

#### 2. Pages 页面组件 (7个)
```
components/pages/
├── home.html              # 首页 - 欢迎和功能介绍
├── manga-browser.html     # 漫画浏览 - 库管理和浏览
├── translation.html       # 漫画翻译 - 翻译处理
├── compression.html       # 漫画压缩 - WebP压缩
├── cache-management.html  # 缓存管理 - 数据管理
├── settings.html          # 设置页面 - 应用配置
└── default.html           # 默认页面 - 未知路由
```

#### 3. Dialogs 对话框组件 (4个)
```
components/dialogs/
├── edit-dialog.html           # 统一编辑对话框
├── harmonization-form.html    # 和谐映射表单
├── translation-form.html      # 翻译表单
└── default-form.html          # 默认表单
```

#### 4. Shared 共享组件 (3个)
```
components/shared/
├── empty-state.html       # 空状态显示
├── loading-state.html     # 加载状态显示
└── no-results-state.html  # 无结果状态显示
```

#### 5. Widgets 小部件组件 (5个)
```
components/widgets/
├── manga-card.html              # 漫画卡片
├── file-upload.html             # 文件上传区域
├── task-list.html               # 翻译任务列表
├── compression-upload.html      # 压缩文件上传
└── compression-task-list.html   # 压缩任务列表
```

## 💻 JavaScript模块化架构

### 🎯 模块化设计原则
- **命名空间隔离**: 使用 `window.ModuleMethods` 避免全局污染
- **功能分离**: 每个模块负责特定功能领域
- **方法合并**: 通过扩展运算符合并到Vue实例
- **调试友好**: 每个模块可独立调试和测试

### 📦 JavaScript模块生态
```
static/js/
├── app-data.js           # 应用数据、计算属性、生命周期
├── utils.js              # 工具函数和基础方法
├── manga-browser.js      # 漫画浏览功能
├── cache-management.js   # 缓存管理功能
├── translation.js        # 翻译功能
├── compression.js        # 压缩功能
└── theme-manager.js      # 主题管理
```

### 🔗 模块组装机制
```javascript
// 主文件中的方法合并
methods: {
    ...window.UtilsMethods,
    ...window.MangaBrowserMethods,
    ...window.CacheManagementMethods,
    ...window.TranslationMethods,
    ...window.CompressionMethods,
}
```

### 📋 模块结构规范
```javascript
// 标准模块结构
window.ModuleMethods = {
    // 功能方法
    methodName() {
        // 实现逻辑
    },

    // 异步方法
    async asyncMethod() {
        // 异步逻辑
    }
};
```

## 🧭 导航和路由系统

### 组件化侧边栏 (`components/layout/sidebar.html`)
- **汉堡包菜单**: 支持折叠/展开
- **响应式设计**: 折叠时只显示图标
- **权限控制**: 根据访问类型显示不同菜单

#### 主导航菜单
- 🏠 **首页** (`home`) - 欢迎页面
- 📚 **漫画浏览** (`manga-browser`) - 库管理
- 🔤 **漫画翻译** (`translation`) - 翻译处理
- 🗜️ **漫画压缩** (`compression`) - WebP压缩
- 💾 **缓存管理** (`cache`) - 仅本地访问

#### 底部设置
- ⚙️ **设置** (`settings`) - 应用配置

### 路由逻辑 (`components/layout/app-container.html`)
```html
<!-- 基于activeMenu的条件渲染 -->
<div v-if="activeMenu === 'home'">
    {% include 'components/pages/home.html' %}
</div>
<div v-else-if="activeMenu === 'manga-browser'">
    {% include 'components/pages/manga-browser.html' %}
</div>
<!-- ... 其他页面 -->
```

## 🔐 权限控制

### 本地访问 (`isLocalAccess = true`)
- 完整功能访问
- 可添加漫画到库
- 可访问缓存管理
- 支持文件替换操作

### 远程访问 (`isLocalAccess = false`)
- 只读漫画浏览
- 文件上传处理模式
- 隐藏缓存管理
- 安全模式提示

## 🎨 UI设计原则

### 现代扁平设计
- 无阴影，纯色块
- 清晰边界
- 简洁图标 (中文字符)

### 响应式布局
- 网格系统
- 弹性容器
- 移动端适配

### 主题系统
- CSS变量驱动
- 实时切换
- 本地存储

## 📂 完整文件结构

```
web/
├── templates/
│   ├── index.html                    # 极简主入口 (76行)
│   └── components/                   # 组件生态系统
│       ├── layout/                   # 布局组件 (4个)
│       │   ├── html-head.html
│       │   ├── app-container.html
│       │   ├── sidebar.html
│       │   └── hidden-elements.html
│       ├── pages/                    # 页面组件 (7个)
│       │   ├── home.html
│       │   ├── manga-browser.html
│       │   ├── translation.html
│       │   ├── compression.html
│       │   ├── cache-management.html
│       │   ├── settings.html
│       │   └── default.html
│       ├── dialogs/                  # 对话框组件 (4个)
│       │   ├── edit-dialog.html
│       │   ├── harmonization-form.html
│       │   ├── translation-form.html
│       │   └── default-form.html
│       ├── shared/                   # 共享组件 (3个)
│       │   ├── empty-state.html
│       │   ├── loading-state.html
│       │   └── no-results-state.html
│       └── widgets/                  # 小部件组件 (5个)
│           ├── manga-card.html
│           ├── file-upload.html
│           ├── task-list.html
│           ├── compression-upload.html
│           └── compression-task-list.html
├── static/
│   ├── css/
│   │   └── modern-theme.css         # 主题样式
│   └── js/                          # JavaScript模块 (6个)
│       ├── app-data.js              # 应用数据
│       ├── utils.js                 # 工具函数
│       ├── manga-browser.js         # 漫画浏览
│       ├── cache-management.js      # 缓存管理
│       ├── translation.js           # 翻译功能
│       ├── compression.js           # 压缩功能
│       └── theme-manager.js         # 主题管理
├── api/                             # 后端API
└── app.py                           # FastAPI应用
```

## 🔄 模块化状态管理

### 数据模块 (`app-data.js`)
```javascript
window.AppData = {
    // 系统状态
    activeMenu: 'home',
    sidebarCollapsed: false,
    isLocalAccess: true,
    currentTheme: 'auto',

    // 漫画浏览数据
    mangaList: [],
    availableTags: [],
    selectedTags: [],

    // 翻译功能数据
    translationTasks: [],
    translationSettings: {},

    // 压缩功能数据
    compressionTasks: [],
    compressionSettings: {},

    // 缓存管理数据
    cacheStats: {},
    cacheEntries: []
};
```

### 计算属性模块 (`app-data.js`)
```javascript
window.AppComputed = {
    filteredMangaList() {
        // 搜索和标签过滤逻辑
    },
    hasCompletedTasks() {
        // 任务完成状态检查
    }
};
```

### 生命周期模块 (`app-data.js`)
```javascript
window.AppLifecycle = {
    mounted() {
        // 初始化各个功能模块
        this.loadInitialData();
        this.initCacheManagement();
    }
};
```

## 🚀 扩展开发指南

### 🔧 组件化开发要求

#### 强制性组件化原则
- **禁止单文件巨大化**: 任何单个文件不得超过300行
- **强制功能分离**: 不同功能必须拆分为独立组件
- **强制模块化**: JavaScript功能必须按模块分离
- **强制复用设计**: 重复代码必须提取为共享组件

#### HTML组件开发规范
1. **组件文件命名**: 使用kebab-case命名，如 `manga-card.html`
2. **组件职责单一**: 每个组件只负责一个明确功能
3. **Vue指令兼容**: 确保所有Vue指令正常工作
4. **Jinja2语法**: 使用 `{% include %}` 引入组件

#### JavaScript模块开发规范
1. **命名空间**: 使用 `window.ModuleMethods` 格式
2. **方法分组**: 相关功能方法放在同一模块
3. **异步处理**: 正确处理async/await
4. **错误处理**: 每个方法都要有错误处理

### 📋 添加新功能的标准流程

#### 1. 添加新页面功能
```bash
# 1. 创建页面组件
components/pages/new-feature.html

# 2. 创建功能模块
static/js/new-feature.js

# 3. 在路由中添加条件
# app-container.html 中添加 v-else-if

# 4. 在导航中添加菜单项
# sidebar.html 中添加导航项

# 5. 在主文件中引入模块
# html-head.html 中添加script标签
# index.html 中合并方法
```

#### 2. 添加新组件类型
```bash
# 1. 创建组件目录
components/new-type/

# 2. 设计组件结构
# 遵循单一职责原则

# 3. 在页面中引用
# 使用 {% include %} 语法

# 4. 测试组件功能
# 确保Vue指令正常工作
```

#### 3. 扩展现有功能
```bash
# 1. 定位相关模块
# 找到对应的JS模块和HTML组件

# 2. 添加新方法
# 在对应模块中添加新方法

# 3. 更新组件模板
# 在对应组件中添加新UI元素

# 4. 测试功能完整性
# 确保新功能不影响现有功能
```

## 🔧 开发原则和规范

### 🏗️ 架构设计原则
- **极致模块化**: 每个文件职责单一明确
- **零耦合设计**: 模块间完全独立
- **组件复用**: 最大化代码复用率
- **扩展友好**: 新功能通过新增模块实现

### 💻 前端开发原则
- **前端优先**: 所有文件处理在前端完成
- **API最小化**: 后端只提供AI服务
- **实时反馈**: 提供详细的进度和状态信息
- **错误处理**: 优雅的错误提示和恢复

### 🎨 UI/UX设计原则
- **极简主义**: 减少不必要的用户选择
- **自动化**: 常用操作自动完成
- **一致性**: 统一的交互模式
- **响应式**: 适配各种屏幕尺寸

### 🔒 安全和权限原则
- **权限分离**: 本地/远程访问不同权限
- **数据隔离**: 敏感操作仅本地可用
- **输入验证**: 严格的数据验证
- **错误隔离**: 单个模块错误不影响整体

### ⚠️ 开发禁忌
- **禁止**: 在主文件中直接写大量代码
- **禁止**: 创建超过300行的单个文件
- **禁止**: 在组件间创建强依赖关系
- **禁止**: 重复代码而不提取为共享组件
- **禁止**: 破坏现有的模块化架构

## 🎯 架构维护指南

### 📊 代码质量监控
- **文件大小**: 定期检查文件行数，超过300行需拆分
- **模块独立性**: 确保模块间无强依赖
- **组件复用率**: 监控重复代码，及时提取共享组件
- **功能完整性**: 确保模块化不影响功能完整性

### 🔄 架构演进策略
- **渐进式改进**: 小步快跑，避免大规模重构
- **向后兼容**: 新功能不破坏现有架构
- **文档同步**: 架构变更及时更新文档
- **测试验证**: 每次变更都要充分测试

这个架构框架为项目的长期发展提供了坚实的技术基础，确保代码质量和可维护性始终保持在最高水平！
