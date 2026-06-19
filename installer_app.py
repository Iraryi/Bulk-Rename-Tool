from __future__ import annotations

import os
import argparse
import shutil
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import BOTH, LEFT, RIGHT, filedialog, messagebox
from tkinter import ttk


APP_EXE_NAME = "BulkRename.exe"
APP_FOLDER = "Bulk Rename Tool"
PORTABLE_MARKER = "portable.mode"
DATA_FOLDER = "BulkRenameData"
GITHUB_NAME = "Iraryi"


TEXT = {
    "zh": {
        "title": "Bulk Rename Tool 安装向导",
        "language_title": "选择安装器语言",
        "language_hint": "这只影响安装器界面，不会强制更改程序本身语言。",
        "welcome_title": "欢迎安装 Bulk Rename Tool",
        "welcome_body": "这是一个开源程序，你可以自行查看、修改和重新分发代码。\nGitHub 账号：Iraryi",
        "path_title": "选择安装位置",
        "path_hint": "选择一个父目录，安装器会自动在里面创建 “Bulk Rename Tool” 文件夹。",
        "browse": "选择",
        "mode_title": "选择安装模式",
        "normal": "普通模式",
        "normal_desc": "缓存、预设和上次配置保存在用户文档目录，适合日常电脑使用。",
        "portable": "便携模式",
        "portable_desc": "缓存、预设和上次配置都保存在安装目录的 BulkRenameData 文件夹里。",
        "shortcut_title": "选择快捷方式",
        "desktop": "创建桌面快捷方式",
        "start_menu": "创建开始菜单快捷方式",
        "ready_title": "准备安装",
        "install": "开始安装",
        "complete_title": "安装完成",
        "complete_body": "Bulk Rename Tool 已安装完成。",
        "back": "上一步",
        "next": "下一步",
        "finish": "完成",
        "cancel": "取消",
        "target": "安装到：",
        "mode": "安装模式：",
        "shortcuts": "快捷方式：",
        "error": "安装失败",
        "source_missing": "找不到要安装的主程序文件。",
    },
    "en": {
        "title": "Bulk Rename Tool Setup",
        "language_title": "Choose Setup Language",
        "language_hint": "This only changes the setup wizard. It does not force the app language.",
        "welcome_title": "Welcome to Bulk Rename Tool",
        "welcome_body": "This is an open-source program. You may inspect, modify, and redistribute the code.\nGitHub account: Iraryi",
        "path_title": "Choose Install Location",
        "path_hint": "Choose a parent folder. Setup will create a “Bulk Rename Tool” folder inside it.",
        "browse": "Browse",
        "mode_title": "Choose Install Mode",
        "normal": "Normal mode",
        "normal_desc": "Cache, presets, and last-used settings are stored in your Documents folder. Best for daily use on this PC.",
        "portable": "Portable mode",
        "portable_desc": "Cache, presets, and last-used settings are stored inside the installation folder under BulkRenameData.",
        "shortcut_title": "Choose Shortcuts",
        "desktop": "Create desktop shortcut",
        "start_menu": "Create Start Menu shortcut",
        "ready_title": "Ready to Install",
        "install": "Install",
        "complete_title": "Setup Complete",
        "complete_body": "Bulk Rename Tool has been installed.",
        "back": "Back",
        "next": "Next",
        "finish": "Finish",
        "cancel": "Cancel",
        "target": "Install to:",
        "mode": "Install mode:",
        "shortcuts": "Shortcuts:",
        "error": "Setup failed",
        "source_missing": "The application file to install was not found.",
    },
}


def resource_path(name: str) -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS")) / name
    return Path(__file__).resolve().parent / "dist" / name


def ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def create_shortcut(shortcut_path: Path, target_path: Path) -> None:
    shortcut_path.parent.mkdir(parents=True, exist_ok=True)
    script = f"""
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut({ps_quote(str(shortcut_path))})
$shortcut.TargetPath = {ps_quote(str(target_path))}
$shortcut.WorkingDirectory = {ps_quote(str(target_path.parent))}
$shortcut.IconLocation = {ps_quote(str(target_path))}
$shortcut.Save()
"""
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        check=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def resolve_target_dir(parent_dir: Path) -> Path:
    parent = parent_dir.expanduser()
    if parent.name.lower() == APP_FOLDER.lower():
        return parent
    return parent / APP_FOLDER


def install_files(parent_dir: Path, mode: str, desktop_shortcut: bool, start_menu_shortcut: bool) -> Path:
    source = resource_path(APP_EXE_NAME)
    if not source.exists():
        raise FileNotFoundError(f"{APP_EXE_NAME} was not found.")
    target_dir = resolve_target_dir(parent_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_exe = target_dir / APP_EXE_NAME
    shutil.copy2(source, target_exe)
    marker = target_dir / PORTABLE_MARKER
    if mode == "portable":
        marker.write_text("portable=1\n", encoding="utf-8")
        (target_dir / DATA_FOLDER).mkdir(exist_ok=True)
    elif marker.exists():
        marker.unlink()
    (target_dir / "README_INSTALL.txt").write_text(
        f"Bulk Rename Tool\nOpen-source program. GitHub account: {GITHUB_NAME}\n",
        encoding="utf-8",
    )
    if desktop_shortcut:
        desktop = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"
        create_shortcut(desktop / "Bulk Rename Tool.lnk", target_exe)
    if start_menu_shortcut:
        start_menu = Path(os.environ.get("APPDATA", str(Path.home()))) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / APP_FOLDER
        create_shortcut(start_menu / "Bulk Rename Tool.lnk", target_exe)
    return target_dir


class SetupApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.language_var = tk.StringVar(value="zh")
        local_app_data = Path(os.environ.get("LOCALAPPDATA", str(Path.home())))
        self.parent_dir_var = tk.StringVar(value=str(local_app_data / "Programs"))
        self.mode_var = tk.StringVar(value="normal")
        self.desktop_var = tk.BooleanVar(value=True)
        self.start_menu_var = tk.BooleanVar(value=True)
        self.page = 0
        self.pages = [
            self._page_language,
            self._page_welcome,
            self._page_path,
            self._page_mode,
            self._page_shortcuts,
            self._page_ready,
            self._page_complete,
        ]
        self.title(self.tr("title"))
        self.geometry("660x460")
        self.minsize(620, 420)
        self._style()
        self._build_shell()
        self._show_page()

    def tr(self, key: str) -> str:
        return TEXT[self.language_var.get()].get(key, key)

    def target_dir(self) -> Path:
        return resolve_target_dir(Path(self.parent_dir_var.get()))

    def _style(self) -> None:
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("TFrame", background="#f7f8fa")
        style.configure("TLabel", background="#f7f8fa", font=("Microsoft YaHei UI", 9))
        style.configure("Title.TLabel", background="#f7f8fa", font=("Microsoft YaHei UI", 15, "bold"))
        style.configure("Hint.TLabel", background="#f7f8fa", foreground="#667085")
        style.configure("TButton", padding=(12, 6), font=("Microsoft YaHei UI", 9))
        style.configure("Primary.TButton", padding=(12, 6), font=("Microsoft YaHei UI", 9, "bold"))

    def _build_shell(self) -> None:
        self.body = ttk.Frame(self, padding=22)
        self.body.pack(fill=BOTH, expand=True)
        self.nav = ttk.Frame(self, padding=(22, 0, 22, 18))
        self.nav.pack(fill="x")

    def _clear(self) -> None:
        for child in self.body.winfo_children():
            child.destroy()
        for child in self.nav.winfo_children():
            child.destroy()

    def _show_page(self) -> None:
        self.title(self.tr("title"))
        self._clear()
        self.pages[self.page]()
        self._build_nav()

    def _title(self, text_key: str) -> None:
        ttk.Label(self.body, text=self.tr(text_key), style="Title.TLabel").pack(anchor="w", pady=(0, 16))

    def _hint(self, text: str) -> None:
        ttk.Label(self.body, text=text, style="Hint.TLabel", wraplength=560, justify="left").pack(anchor="w", pady=(0, 14))

    def _page_language(self) -> None:
        self._title("language_title")
        self._hint(self.tr("language_hint"))
        for value, label in [("zh", "中文"), ("en", "English")]:
            ttk.Radiobutton(self.body, text=label, variable=self.language_var, value=value, command=self._show_page).pack(anchor="w", pady=6)

    def _page_welcome(self) -> None:
        self._title("welcome_title")
        self._hint(self.tr("welcome_body"))

    def _page_path(self) -> None:
        self._title("path_title")
        self._hint(self.tr("path_hint"))
        row = ttk.Frame(self.body)
        row.pack(fill="x", pady=(8, 8))
        entry = ttk.Entry(row, textvariable=self.parent_dir_var)
        entry.pack(side=LEFT, fill="x", expand=True, padx=(0, 8))
        ttk.Button(row, text=self.tr("browse"), command=self._browse_parent).pack(side=RIGHT)
        ttk.Label(self.body, text=f"{self.tr('target')} {self.target_dir()}", wraplength=560).pack(anchor="w", pady=(12, 0))

    def _page_mode(self) -> None:
        self._title("mode_title")
        ttk.Radiobutton(self.body, text=self.tr("normal"), variable=self.mode_var, value="normal").pack(anchor="w", pady=(2, 4))
        self._hint(self.tr("normal_desc"))
        ttk.Radiobutton(self.body, text=self.tr("portable"), variable=self.mode_var, value="portable").pack(anchor="w", pady=(10, 4))
        self._hint(self.tr("portable_desc"))

    def _page_shortcuts(self) -> None:
        self._title("shortcut_title")
        ttk.Checkbutton(self.body, text=self.tr("desktop"), variable=self.desktop_var).pack(anchor="w", pady=8)
        ttk.Checkbutton(self.body, text=self.tr("start_menu"), variable=self.start_menu_var).pack(anchor="w", pady=8)

    def _page_ready(self) -> None:
        self._title("ready_title")
        mode_label = self.tr("portable") if self.mode_var.get() == "portable" else self.tr("normal")
        shortcuts = []
        if self.desktop_var.get():
            shortcuts.append(self.tr("desktop"))
        if self.start_menu_var.get():
            shortcuts.append(self.tr("start_menu"))
        summary = (
            f"{self.tr('target')} {self.target_dir()}\n\n"
            f"{self.tr('mode')} {mode_label}\n\n"
            f"{self.tr('shortcuts')} {', '.join(shortcuts) if shortcuts else '-'}"
        )
        self._hint(summary)

    def _page_complete(self) -> None:
        self._title("complete_title")
        self._hint(self.tr("complete_body"))

    def _build_nav(self) -> None:
        if self.page == len(self.pages) - 1:
            ttk.Button(self.nav, text=self.tr("finish"), style="Primary.TButton", command=self.destroy).pack(side=RIGHT)
            return
        ttk.Button(self.nav, text=self.tr("cancel"), command=self.destroy).pack(side=RIGHT, padx=(8, 0))
        if self.page == len(self.pages) - 2:
            ttk.Button(self.nav, text=self.tr("install"), style="Primary.TButton", command=self._install).pack(side=RIGHT, padx=(8, 0))
        else:
            ttk.Button(self.nav, text=self.tr("next"), style="Primary.TButton", command=self._next).pack(side=RIGHT, padx=(8, 0))
        if self.page > 0:
            ttk.Button(self.nav, text=self.tr("back"), command=self._back).pack(side=RIGHT, padx=(8, 0))

    def _next(self) -> None:
        self.page = min(self.page + 1, len(self.pages) - 1)
        self._show_page()

    def _back(self) -> None:
        self.page = max(self.page - 1, 0)
        self._show_page()

    def _browse_parent(self) -> None:
        selected = filedialog.askdirectory(title=self.tr("path_title"), initialdir=self.parent_dir_var.get())
        if selected:
            self.parent_dir_var.set(selected)
            self._show_page()

    def _install(self) -> None:
        try:
            install_files(self.target_dir(), self.mode_var.get(), self.desktop_var.get(), self.start_menu_var.get())
            self.page = len(self.pages) - 1
            self._show_page()
        except Exception as exc:
            messagebox.showerror(self.tr("error"), str(exc), parent=self)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bulk Rename Tool setup")
    parser.add_argument("--install-to", help="Install to a parent folder without opening the wizard.")
    parser.add_argument("--mode", choices=["normal", "portable"], default="normal")
    parser.add_argument("--no-desktop-shortcut", action="store_true")
    parser.add_argument("--no-start-menu-shortcut", action="store_true")
    args = parser.parse_args()
    if args.install_to:
        install_files(
            Path(args.install_to),
            args.mode,
            not args.no_desktop_shortcut,
            not args.no_start_menu_shortcut,
        )
        return 0
    app = SetupApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
