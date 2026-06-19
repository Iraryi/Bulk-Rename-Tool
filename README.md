# Bulk Rename Tool / 批量改名工具

Bulk Rename Tool is a clean Windows desktop app for batch renaming files and folders. It is designed for normal users first: choose a folder, choose the rename task that matches your need, preview every change, then execute only when the result is clear.

Bulk Rename Tool 是一个面向普通用户的 Windows 批量改名工具。它的设计目标是：先选择文件夹，再按需求进入对应任务界面，所有改名前都能预览，确认无误后再执行。

GitHub account / GitHub 账号: `Iraryi`

## Downloads / 下载

The release provides two Windows executables:

- `BulkRename.exe`: portable single-file app. Double-click to run directly.
- `BulkRenameSetup.exe`: setup wizard. It can install the app in normal mode or portable mode.

Release 会提供两个 Windows 文件：

- `BulkRename.exe`：直接运行版，双击即可使用。
- `BulkRenameSetup.exe`：安装向导版，可选择普通模式或便携模式。

## Main Features / 主要功能

- Task-based home screen: Text Rename, Numbered Template, Extension Change, Name Cleanup, and Settings.
- Global filters are available from every editing page and can be saved as filter presets.
- Full preset save/load for complete workflows.
- Preview table shows original name, new name, folder, status, and warnings before execution.
- Collision detection and optional automatic numbering for duplicate names.
- Undo history is saved after rename operations.
- First launch asks for interface language and remembers it.
- Last-used settings are restored, but scanning starts only after clicking Preview.
- Clean, resize-aware UI with a wider default workspace for complete text display.

- 主界面按任务分类：普通重命名、编号模板、扩展名修改、名称清理、设置。
- 筛选是全局功能，在每个编辑页面都能快速打开，并可保存为筛选预设。
- 支持保存/加载整套改名方案。
- 执行前预览原名称、新名称、所在文件夹、状态和提示。
- 检测重名冲突，可选择自动追加序号。
- 执行后保存撤销记录。
- 首次启动会询问界面语言，并记住选择。
- 自动恢复上次配置，但不会启动时自动扫描，点击 Preview/预览 后才扫描。
- 默认窗口采用更宽的工作型比例，减少文字截断。

## Rename Modes / 改名模式

### Text Rename / 普通重命名

Use this mode for common text operations:

- Find and replace text.
- Regular expression replacement.
- Case-sensitive matching.
- Remove specific text.
- Remove characters by position range.
- Add prefix or suffix.

适合常见文字处理：查找替换、正则替换、区分大小写、删除指定文字、按位置删除、加前缀或后缀。

### Numbered Template / 编号模板

Generate names from a template after sorting files by a useful order.

Supported variables include:

- `#NUM#`: number generated from the current order.
- `#DATE#`: date based on the selected date source and format.
- `#NAME#`: current base name.
- `#ORIGINAL#`: original file name without extension.
- `#EXT#`: extension without dot.
- `#PARENT#`: parent folder name.
- `#MTIME#`: modified time.
- `#CTIME#`: created time.
- `#TODAY#`: today.

可以按名称、修改时间、创建时间、大小、扩展名、路径深度等顺序排序，然后用模板生成新名称，例如 `Photo_#NUM#` 或 `#DATE#_#NUM#`。

### Extension Change / 扩展名修改

Change extensions without changing base names:

- Keep extension.
- Convert extension to lowercase.
- Convert extension to uppercase.
- Set a custom extension such as `jpg`.
- Remove extension.
- Optional multi-part extension handling.

用于批量把 `.jpeg` 改为 `.jpg`、统一 `.TXT` 为 `.txt`、移除临时扩展名等。

### Name Cleanup / 名称清理

Clean existing names without designing a full template:

- Trim leading/trailing spaces.
- Collapse repeated spaces.
- Convert case.
- Convert spaces, underscores, and hyphens.

用于清理多余空格、统一大小写、调整空格/下划线/短横线风格。

## Filters / 筛选

Filters apply to every rename mode. They are intentionally separate from rename output modes.

Supported filter fields:

- File types/extensions.
- Wildcards.
- Name contains text.
- Exclude wildcards.
- Exclude text.
- Exclude extensions.
- Exclude folders.

筛选适用于所有改名模式，并且可以单独保存/加载，不会覆盖当前改名规则。

## Settings / 设置

Settings contains:

- Filter presets.
- Full presets.
- Date source and date format.
- Safety behavior.
- Variable reference.
- Interface language.

设置页集中管理筛选预设、整套预设、日期格式、安全策略、变量说明和界面语言。

## Install Modes / 安装模式

`BulkRenameSetup.exe` supports two install modes:

- Normal mode: cache, presets, and last-used settings are stored in the user's Documents folder.
- Portable mode: the installer creates `portable.mode`; cache, presets, and last-used settings are stored in `BulkRenameData` inside the installation folder.

`BulkRenameSetup.exe` 支持两种模式：

- 普通模式：缓存、预设、上次配置保存在用户文档目录。
- 便携模式：安装目录里会创建 `portable.mode`，缓存、预设、上次配置会保存在安装目录的 `BulkRenameData` 文件夹中。

## Build From Source / 从源码构建

Requirements:

- Windows
- Python 3.10
- PyInstaller

Build both release files:

```powershell
.\build_exe.ps1
```

Output files:

```text
dist\BulkRename.exe
dist\BulkRenameSetup.exe
```

## Run From Source / 运行源码

```powershell
py -3.10 bulk_rename_app.py
```

## Batch Mode / 批处理模式

The same rename engine can run from JSON config:

```powershell
.\dist\BulkRename.exe --config D:\TEST\config.json --execute --report D:\TEST\report.json
```

Without `--execute`, it only writes a preview report and does not rename files.

不加 `--execute` 时只生成预览报告，不实际改名。

## Safety Notes / 安全说明

- Always preview before executing.
- Conflicts and invalid names are shown before rename.
- Rename operations create undo history.
- Testing during development should use a dedicated safe folder.

- 执行前请先预览。
- 冲突和非法名称会在预览中提示。
- 改名后会保存撤销记录。
- 开发测试建议只在专门测试目录中进行。

## License / 开源许可

This project is released under the MIT License. See `LICENSE` for details.

本项目使用 MIT License 开源。详见 `LICENSE`。
