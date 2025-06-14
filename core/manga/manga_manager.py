# core/manga_manager.py

import os
from PySide6.QtCore import QObject, Signal  # 导入 PySide6 的信号
from core.manga.manga_model import MangaInfo, MangaLoader
from core.config import config
from utils import manga_logger as log
from core.translation.translator import TranslatorFactory
from core.core_cache.cache_factory import get_cache_factory_instance # Added
from core.core_cache.cache_interface import CacheInterface # Added


class MangaManager(QObject):
    # 信号定义
    data_loaded = Signal(list)
    data_loading = Signal()
    data_load_failed = Signal(str)
    tags_updated = Signal(set)

    filter_applied = Signal(list)
    filter_cleared = Signal()
    file_renamed = Signal(str, str)
    file_opened = Signal(str)
    dir_changed = Signal(str)

    current_manga_changed = Signal(object)
    view_mode_changed = Signal(int)
    page_changed = Signal(int)
    manga_list_updated = Signal(list)
    tags_cleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        import inspect
        caller_frame = inspect.currentframe().f_back
        caller_info = inspect.getframeinfo(caller_frame)
        log.info(f"MangaManager初始化 - 调用者: {caller_info.filename}:{caller_info.lineno} 函数: {caller_info.function}")
        if self.parent: # Check if parent exists
             log.info(f"父类类型: {self.parent.__class__}")
        else:
            log.info("MangaManager 没有父对象")


        self.manga_list_cache_manager: CacheInterface = get_cache_factory_instance().get_manager("manga_list")
        self.translation_cache_manager: CacheInterface = get_cache_factory_instance().get_manager("translation")
        # self.ocr_cache_manager: CacheInterface = get_cache_factory_instance().get_manager("ocr") # If needed directly

        self.manga_list = []
        self.tags = set()
        self.current_manga = None

        log.info(
            f"MangaManager初始化完成，最新目录: {config.manga_dir.value}, 漫画数量: {len(self.manga_list)}"
        )

    def set_manga_dir(self, dir_path, force_rescan=False):
        log.info(f"设置漫画目录: {dir_path}")
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            config.manga_dir.value = dir_path  # 设置 config 值时使用 .value
            self.save_config()
            log.info(f"目录有效，开始扫描漫画文件")
            self.scan_manga_files(force_rescan=force_rescan)
            self.dir_changed.emit(config.manga_dir.value)  # 发送信号时使用 .value
        else:
            log.warning(f"目录无效或不存在: {dir_path}")
            
    def save_config(self):
        """保存配置到文件"""
        try:
            config.save()
            log.info("配置已保存")
        except Exception as e:
            log.error(f"保存配置时发生错误: {str(e)}")
            
    def create_translator(self):
        """根据配置创建翻译器实例"""
        try:
            translator_type = config.translator_type.value
            log.info(f"创建翻译器: {translator_type}")
            
            if translator_type == "智谱":
                return TranslatorFactory.create_translator(
                    translator_type=translator_type,
                    api_key=config.zhipu_api_key.value,
                    model=config.zhipu_model.value
                )
            elif translator_type == "Google":
                return TranslatorFactory.create_translator(
                    translator_type=translator_type,
                    api_key=config.google_api_key.value
                )
            else:
                log.warning(f"未知的翻译器类型: {translator_type}，使用Google翻译作为默认选项")
                return TranslatorFactory.create_translator("Google")
        except Exception as e:
            log.error(f"创建翻译器时发生错误: {str(e)}，使用Google翻译作为备选")
            return TranslatorFactory.create_translator("Google")
            
    def clear_translation_cache(self):
        """清空翻译缓存"""
        try:
            self.translation_cache_manager.clear()
            log.info("翻译缓存已通过 TranslationCacheManager 清空")
            # 移除旧的兼容代码，因为它直接操作文件，与新管理器冲突
        except Exception as e:
            log.error(f"通过 TranslationCacheManager 清空翻译缓存时发生错误: {str(e)}")
            
    def clear_manga_cache(self):
        """清空漫画扫描缓存"""
        try:
            self.manga_list_cache_manager.clear()
            log.info("漫画扫描缓存已通过 MangaListCacheManager 清空")
        except Exception as e:
            log.error(f"通过 MangaListCacheManager 清空漫画扫描缓存时发生错误: {str(e)}")

    def clear_all_data(self):
        """清空所有加载的漫画数据和缓存"""
        log.info("开始清空所有漫画数据和缓存")
        self.manga_list.clear()
        self.tags.clear()
        self.current_manga = None
        
        # 清空配置中的目录和当前漫画路径
        config.manga_dir.value = ""
        config.current_manga_path.value = ""
        config.current_page.value = 0
        self.save_config()

        # 清空缓存
        self.clear_manga_cache()
        self.clear_translation_cache()
        

        # 发送信号通知UI更新
        self.filter_applied.emit([])
        self.tags_cleared.emit() # 发送标签清空信号
        log.info("所有漫画数据和缓存已清空")

    def scan_manga_files(self, force_rescan=False):
        # 访问 config 值时使用 .value
        if not config.manga_dir.value:
            log.warning("未设置漫画目录，无法扫描文件")
            return

        self.data_loading.emit()
        # self.manga_list.clear() # 移除此行
        # self.tags.clear() # 移除此行

        try:
            # 使用新的 MangaListCacheManager
            cache_key = self.manga_list_cache_manager.generate_key(config.manga_dir.value)
            
            cached_manga_data_list = None
            if not force_rescan:
                cached_manga_data_list = self.manga_list_cache_manager.get(cache_key)
            
            current_scan_mangas = []
            if cached_manga_data_list and not force_rescan:
                log.info(f"从缓存加载漫画列表数据，共 {len(cached_manga_data_list)} 条记录")
                
                for manga_data in cached_manga_data_list:
                    file_path = manga_data.get("file_path")
                    if not file_path:
                        log.warning(f"缓存数据中缺少 file_path: {manga_data.get('title', 'N/A')}")
                        continue

                    # is_manga_modified is now part of MangaListCacheManager
                    if os.path.exists(file_path):
                        try:
                            manga = MangaInfo(file_path) # Recreate MangaInfo from path
                            manga.title = manga_data.get("title", os.path.basename(file_path))
                            manga.tags = set(manga_data.get("tags", []))
                            manga.total_pages = manga_data.get("total_pages", 0)
                            manga.is_valid = manga_data.get("is_valid", False) # Rely on cached validity
                            manga.last_modified = manga_data.get("last_modified", 0)
                            manga.pages = manga_data.get("pages", []) # Assuming pages are serializable
                            # manga.is_translated = manga_data.get("is_translated", False) # If this field is used

                            # 恢复页面尺寸分析数据
                            manga.page_dimensions = manga_data.get("page_dimensions", [])
                            manga.dimension_variance = manga_data.get("dimension_variance", None)
                            manga.is_likely_manga = manga_data.get("is_likely_manga", None)
                            if manga.is_valid: # Double check validity if needed, or trust cache
                                current_scan_mangas.append(manga)
                            else:
                                log.warning(f"从缓存加载的漫画 {file_path} 无效，将尝试重新加载。")
                                fresh_manga = MangaLoader.load_manga(file_path)
                                if fresh_manga and fresh_manga.is_valid:
                                    current_scan_mangas.append(fresh_manga)
                        except Exception as e_load:
                            log.error(f"从缓存数据创建 MangaInfo 对象失败 ({file_path}): {e_load}, 将尝试重新加载。")
                            fresh_manga = MangaLoader.load_manga(file_path)
                            if fresh_manga and fresh_manga.is_valid:
                                current_scan_mangas.append(fresh_manga)
                    else:
                        log.info(f"漫画文件不存在于缓存: {file_path}，将重新加载。")
                        manga = MangaLoader.load_manga(file_path)
                        if manga and manga.is_valid:
                            current_scan_mangas.append(manga)
                        else:
                            log.warning(f"无法加载漫画: {file_path}")
            else:
                log.info(f"开始扫描漫画目录 (无缓存或强制重新扫描): {config.manga_dir.value}")
                manga_files = MangaLoader.find_manga_files(config.manga_dir.value)

                for file_path_scan in manga_files:
                    # 根据配置决定是否进行尺寸分析
                    analyze_dimensions = config.enable_dimension_analysis.value
                    manga = MangaLoader.load_manga(file_path_scan, analyze_dimensions=analyze_dimensions)

                    if manga and manga.is_valid:
                        # 根据配置决定是否过滤非漫画文件
                        if config.filter_non_manga.value and manga.is_likely_manga is not None:
                            if not manga.is_likely_manga:
                                log.info(f"根据尺寸分析过滤非漫画文件: {file_path_scan} "
                                        f"(方差分数: {manga.dimension_variance:.3f})")
                                continue

                        current_scan_mangas.append(manga)
                    else:
                        log.warning(f"无法加载漫画: {file_path_scan}")
            
            # 更新缓存，只缓存当前目录的漫画
            # The `set` method of MangaListCacheManager expects a list of manga objects
            # or serializable dicts. current_scan_mangas contains MangaInfo objects.
            # The MangaListCacheManager's set method should handle serialization.
            self.manga_list_cache_manager.set(cache_key, current_scan_mangas)

            # 合并新扫描到的漫画到主列表，并去重
            existing_manga_paths = {manga.file_path for manga in self.manga_list}
            
            for manga in current_scan_mangas:
                if manga.file_path not in existing_manga_paths:
                    self.manga_list.append(manga)
                    existing_manga_paths.add(manga.file_path) 

            log.info(f"扫描完成，当前共加载 {len(self.manga_list)} 本漫画")

            # 重新收集所有漫画的标签
            self.tags.clear() # 每次扫描后重新收集所有标签
            for manga in self.manga_list:
                self.tags.update(manga.tags)

            log.info(f"标签收集完成，共收集 {len(self.tags)} 个标签")

            self.data_loaded.emit(self.manga_list)
            self.tags_updated.emit(self.tags)
            self.filter_manga([])

            # 恢复上次阅读状态
            # 访问 config 值时使用 .value
            if config.current_manga_path.value and os.path.exists(
                config.current_manga_path.value
            ):
                # 访问 config 值时使用 .value
                found_manga = next(
                    (
                        m
                        for m in self.manga_list
                        if m.file_path == config.current_manga_path.value
                    ),
                    None,
                )
                if found_manga:
                    self.set_current_manga(found_manga)
                    # 访问 config 值时使用 .value
                    self.change_page(config.current_page.value)

        except Exception as e:
            error_msg = f"扫描漫画文件时发生错误: {str(e)}"
            log.error(error_msg)
            self.data_load_failed.emit(error_msg)

    def change_page(self, page_number):
        if self.current_manga is None:
            log.warning("未选择漫画，无法改变页码")
            return

        total_pages = len(self.current_manga.pages) if self.current_manga.pages else 0
        if 0 <= page_number < total_pages:
            config.current_page.value = page_number  # 设置 config 值时使用 .value
            # self.current_page = page_number # 移除了 MangaManager 自身的页码属性
            self.page_changed.emit(page_number)
        else:
            log.warning(f"页码超出范围: {page_number + 1}, 总页数: {total_pages}")

    def filter_manga(self, tag_filters):
        if not tag_filters:
            self.filter_cleared.emit()
            self.filter_applied.emit(self.manga_list)
            return self.manga_list

        log.info(f"开始按标签过滤漫画，过滤标签: {tag_filters}")
        filtered_list = []
        for manga in self.manga_list:
            match = True
            for tag in tag_filters:
                if tag not in manga.tags:
                    match = False
                    break
            if match:
                filtered_list.append(manga)

        log.info(
            f"过滤完成，从 {len(self.manga_list)} 本漫画中筛选出 {len(filtered_list)} 本"
        )
        self.filter_applied.emit(filtered_list)
        return filtered_list

    def translate_titles(self):
        if not config.translate_title.value:  # 访问 config 值时使用 .value
            return

        import zhconv

        log.info("开始翻译作品名和标题")
        for manga in self.manga_list:
            if manga.title:
                manga.title = zhconv.convert(manga.title, "zh-hans")
        log.info("作品名和标题翻译完成")

    def analyze_manga_dimensions(self, force_reanalyze: bool = False):
        """
        为需要的ZIP漫画进行尺寸分析（只分析ZIP文件，文件夹漫画不需要分析）

        Args:
            force_reanalyze: 是否强制重新分析（即使已有分析结果）
        """
        from core.manga.manga_model import MangaLoader
        import os

        # 筛选需要分析的ZIP漫画（排除文件夹）
        need_analysis = []
        for manga in self.manga_list:
            # 只分析ZIP文件，跳过文件夹
            if os.path.isdir(manga.file_path):
                continue
            if force_reanalyze or manga.dimension_variance is None:
                need_analysis.append(manga)

        # DEBUG: 检查漫画列表中的方差数据
        zip_count = 0
        analyzed_count = 0
        for manga in self.manga_list[:10]:  # 只检查前10个
            if not os.path.isdir(manga.file_path):
                zip_count += 1
                if manga.dimension_variance is not None:
                    analyzed_count += 1
                log.debug(f"DEBUG ZIP漫画: {os.path.basename(manga.file_path)}, 方差={manga.dimension_variance}, 类型={type(manga.dimension_variance)}")

        log.info(f"DEBUG 统计: 前10个中有{zip_count}个ZIP文件，其中{analyzed_count}个已分析")

        if not need_analysis:
            log.info("所有ZIP漫画都已有尺寸分析数据，无需重新分析")
            return 0

        total_zip_count = len([m for m in self.manga_list if not os.path.isdir(m.file_path)])
        log.info(f"开始为 {len(need_analysis)} 本ZIP漫画进行尺寸分析（总共 {total_zip_count} 本ZIP漫画）")

        analyzed_count = 0
        failed_count = 0

        for i, manga in enumerate(need_analysis):
            try:
                log.info(f"正在分析 ({i+1}/{len(need_analysis)}): {manga.title}")

                # 调用MangaLoader的尺寸分析方法
                MangaLoader._analyze_manga_dimensions(manga)
                analyzed_count += 1

                log.debug(f"完成尺寸分析: {manga.file_path}, "
                         f"方差分数={manga.dimension_variance:.3f}, "
                         f"可能是漫画={manga.is_likely_manga}")

            except Exception as e:
                log.error(f"尺寸分析失败 {manga.file_path}: {e}")
                failed_count += 1
                # 设置默认值，避免重复分析
                manga.dimension_variance = 0.0
                manga.is_likely_manga = True

        log.info(f"尺寸分析完成: 成功分析 {analyzed_count} 本，失败 {failed_count} 本")

        # 更新缓存（保存分析结果）
        if analyzed_count > 0:
            try:
                from core.config import config
                cache_key = self.manga_list_cache_manager.generate_key(config.manga_dir.value)
                self.manga_list_cache_manager.set(cache_key, self.manga_list)
                log.info("已保存尺寸分析结果到缓存")
            except Exception as e:
                log.warning(f"保存尺寸分析结果到缓存失败: {e}")

        return analyzed_count

    def optimize_tags(self):
        if not config.simplify_chinese.value:  # 访问 config 值时使用 .value
            return

        import zhconv

        for manga in self.manga_list:
            simplified_tags = set()
            for tag in manga.tags:
                simplified_tag = zhconv.convert(tag, "zh-hans")
                simplified_tags.add(simplified_tag)
            manga.tags = simplified_tags

    def analyze_and_merge_tags(self, similarity_threshold=0.9):
        if not config.merge_tags.value:  # 访问 config 值时使用 .value
            return

        from difflib import SequenceMatcher

        for manga in self.manga_list:
            tags_list = list(manga.tags)
            merged_tags = set()
            while tags_list:
                current_tag = tags_list.pop(0)
                merged = False
                if current_tag.startswith(("作者", "作品", "汉化")):
                    for merged_tag in merged_tags:
                        similarity = SequenceMatcher(
                            None, current_tag, merged_tag
                        ).ratio()
                        if similarity >= similarity_threshold:
                            merged = True
                            break
                if not merged:
                    merged_tags.add(current_tag)
            manga.tags = merged_tags

    def save_config(self):
        log.info(f"保存配置到文件: {config.config_file}")
        try:
            # 调用 config.save 方法保存所有 ConfigItem
            config.save()
            log.info("配置保存成功")
        except Exception as e:
            log.error(f"保存配置文件失败: {e}")

    def rename_manga_file(self, manga, new_name):
        log.info(f"尝试重命名漫画: {manga.title} -> {new_name}")
        if not manga or not manga.file_path or not os.path.exists(manga.file_path):
            log.error("无效的漫画对象或文件不存在")
            return False

        try:
            file_dir = os.path.dirname(manga.file_path)
            file_ext = os.path.splitext(manga.file_path)[1]
            new_file_path = os.path.join(file_dir, new_name + file_ext)

            if os.path.exists(new_file_path):
                log.error(f"文件已存在，无法重命名: {new_file_path}")
                return False

            os.rename(manga.file_path, new_file_path)
            old_title = manga.title
            manga.title = new_name
            manga.file_path = new_file_path

            log.info(f"漫画重命名成功: {old_title} -> {manga.title}")
            self.file_renamed.emit(manga.file_path, new_file_path)

            if self.current_manga == manga:
                config.current_manga_path.value = (
                    new_file_path  # 设置 config 值时使用 .value
                )
                self.save_config()

            return True
        except Exception as e:
            log.error(f"重命名漫画时发生错误: {str(e)}")
            return False

    def set_current_manga(self, manga):
        if manga != self.current_manga:
            log.info(f"切换当前漫画: {manga.title if manga else 'None'}")
            
            # 检查漫画文件是否存在，如果不存在则更新漫画列表
            if manga and not os.path.exists(manga.file_path):
                log.warning(f"漫画文件不存在: {manga.file_path}，将从列表中移除")
                self.manga_list = [m for m in self.manga_list if m.file_path != manga.file_path]
                # 更新缓存
                cache_key_update = self.manga_list_cache_manager.generate_key(config.manga_dir.value)
                self.manga_list_cache_manager.set(cache_key_update, self.manga_list)
                self.current_manga = None
                config.current_manga_path.value = ""
                self.current_manga_changed.emit(None)
                return
            
            # 检查漫画文件是否被修改，如果被修改则重新加载
            if manga:
                # is_manga_modified is now part of MangaListCacheManager
                if self.manga_list_cache_manager.is_manga_modified(manga.file_path):
                    log.info(f"漫画文件已修改，重新加载: {manga.file_path}")
                    updated_manga = MangaLoader.load_manga(manga.file_path)
                    if updated_manga and updated_manga.is_valid:
                        # 更新列表中的漫画对象
                        for i, m_loop in enumerate(self.manga_list): # Renamed m to m_loop to avoid conflict
                            if m_loop.file_path == manga.file_path:
                                self.manga_list[i] = updated_manga
                                manga = updated_manga # Update the manga variable being processed
                                break
                        # 更新缓存
                        cache_key_update_modified = self.manga_list_cache_manager.generate_key(config.manga_dir.value)
                        self.manga_list_cache_manager.set(cache_key_update_modified, self.manga_list)
            
            self.current_manga = manga
            config.current_manga_path.value = (
                manga.file_path if manga else ""
            )  # 设置 config 值时使用 .value
            # 调用 change_page，change_page 会负责更新 config.current_page
            self.change_page(0)
            self.current_manga_changed.emit(manga)

    def set_current_manga_by_path(self, file_path):
        found_manga = next(
            (m for m in self.manga_list if m.file_path == file_path), None
        )
        if found_manga:
            self.set_current_manga(found_manga)
            # 访问 config 值时使用 .value
            self.change_page(config.current_page.value)

    def clear_manga_cache(self):
        """清空漫画列表缓存"""
        try:
            cache_key = self.manga_list_cache_manager.generate_key(config.manga_dir.value)
            self.manga_list_cache_manager.delete(cache_key)
            log.info("漫画列表缓存已清空")
        except Exception as e:
            log.error(f"清空漫画列表缓存失败: {e}")
            raise
