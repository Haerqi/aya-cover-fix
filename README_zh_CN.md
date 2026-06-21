# AYANEO Space 封面修复工具

[English](README.md)

**自动补全 AYANEO Space 中本地游戏缺失的封面图。**

AYANEO Space 只会自动获取 Steam 游戏的封面。如果你添加了本地/非 Steam 游戏（例如破解游戏、独立可执行文件），它们会显示为无封面状态。本工具通过搜索 Steam Store API 查找匹配的游戏，并将封面图片 URL 直接写入 AYANEO Space 的数据库，从而修复此问题。

## 功能特性

- 扫描 AYANEO Space 的 SQLite 数据库，找出缺失封面的本地游戏
- 通过游戏名称搜索 Steam Store API 以查找匹配项
- 智能匹配：优先精确名称匹配，自动过滤 DLC / 原声集
- 写入封面图、背景图和 Logo 的 URL
- 在修改前自动备份数据库
- 无需依赖 Python 运行环境（提供独立 `.exe` 文件）

## 截图（概念展示）

```
╔══════════════════════════════════════════════╗
║   AYANEO Space Cover Art Fix Tool v1.0.0     ║
║   Auto-fill missing game covers from Steam    ║
╚══════════════════════════════════════════════╝

Found 3 local game(s) without cover art:

 - Brotato
    Searching Steam for: "Brotato"
    > Matched: Steam appid 1942280 "Brotato"

 - SenrenBanka
    Searching Steam for: "SenrenBanka"
    > Matched: Steam appid 1144400 "SenrenBanka"

 - flowersblooming
    Searching Steam for: "flowersblooming"
    > Matched: Steam appid 1173010 "Flowers Blooming at the End of Summer"

 --------------------------------------------------
 3 game(s) will be updated:
    Brotato          ->  Steam 1942280
    SenrenBanka      ->  Steam 1144400
    flowersblooming  ->  Steam 1173010
 --------------------------------------------------

 Apply changes? [Y/n] Y

 Database backed up: database.db.backup_20260621_150700
 [OK] Brotato
 [OK] SenrenBanka
 [OK] flowersblooming

 Done! 3/3 game(s) updated successfully.

 Please restart AYANEO Space to see the cover art changes.
```

## 下载

前往 [Releases](https://github.com/Haerqi/aya-cover-fix/releases) 页面下载最新的 `aya-cover-fix.exe`。

## 使用方法

### 快速开始

1. **关闭 AYANEO Space**（推荐，非必须）
2. 双击运行 `aya-cover-fix.exe`
3. 查看匹配到的游戏列表
4. 按 `Y` 确认并应用修改
5. **重启 AYANEO Space** 以查看封面变化

### 命令行参数

```bash
aya-cover-fix.exe              # 交互模式（默认）
aya-cover-fix.exe --dry-run    # 仅预览，不修改数据库
aya-cover-fix.exe --auto       # 跳过确认，自动应用
aya-cover-fix.exe --force      # 重新处理所有本地游戏（包括已有封面的）
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `--dry-run` | 预览将要更新的内容，不执行任何修改 |
| `--auto` | 跳过确认提示，直接应用 |
| `--force` | 更新所有本地游戏，包括已有封面的 |

## 工作原理

1. 读取 AYANEO Space 数据库：`%APPDATA%\AYASpace\database.db`
2. 找出所有 `source='local'` 且 `imageLibrary` 为空的游戏
3. 对每个游戏，使用游戏名称搜索 Steam Store API
4. 选择最佳匹配项（优先精确名称匹配，过滤 DLC / 原声集）
5. 写入 Steam CDN 图片 URL：
   - **封面图**（`library_600x900.jpg`）
   - **背景图**（`page_bg_generated_v6b.jpg`）
   - **Logo**（`logo.png`）
6. 在修改前自动备份数据库

## 环境要求

- Windows 10 / 11
- 已安装 AYANEO Space（至少运行过一次）
- 网络连接（用于访问 Steam API）

## 从源码构建

```bash
# 前置依赖：Python 3.8+，pip

# 安装依赖
pip install pyinstaller

# 构建独立可执行文件
pyinstaller --onefile --console --name aya-cover-fix src/aya_cover_fix.py

# 输出：dist/aya-cover-fix.exe
```

## 常见问题

**问：游戏在 Steam 上找不到？**
> 部分游戏可能未上架 Steam。工具会报告「[!] Could not find on Steam」并跳过该游戏，你需要手动添加封面图。

**问：匹配到了错误的游戏？**
> 先使用 `--dry-run` 预览匹配结果。如果某个游戏持续匹配错误，可能是 Steam API 对该名称没有合适的结果，你可以手动修改数据库。

**问：AYANEO Space 中没有显示变化？**
> 运行工具后必须重启 AYANEO Space。如果仍然无效，AYANEO Space 可能在启动时重新下载自身数据——尝试先关闭它，再运行工具，然后再打开。

**问：出了什么问题？**
> 工具会在每次修改前创建一个带时间戳的数据库备份（例如 `database.db.backup_20260621_150700`）。将备份文件复制回 `database.db` 即可恢复。

## 免责声明

本工具修改 AYANEO Space 的本地数据库，使用风险由你自己承担。请务必保留备份。本项目与 AYANEO 无关，也未获得其认可或授权。

## 开源协议

MIT License
