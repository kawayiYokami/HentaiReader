# 缓存管理增强计划 V3.0 (最终版)

## 1. 计划概述

本计划是对缓存管理模块的一次全方位功能增强和可用性提升。它基于之前的讨论，并整合了所有新的需求，旨在提供一个最终的、可执行的重构蓝图。

此计划包含三个核心任务：
1.  **持久化翻译缓存分组**: 从根本上解决缓存条目过多的问题。
2.  **翻译缓存敏感内容筛选**: 提供快速查看敏感内容的能力。
3.  **漫画列表分类展示**: 方便用户识别和管理可能非漫画的内容。

---

## 2. 任务一: 持久化翻译缓存分组 (后端聚合)

**目标**: 改变 `PersistentTranslationCacheHandler` 的行为，使其返回按`(漫画, 翻译引擎)`聚合后的数据，而不是原始的、按页的条目。

### 2.1 后端修改 (`web/api/cache.py`)

**文件**: `web/api/cache.py`  
**定位**: `PersistentTranslationCacheHandler` 类

#### 步骤 2.1.1: 重写 `get_entries` 方法

将 `get_entries` 方法的实现替换为以下聚合逻辑。这会将原始数据在后端处理成对用户友好的摘要信息。

```python
# 在 PersistentTranslationCacheHandler 类中
async def get_entries(self, page: int, page_size: int, search: Optional[str] = None) -> Dict[str, Any]:
    """获取持久化翻译缓存条目，并按（漫画路径, 翻译器类型）聚合"""
    try:
        # 1. 从管理器获取所有原始、未分组的条目
        all_raw_entries = self.manager.get_all_entries_for_display()

        # 2. 按 (manga_path, translator_type) 进行分组
        grouped_entries = {}
        for entry in all_raw_entries:
            group_key = (entry.get("manga_path"), entry.get("translator_type"))
            if not all(group_key):
                continue

            if group_key not in grouped_entries:
                grouped_entries[group_key] = {
                    "manga_path": entry.get("manga_path"),
                    "manga_name": entry.get("manga_name"),
                    "translator_type": entry.get("translator_type"),
                    "page_indices": set(), # 使用集合以避免重复并提高效率
                    "last_accessed": entry.get("last_accessed", "1970-01-01T00:00:00")
                }
            
            page_index = entry.get("page_index")
            if page_index is not None:
                grouped_entries[group_key]["page_indices"].add(page_index)
            
            # 更新为最新的访问时间
            current_last_accessed = entry.get("last_accessed", "1970-01-01T00:00:00")
            if current_last_accessed > grouped_entries[group_key]["last_accessed"]:
                grouped_entries[group_key]["last_accessed"] = current_last_accessed

        # 3. 将分组后的数据转换为最终的列表格式
        final_list = []
        for (manga_path, translator_type), group_data in grouped_entries.items():
            page_indices = sorted(list(group_data["page_indices"]))
            
            # 创建一个唯一的、稳定的复合键，用于前端操作
            composite_key = f"{manga_path}:::{translator_type}"

            final_list.append({
                "key": composite_key,
                "manga_path": manga_path,
                "manga_name": group_data["manga_name"],
                "translator_type": translator_type,
                "cached_pages_count": len(page_indices),
                "first_page": page_indices[0] if page_indices else -1,
                "last_page": page_indices[-1] if page_indices else -1,
                "last_accessed": group_data["last_accessed"],
                "value_preview": f"漫画: {group_data['manga_name']} ({translator_type})"
            })
        
        # 4. 对聚合后的列表进行搜索过滤
        if search:
            query = search.lower()
            final_list = [
                entry for entry in final_list 
                if query in entry["manga_name"].lower() or query in entry["manga_path"].lower()
            ]

        # 5. 对最终列表进行分页
        total = len(final_list)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_list = final_list[start:end]

        return {
            "entries": paginated_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
        }

    except Exception as e:
        self.log.error(f"聚合获取持久化翻译缓存条目失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取缓存条目失败: {e}")
```

#### 步骤 2.1.2: 修改 `delete_entry` 方法

修改此方法以正确解析前端传来的复合键，并调用一个更精确的核心删除方法。

**重要提示**: 此步骤**需要您在 `core.persistent_translation_cache.PersistentTranslationCache` 中实现一个名为 `delete_by_manga_and_translator` 的新方法**，该方法接受 `manga_path` 和 `translator_type` 作为参数。

```python
# 在 PersistentTranslationCacheHandler 类中
async def delete_entry(self, key: str) -> Dict[str, Any]:
    """删除持久化翻译缓存中的一个聚合条目"""
    try:
        if ":::" not in key:
            raise ValueError("无效的缓存键格式，无法解析。")
        manga_path, translator_type = key.split(":::", 1)

        # 检查核心管理器中是否存在所需的方法
        if not hasattr(self.manager, 'delete_by_manga_and_translator'):
            self.log.error("核心缓存管理器 'PersistentTranslationCache' 缺少 'delete_by_manga_and_translator' 方法。")
            raise NotImplementedError("后端核心功能不支持按翻译引擎精确删除。")

        # 调用核心删除方法
        deleted_count = self.manager.delete_by_manga_and_translator(manga_path, translator_type)
        return {"success": True, "message": f"成功删除 {deleted_count} 个相关缓存条目。"}

    except (ValueError, NotImplementedError) as e:
        self.log.warning(f"删除操作失败 (客户端错误): {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        self.log.error(f"删除持久化翻译缓存聚合条目时发生意外错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"服务器内部错误，删除失败: {e}")
```

---

## 3. 任务二 & 三: UI 筛选功能 (前端实现)

**目标**: 在“翻译缓存”和“漫画列表”视图中，增加开关以实现客户端的快速内容筛选。

### 3.1 JavaScript 修改 (`web/static/js/cache-management.js`)

**文件**: `web/static/js/cache-management.js`

#### 步骤 3.1.1: 增加新的状态变量

在 `data` 对象中（通常由 `Vue.createApp` 的 `data()` 方法返回），增加两个用于控制筛选的布尔值。

```javascript
// 在 data() 返回的对象中
showOnlySensitive: false, // 用于翻译缓存
showOnlyUnlikelyManga: false, // 用于漫画列表
```

#### 步骤 3.1.2: 增强 `filterCacheEntries` 函数

这是实现所有前端筛选的核心。用以下版本替换现有的 `filterCacheEntries` 函数。

```javascript
filterCacheEntries() {
    let entries = this.cacheEntries; // 从完整列表开始

    // === 阶段1: 应用特定类型的过滤器 ===

    // -> 翻译缓存: 仅显示敏感内容
    if (this.selectedCacheType === 'translation' && this.showOnlySensitive) {
        entries = entries.filter(entry => entry.is_sensitive === true);
    }

    // -> 漫画列表: 仅显示可能非漫画项
    if (this.selectedCacheType === 'manga_list' && this.showOnlyUnlikelyManga) {
        // 重要: is_likely_manga 必须明确为 false 才被视为“非漫画”。
        // 这将自动忽略值为 null 或 undefined 的“未分析”条目。
        entries = entries.filter(entry => entry.is_likely_manga === false);
    }

    // === 阶段2: 应用全局搜索查询 ===
    if (this.cacheSearchQuery) {
        const query = this.cacheSearchQuery.toLowerCase();
        entries = entries.filter(entry =>
            (entry.key && String(entry.key).toLowerCase().includes(query)) ||
            (entry.value_preview && String(entry.value_preview).toLowerCase().includes(query))
        );
    }

    this.filteredCacheEntries = entries;
},
```

#### 步骤 3.1.3: 确保状态重置

在切换缓存类型时，应重置筛选开关的状态，以避免在不适用的类型上保留筛选。

```javascript
// 修改 selectCacheType 函数
async selectCacheType(cacheType) {
    this.selectedCacheType = cacheType;
    this.currentPage = 1;
    this.cacheSearchQuery = '';

    // 新增：重置筛选状态
    this.showOnlySensitive = false;
    this.showOnlyUnlikelyManga = false;
    
    await this.loadCacheEntries();
},
```

### 3.2 HTML 视图修改 (`web/templates/components/pages/cache-management.html`)

**文件**: `web/templates/components/pages/cache-management.html`

#### 步骤 3.2.1: 为聚合后的持久化缓存添加专用列

```html
<!-- 在 thead 中 -->
<template v-if="selectedCacheType === 'persistent_translation'">
    <th class="cache-table-header-cell">翻译引擎</th>
    <th class="cache-table-header-cell">缓存页数</th>
    <th class="cache-table-header-cell">页面范围</th>
    <th class="cache-table-header-cell">最后访问</th>
</template>

<!-- 在 tbody 的 v-for 中 -->
<template v-if="selectedCacheType === 'persistent_translation'">
    <td class="cache-table-cell">
        <el-tag size="small" type="success">{{ entry.translator_type }}</el-tag>
    </td>
    <td class="cache-table-cell">{{ entry.cached_pages_count }}</td>
    <td class="cache-table-cell">
        <span v-if="entry.cached_pages_count > 0">
            第{{ entry.first_page + 1 }} - {{ entry.last_page + 1 }}页
        </span>
        <span v-else>无</span>
    </td>
    <td class="cache-table-cell">{{ formatDateTime(entry.last_accessed) }}</td>
</template>
```

#### 步骤 3.2.2: 在操作栏添加筛选开关

在 `<div class="md-card-actions">` 内，添加以下 `<template>` 块。

```html
<!-- 用于“翻译”缓存的筛选开关 -->
<template v-if="selectedCacheType === 'translation'">
    <el-switch
        v-model="showOnlySensitive"
        @change="filterCacheEntries"
        active-text="仅显示敏感内容"
        style="margin-left: 16px; --el-switch-on-color: #E6A23C;">
    </el-switch>
</template>

<!-- 用于“漫画列表”的筛选开关 -->
<template v-if="selectedCacheType === 'manga_list'">
    <el-switch
        v-model="showOnlyUnlikelyManga"
        @change="filterCacheEntries"
        active-text="仅显示可能非漫画项"
        style="margin-left: 16px; --el-switch-on-color: #F56C6C;">
    </el-switch>
</template>
```
**原因**: 使用 `el-switch` 并将其 `@change` 事件绑定到 `filterCacheEntries` 方法，提供了一个即时反馈的用户界面。当用户拨动开关时，表格内容会立即根据新的筛选条件重新渲染，体验流畅。

---
此 V3.0 计划现已完整，覆盖了后端数据处理的优化和前端用户体验的增强，是您进行下一步开发的坚实基础。