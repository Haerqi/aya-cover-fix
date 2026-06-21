"""
AYANEO Space Cover Art Fix Tool

Automatically finds local games in AYANEO Space that are missing cover art,
searches Steam Store API for matching games, and fills in cover image URLs.

Usage:
  aya-cover-fix.exe              # Interactive mode (shows preview, asks confirmation)
  aya-cover-fix.exe --dry-run    # Preview only, no database changes
  aya-cover-fix.exe --force      # Re-process ALL local games (even those with covers)
  aya-cover-fix.exe --auto        # Skip confirmation prompt, auto-apply
"""

import sqlite3
import urllib.request
import urllib.parse
import json
import sys
import os
import shutil

VERSION = "1.0.0"

# Steam image URL templates (CDN URLs used by AYANEO Space internally)
STEAM_CDN = "https://steamcdn-a.akamaihd.net/steam/apps/{appid}/library_600x900.jpg"
STEAM_BG = "https://cdn.akamai.steamstatic.com/steam/apps/{appid}/page_bg_generated_v6b.jpg"
STEAM_LOGO = "https://steamcdn-a.akamaihd.net/steam/apps/{appid}/logo.png"

# AYANEO Space database path
DB_PATH = os.path.join(os.environ.get("APPDATA", ""), "AYASpace", "database.db")

# Filter keywords to skip non-game entries
SKIP_KEYWORDS = ["soundtrack", "dlc", "design works", "wallpaper", "artbook", "ost"]


def ensure_utf8_console():
    """Fix console encoding on Windows."""
    if sys.platform == "win32":
        os.system("")  # Enable ANSI escape codes
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass


def search_steam(game_name):
    """Search Steam Store API for a game. Returns list of (appid, name, type)."""
    url = (
        f"https://store.steampowered.com/api/storesearch/"
        f"?term={urllib.parse.quote(game_name)}&l=english&cc=US"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        items = data.get("items", [])
        results = []
        for item in items:
            if item.get("type") == "app" and item.get("id"):
                name_lower = item.get("name", "").lower()
                if any(kw in name_lower for kw in SKIP_KEYWORDS):
                    continue
                results.append((item["id"], item.get("name", ""), item.get("type", "")))
        return results
    except Exception as e:
        print(f"  [ERROR] Steam API request failed: {e}")
        return []


def pick_best_match(results, search_term):
    """Pick the best match from Steam results, preferring exact name matches."""
    if not results:
        return None
    # Prefer exact match
    term_lower = search_term.lower().strip()
    for r in results:
        if r[1].lower().strip() == term_lower:
            return r
    # Avoid DLC/subtitle matches when searching for base game
    if ":" not in term_lower:
        for r in results:
            if ":" not in r[1]:
                return r
    # Fallback to first result
    return results[0]


def get_local_games(db_path, force=False):
    """Read local games from AYANEO Space database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if force:
        cursor.execute(
            "SELECT source, gameid, name, cname, exeFilePath, imageLibrary "
            "FROM Game WHERE source='local' AND isRemove=0"
        )
    else:
        cursor.execute(
            "SELECT source, gameid, name, cname, exeFilePath, imageLibrary "
            "FROM Game WHERE source='local' AND isRemove=0 "
            "AND (imageLibrary IS NULL OR imageLibrary = '')"
        )
    games = cursor.fetchall()
    conn.close()
    return games


def update_game_covers(db_path, gameid, appid):
    """Write cover art URLs into the database for a given game."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Game SET imageLibrary=?, imageBackground=?, clearLogo=? "
        "WHERE gameid=? AND source='local'",
        (
            STEAM_CDN.format(appid=appid),
            STEAM_BG.format(appid=appid),
            STEAM_LOGO.format(appid=appid),
            gameid,
        ),
    )
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected


def backup_db(db_path):
    """Create a timestamped backup of the database."""
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path + f".backup_{ts}"
    shutil.copy2(db_path, backup)
    return backup


def find_match_for_game(game):
    """Try to find a Steam match for a single game."""
    source, gameid, name, cname, exe_path, _ = game
    display_name = cname or name or (os.path.basename(exe_path) if exe_path else "Unknown")

    # Build list of search terms to try
    search_terms = []
    if name:
        search_terms.append(name)
    if cname and cname != name:
        search_terms.append(cname)
    if exe_path:
        folder = os.path.basename(os.path.dirname(exe_path))
        if folder and folder not in search_terms:
            search_terms.append(folder)

    for term in search_terms:
        print(f'  Searching Steam for: "{term}"')
        results = search_steam(term)
        if results:
            match = pick_best_match(results, term)
            if match:
                return {
                    "gameid": gameid,
                    "display_name": display_name,
                    "appid": match[0],
                    "steam_name": match[1],
                }
        print("  No match")

    return None


def main():
    ensure_utf8_console()

    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv
    auto = "--auto" in sys.argv

    print()
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║   AYANEO Space Cover Art Fix Tool v" + VERSION.ljust(14) + "║")
    print("  ║   Auto-fill missing game covers from Steam  ║")
    print("  ╚══════════════════════════════════════════════╝")
    print()

    # Validate database exists
    if not os.path.exists(DB_PATH):
        print(f"  [ERROR] AYANEO Space database not found at:")
        print(f"          {DB_PATH}")
        print()
        print("  Please make sure AYANEO Space is installed and has been run at least once.")
        sys.exit(1)

    # Read games
    games = get_local_games(DB_PATH, force)
    if not games:
        print("  All local games already have cover art. Nothing to do!")
        if not force:
            print("  (Use --force to re-process all games)")
        sys.exit(0)

    print(f"  Found {len(games)} local game(s) without cover art:\n")

    # Search Steam for each game
    updates = []
    for game in games:
        display_name = game[3] or game[2] or os.path.basename(game[4]) if game[4] else "Unknown"
        print(f"  - {display_name}")
        match = find_match_for_game(game)
        if match:
            print(f"    > Matched: Steam appid {match['appid']} \"{match['steam_name']}\"")
            updates.append(match)
        else:
            print(f"    [!] Could not find on Steam")
        print()

    if not updates:
        print("  No matching games found on Steam. Nothing to update.")
        sys.exit(0)

    # Show summary
    print("  " + "-" * 50)
    print(f"  {len(updates)} game(s) will be updated:")
    for u in updates:
        print(f"    {u['display_name']}  ->  Steam {u['appid']}")
    print("  " + "-" * 50)

    if dry_run:
        print()
        print("  [DRY RUN] No changes made. Run without --dry-run to apply.")
        sys.exit(0)

    # Confirm
    if not auto:
        print()
        try:
            confirm = input("  Apply changes? [Y/n] ").strip().lower()
            if confirm and confirm != "y":
                print("  Cancelled.")
                sys.exit(0)
        except (EOFError, KeyboardInterrupt):
            print("\n  Cancelled.")
            sys.exit(0)

    # Backup and apply
    print()
    backup = backup_db(DB_PATH)
    print(f"  Database backed up: {os.path.basename(backup)}")

    success_count = 0
    for u in updates:
        affected = update_game_covers(DB_PATH, u["gameid"], u["appid"])
        if affected > 0:
            print(f"  [OK] {u['display_name']}")
            success_count += 1
        else:
            print(f"  [FAIL] {u['display_name']} (0 rows affected)")

    print()
    print(f"  Done! {success_count}/{len(updates)} game(s) updated successfully.")
    print()
    print("  Please restart AYANEO Space to see the cover art changes.")
    print(f"  Backup: {backup}")
    print()


if __name__ == "__main__":
    main()
