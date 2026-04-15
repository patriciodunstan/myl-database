# -*- coding: utf-8 -*-
"""
Quick update scraper - solo datos de cartas, SIN imágenes.
Para actualizar la DB local con las cartas que faltan.
"""
import os
import json
import sqlite3
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = Path(os.environ.get("MYL_DATA_DIR", str(BASE_DIR / "data")))
DB_PATH = Path(os.environ.get("MYL_DB_PATH", str(DATA_DIR / "myl.db")))
API_BASE = "https://api.myl.cl"

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

def fetch_json(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MyL-Scraper/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"    Retry {attempt+1}: {e}")
            time.sleep(2)
    return None

def main():
    print("=" * 50)
    print("Quick DB Update - SOLO DATOS, SIN IMAGENES")
    print("=" * 50)
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    
    total_new = 0
    total_skipped = 0
    
    for i, slug in enumerate(EDITION_SLUGS):
        print(f"\n[{i+1}/{len(EDITION_SLUGS)}] {slug}...", end=" ", flush=True)
        
        url = f"{API_BASE}/cards/edition/{slug}"
        data = fetch_json(url)
        
        if not data or data.get("code") != 200:
            print("ERROR")
            continue
        
        cards = data.get("cards", [])
        edition_data = data.get("edition", {})
        edition_id = int(edition_data["id"])
        
        # Insert reference data
        for race in data.get("races", []):
            conn.execute("INSERT OR IGNORE INTO races (id, slug, name) VALUES (?, ?, ?)",
                        (int(race["id"]), race["slug"], race["name"]))
        for t in data.get("types", []):
            conn.execute("INSERT OR IGNORE INTO types (id, slug, name) VALUES (?, ?, ?)",
                        (int(t["id"]), t["slug"], t["name"]))
        for r in data.get("rarities", []):
            conn.execute("INSERT OR IGNORE INTO rarities (id, slug, name) VALUES (?, ?, ?)",
                        (int(r["id"]), r.get("slug", ""), r["name"]))
        
        # Insert edition
        conn.execute("INSERT OR IGNORE INTO editions (id, slug, title, image, date_release, flags) VALUES (?, ?, ?, ?, ?, ?)",
                    (edition_id, edition_data["slug"], edition_data.get("title", slug),
                     edition_data.get("image", ""), edition_data.get("date_release", ""),
                     int(edition_data.get("flags", 0))))
        
        # Insert cards
        new = 0
        for card in cards:
            try:
                cost = int(card["cost"]) if card.get("cost") else None
            except (ValueError, TypeError):
                cost = None
            try:
                damage = int(card["damage"]) if card.get("damage") else None
            except (ValueError, TypeError):
                damage = None
            
            cur = conn.execute(
                "SELECT id FROM cards WHERE id = ?", (int(card["id"]),))
            if cur.fetchone():
                total_skipped += 1
                continue
            
            conn.execute(
                """INSERT OR IGNORE INTO cards 
                   (id, edid, slug, name, edition_id, race_id, type_id, rarity_id, 
                    cost, damage, ability, flavour, keywords, image_path)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (int(card["id"]), card.get("edid", ""), card["slug"], card["name"],
                 edition_id,
                 int(card["race"]) if card.get("race") else None,
                 int(card["type"]) if card.get("type") else None,
                 int(card["rarity"]) if card.get("rarity") else None,
                 cost, damage,
                 card.get("ability", ""), card.get("flavour", ""),
                 card.get("keywords", ""),
                 f"{edition_id}/{card.get('edid', '')}.png"))
            new += 1
        
        conn.commit()
        total_new += new
        print(f"{len(cards)} total, {new} nuevas")
        
        # Update image paths for existing cards
        conn.execute("UPDATE cards SET image_path = edition_id || '/' || edid || '.png' WHERE edition_id = ? AND image_path IS NULL", (edition_id,))
        conn.commit()
        
        time.sleep(0.5)
    
    # Final count
    cur = conn.execute("SELECT COUNT(*) FROM cards")
    total = cur.fetchone()[0]
    
    print("\n" + "=" * 50)
    print(f"Nuevas cartas insertadas: {total_new}")
    print(f"Cartas ya existentes:     {total_skipped}")
    print(f"Total cartas en DB:       {total}")
    print("=" * 50)
    
    conn.close()

if __name__ == "__main__":
    main()
