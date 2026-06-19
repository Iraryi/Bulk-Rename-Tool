from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, VERTICAL, filedialog, messagebox
import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk


APP_NAME = "批量改名"
INVALID_CHARS = r'<>:"/\|?*'
HISTORY_PREFIX = ".bulk_rename_history_"
PORTABLE_MARKER = "portable.mode"


def app_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def preset_base_dir() -> Path:
    base = app_base_dir()
    if (base / PORTABLE_MARKER).exists():
        return base / "BulkRenameData"
    return Path.home() / "Documents" / "批量改名预设"


PRESET_DIR = preset_base_dir()
FILTER_PRESET_DIR = PRESET_DIR / "筛选预设"
LAST_SESSION_PATH = PRESET_DIR / "last_session.json"


EN_TEXT = {
    "批量改名": "Bulk Rename",
    "扫描路径": "Folder",
    "选择": "Browse",
    "选择要扫描的文件夹": "Choose a folder to scan",
    "预览": "Preview",
    "包含子文件夹": "Include subfolders",
    "包含隐藏项": "Include hidden items",
    "对象": "Target",
    "文件": "Files",
    "文件夹": "Folders",
    "筛选": "Filter",
    "编辑所有模式都会使用的筛选条件。": "Edit filters used by every rename mode.",
    "选择要批量处理的文件夹。": "Choose the folder to scan.",
    "扫描当前路径并在右侧显示改名前后的对照。": "Scan the current folder and show before/after names on the right.",
    "返回主界面": "Back",
    "返回任务选择，不改变当前规则。": "Return to task selection without changing rules.",
    "选择要完成的任务": "Choose a task",
    "普通重命名": "Text Rename",
    "编号模板": "Numbered Template",
    "扩展名修改": "Extension Change",
    "名称清理": "Name Cleanup",
    "设置": "Settings",
    "批量查找替换、删除指定文字、加前缀/后缀。": "Find/replace, remove text, and add prefixes or suffixes.",
    "把文件按时间、名称、大小等顺序排列，再生成 XXX_#NUM# 或 #DATE#_#NUM#。": "Sort by time, name, size, etc., then generate names like XXX_#NUM# or #DATE#_#NUM#.",
    "批量把 .jpeg 改成 .jpg、统一扩展名大小写，或移除扩展名。": "Change .jpeg to .jpg, normalize extension case, or remove extensions.",
    "批量清理多余空格、统一大小写、空格/下划线/短横线风格。": "Clean spaces, normalize case, and convert spaces/underscores/hyphens.",
    "管理全局筛选、预设、日期格式、安全策略和变量说明。": "Manage global filters, presets, date formats, safety, and variable help.",
    "查找": "Find",
    "替换为": "Replace with",
    "正则表达式": "Regular expression",
    "区分大小写": "Case sensitive",
    "删除文字": "Remove text",
    "删除位置": "Remove positions",
    "前缀": "Prefix",
    "后缀": "Suffix",
    "名称模板": "Name template",
    "排序": "Sort",
    "启用编号 #NUM#": "Enable #NUM#",
    "起始": "Start",
    "步长": "Step",
    "位数": "Digits",
    "添加编号": "Add number",
    "位置": "Position",
    "处理方式": "Action",
    "自定义扩展名": "Custom extension",
    "把多段扩展名作为整体保留": "Keep multi-part extensions together",
    "适合场景": "Useful for",
    "例如把 .jpeg 批量改为 .jpg，把 .TXT 统一为 .txt，或移除临时扩展名。": "For example, change .jpeg to .jpg, normalize .TXT to .txt, or remove temporary extensions.",
    "去掉首尾空格": "Trim leading/trailing spaces",
    "合并连续空格": "Collapse repeated spaces",
    "大小写": "Case",
    "分隔符": "Separators",
    "筛选/预设": "Filters/Presets",
    "日期/扩展名": "Date",
    "安全": "Safety",
    "变量说明": "Variables",
    "日期": "Date",
    "变量": "Variables",
    "保存筛选预设": "Save filter preset",
    "加载筛选预设": "Load filter preset",
    "保存整套预设": "Save full preset",
    "加载整套预设": "Load full preset",
    "只保存筛选条件，不保存当前重命名规则。": "Save only filter rules, not rename rules.",
    "只加载筛选条件，不覆盖当前输出任务。": "Load only filter rules without changing the current task.",
    "保存当前任务、筛选、日期、扩展名和安全策略。": "Save the current task, filters, dates, extension rules, and safety settings.",
    "加载一个完整方案。": "Load a complete preset.",
    "按当前排序生成的编号": "Number generated from the current sort order",
    "按 SETTING 中日期来源和日期格式生成": "Generated from the date source and format in Settings",
    "当前任务中的基础名称": "Base name in the current task",
    "文件原始名称，不含扩展名": "Original file name without extension",
    "扩展名，不含点": "Extension without the dot",
    "父文件夹名称": "Parent folder name",
    "文件修改时间": "Modified time",
    "文件创建时间": "Created time",
    "今天的日期": "Today's date",
    "日期来源": "Date source",
    "日期格式": "Date format",
    "说明": "Note",
    "这里定义 #DATE#、#MTIME#、#CTIME# 等日期变量的格式。真正更改扩展名请回主界面选择“扩展名修改”。": "This defines the format for #DATE#, #MTIME#, #CTIME#, and similar date variables. To change extensions, choose Extension Change from the main screen.",
    "自动替换非法字符": "Replace invalid characters",
    "重名处理": "Duplicate handling",
    "重新预览": "Refresh preview",
    "清空规则": "Clear rules",
    "撤销上次": "Undo last",
    "状态": "Status",
    "原名称": "Original name",
    "新名称": "New name",
    "所在文件夹": "Folder",
    "执行改名": "Rename",
    "请选择文件夹": "Choose a folder",
    "文件类型": "File types",
    "通配符": "Wildcards",
    "包含文字": "Contains text",
    "排除通配符": "Exclude wildcards",
    "排除文字": "Exclude text",
    "排除扩展名": "Exclude extensions",
    "排除文件夹": "Exclude folders",
    "填写方式": "How to fill",
    "多个条件用逗号或分号分隔。通配符可写 *.tmp、backup*、*/skip/*；排除文件夹可写 temp 或 */temp。": "Separate multiple rules with commas or semicolons. Wildcards can be *.tmp, backup*, */skip/*; folders can be temp or */temp.",
    "清空筛选": "Clear filters",
    "应用并预览": "Apply and preview",
    "只清空筛选条件，不影响当前重命名规则。": "Clear only filters, not rename rules.",
    "只加载筛选条件，不覆盖重命名模板、编号和扩展名设置。": "Load only filters without overwriting templates, numbering, or extension settings.",
    "把当前筛选条件保存起来，下次可以在任何任务中复用。": "Save current filters for reuse in any task.",
    "关闭窗口并刷新右侧预览。": "Close this window and refresh the preview.",
    "预设名称：": "Preset name:",
    "筛选预设名称：": "Filter preset name:",
    "加载预设": "Load preset",
    "导入预设": "Import preset",
    "JSON 预设": "JSON preset",
    "所有文件": "All files",
    "请选择一个存在的文件夹": "Please choose an existing folder",
    "未变化": "Unchanged",
    "就绪": "Ready",
    "错误": "Error",
    "冲突": "Conflict",
    "有 {count} 项需要处理": "{count} item(s) need attention",
    "预览已更新": "Preview updated",
    "{total} 项，{changed} 项将改名": "{total} item(s), {changed} will be renamed",
    "仍有冲突或错误，请先处理预览中的提示。": "There are still conflicts or errors. Please fix the preview warnings first.",
    "没有需要改名的项目。": "No items need renaming.",
    "确认改名 {count} 项？": "Rename {count} item(s)?",
    "已完成 {count} 项，撤销记录已保存": "Renamed {count} item(s); undo history saved",
    "改名完成。": "Rename complete.",
    "请先选择文件夹。": "Please choose a folder first.",
    "没有找到可撤销的记录。": "No undo history was found.",
    "撤销记录：{name}？": "Undo history: {name}?",
    "已撤销上次改名": "Last rename was undone",
    "撤销完成。": "Undo complete.",
    "已保存预设：{name}": "Saved preset: {name}",
    "已保存筛选预设：{name}": "Saved filter preset: {name}",
    "已恢复上次配置，点击预览开始扫描": "Last settings restored. Click Preview to scan.",
    "语言": "Language",
    "界面语言": "Interface language",
    "应用语言": "Apply language",
    "语言设置通常只需要修改一次。": "Language is usually changed only once.",
    "中文": "Chinese",
    "英语": "English",
    "首次使用请选择界面语言": "Choose interface language for first use",
    "以后可在“设置 > 语言”中修改。": "You can change this later in Settings > Language.",
    "名称 A-Z": "Name A-Z",
    "名称 Z-A": "Name Z-A",
    "修改时间 旧->新": "Modified old->new",
    "修改时间 新->旧": "Modified new->old",
    "创建时间 旧->新": "Created old->new",
    "创建时间 新->旧": "Created new->old",
    "文件大小 小->大": "Size small->large",
    "文件大小 大->小": "Size large->small",
    "扩展名 A-Z": "Extension A-Z",
    "扩展名 Z-A": "Extension Z-A",
    "路径深度 浅->深": "Path depth shallow->deep",
    "路径深度 深->浅": "Path depth deep->shallow",
    "保留": "Keep",
    "小写": "Lowercase",
    "大写": "Uppercase",
    "自定义": "Custom",
    "移除": "Remove",
    "不处理": "Do not change",
    "全部小写": "All lowercase",
    "全部大写": "All uppercase",
    "首字母大写": "Capitalize",
    "单词首字母大写": "Title Case",
    "空格转下划线": "Spaces to underscores",
    "空格转短横线": "Spaces to hyphens",
    "下划线转空格": "Underscores to spaces",
    "短横线转空格": "Hyphens to spaces",
    "不添加": "Do not add",
    "开头": "Beginning",
    "结尾": "End",
    "修改时间": "Modified time",
    "创建时间": "Created time",
    "今天": "Today",
    "阻止": "Block",
    "自动追加序号": "Auto append number",
}

OPTION_TEXTS = {
    "文件", "文件夹", "名称 A-Z", "名称 Z-A", "修改时间 旧->新", "修改时间 新->旧", "创建时间 旧->新", "创建时间 新->旧",
    "文件大小 小->大", "文件大小 大->小", "扩展名 A-Z", "扩展名 Z-A", "路径深度 浅->深", "路径深度 深->浅",
    "保留", "小写", "大写", "自定义", "移除", "不处理", "全部小写", "全部大写", "首字母大写", "单词首字母大写",
    "空格转下划线", "空格转短横线", "下划线转空格", "短横线转空格", "不添加", "开头", "结尾",
    "修改时间", "创建时间", "今天", "阻止", "自动追加序号",
}
EN_TO_ZH = {english: chinese for chinese, english in EN_TEXT.items() if chinese in OPTION_TEXTS}


@dataclass
class RenameItem:
    path: Path
    kind: str


@dataclass
class PreviewItem:
    source: Path
    target: Path
    kind: str
    status: str
    message: str

    @property
    def changed(self) -> bool:
        return str(self.source) != str(self.target)

    @property
    def can_rename(self) -> bool:
        return self.status in {"就绪", "未变化"} and self.changed


class ToolTip:
    def __init__(self, widget: tk.Widget, text: str):
        self.widget = widget
        self.text = text
        self.window: tk.Toplevel | None = None
        self.after_id: str | None = None
        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._hide)
        widget.bind("<ButtonPress>", self._hide)

    def _schedule(self, _event=None) -> None:
        self.after_id = self.widget.after(450, self._show)

    def _show(self) -> None:
        if self.window or not self.text:
            return
        x = self.widget.winfo_rootx() + 18
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self.window = tk.Toplevel(self.widget)
        self.window.wm_overrideredirect(True)
        self.window.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(self.window, text=self.text, padding=(10, 7), wraplength=280)
        label.pack()

    def _hide(self, _event=None) -> None:
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        if self.window:
            self.window.destroy()
            self.window = None


class RenameEngine:
    def __init__(self, config: dict):
        self.config = config

    def scan(self) -> list[RenameItem]:
        root = Path(self.config["root"]).expanduser()
        if not root.exists() or not root.is_dir():
            raise ValueError("请选择一个存在的文件夹")

        recursive = self.config["recursive"]
        include_hidden = self.config["include_hidden"]
        item_kind = self.config["item_kind"]
        patterns = self._split_csv(self.config["patterns"])
        extensions = self._normal_extensions(self.config["extensions"])
        contains = self.config["contains"].strip()
        case_sensitive = self.config.get("case_sensitive", False)
        exclude_patterns = self._split_csv(self.config.get("exclude_patterns", ""))
        exclude_contains = self.config.get("exclude_contains", "").strip()
        exclude_extensions = self._normal_extensions(self.config.get("exclude_extensions", ""))
        exclude_folders = self._split_csv(self.config.get("exclude_folders", ""))

        paths: list[Path] = []
        if recursive:
            walker = os.walk(root)
            for current, dirs, files in walker:
                current_path = Path(current)
                if not include_hidden:
                    dirs[:] = [d for d in dirs if not self._is_hidden(current_path / d)]
                if exclude_folders:
                    dirs[:] = [d for d in dirs if not self._matches_any(d, exclude_folders) and not self._matches_any(str((current_path / d).relative_to(root)), exclude_folders)]
                names = files if item_kind == "文件" else dirs
                for name in names:
                    paths.append(current_path / name)
        else:
            for child in root.iterdir():
                if item_kind == "文件" and not child.is_file():
                    continue
                if item_kind == "文件夹" and not child.is_dir():
                    continue
                paths.append(child)

        items: list[RenameItem] = []
        for path in sorted(paths, key=lambda value: str(value).lower()):
            if not include_hidden and self._is_hidden(path):
                continue
            if contains and not self._text_contains(path.name, contains, case_sensitive):
                continue
            if patterns and not any(fnmatch.fnmatch(path.name, pattern) for pattern in patterns):
                continue
            if item_kind == "文件" and extensions:
                if path.suffix.lower().lstrip(".") not in extensions:
                    continue
            relative_text = str(path.relative_to(root))
            if exclude_contains and (self._text_contains(path.name, exclude_contains, case_sensitive) or self._text_contains(relative_text, exclude_contains, case_sensitive)):
                continue
            if exclude_patterns and (self._matches_any(path.name, exclude_patterns) or self._matches_any(relative_text, exclude_patterns)):
                continue
            if item_kind == "文件" and exclude_extensions:
                if path.suffix.lower().lstrip(".") in exclude_extensions:
                    continue
            items.append(RenameItem(path=path, kind=item_kind))
        return self._sort_items(items)

    def preview(self, items: list[RenameItem]) -> list[PreviewItem]:
        raw: list[PreviewItem] = []
        for index, item in enumerate(items):
            try:
                target_name = self.build_name(item.path, index)
                target = item.path.with_name(target_name)
                status = "未变化" if str(item.path) == str(target) else "就绪"
                raw.append(PreviewItem(item.path, target, item.kind, status, ""))
            except Exception as exc:
                raw.append(PreviewItem(item.path, item.path, item.kind, "错误", str(exc)))
        return self._resolve_conflicts(raw)

    def build_name(self, path: Path, index: int) -> str:
        original_name = path.name
        original_stem, original_ext = self._split_name(path)
        task_mode = self.config.get("task_mode") or ("template" if self.config["template"].strip() else "basic")
        name = original_stem

        number = self._number_for(index)
        date_text = self._date_for(path)

        if task_mode == "template":
            tokens = self._tokens(
                original=original_stem,
                name=original_stem,
                ext=original_ext.lstrip("."),
                number=number,
                date_text=date_text,
                path=path,
                index=index,
            )
            template = self.config["template"].strip() or "#NAME#"
            name = self._format_tokens(template, tokens)
        elif task_mode == "clean":
            if self.config["trim"]:
                name = name.strip()
            if self.config["collapse_spaces"]:
                name = re.sub(r"\s+", " ", name)
            if self.config["separator_style"] != "不处理":
                name = self._normalize_separators(name, self.config["separator_style"])
            name = self._apply_case(name, self.config["case_mode"])
        elif task_mode == "extension":
            name = original_stem
        else:
            find_text = self.config["find_text"]
            if find_text:
                flags = 0 if self.config["case_sensitive"] else re.IGNORECASE
                replace_text = self.config["replace_text"]
                if self.config["regex"]:
                    name = re.sub(find_text, replace_text, name, flags=flags)
                else:
                    name = self._plain_replace(name, find_text, replace_text, self.config["case_sensitive"])

            remove_text = self.config["remove_text"]
            if remove_text:
                for token in self._split_csv(remove_text):
                    name = self._plain_replace(name, token, "", self.config["case_sensitive"])

            if self.config["remove_range"]:
                name = self._remove_range(name, self.config["remove_range"])

            tokens = self._tokens(
                original=original_stem,
                name=name,
                ext=original_ext.lstrip("."),
                number=number,
                date_text=date_text,
                path=path,
                index=index,
            )
            prefix = self._format_tokens(self.config["prefix"], tokens)
            suffix = self._format_tokens(self.config["suffix"], tokens)
            name = f"{prefix}{name}{suffix}"

        ext = self._extension_for(original_ext) if task_mode == "extension" or not self.config.get("task_mode") else original_ext
        full = f"{name}{ext}"
        if self.config["clean_invalid"]:
            full = self._clean_filename(full)
        else:
            self._validate_filename(full)
        if not full:
            raise ValueError("新名称为空")
        if full in {".", ".."}:
            raise ValueError("新名称不可用")
        return full

    def _resolve_conflicts(self, items: list[PreviewItem]) -> list[PreviewItem]:
        mode = self.config["collision_mode"]
        occupied = {item.source.resolve().as_posix().lower() for item in items}
        proposed: set[str] = set()
        result: list[PreviewItem] = []

        for item in items:
            if item.status == "错误" or not item.changed:
                result.append(item)
                continue

            target = item.target
            key = target.resolve().as_posix().lower()
            external_exists = target.exists() and key not in occupied
            duplicate = key in proposed

            if not external_exists and not duplicate:
                proposed.add(key)
                result.append(item)
                continue

            if mode == "自动追加序号":
                target = self._next_available_name(target, occupied | proposed)
                proposed.add(target.resolve().as_posix().lower())
                result.append(PreviewItem(item.source, target, item.kind, "就绪", "已自动避开重名"))
            else:
                reason = "目标已存在" if external_exists else "预览中重名"
                result.append(PreviewItem(item.source, item.target, item.kind, "冲突", reason))
        return result

    def _next_available_name(self, path: Path, occupied: set[str]) -> Path:
        stem = path.stem
        suffix = path.suffix
        for counter in range(2, 10000):
            candidate = path.with_name(f"{stem} ({counter}){suffix}")
            key = candidate.resolve().as_posix().lower()
            if key not in occupied and not candidate.exists():
                return candidate
        raise ValueError("无法生成不重名的新名称")

    def _tokens(
        self,
        original: str,
        name: str,
        ext: str,
        number: str,
        date_text: str,
        path: Path,
        index: int,
    ) -> dict[str, str]:
        stat = path.stat()
        values = {
            "原名": original,
            "original": original,
            "name": name,
            "名称": name,
            "ext": ext,
            "扩展名": ext,
            "num": number,
            "编号": number,
            "date": date_text,
            "日期": date_text,
            "parent": path.parent.name,
            "父文件夹": path.parent.name,
            "index": str(index + 1),
            "序号": str(index + 1),
            "mtime": datetime.fromtimestamp(stat.st_mtime).strftime(self.config["date_format"]),
            "修改时间": datetime.fromtimestamp(stat.st_mtime).strftime(self.config["date_format"]),
            "ctime": datetime.fromtimestamp(stat.st_ctime).strftime(self.config["date_format"]),
            "创建时间": datetime.fromtimestamp(stat.st_ctime).strftime(self.config["date_format"]),
            "today": datetime.now().strftime(self.config["date_format"]),
            "今天": datetime.now().strftime(self.config["date_format"]),
        }
        values.update({key.upper(): value for key, value in values.items() if key.isascii()})
        return values

    def _format_tokens(self, value: str, tokens: dict[str, str]) -> str:
        if not value:
            return ""

        lookup = {key.lower(): text for key, text in tokens.items()}

        def replace_brace(match: re.Match[str]) -> str:
            key = match.group(1)
            return tokens.get(key, lookup.get(key.lower(), match.group(0)))

        def replace_hash(match: re.Match[str]) -> str:
            key = match.group(1)
            return tokens.get(key, lookup.get(key.lower(), match.group(0)))

        value = re.sub(r"\{([^{}]+)\}", replace_brace, value)
        return re.sub(r"#([^#]+)#", replace_hash, value)

    def _number_for(self, index: int) -> str:
        if not self.config["number_enabled"]:
            return ""
        value = self.config["number_start"] + index * self.config["number_step"]
        width = max(0, self.config["number_width"])
        return str(value).zfill(width)

    def _date_for(self, path: Path) -> str:
        token_text = " ".join([self.config["template"], self.config["prefix"], self.config["suffix"]]).lower()
        uses_date_token = any(token in token_text for token in ("{date}", "{日期}", "#date#", "#日期#"))
        if self.config["date_position"] == "不添加" and not uses_date_token:
            return ""
        source = self.config["date_source"]
        if source == "修改时间":
            timestamp = path.stat().st_mtime
        elif source == "创建时间":
            timestamp = path.stat().st_ctime
        else:
            timestamp = datetime.now().timestamp()
        return datetime.fromtimestamp(timestamp).strftime(self.config["date_format"])

    def _extension_for(self, original_ext: str) -> str:
        mode = self.config["extension_mode"]
        custom = self.config["custom_extension"].strip().lstrip(".")
        if mode == "保留":
            return original_ext
        if mode == "小写":
            return original_ext.lower()
        if mode == "大写":
            return original_ext.upper()
        if mode == "自定义":
            return f".{custom}" if custom else ""
        if mode == "移除":
            return ""
        return original_ext

    def _place_piece(self, name: str, piece: str, position: str, separator: str) -> str:
        if not piece or position == "不添加":
            return name
        sep = separator
        if position == "开头":
            return f"{piece}{sep}{name}" if sep else f"{piece}{name}"
        if position == "结尾":
            return f"{name}{sep}{piece}" if sep else f"{name}{piece}"
        return name

    def _split_name(self, path: Path) -> tuple[str, str]:
        if self.config["item_kind"] == "文件夹":
            return path.name, ""
        if self.config["multi_ext"]:
            suffixes = path.suffixes
            if len(suffixes) > 1:
                ext = "".join(suffixes)
                return path.name[: -len(ext)], ext
        return path.stem, path.suffix

    def _apply_case(self, name: str, mode: str) -> str:
        if mode == "不处理":
            return name
        if mode == "全部小写":
            return name.lower()
        if mode == "全部大写":
            return name.upper()
        if mode == "首字母大写":
            return name.capitalize()
        if mode == "单词首字母大写":
            return name.title()
        return name

    def _normalize_separators(self, name: str, mode: str) -> str:
        if mode == "空格转下划线":
            return re.sub(r"\s+", "_", name)
        if mode == "空格转短横线":
            return re.sub(r"\s+", "-", name)
        if mode == "下划线转空格":
            return name.replace("_", " ")
        if mode == "短横线转空格":
            return name.replace("-", " ")
        return name

    def _remove_range(self, name: str, value: str) -> str:
        match = re.fullmatch(r"\s*(\d+)\s*[-:]\s*(\d+)\s*", value)
        if not match:
            raise ValueError("删除位置格式应为 1-3")
        start = int(match.group(1))
        end = int(match.group(2))
        if start < 1 or end < start:
            raise ValueError("删除位置范围不正确")
        return name[: start - 1] + name[end:]

    def _clean_filename(self, name: str) -> str:
        cleaned = "".join("_" if char in INVALID_CHARS or ord(char) < 32 else char for char in name)
        cleaned = cleaned.strip().rstrip(".")
        self._validate_filename(cleaned)
        return cleaned

    def _validate_filename(self, name: str) -> None:
        if any(char in INVALID_CHARS or ord(char) < 32 for char in name):
            raise ValueError("新名称包含 Windows 不允许的字符")
        if name.rstrip(". ") != name:
            raise ValueError("新名称不能以空格或点结尾")

    def _normal_extensions(self, value: str) -> set[str]:
        return {part.lower().lstrip(".") for part in self._split_csv(value)}

    def _split_csv(self, value: str) -> list[str]:
        return [part.strip() for part in re.split(r"[,;，；]", value) if part.strip()]

    def _matches_any(self, value: str, patterns: list[str]) -> bool:
        normalized = value.replace("\\", "/")
        return any(fnmatch.fnmatch(normalized, pattern.replace("\\", "/")) for pattern in patterns)

    def _sort_items(self, items: list[RenameItem]) -> list[RenameItem]:
        mode = self.config.get("sort_mode", "名称 A-Z")
        reverse_modes = {"名称 Z-A", "修改时间 新->旧", "创建时间 新->旧", "文件大小 大->小", "扩展名 Z-A", "路径深度 深->浅"}
        reverse = mode in reverse_modes

        def safe_stat(path: Path):
            try:
                return path.stat()
            except OSError:
                return None

        def sort_key(item: RenameItem):
            path = item.path
            stat = safe_stat(path)
            name_key = path.name.lower()
            path_key = str(path).lower()
            if mode in {"修改时间 旧->新", "修改时间 新->旧"}:
                return ((stat.st_mtime if stat else 0), path_key)
            if mode in {"创建时间 旧->新", "创建时间 新->旧"}:
                return ((stat.st_ctime if stat else 0), path_key)
            if mode in {"文件大小 小->大", "文件大小 大->小"}:
                return ((stat.st_size if stat else 0), path_key)
            if mode in {"扩展名 A-Z", "扩展名 Z-A"}:
                return (path.suffix.lower(), name_key, path_key)
            if mode in {"路径深度 浅->深", "路径深度 深->浅"}:
                return (len(path.parts), path_key)
            return (name_key, path_key)

        return sorted(items, key=sort_key, reverse=reverse)

    def _plain_replace(self, source: str, old: str, new: str, case_sensitive: bool) -> str:
        if case_sensitive:
            return source.replace(old, new)
        return re.sub(re.escape(old), lambda _: new, source, flags=re.IGNORECASE)

    def _text_contains(self, source: str, text: str, case_sensitive: bool) -> bool:
        if case_sensitive:
            return text in source
        return text.lower() in source.lower()

    def _is_hidden(self, path: Path) -> bool:
        return any(part.startswith(".") for part in path.parts if part not in {path.anchor, "\\"})

    def _same_path(self, left: Path, right: Path) -> bool:
        return left.resolve().as_posix().lower() == right.resolve().as_posix().lower()


def rename_with_history(root: Path, items: list[PreviewItem]) -> Path:
    batch_id = uuid.uuid4().hex[:10]
    entries: list[dict[str, str]] = []
    staged: list[tuple[Path, Path, Path]] = []

    try:
        for item in items:
            temp = item.source.with_name(f"__bulk_rename_tmp_{batch_id}_{uuid.uuid4().hex}{item.source.suffix}")
            item.source.rename(temp)
            staged.append((temp, item.source, item.target))

        for temp, source, target in staged:
            temp.rename(target)
            entries.append({"source": str(source), "target": str(target), "kind": "file" if target.is_file() else "folder"})
    except Exception:
        for temp, source, _target in reversed(staged):
            if temp.exists() and not source.exists():
                temp.rename(source)
        raise

    history = root / f"{HISTORY_PREFIX}{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    history.write_text(json.dumps({"created_at": datetime.now().isoformat(), "items": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    return history


def undo_history_file(history: Path) -> int:
    data = json.loads(history.read_text(encoding="utf-8"))
    count = 0
    for entry in reversed(data.get("items", [])):
        target = Path(entry["target"])
        source = Path(entry["source"])
        if target.exists():
            source.parent.mkdir(parents=True, exist_ok=True)
            target.rename(source)
            count += 1
    history.unlink(missing_ok=True)
    return count


def run_batch(config_path: Path, execute: bool, report_path: Path | None) -> int:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    root = Path(config["root"]).expanduser()
    report_path = report_path or config_path.with_suffix(".report.json")
    engine = RenameEngine(config)
    items = engine.scan()
    preview = engine.preview(items)
    ready = [item for item in preview if item.can_rename]
    blocked = [item for item in preview if item.status in {"错误", "冲突"}]
    history: Path | None = None

    if execute and not blocked and ready:
        history = rename_with_history(root, ready)

    report = {
        "created_at": datetime.now().isoformat(),
        "root": str(root),
        "execute": execute,
        "scanned": len(preview),
        "ready": len(ready),
        "blocked": len(blocked),
        "history": str(history) if history else "",
        "items": [
            {
                "source": str(item.source),
                "target": str(item.target),
                "status": item.status,
                "message": item.message,
            }
            for item in preview
        ],
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 2 if blocked else 0


class BulkRenameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1440x820")
        self.minsize(1280, 720)
        self.preview_items: list[PreviewItem] = []
        self.last_history: Path | None = None
        self._build_vars()
        self._style()
        self.load_last_session()
        self.title(self.t(APP_NAME))
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._set_startup_status()
        if not self.language_prompted_var.get():
            self.after(120, self.ask_initial_language)

    def _build_vars(self) -> None:
        self.root_var = tk.StringVar()
        self.recursive_var = tk.BooleanVar(value=False)
        self.hidden_var = tk.BooleanVar(value=False)
        self.kind_var = tk.StringVar(value="文件")
        self.pattern_var = tk.StringVar()
        self.extension_filter_var = tk.StringVar()
        self.contains_var = tk.StringVar()
        self.exclude_patterns_var = tk.StringVar()
        self.exclude_contains_var = tk.StringVar()
        self.exclude_extensions_var = tk.StringVar()
        self.exclude_folders_var = tk.StringVar()
        self.sort_mode_var = tk.StringVar(value="名称 A-Z")

        self.find_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self.regex_var = tk.BooleanVar(value=False)
        self.case_sensitive_var = tk.BooleanVar(value=False)
        self.remove_var = tk.StringVar()
        self.remove_range_var = tk.StringVar()
        self.trim_var = tk.BooleanVar(value=True)
        self.collapse_spaces_var = tk.BooleanVar(value=False)
        self.separator_var = tk.StringVar(value="不处理")
        self.case_mode_var = tk.StringVar(value="不处理")
        self.prefix_var = tk.StringVar()
        self.suffix_var = tk.StringVar()
        self.template_var = tk.StringVar()

        self.number_enabled_var = tk.BooleanVar(value=False)
        self.number_start_var = tk.IntVar(value=1)
        self.number_step_var = tk.IntVar(value=1)
        self.number_width_var = tk.IntVar(value=3)
        self.number_position_var = tk.StringVar(value="结尾")
        self.number_separator_var = tk.StringVar(value="_")

        self.date_source_var = tk.StringVar(value="修改时间")
        self.date_format_var = tk.StringVar(value="%Y%m%d")
        self.date_position_var = tk.StringVar(value="不添加")
        self.date_separator_var = tk.StringVar(value="_")

        self.multi_ext_var = tk.BooleanVar(value=False)
        self.extension_mode_var = tk.StringVar(value="保留")
        self.custom_extension_var = tk.StringVar()
        self.clean_invalid_var = tk.BooleanVar(value=True)
        self.collision_mode_var = tk.StringVar(value="阻止")

        self.status_var = tk.StringVar()
        self.count_var = tk.StringVar(value="0 项")
        self.task_mode_var = tk.StringVar(value="basic")
        self.language_var = tk.StringVar(value="zh")
        self.language_display_var = tk.StringVar(value="中文")
        self.language_prompted_var = tk.BooleanVar(value=False)

    def t(self, text: str, **kwargs) -> str:
        value = EN_TEXT.get(text, text) if self.language_var.get() == "en" else text
        return value.format(**kwargs) if kwargs else value

    def option_label(self, value: str) -> str:
        return self.t(value)

    def option_value(self, label: str) -> str:
        return EN_TO_ZH.get(label, label)

    def _localized_combobox(self, parent: tk.Widget, variable: tk.StringVar, values: list[str], **kwargs) -> ttk.Combobox:
        display_var = tk.StringVar(value=self.option_label(variable.get()))
        combo = ttk.Combobox(
            parent,
            textvariable=display_var,
            values=[self.option_label(value) for value in values],
            state="readonly",
            **kwargs,
        )

        def sync_from_internal(*_args) -> None:
            label = self.option_label(variable.get())
            if display_var.get() != label:
                display_var.set(label)

        def sync_to_internal(_event=None) -> None:
            variable.set(self.option_value(display_var.get()))
            sync_from_internal()

        variable.trace_add("write", sync_from_internal)
        combo.bind("<<ComboboxSelected>>", sync_to_internal)
        return combo

    def ask_initial_language(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Language / 语言")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        body = ttk.Frame(dialog, padding=18)
        body.pack(fill=BOTH, expand=True)
        ttk.Label(body, text="首次使用请选择界面语言", font=("Microsoft YaHei UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        ttk.Label(body, text="Choose interface language for first use").pack(anchor="w", pady=(0, 12))
        ttk.Label(body, text="以后可在“设置 > 语言”中修改。").pack(anchor="w", pady=(0, 14))

        buttons = ttk.Frame(body)
        buttons.pack(fill="x")

        def choose(language: str) -> None:
            self.language_var.set(language)
            self.language_prompted_var.set(True)
            current = self.config()
            self.save_last_session()
            dialog.destroy()
            self._rebuild_ui(current, refresh_page=False, page="home")

        ttk.Button(buttons, text="中文", command=lambda: choose("zh")).pack(side=LEFT, expand=True, fill="x", padx=(0, 6))
        ttk.Button(buttons, text="English", command=lambda: choose("en")).pack(side=LEFT, expand=True, fill="x", padx=(6, 0))
        dialog.protocol("WM_DELETE_WINDOW", lambda: choose("zh"))
        self.update_idletasks()
        x = self.winfo_screenwidth() // 2 - 190
        y = self.winfo_screenheight() // 2 - 95
        dialog.geometry(f"380x190+{x}+{y}")
        dialog.lift()
        dialog.focus_force()
        dialog.attributes("-topmost", True)
        dialog.after(900, lambda: dialog.attributes("-topmost", False) if dialog.winfo_exists() else None)

    def apply_language_change(self) -> None:
        display = self.language_display_var.get()
        if display in {"中文", "Chinese"}:
            self.language_var.set("zh")
        elif display in {"English", "英语"}:
            self.language_var.set("en")
        self.language_prompted_var.set(True)
        current = self.config()
        page = getattr(self, "current_page", "home")
        self.save_last_session()
        self._rebuild_ui(current, refresh_page=False, page=page)

    def _rebuild_ui(self, config: dict, refresh_page: bool = False, page: str = "home") -> None:
        for child in self.winfo_children():
            child.destroy()
        self.title(self.t(APP_NAME))
        self._build_ui()
        self.apply_config(config, refresh_page=refresh_page, show_task_page=False)
        if page in getattr(self, "pages", {}):
            self.show_page(page, refresh=refresh_page)
        self._set_startup_status()

    def _set_startup_status(self) -> None:
        if self.root_var.get().strip():
            self._set_status(self.t("已恢复上次配置，点击预览开始扫描"))
        else:
            self._set_status(self.t("请选择文件夹"))

    def _style(self) -> None:
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("TFrame", background="#f7f8fa")
        style.configure("Surface.TFrame", background="#ffffff")
        style.configure("TLabel", background="#f7f8fa", foreground="#20242a", font=("Microsoft YaHei UI", 9))
        style.configure("Surface.TLabel", background="#ffffff")
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 15, "bold"), background="#f7f8fa")
        style.configure("Hint.TLabel", foreground="#667085", background="#f7f8fa")
        style.configure("TButton", font=("Microsoft YaHei UI", 9), padding=(10, 5))
        style.configure("Primary.TButton", font=("Microsoft YaHei UI", 9, "bold"), padding=(12, 6))
        style.configure("TNotebook", background="#f7f8fa", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Microsoft YaHei UI", 9), padding=(10, 8))
        style.configure("Treeview", font=("Microsoft YaHei UI", 9), rowheight=28)
        style.configure("Treeview.Heading", font=("Microsoft YaHei UI", 9, "bold"))

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, padding=18)
        outer.pack(fill=BOTH, expand=True)

        header = ttk.Frame(outer)
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text=self.t(APP_NAME), style="Title.TLabel").pack(side=LEFT)
        ttk.Label(header, textvariable=self.count_var, style="Hint.TLabel").pack(side=RIGHT)

        top = ttk.Frame(outer, style="Surface.TFrame", padding=12)
        top.pack(fill="x")
        self._build_path_panel(top)

        middle = ttk.PanedWindow(outer, orient="horizontal")
        middle.pack(fill=BOTH, expand=True, pady=12)

        settings = ttk.Frame(middle, padding=(0, 0, 10, 0), width=520)
        preview = ttk.Frame(middle, width=660)
        middle.add(settings, weight=0)
        middle.add(preview, weight=1)
        self.after_idle(lambda: self._set_initial_sash(middle))
        self.after(160, lambda: self._set_initial_sash(middle))

        self._build_task_pages(settings)
        self._build_preview(preview)
        self._build_footer(outer)

    def _set_initial_sash(self, middle: ttk.PanedWindow) -> None:
        try:
            width = middle.winfo_width()
            if width > 0:
                middle.sashpos(0, min(580, max(520, width // 2)))
        except tk.TclError:
            pass

    def _build_path_panel(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text=self.t("扫描路径"), style="Surface.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Entry(parent, textvariable=self.root_var).grid(row=0, column=1, sticky="ew", padx=(0, 8))
        choose = ttk.Button(parent, text=self.t("选择"), command=self.choose_folder)
        choose.grid(row=0, column=2, padx=(0, 8))
        self._tip(choose, self.t("选择要批量处理的文件夹。"))
        scan = ttk.Button(parent, text=self.t("预览"), style="Primary.TButton", command=self.refresh_preview)
        scan.grid(row=0, column=3)
        self._tip(scan, self.t("扫描当前路径并在右侧显示改名前后的对照。"))

        options = ttk.Frame(parent, style="Surface.TFrame")
        options.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        ttk.Checkbutton(options, text=self.t("包含子文件夹"), variable=self.recursive_var, command=self.refresh_preview_later).pack(side=LEFT)
        ttk.Checkbutton(options, text=self.t("包含隐藏项"), variable=self.hidden_var, command=self.refresh_preview_later).pack(side=LEFT, padx=(14, 0))
        ttk.Label(options, text=self.t("对象"), style="Surface.TLabel").pack(side=LEFT, padx=(20, 6))
        self._localized_combobox(options, self.kind_var, ["文件", "文件夹"], width=10).pack(side=LEFT)
        filter_btn = ttk.Button(options, text=self.t("筛选"), command=self.open_filter_dialog)
        filter_btn.pack(side=LEFT, padx=(18, 0))
        self._tip(filter_btn, self.t("编辑所有模式都会使用的筛选条件。"))

    def _build_task_pages(self, parent: ttk.Frame) -> None:
        self.page_area = ttk.Frame(parent)
        self.page_area.pack(fill=BOTH, expand=True)
        self.pages: dict[str, ttk.Frame] = {}

        home = ttk.Frame(self.page_area, padding=12)
        basic = ttk.Frame(self.page_area, padding=12)
        template = ttk.Frame(self.page_area, padding=12)
        extension = ttk.Frame(self.page_area, padding=12)
        clean = ttk.Frame(self.page_area, padding=12)
        setting = ttk.Frame(self.page_area, padding=12)
        self.pages.update({"home": home, "basic": basic, "template": template, "extension": extension, "clean": clean, "setting": setting})

        self._build_home_page(home)
        self._build_basic_tab(self._page_content(basic, self.t("普通重命名")))
        self._build_template_tab(self._page_content(template, self.t("编号模板")))
        self._build_extension_tab(self._page_content(extension, self.t("扩展名修改")))
        self._build_clean_tab(self._page_content(clean, self.t("名称清理")))
        self._build_setting_page(self._page_content(setting, self.t("设置"), scroll=True))
        self.show_page("home")

    def show_page(self, name: str, refresh: bool = True) -> None:
        self.current_page = name
        if name in {"basic", "template", "extension", "clean"}:
            self.task_mode_var.set(name)
        for frame in self.pages.values():
            frame.pack_forget()
        self.pages[name].pack(fill=BOTH, expand=True)
        if refresh and name in {"basic", "template", "extension", "clean"}:
            self.refresh_preview_later()

    def _page_content(self, parent: ttk.Frame, title: str, scroll: bool = False) -> ttk.Frame:
        header = ttk.Frame(parent)
        header.pack(fill="x", pady=(0, 12))
        back = ttk.Button(header, text=self.t("返回主界面"), command=lambda: self.show_page("home"))
        back.pack(side=LEFT)
        self._tip(back, self.t("返回任务选择，不改变当前规则。"))
        ttk.Label(header, text=title, font=("Microsoft YaHei UI", 12, "bold")).pack(side=LEFT, padx=(12, 0))
        if scroll:
            return self._scrollable_frame(parent)
        body = ttk.Frame(parent)
        body.pack(fill=BOTH, expand=True)
        return body

    def _scrollable_frame(self, parent: ttk.Frame) -> ttk.Frame:
        container = ttk.Frame(parent)
        container.pack(fill=BOTH, expand=True)
        canvas = tk.Canvas(container, highlightthickness=0, background="#f7f8fa")
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        body = ttk.Frame(canvas)
        body_id = canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill="y")

        def sync_scroll_region(_event=None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(body_id, width=canvas.winfo_width())

        def on_mousewheel(event) -> None:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        body.bind("<Configure>", sync_scroll_region)
        canvas.bind("<Configure>", sync_scroll_region)
        canvas.bind("<Enter>", lambda _event: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda _event: canvas.unbind_all("<MouseWheel>"))
        return body

    def _build_home_page(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text=self.t("选择要完成的任务"), font=("Microsoft YaHei UI", 12, "bold")).pack(anchor="w", pady=(0, 12))
        for key, text, tip in [
            ("basic", "普通重命名", "批量查找替换、删除指定文字、加前缀/后缀。"),
            ("template", "编号模板", "把文件按时间、名称、大小等顺序排列，再生成 XXX_#NUM# 或 #DATE#_#NUM#。"),
            ("extension", "扩展名修改", "批量把 .jpeg 改成 .jpg、统一扩展名大小写，或移除扩展名。"),
            ("clean", "名称清理", "批量清理多余空格、统一大小写、空格/下划线/短横线风格。"),
            ("setting", "设置", "管理全局筛选、预设、日期格式、安全策略和变量说明。"),
        ]:
            button = ttk.Button(parent, text=self.t(text), command=lambda page=key: self.show_page(page))
            button.pack(fill="x", pady=5)
            self._tip(button, self.t(tip))

    def _build_basic_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(1, weight=1)
        row = 0
        self._entry_row(parent, row, "查找", self.find_var)
        row += 1
        self._entry_row(parent, row, "替换为", self.replace_var)
        row += 1
        checks = ttk.Frame(parent)
        checks.grid(row=row, column=1, sticky="w", pady=(2, 10))
        ttk.Checkbutton(checks, text=self.t("正则表达式"), variable=self.regex_var).pack(side=LEFT)
        ttk.Checkbutton(checks, text=self.t("区分大小写"), variable=self.case_sensitive_var).pack(side=LEFT, padx=(14, 0))
        row += 1
        self._entry_row(parent, row, "删除文字", self.remove_var)
        row += 1
        self._entry_row(parent, row, "删除位置", self.remove_range_var)
        row += 1
        self._entry_row(parent, row, "前缀", self.prefix_var)
        row += 1
        self._entry_row(parent, row, "后缀", self.suffix_var)

    def _build_template_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(1, weight=1)
        self._entry_row(parent, 0, "名称模板", self.template_var)
        ttk.Label(parent, text=self.t("排序")).grid(row=1, column=0, sticky="w", pady=6, padx=(0, 12))
        self._localized_combobox(
            parent,
            self.sort_mode_var,
            [
                "名称 A-Z",
                "名称 Z-A",
                "修改时间 旧->新",
                "修改时间 新->旧",
                "创建时间 旧->新",
                "创建时间 新->旧",
                "文件大小 小->大",
                "文件大小 大->小",
                "扩展名 A-Z",
                "扩展名 Z-A",
                "路径深度 浅->深",
                "路径深度 深->浅",
            ],
        ).grid(row=1, column=1, sticky="ew", pady=6)
        ttk.Checkbutton(parent, text=self.t("启用编号 #NUM#"), variable=self.number_enabled_var).grid(row=2, column=1, sticky="w", pady=(10, 8))
        self._spin_row(parent, 3, "起始", self.number_start_var, 0, 999999)
        self._spin_row(parent, 4, "步长", self.number_step_var, 1, 9999)
        self._spin_row(parent, 5, "位数", self.number_width_var, 0, 12)

    def _build_extension_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text=self.t("处理方式")).grid(row=0, column=0, sticky="w", pady=6, padx=(0, 12))
        self._localized_combobox(parent, self.extension_mode_var, ["保留", "小写", "大写", "自定义", "移除"]).grid(row=0, column=1, sticky="ew", pady=6)
        self._entry_row(parent, 1, "自定义扩展名", self.custom_extension_var)
        ttk.Checkbutton(parent, text=self.t("把多段扩展名作为整体保留"), variable=self.multi_ext_var).grid(row=2, column=1, sticky="w", pady=(8, 0))

        hint = ttk.LabelFrame(parent, text=self.t("适合场景"), padding=10)
        hint.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        ttk.Label(hint, text=self.t("例如把 .jpeg 批量改为 .jpg，把 .TXT 统一为 .txt，或移除临时扩展名。"), wraplength=360).pack(anchor="w")

    def _build_clean_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(1, weight=1)
        ttk.Checkbutton(parent, text=self.t("去掉首尾空格"), variable=self.trim_var).grid(row=0, column=1, sticky="w", pady=(0, 8))
        ttk.Checkbutton(parent, text=self.t("合并连续空格"), variable=self.collapse_spaces_var).grid(row=1, column=1, sticky="w", pady=8)
        ttk.Label(parent, text=self.t("大小写")).grid(row=2, column=0, sticky="w", pady=6, padx=(0, 12))
        self._localized_combobox(
            parent,
            self.case_mode_var,
            ["不处理", "全部小写", "全部大写", "首字母大写", "单词首字母大写"],
        ).grid(row=2, column=1, sticky="ew", pady=6)
        ttk.Label(parent, text=self.t("分隔符")).grid(row=3, column=0, sticky="w", pady=6, padx=(0, 12))
        self._localized_combobox(
            parent,
            self.separator_var,
            ["不处理", "空格转下划线", "空格转短横线", "下划线转空格", "短横线转空格"],
        ).grid(row=3, column=1, sticky="ew", pady=6)

    def _build_setting_page(self, parent: ttk.Frame) -> None:
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=BOTH, expand=True)

        filter_page = ttk.Frame(notebook, padding=12)
        date_ext = ttk.Frame(notebook, padding=12)
        safe = ttk.Frame(notebook, padding=12)
        variables = ttk.Frame(notebook, padding=12)
        language = ttk.Frame(notebook, padding=12)
        notebook.add(filter_page, text=self.t("筛选/预设"))
        notebook.add(date_ext, text=self.t("日期/扩展名"))
        notebook.add(safe, text=self.t("安全"))
        notebook.add(variables, text=self.t("变量说明"))
        notebook.add(language, text=self.t("语言"))

        self._build_filter_setting_tab(filter_page)
        self._build_date_ext_tab(date_ext)
        self._build_safe_tab(safe)
        self._build_variable_tab(variables)
        self._build_language_tab(language)

    def _build_filter_setting_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        save_filter = ttk.Button(parent, text=self.t("保存筛选预设"), command=self.save_filter_preset)
        save_filter.grid(row=0, column=0, sticky="ew", pady=5)
        self._tip(save_filter, self.t("只保存筛选条件，不保存当前重命名规则。"))
        load_filter = ttk.Button(parent, text=self.t("加载筛选预设"), command=self.load_filter_preset)
        load_filter.grid(row=1, column=0, sticky="ew", pady=5)
        self._tip(load_filter, self.t("只加载筛选条件，不覆盖当前输出任务。"))
        ttk.Separator(parent).grid(row=2, column=0, sticky="ew", pady=14)
        save_all = ttk.Button(parent, text=self.t("保存整套预设"), command=self.save_preset)
        save_all.grid(row=3, column=0, sticky="ew", pady=5)
        self._tip(save_all, self.t("保存当前任务、筛选、日期、扩展名和安全策略。"))
        load_all = ttk.Button(parent, text=self.t("加载整套预设"), command=self.load_preset)
        load_all.grid(row=4, column=0, sticky="ew", pady=5)
        self._tip(load_all, self.t("加载一个完整方案。"))

    def _build_variable_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=3)
        rows = [
            ("#NUM#", "按当前排序生成的编号"),
            ("#DATE#", "按 SETTING 中日期来源和日期格式生成"),
            ("#NAME#", "当前任务中的基础名称"),
            ("#ORIGINAL#", "文件原始名称，不含扩展名"),
            ("#EXT#", "扩展名，不含点"),
            ("#PARENT#", "父文件夹名称"),
            ("#MTIME#", "文件修改时间"),
            ("#CTIME#", "文件创建时间"),
            ("#TODAY#", "今天的日期"),
        ]
        for row, (token, desc) in enumerate(rows):
            ttk.Label(parent, text=token, font=("Microsoft YaHei UI", 9, "bold")).grid(row=row, column=0, sticky="w", pady=4)
            ttk.Label(parent, text=self.t(desc), style="Hint.TLabel", wraplength=280).grid(row=row, column=1, sticky="ew", padx=(16, 0), pady=4)

    def _build_language_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(1, weight=1)
        self.language_display_var.set("English" if self.language_var.get() == "en" else self.t("中文"))
        ttk.Label(parent, text=self.t("界面语言")).grid(row=0, column=0, sticky="w", pady=6, padx=(0, 12))
        ttk.Combobox(parent, textvariable=self.language_display_var, values=[self.t("中文"), "English"], state="readonly", width=16).grid(row=0, column=1, sticky="w", pady=6)
        apply_btn = ttk.Button(parent, text=self.t("应用语言"), command=self.apply_language_change)
        apply_btn.grid(row=1, column=1, sticky="ew", pady=(10, 4))
        self._tip(apply_btn, self.t("语言设置通常只需要修改一次。"))
        ttk.Label(parent, text=self.t("语言设置通常只需要修改一次。"), style="Hint.TLabel", wraplength=300).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))

    def _build_scan_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(1, weight=1)
        self._entry_row(parent, 0, "排除通配符", self.exclude_patterns_var)
        self._entry_row(parent, 1, "排除文字", self.exclude_contains_var)
        self._entry_row(parent, 2, "排除扩展名", self.exclude_extensions_var)
        self._entry_row(parent, 3, "排除文件夹", self.exclude_folders_var)
        ttk.Label(parent, text=self.t("排序")).grid(row=4, column=0, sticky="w", pady=6, padx=(0, 12))
        self._localized_combobox(
            parent,
            self.sort_mode_var,
            [
                "名称 A-Z",
                "名称 Z-A",
                "修改时间 旧->新",
                "修改时间 新->旧",
                "创建时间 旧->新",
                "创建时间 新->旧",
                "文件大小 小->大",
                "文件大小 大->小",
                "扩展名 A-Z",
                "扩展名 Z-A",
                "路径深度 浅->深",
                "路径深度 深->浅",
            ],
        ).grid(row=4, column=1, sticky="ew", pady=6)

        hint = ttk.LabelFrame(parent, text=self.t("填写方式"), padding=10)
        hint.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        ttk.Label(
            hint,
            text=self.t("多个条件用逗号或分号分隔。通配符可写 *.tmp、backup*、*/skip/*；排除文件夹可写 temp 或 */temp。"),
            wraplength=330,
        ).pack(anchor="w")

    def _build_number_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(1, weight=1)
        ttk.Checkbutton(parent, text=self.t("添加编号"), variable=self.number_enabled_var).grid(row=0, column=1, sticky="w", pady=(0, 12))
        self._spin_row(parent, 1, "起始", self.number_start_var, 0, 999999)
        self._spin_row(parent, 2, "步长", self.number_step_var, 1, 9999)
        self._spin_row(parent, 3, "位数", self.number_width_var, 0, 12)
        ttk.Label(parent, text=self.t("位置")).grid(row=4, column=0, sticky="w", pady=6)
        self._localized_combobox(parent, self.number_position_var, ["不添加", "开头", "结尾"]).grid(row=4, column=1, sticky="ew", pady=6)
        self._entry_row(parent, 5, "分隔符", self.number_separator_var)

    def _build_date_ext_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text=self.t("日期来源")).grid(row=0, column=0, sticky="w", pady=6)
        self._localized_combobox(parent, self.date_source_var, ["修改时间", "创建时间", "今天"]).grid(row=0, column=1, sticky="ew", pady=6)
        self._entry_row(parent, 1, "日期格式", self.date_format_var)

        hint = ttk.LabelFrame(parent, text=self.t("说明"), padding=10)
        hint.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        ttk.Label(hint, text=self.t("这里定义 #DATE#、#MTIME#、#CTIME# 等日期变量的格式。真正更改扩展名请回主界面选择“扩展名修改”。"), wraplength=360).pack(anchor="w")

    def _build_safe_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(1, weight=1)
        ttk.Checkbutton(parent, text=self.t("自动替换非法字符"), variable=self.clean_invalid_var).grid(row=0, column=1, sticky="w", pady=(0, 12))
        ttk.Label(parent, text=self.t("重名处理")).grid(row=1, column=0, sticky="w", pady=6)
        self._localized_combobox(parent, self.collision_mode_var, ["阻止", "自动追加序号"]).grid(row=1, column=1, sticky="ew", pady=6)

    def _build_preview(self, parent: ttk.Frame) -> None:
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(toolbar, text=self.t("重新预览"), command=self.refresh_preview).pack(side=LEFT)
        ttk.Button(toolbar, text=self.t("清空规则"), command=self.reset_rules).pack(side=LEFT, padx=(8, 0))
        ttk.Button(toolbar, text=self.t("撤销上次"), command=self.undo_last).pack(side=RIGHT)

        columns = ("status", "old", "new", "folder", "message")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("status", text=self.t("状态"))
        self.tree.heading("old", text=self.t("原名称"))
        self.tree.heading("new", text=self.t("新名称"))
        self.tree.heading("folder", text=self.t("所在文件夹"))
        self.tree.heading("message", text=self.t("说明"))
        self.tree.column("status", width=78, stretch=False, anchor="center")
        self.tree.column("old", width=190)
        self.tree.column("new", width=190)
        self.tree.column("folder", width=250)
        self.tree.column("message", width=150)

        scroll = ttk.Scrollbar(parent, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scroll.pack(side=RIGHT, fill="y")

    def _build_footer(self, parent: ttk.Frame) -> None:
        footer = ttk.Frame(parent)
        footer.pack(fill="x")
        ttk.Label(footer, textvariable=self.status_var, style="Hint.TLabel").pack(side=LEFT)
        ttk.Button(footer, text=self.t("执行改名"), style="Primary.TButton", command=self.execute).pack(side=RIGHT)

    def _entry_row(self, parent: ttk.Frame, row: int, label: str, variable: tk.Variable) -> None:
        ttk.Label(parent, text=self.t(label)).grid(row=row, column=0, sticky="w", pady=6, padx=(0, 12))
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=6)

    def _spin_row(self, parent: ttk.Frame, row: int, label: str, variable: tk.IntVar, start: int, end: int) -> None:
        ttk.Label(parent, text=self.t(label)).grid(row=row, column=0, sticky="w", pady=6, padx=(0, 12))
        ttk.Spinbox(parent, from_=start, to=end, textvariable=variable, width=10).grid(row=row, column=1, sticky="w", pady=6)

    def choose_folder(self) -> None:
        folder = filedialog.askdirectory(title=self.t("选择要扫描的文件夹"))
        if folder:
            self.root_var.set(folder)
            self.refresh_preview()

    def refresh_preview_later(self) -> None:
        self.after(120, self.refresh_preview)

    def open_filter_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title(self.t("筛选"))
        dialog.transient(self)
        dialog.grab_set()
        dialog.geometry("560x520")
        dialog.minsize(500, 360)

        container = ttk.Frame(dialog)
        container.pack(fill=BOTH, expand=True)
        canvas = tk.Canvas(container, highlightthickness=0, background="#f7f8fa")
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        body = ttk.Frame(canvas, padding=16)
        body_id = canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill="y")

        def sync_scroll_region(_event=None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(body_id, width=canvas.winfo_width())

        def on_mousewheel(event) -> None:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        body.bind("<Configure>", sync_scroll_region)
        canvas.bind("<Configure>", sync_scroll_region)
        canvas.bind("<Enter>", lambda _event: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda _event: canvas.unbind_all("<MouseWheel>"))
        dialog.bind("<Destroy>", lambda _event: canvas.unbind_all("<MouseWheel>"))
        body.columnconfigure(1, weight=1)

        self._entry_row(body, 0, "文件类型", self.extension_filter_var)
        self._entry_row(body, 1, "通配符", self.pattern_var)
        self._entry_row(body, 2, "包含文字", self.contains_var)
        ttk.Separator(body).grid(row=3, column=0, columnspan=2, sticky="ew", pady=14)
        self._entry_row(body, 4, "排除通配符", self.exclude_patterns_var)
        self._entry_row(body, 5, "排除文字", self.exclude_contains_var)
        self._entry_row(body, 6, "排除扩展名", self.exclude_extensions_var)
        self._entry_row(body, 7, "排除文件夹", self.exclude_folders_var)

        hint = ttk.LabelFrame(body, text=self.t("填写方式"), padding=10)
        hint.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(12, 8))
        ttk.Label(
            hint,
            text=self.t("多个条件用逗号或分号分隔。通配符可写 *.tmp、backup*、*/skip/*；排除文件夹可写 temp 或 */temp。"),
            wraplength=430,
        ).pack(anchor="w")

        buttons = ttk.Frame(body)
        buttons.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        buttons.columnconfigure(0, weight=1)
        clear = ttk.Button(buttons, text=self.t("清空筛选"), command=self.clear_filter)
        clear.grid(row=0, column=0, sticky="ew", pady=3)
        self._tip(clear, self.t("只清空筛选条件，不影响当前重命名规则。"))
        load = ttk.Button(buttons, text=self.t("加载筛选预设"), command=self.load_filter_preset)
        load.grid(row=1, column=0, sticky="ew", pady=3)
        self._tip(load, self.t("只加载筛选条件，不覆盖重命名模板、编号和扩展名设置。"))
        save = ttk.Button(buttons, text=self.t("保存筛选预设"), command=self.save_filter_preset)
        save.grid(row=2, column=0, sticky="ew", pady=3)
        self._tip(save, self.t("把当前筛选条件保存起来，下次可以在任何任务中复用。"))
        close = ttk.Button(buttons, text=self.t("应用并预览"), style="Primary.TButton", command=lambda: (dialog.destroy(), self.refresh_preview()))
        close.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        self._tip(close, self.t("关闭窗口并刷新右侧预览。"))

    def _tip(self, widget: tk.Widget, text: str) -> None:
        ToolTip(widget, text)

    def preset_path(self, folder: Path, name: str) -> Path:
        folder.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", name).strip().strip(".")
        if not safe:
            safe = datetime.now().strftime("%Y%m%d_%H%M%S")
        return folder / f"{safe}.json"

    def save_preset(self) -> None:
        name = simpledialog.askstring(self.t(APP_NAME), self.t("预设名称："), parent=self)
        if not name:
            return
        path = self.preset_path(PRESET_DIR, name)
        path.write_text(json.dumps(self.config(), ensure_ascii=False, indent=2), encoding="utf-8")
        self._set_status(self.t("已保存预设：{name}", name=path.name))

    def load_preset(self) -> None:
        PRESET_DIR.mkdir(parents=True, exist_ok=True)
        path = filedialog.askopenfilename(title=self.t("加载预设"), initialdir=str(PRESET_DIR), filetypes=[(self.t("JSON 预设"), "*.json"), (self.t("所有文件"), "*.*")])
        if path:
            self.apply_config(json.loads(Path(path).read_text(encoding="utf-8")))
            self.refresh_preview()

    def import_preset(self) -> None:
        path = filedialog.askopenfilename(title=self.t("导入预设"), filetypes=[(self.t("JSON 预设"), "*.json"), (self.t("所有文件"), "*.*")])
        if path:
            self.apply_config(json.loads(Path(path).read_text(encoding="utf-8")))
            self.refresh_preview()

    def save_last_session(self) -> None:
        try:
            LAST_SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
            LAST_SESSION_PATH.write_text(json.dumps(self.config(), ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def load_last_session(self) -> None:
        if not LAST_SESSION_PATH.exists():
            return
        try:
            self.apply_config(json.loads(LAST_SESSION_PATH.read_text(encoding="utf-8")))
        except Exception:
            pass

    def on_close(self) -> None:
        self.save_last_session()
        self.destroy()

    def filter_config(self) -> dict:
        return {
            "patterns": self.pattern_var.get(),
            "extensions": self.extension_filter_var.get(),
            "contains": self.contains_var.get(),
            "exclude_patterns": self.exclude_patterns_var.get(),
            "exclude_contains": self.exclude_contains_var.get(),
            "exclude_extensions": self.exclude_extensions_var.get(),
            "exclude_folders": self.exclude_folders_var.get(),
        }

    def apply_filter_config(self, config: dict) -> None:
        mapping = {
            "patterns": self.pattern_var,
            "extensions": self.extension_filter_var,
            "contains": self.contains_var,
            "exclude_patterns": self.exclude_patterns_var,
            "exclude_contains": self.exclude_contains_var,
            "exclude_extensions": self.exclude_extensions_var,
            "exclude_folders": self.exclude_folders_var,
        }
        for key, variable in mapping.items():
            variable.set(config.get(key, ""))

    def save_filter_preset(self) -> None:
        name = simpledialog.askstring(self.t(APP_NAME), self.t("筛选预设名称："), parent=self)
        if not name:
            return
        path = self.preset_path(FILTER_PRESET_DIR, name)
        path.write_text(json.dumps(self.filter_config(), ensure_ascii=False, indent=2), encoding="utf-8")
        self._set_status(self.t("已保存筛选预设：{name}", name=path.name))

    def load_filter_preset(self) -> None:
        FILTER_PRESET_DIR.mkdir(parents=True, exist_ok=True)
        path = filedialog.askopenfilename(title=self.t("加载筛选预设"), initialdir=str(FILTER_PRESET_DIR), filetypes=[(self.t("JSON 预设"), "*.json"), (self.t("所有文件"), "*.*")])
        if path:
            self.apply_filter_config(json.loads(Path(path).read_text(encoding="utf-8")))
            self.refresh_preview()

    def clear_filter(self) -> None:
        self.apply_filter_config({})

    def apply_config(self, config: dict, refresh_page: bool = True, show_task_page: bool = True) -> None:
        mapping: dict[str, tk.Variable] = {
            "root": self.root_var,
            "recursive": self.recursive_var,
            "include_hidden": self.hidden_var,
            "item_kind": self.kind_var,
            "patterns": self.pattern_var,
            "extensions": self.extension_filter_var,
            "contains": self.contains_var,
            "exclude_patterns": self.exclude_patterns_var,
            "exclude_contains": self.exclude_contains_var,
            "exclude_extensions": self.exclude_extensions_var,
            "exclude_folders": self.exclude_folders_var,
            "sort_mode": self.sort_mode_var,
            "find_text": self.find_var,
            "replace_text": self.replace_var,
            "regex": self.regex_var,
            "case_sensitive": self.case_sensitive_var,
            "remove_text": self.remove_var,
            "remove_range": self.remove_range_var,
            "trim": self.trim_var,
            "collapse_spaces": self.collapse_spaces_var,
            "separator_style": self.separator_var,
            "case_mode": self.case_mode_var,
            "prefix": self.prefix_var,
            "suffix": self.suffix_var,
            "template": self.template_var,
            "number_enabled": self.number_enabled_var,
            "number_start": self.number_start_var,
            "number_step": self.number_step_var,
            "number_width": self.number_width_var,
            "number_position": self.number_position_var,
            "number_separator": self.number_separator_var,
            "date_source": self.date_source_var,
            "date_format": self.date_format_var,
            "date_position": self.date_position_var,
            "date_separator": self.date_separator_var,
            "multi_ext": self.multi_ext_var,
            "extension_mode": self.extension_mode_var,
            "custom_extension": self.custom_extension_var,
            "clean_invalid": self.clean_invalid_var,
            "collision_mode": self.collision_mode_var,
            "task_mode": self.task_mode_var,
            "language": self.language_var,
            "language_prompted": self.language_prompted_var,
        }
        for key, variable in mapping.items():
            if key in config:
                variable.set(config[key])
        self.language_display_var.set("English" if self.language_var.get() == "en" else "中文")
        task = config.get("task_mode")
        if show_task_page and task in getattr(self, "pages", {}):
            self.show_page(task, refresh=refresh_page)

    def config(self) -> dict:
        return {
            "language": self.language_var.get(),
            "language_prompted": self.language_prompted_var.get(),
            "task_mode": self.task_mode_var.get(),
            "root": self.root_var.get(),
            "recursive": self.recursive_var.get(),
            "include_hidden": self.hidden_var.get(),
            "item_kind": self.kind_var.get(),
            "patterns": self.pattern_var.get(),
            "extensions": self.extension_filter_var.get(),
            "contains": self.contains_var.get(),
            "exclude_patterns": self.exclude_patterns_var.get(),
            "exclude_contains": self.exclude_contains_var.get(),
            "exclude_extensions": self.exclude_extensions_var.get(),
            "exclude_folders": self.exclude_folders_var.get(),
            "sort_mode": self.sort_mode_var.get(),
            "find_text": self.find_var.get(),
            "replace_text": self.replace_var.get(),
            "regex": self.regex_var.get(),
            "case_sensitive": self.case_sensitive_var.get(),
            "remove_text": self.remove_var.get(),
            "remove_range": self.remove_range_var.get(),
            "trim": self.trim_var.get(),
            "collapse_spaces": self.collapse_spaces_var.get(),
            "separator_style": self.separator_var.get(),
            "case_mode": self.case_mode_var.get(),
            "prefix": self.prefix_var.get(),
            "suffix": self.suffix_var.get(),
            "template": self.template_var.get(),
            "number_enabled": self.number_enabled_var.get(),
            "number_start": int(self.number_start_var.get()),
            "number_step": int(self.number_step_var.get()),
            "number_width": int(self.number_width_var.get()),
            "number_position": self.number_position_var.get(),
            "number_separator": self.number_separator_var.get(),
            "date_source": self.date_source_var.get(),
            "date_format": self.date_format_var.get(),
            "date_position": self.date_position_var.get(),
            "date_separator": self.date_separator_var.get(),
            "multi_ext": self.multi_ext_var.get(),
            "extension_mode": self.extension_mode_var.get(),
            "custom_extension": self.custom_extension_var.get(),
            "clean_invalid": self.clean_invalid_var.get(),
            "collision_mode": self.collision_mode_var.get(),
        }

    def refresh_preview(self) -> None:
        if not self.root_var.get().strip():
            self.preview_items = []
            self._fill_tree([])
            self._set_status(self.t("请选择文件夹"))
            return
        try:
            engine = RenameEngine(self.config())
            items = engine.scan()
            self.preview_items = engine.preview(items)
            self._fill_tree(self.preview_items)
            changed = sum(1 for item in self.preview_items if item.can_rename)
            blocked = sum(1 for item in self.preview_items if item.status in {"错误", "冲突"})
            self.count_var.set(self.t("{total} 项，{changed} 项将改名", total=len(self.preview_items), changed=changed))
            if blocked:
                self._set_status(self.t("有 {count} 项需要处理", count=blocked))
            else:
                self._set_status(self.t("预览已更新"))
        except Exception as exc:
            self.preview_items = []
            self._fill_tree([])
            self._set_status(str(exc))
            messagebox.showerror(self.t(APP_NAME), str(exc))

    def _fill_tree(self, items: list[PreviewItem]) -> None:
        self.tree.delete(*self.tree.get_children())
        for index, item in enumerate(items):
            tag = item.status
            self.tree.insert(
                "",
                END,
                iid=str(index),
                values=(self.t(item.status), item.source.name, item.target.name, str(item.source.parent), self.t(item.message)),
                tags=(tag,),
            )
        self.tree.tag_configure("错误", foreground="#b42318")
        self.tree.tag_configure("冲突", foreground="#b54708")
        self.tree.tag_configure("未变化", foreground="#667085")
        self.tree.tag_configure("就绪", foreground="#067647")

    def execute(self) -> None:
        self.refresh_preview()
        blocked = [item for item in self.preview_items if item.status in {"错误", "冲突"}]
        ready = [item for item in self.preview_items if item.can_rename]
        if blocked:
            messagebox.showwarning(self.t(APP_NAME), self.t("仍有冲突或错误，请先处理预览中的提示。"))
            return
        if not ready:
            messagebox.showinfo(self.t(APP_NAME), self.t("没有需要改名的项目。"))
            return
        if not messagebox.askyesno(self.t(APP_NAME), self.t("确认改名 {count} 项？", count=len(ready))):
            return

        try:
            history = self._rename_with_history(ready)
            self.last_history = history
            self._set_status(self.t("已完成 {count} 项，撤销记录已保存", count=len(ready)))
            messagebox.showinfo(self.t(APP_NAME), self.t("改名完成。"))
            self.refresh_preview()
        except Exception as exc:
            self._set_status(str(exc))
            messagebox.showerror(self.t(APP_NAME), str(exc))

    def _rename_with_history(self, items: list[PreviewItem]) -> Path:
        return rename_with_history(Path(self.root_var.get()), items)

    def undo_last(self) -> None:
        root_value = self.root_var.get().strip()
        if not root_value:
            messagebox.showinfo(self.t(APP_NAME), self.t("请先选择文件夹。"))
            return
        root = Path(root_value)
        history = self.last_history if self.last_history and self.last_history.exists() else self._latest_history(root)
        if not history:
            messagebox.showinfo(self.t(APP_NAME), self.t("没有找到可撤销的记录。"))
            return
        if not messagebox.askyesno(self.t(APP_NAME), self.t("撤销记录：{name}？", name=history.name)):
            return
        try:
            undo_history_file(history)
            self._set_status(self.t("已撤销上次改名"))
            messagebox.showinfo(self.t(APP_NAME), self.t("撤销完成。"))
            self.refresh_preview()
        except Exception as exc:
            self._set_status(str(exc))
            messagebox.showerror(self.t(APP_NAME), str(exc))

    def _latest_history(self, root: Path) -> Path | None:
        histories = sorted(root.glob(f"{HISTORY_PREFIX}*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
        return histories[0] if histories else None

    def reset_rules(self) -> None:
        mode = self.task_mode_var.get()
        if mode == "template":
            self.template_var.set("")
            self.number_enabled_var.set(False)
            self.number_start_var.set(1)
            self.number_step_var.set(1)
            self.number_width_var.set(3)
            self.sort_mode_var.set("名称 A-Z")
        elif mode == "extension":
            self.multi_ext_var.set(False)
            self.extension_mode_var.set("保留")
            self.custom_extension_var.set("")
        elif mode == "clean":
            self.trim_var.set(True)
            self.collapse_spaces_var.set(False)
            self.separator_var.set("不处理")
            self.case_mode_var.set("不处理")
        else:
            for variable in (
                self.find_var,
                self.replace_var,
                self.remove_var,
                self.remove_range_var,
                self.prefix_var,
                self.suffix_var,
            ):
                variable.set("")
            self.regex_var.set(False)
            self.case_sensitive_var.set(False)
        self.refresh_preview()

    def _set_status(self, value: str) -> None:
        self.status_var.set(value)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument("--config", help="读取 JSON 配置并以批处理方式运行")
    parser.add_argument("--execute", action="store_true", help="批处理模式下实际执行改名")
    parser.add_argument("--report", help="批处理报告 JSON 输出路径")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.config:
        return run_batch(Path(args.config), args.execute, Path(args.report) if args.report else None)
    app = BulkRenameApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
