# AYANEO Space Cover Art Fix Tool

[中文文档](README_zh_CN.md)

**Automatically fill in missing cover art for local games in AYANEO Space.**

AYANEO Space only auto-fetches cover images for Steam games. If you add local/non-Steam games (e.g., pirated games, standalone executables), they show up without cover art. This tool fixes that by searching the Steam Store API for matching games and writing the cover image URLs directly into AYANEO Space's database.

## Features

- Scans AYANEO Space's SQLite database for local games missing cover art
- Searches Steam Store API to find matching games by name
- Smart matching: prefers exact name matches, avoids DLCs/soundtracks
- Writes cover art, background image, and logo URLs
- Auto-backs up the database before any changes
- No dependency on Python runtime (standalone `.exe` available)

## Screenshot (Concept)

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

## Download

Go to [Releases](https://github.com/Haerqi/aya-cover-fix/releases) and download the latest `aya-cover-fix.exe`.

## Usage

### Quick Start

1. **Close AYANEO Space** (recommended, though not required)
2. Double-click `aya-cover-fix.exe`
3. Review the matched games
4. Press `Y` to apply
5. **Restart AYANEO Space** to see the changes

### Command Line Options

```bash
aya-cover-fix.exe              # Interactive mode (default)
aya-cover-fix.exe --dry-run    # Preview only, don't modify database
aya-cover-fix.exe --auto       # Skip confirmation, auto-apply
aya-cover-fix.exe --force      # Re-process ALL local games (even those with covers)
```

### Flags

| Flag | Description |
|------|-------------|
| `--dry-run` | Show what would be updated without making any changes |
| `--auto` | Skip the confirmation prompt |
| `--force` | Update all local games, including ones that already have cover art |

## How It Works

1. Reads the AYANEO Space database at `%APPDATA%\AYASpace\database.db`
2. Finds all `source='local'` games where `imageLibrary` is empty
3. For each game, searches the Steam Store API using the game name
4. Picks the best match (exact name preferred, DLCs/soundtracks filtered out)
5. Writes Steam CDN URLs for:
   - **Cover image** (`library_600x900.jpg`)
   - **Background image** (`page_bg_generated_v6b.jpg`)
   - **Logo** (`logo.png`)
6. Backs up the database before any changes

## Requirements

- Windows 10/11
- AYANEO Space installed (must have been run at least once)
- Internet connection (for Steam API)

## Build from Source

```bash
# Prerequisites: Python 3.8+, pip

# Install dependencies
pip install pyinstaller

# Build standalone executable
pyinstaller --onefile --console --name aya-cover-fix src/aya_cover_fix.py

# Output: dist/aya-cover-fix.exe
```

## Troubleshooting

**Q: Game not found on Steam?**
> Some games may not be on Steam. The tool will report "[!] Could not find on Steam" and skip that game. You'll need to add cover art manually.

**Q: Wrong game matched?**
> Use `--dry-run` first to preview matches. If a game consistently matches wrong, the Steam API may not have a good result for that name. You can manually update the database.

**Q: Changes not showing in AYANEO Space?**
> You must restart AYANEO Space after running the tool. If it still doesn't work, AYANEO Space may re-download its own data on startup — try closing it, running the tool, then opening it.

**Q: Something went wrong?**
> The tool creates a timestamped backup of the database before any changes (e.g., `database.db.backup_20260621_150700`). Copy the backup file back to `database.db` to restore.

## Disclaimer

This tool modifies AYANEO Space's local database at your own risk. Always keep backups. This project is not affiliated with or endorsed by AYANEO.

## License

MIT License
