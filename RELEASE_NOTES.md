# Bulk Rename Tool / 批量改名工具 v1.0.0

## Release Assets / 发布文件

- `BulkRename.exe`  
  Direct-run Windows executable. No installation required.

- `BulkRenameSetup.exe`  
  Setup wizard with normal mode and portable mode.

## Highlights / 亮点

- Task-based UI for text rename, numbered templates, extension changes, and name cleanup.
- Global filter dialog with filter presets.
- Full workflow presets.
- Preview before execution with conflict detection.
- Undo history after rename.
- Chinese/English interface language support.
- Installer language selection.
- Normal install mode and portable install mode.
- Optional Desktop and Start Menu shortcuts, enabled by default.
- Open-source notice in setup wizard. GitHub account: `Iraryi`.

## Install Modes / 安装模式

### Normal Mode / 普通模式

Stores cache, presets, and last-used settings in the user's Documents folder.

缓存、预设和上次配置会保存在用户文档目录。

### Portable Mode / 便携模式

Creates `portable.mode` in the install folder. All cache and preset data is stored under `BulkRenameData` inside the install folder.

安装目录会创建 `portable.mode`，缓存和预设数据会保存在安装目录下的 `BulkRenameData` 中。

## Notes / 说明

Please preview rename results before executing. Batch rename operations can affect many files at once.

执行批量改名前请先预览结果。批量操作可能一次影响很多文件。
