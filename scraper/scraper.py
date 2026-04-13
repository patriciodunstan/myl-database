#!/usr/bin/env python3
"""
MyL Primer Bloque Extendido - Scraper & Database Builder
Descarga cartas de api.myl.cl y las almacena en SQLite con imagenes.
"""

import os
import sys
import json
import sqlite3
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# --- Config ---
BASE_DIR = Path(__file__).parent
DATA_DIR = Path(os.environ.get("MYL_DATA_DIR", str(BASE_DIR / "data")))
DB_PATH = Path(os.environ.get("MYL_DB_PATH", str(DATA_DIR / "myl.db")))
IMAGES_DIR = Path(os.environ.get("MYL_IMAGES_DIR", str(DATA_DIR / "images")))
API_BASE = "https://api.myl.cl"
IMG_BASE = "https://api.myl.cl/static/cards"
DELAY_BETWEEN_REQUESTS = 1.0
MAX_RETRIES = 3
MAX_IMAGE_WORKERS = 5

EDITION_SLUGS = [
    "espada-sagrada",
    "cruzadas",
    "helenica",
    "imperio",
    "hijos_de_daana",
    "tierras_altas",
    "dominios-de-ra",
    "encrucijada",
    "promocionales_primer_bloque",
    "raciales_pb",
    "leyendas_pb_3.0",
    "primer_bloque_2",
    "extensiones_pb_2023",
    "toolkit_fe_sin_limite",
    "toolkit_dragon_dorado",
    "toolkit_pb_magia_y_divinidad",
    "toolkit_pb_fuerza_y_destino",
    "espada_sagrada_aniversario",
    "helenica_aniversario",
    "dracula_pb",
    "dante_pb",
    "shogun_1",
    "shogun_ii",
]

# Banlist Racial Edicion - Abril 2026
BANLIST = {
    "prohibida": [
        "Ataque a Traicion", "Juglares", "Felipe II", "Dragon Dorado", "Joyero",
        "Curandera", "Caballo Lunar", "Hogar de Demonios", "Red de Aracne",
        "Romulo y Remo", "Rayos", "Eolo", "Forma de Toro", "Furias", "Urisk",
        "Traficante de Esclavos", "La Traicion de Macalpin", "Guiza",
        "Vuelta a lo primordial", "Nuh", "Daga de Bote", "Bas-Pef",
        "Kernuac el Cazador",
    ],
    "limitada_1": [
        "Totem de Nwyre", "Dragon Nival", "La Llama Fria", "Antorcha Olimpica",
        "Cesar Augusto", "Aceite de Oliva", "Leucrota", "Yelmo Alejandrino",
        "Gaitas", "Carmix", "Druida Maldito", "Ulster", "Rito de Aton",
        "Beni Hassam", "Pwyll", "Jinetes de Fuego", "Cathbadh el Druida",
        "Montuhopet II", "Fergus", "Jeroglificos", "Avalon", "Ptolomeo II",
        "Furia Irracional", "Tebas", "Baal-Zaphon", "Bennu", "Qer-Her",
        "Marmita Druida", "Kobold",
    ],
    "limitada_2": [
        "Mercaderes", "Ma'arrat an-Numan", "Fe sin Limite", "Idmon el Adivino",
        "Alejandro Magno", "Afrodita", "Corona del Dia", "Haquika", "Zagreus",
        "Papiros de Lahun", "Morir de Pie", "Helios", "Amergin el Druida",
        "Red de Plata", "Cantobele", "La Iliada", "Kamose el Guerrero",
        "Qadesh", "Panteon", "Mineros de Lapislazuli", "Amosis I",
    ],
}


def fetch_json(url, retries=MAX_RETRIES):
    """Fetch JSON from URL with retry logic."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MyL-Scraper/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            wait = (2 ** attempt)
            print(f"    Retry {attempt+1}/{retries} after error: {e} (waiting {wait}s)")
            time.sleep(wait)
    return None


def download_image(args):
    """Download a single card image. args = (edition_id, card_edid, dest_path)"""
    edition_id, card_edid, dest_path = args
    if dest_path.exists():
        return True, dest_path.name
    url = f"{IMG_BASE}/{edition_id}/{card_edid}.png"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MyL-Scraper/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(resp.read())
        return True, dest_path.name
    except Exception:
        return False, dest_path.name


def create_database():
    """Create SQLite database with schema."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS editions (
            id INTEGER PRIMARY KEY,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            image TEXT,
            date_release TEXT,
            flags INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS races (
            id INTEGER PRIMARY KEY,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS types (
            id INTEGER PRIMARY KEY,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS rarities (
            id INTEGER PRIMARY KEY,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY,
            edid TEXT,
            slug TEXT NOT NULL,
            name TEXT NOT NULL,
            edition_id INTEGER REFERENCES editions(id),
            race_id INTEGER REFERENCES races(id),
            type_id INTEGER REFERENCES types(id),
            rarity_id INTEGER REFERENCES rarities(id),
            cost INTEGER,
            damage INTEGER,
            ability TEXT,
            flavour TEXT,
            keywords TEXT,
            image_path TEXT,
            UNIQUE(slug, edition_id)
        );
        CREATE TABLE IF NOT EXISTS banlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_name TEXT NOT NULL,
            edition TEXT,
            format TEXT NOT NULL,
            restriction TEXT NOT NULL,
            updated TEXT DEFAULT '2026-04-07'
        );
        CREATE TABLE IF NOT EXISTS decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            race TEXT,
            format TEXT DEFAULT 'racial_edicion',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS deck_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER REFERENCES decks(id) ON DELETE CASCADE,
            card_id INTEGER REFERENCES cards(id),
            quantity INTEGER DEFAULT 1
        );
        CREATE INDEX IF NOT EXISTS idx_cards_name ON cards(name);
        CREATE INDEX IF NOT EXISTS idx_cards_race ON cards(race_id);
        CREATE INDEX IF NOT EXISTS idx_cards_type ON cards(type_id);
        CREATE INDEX IF NOT EXISTS idx_cards_edition ON cards(edition_id);
        CREATE INDEX IF NOT EXISTS idx_cards_cost ON cards(cost);
        CREATE INDEX IF NOT EXISTS idx_banlist_format ON banlist(format);
        CREATE INDEX IF NOT EXISTS idx_deck_cards_deck ON deck_cards(deck_id);
    """)
    conn.commit()
    return conn


def insert_reference_data(conn, data):
    """Insert races, types, rarities from API response."""
    for race in data.get("races", []):
        conn.execute(
            "INSERT OR IGNORE INTO races (id, slug, name) VALUES (?, ?, ?)",
            (int(race["id"]), race["slug"], race["name"])
        )
    for t in data.get("types", []):
        conn.execute(
            "INSERT OR IGNORE INTO types (id, slug, name) VALUES (?, ?, ?)",
            (int(t["id"]), t["slug"], t["name"])
        )
    for r in data.get("rarities", []):
        conn.execute(
            "INSERT OR IGNORE INTO rarities (id, slug, name) VALUES (?, ?, ?)",
            (int(r["id"]), r.get("slug", ""), r["name"])
        )
    conn.commit()


def insert_edition(conn, edition_data):
    """Insert edition record."""
    conn.execute(
        "INSERT OR IGNORE INTO editions (id, slug, title, image, date_release, flags) VALUES (?, ?, ?, ?, ?, ?)",
        (
            int(edition_data["id"]),
            edition_data["slug"],
            edition_data["title"],
            edition_data.get("image", ""),
            edition_data.get("date_release", ""),
            int(edition_data.get("flags", 0)),
        )
    )
    conn.commit()


def insert_cards(conn, cards, edition_id):
    """Insert card records for an edition."""
    inserted = 0
    for card in cards:
        try:
            cost = int(card["cost"]) if card.get("cost") else None
        except (ValueError, TypeError):
            cost = None
        try:
            damage = int(card["damage"]) if card.get("damage") else None
        except (ValueError, TypeError):
            damage = None

        conn.execute(
            """INSERT OR IGNORE INTO cards 
               (id, edid, slug, name, edition_id, race_id, type_id, rarity_id, 
                cost, damage, ability, flavour, keywords, image_path)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                int(card["id"]),
                card.get("edid", ""),
                card["slug"],
                card["name"],
                edition_id,
                int(card["race"]) if card.get("race") else None,
                int(card["type"]) if card.get("type") else None,
                int(card["rarity"]) if card.get("rarity") else None,
                cost,
                damage,
                card.get("ability", ""),
                card.get("flavour", ""),
                card.get("keywords", ""),
                None,  # will be updated after image download
            )
        )
        inserted += 1
    conn.commit()
    return inserted


def update_image_paths(conn, edition_id, edition_slug):
    """Update image_path for cards that have images downloaded."""
    pattern = f"{IMAGES_DIR}/{edition_id}/%"
    conn.execute(
        "UPDATE cards SET image_path = edition_id || '/' || edid || '.png' WHERE edition_id = ?",
        (edition_id,)
    )
    conn.commit()


def insert_banlist(conn):
    """Insert banlist data."""
    conn.execute("DELETE FROM banlist WHERE format = 'racial_edicion'")
    for restriction, cards in BANLIST.items():
        for card_name in cards:
            conn.execute(
                "INSERT INTO banlist (card_name, format, restriction) VALUES (?, 'racial_edicion', ?)",
                (card_name, restriction)
            )
    conn.commit()


def download_edition_images(edition_id, cards):
    """Download all card images for an edition in parallel."""
    edition_img_dir = IMAGES_DIR / str(edition_id)
    edition_img_dir.mkdir(parents=True, exist_ok=True)

    tasks = []
    for card in cards:
        edid = card.get("edid", "")
        if not edid:
            continue
        dest = edition_img_dir / f"{edid}.png"
        tasks.append((edition_id, edid, dest))

    if not tasks:
        return 0, 0

    downloaded = 0
    failed = 0
    with ThreadPoolExecutor(max_workers=MAX_IMAGE_WORKERS) as pool:
        futures = {pool.submit(download_image, t): t for t in tasks}
        for future in as_completed(futures):
            ok, name = future.result()
            if ok:
                downloaded += 1
            else:
                failed += 1
    return downloaded, failed


def main():
    print("=" * 60)
    print("MyL Primer Bloque Extendido - Scraper")
    print("=" * 60)

    conn = create_database()
    total_cards = 0
    total_images = 0
    total_errors = 0
    ref_data_loaded = False

    for i, slug in enumerate(EDITION_SLUGS):
        print(f"\n[{i+1}/{len(EDITION_SLUGS)}] Descargando: {slug}")
        
        url = f"{API_BASE}/cards/edition/{slug}"
        data = fetch_json(url)
        
        if not data or data.get("code") != 200:
            print(f"  ERROR: No se pudo obtener {slug}")
            total_errors += 1
            continue

        cards = data.get("cards", [])
        if not cards:
            print(f"  SIN CARTAS: {slug} (0 cartas)")
            continue

        edition_data = data.get("edition", {})
        edition_id = int(edition_data["id"])
        title = edition_data.get("title", slug)

        # Insert reference data (races, types, rarities) from first successful response
        if not ref_data_loaded:
            insert_reference_data(conn, data)
            ref_data_loaded = True

        insert_edition(conn, edition_data)
        inserted = insert_cards(conn, cards, edition_id)
        print(f"  {title}: {inserted} cartas insertadas")

        # Download images
        dl, fail = download_edition_images(edition_id, cards)
        total_images += dl
        if fail > 0:
            print(f"  Imagenes: {dl} OK, {fail} fallidas")
        else:
            print(f"  Imagenes: {dl} descargadas")

        update_image_paths(conn, edition_id, slug)
        total_cards += inserted

        # Rate limiting
        time.sleep(DELAY_BETWEEN_REQUESTS)

    # Insert banlist
    print("\nInsertando banlist Racial Edicion (Abril 2026)...")
    insert_banlist(conn)
    
    # Final stats
    cursor = conn.execute("SELECT COUNT(*) FROM editions")
    editions_count = cursor.fetchone()[0]
    cursor = conn.execute("SELECT COUNT(*) FROM cards")
    cards_count = cursor.fetchone()[0]
    cursor = conn.execute("SELECT COUNT(*) FROM banlist")
    banlist_count = cursor.fetchone()[0]

    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"  Ediciones procesadas: {len(EDITION_SLUGS)}")
    print(f"  Ediciones en BD:      {editions_count}")
    print(f"  Cartas insertadas:    {cards_count}")
    print(f"  Imagenes descargadas: {total_images}")
    print(f"  Cartas en banlist:    {banlist_count}")
    print(f"  Errores:              {total_errors}")
    print(f"\n  Base de datos: {DB_PATH}")
    print(f"  Imagenes:     {IMAGES_DIR}")
    print("=" * 60)

    conn.close()


if __name__ == "__main__":
    main()
