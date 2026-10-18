#!/usr/bin/env python3
"""Публікація пінів у Pinterest через API v5.

Використання:
  python3 publish_pins.py boards            # показати дошки акаунта
  python3 publish_pins.py publish pins.csv  # опублікувати всі піни з CSV
  python3 publish_pins.py publish pins.csv --dry-run   # перевірити без публікації
"""
import base64
import csv
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_env() -> None:
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def api(method: str, path: str, body: dict | None = None) -> dict:
    token = os.environ.get("PINTEREST_ACCESS_TOKEN")
    if not token:
        sys.exit("Немає PINTEREST_ACCESS_TOKEN. Скопіюйте .env.example у .env і впишіть токен.")
    base = os.environ.get("PINTEREST_API_BASE", "https://api.pinterest.com/v5").rstrip("/")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{base}{path}",
        data=data,
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        sys.exit(f"Pinterest API {e.code} на {method} {path}: {detail}")


def list_boards() -> list[dict]:
    boards: list[dict] = []
    bookmark = None
    while True:
        query = f"?page_size=100&bookmark={bookmark}" if bookmark else "?page_size=100"
        page = api("GET", f"/boards{query}")
        boards.extend(page.get("items", []))
        bookmark = page.get("bookmark")
        if not bookmark:
            return boards


def image_payload(path: Path) -> dict:
    content_type = mimetypes.guess_type(path.name)[0] or "image/png"
    return {
        "source_type": "image_base64",
        "content_type": content_type,
        "data": base64.b64encode(path.read_bytes()).decode(),
    }


def create_pin(row: dict, board_id: str, dry_run: bool) -> None:
    image = ROOT / row["image"]
    if not image.exists():
        sys.exit(f"Немає файлу картинки: {image}")
    body = {
        "board_id": board_id,
        "title": row["title"][:100],
        "description": row.get("description", "")[:500],
        "link": row.get("link") or None,
        "alt_text": row.get("alt_text", "")[:500] or None,
        "media_source": image_payload(image),
    }
    body = {k: v for k, v in body.items() if v}
    if dry_run:
        print(f"[dry-run] {row['title']} -> дошка {row['board']} ({image.name})")
        return
    pin = api("POST", "/pins", body)
    print(f"Опубліковано: {row['title']} -> https://www.pinterest.com/pin/{pin['id']}/")


def publish(csv_path: Path, dry_run: bool) -> None:
    boards = {b["name"].strip().lower(): b["id"] for b in list_boards()}
    with csv_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        board_id = boards.get(row["board"].strip().lower())
        if not board_id:
            sys.exit(f"Дошку '{row['board']}' не знайдено. Доступні: {', '.join(boards) or 'немає'}")
        create_pin(row, board_id, dry_run)
    print(f"Готово: {len(rows)} пінів.")


def main() -> None:
    load_env()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry_run = "--dry-run" in sys.argv
    if not args or args[0] not in {"boards", "publish"}:
        sys.exit(__doc__)
    if args[0] == "boards":
        for b in list_boards():
            print(f"{b['id']}  {b['name']}  ({b.get('pin_count', 0)} пінів)")
        return
    publish(ROOT / (args[1] if len(args) > 1 else "pins.csv"), dry_run)


if __name__ == "__main__":
    main()
