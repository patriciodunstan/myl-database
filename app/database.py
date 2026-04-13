"""Database connection and queries for MyL card database."""
import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(os.environ.get("MYL_DB_PATH", str(Path(__file__).parent.parent / "scraper" / "data" / "myl.db")))
IMAGES_DIR = Path(os.environ.get("MYL_IMAGES_DIR", str(Path(__file__).parent.parent / "scraper" / "data" / "images")))


@contextmanager
def get_db():
    """Get database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def query_one(sql, params=()):
    with get_db() as conn:
        cur = conn.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None


def query_all(sql, params=()):
    with get_db() as conn:
        cur = conn.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]


def execute(sql, params=()):
    with get_db() as conn:
        conn.execute(sql, params)
        conn.commit()


def execute_many(sql, params_list):
    with get_db() as conn:
        conn.executemany(sql, params_list)
        conn.commit()


def execute_returning_id(sql, params=()):
    with get_db() as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid


# ---- Card queries ----

def get_cards(search=None, race=None, card_type=None, edition=None, rarity=None,
              cost_min=None, cost_max=None, damage_min=None, damage_max=None,
              sort="name", page=1, per_page=50):
    """Get cards with filters and pagination."""
    conditions = []
    params = []
    joins = ""

    if search:
        conditions.append("c.name LIKE ?")
        params.append(f"%{search}%")
    if race:
        joins += " JOIN races r2 ON c.race_id = r2.id"
        conditions.append("r2.slug = ?")
        params.append(race)
    if card_type:
        joins += " JOIN types t2 ON c.type_id = t2.id"
        conditions.append("t2.slug = ?")
        params.append(card_type)
    if edition:
        joins += " JOIN editions e2 ON c.edition_id = e2.id"
        conditions.append("e2.slug = ?")
        params.append(edition)
    if rarity:
        joins += " JOIN rarities ra2 ON c.rarity_id = ra2.id"
        conditions.append("ra2.slug = ?")
        params.append(rarity)
    if cost_min is not None:
        conditions.append("c.cost >= ?")
        params.append(cost_min)
    if cost_max is not None:
        conditions.append("c.cost <= ?")
        params.append(cost_max)
    if damage_min is not None:
        conditions.append("c.damage >= ?")
        params.append(damage_min)
    if damage_max is not None:
        conditions.append("c.damage <= ?")
        params.append(damage_max)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # Count
    count_sql = f"SELECT COUNT(*) as total FROM cards c {joins} {where}"
    total = query_one(count_sql, params)["total"]

    # Sort
    sort_map = {
        "name": "c.name ASC",
        "cost": "c.cost ASC",
        "damage": "COALESCE(c.damage, 0) DESC",
        "edition": "e.title ASC",
    }
    order = sort_map.get(sort, "c.name ASC")

    offset = (page - 1) * per_page
    data_sql = f"""
        SELECT c.*, e.title as edition_title, e.slug as edition_slug,
               r.name as race_name, r.slug as race_slug,
               t.name as type_name, t.slug as type_slug,
               ra.name as rarity_name, ra.slug as rarity_slug
        FROM cards c
        JOIN editions e ON c.edition_id = e.id
        LEFT JOIN races r ON c.race_id = r.id
        LEFT JOIN types t ON c.type_id = t.id
        LEFT JOIN rarities ra ON c.rarity_id = ra.id
        {joins}
        {where}
        ORDER BY {order}
        LIMIT ? OFFSET ?
    """
    cards = query_all(data_sql, params + [per_page, offset])

    return {
        "cards": cards,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }


def get_card_by_id(card_id):
    return query_one("""
        SELECT c.*, e.title as edition_title, e.slug as edition_slug,
               r.name as race_name, r.slug as race_slug,
               t.name as type_name, t.slug as type_slug,
               ra.name as rarity_name, ra.slug as rarity_slug
        FROM cards c
        JOIN editions e ON c.edition_id = e.id
        LEFT JOIN races r ON c.race_id = r.id
        LEFT JOIN types t ON c.type_id = t.id
        LEFT JOIN rarities ra ON c.rarity_id = ra.id
        WHERE c.id = ?
    """, (card_id,))


def search_cards(q, limit=20):
    return query_all("""
        SELECT c.id, c.name, c.cost, c.damage, c.slug,
               e.title as edition_title, e.slug as edition_slug,
               r.name as race_name, t.name as type_name, ra.name as rarity_name
        FROM cards c
        JOIN editions e ON c.edition_id = e.id
        LEFT JOIN races r ON c.race_id = r.id
        LEFT JOIN types t ON c.type_id = t.id
        LEFT JOIN rarities ra ON c.rarity_id = ra.id
        WHERE c.name LIKE ?
        ORDER BY c.name
        LIMIT ?
    """, (f"%{q}%", limit))


# ---- Edition queries ----

def get_editions():
    return query_all("""
        SELECT e.id, e.slug, e.title, e.image, e.date_release, e.flags,
               COUNT(c.id) as card_count
        FROM editions e
        LEFT JOIN cards c ON c.edition_id = e.id
        GROUP BY e.id
        ORDER BY e.title
    """)


def get_edition_by_slug(slug):
    return query_one("""
        SELECT e.id, e.slug, e.title, e.image, e.date_release, e.flags,
               COUNT(c.id) as card_count
        FROM editions e
        LEFT JOIN cards c ON c.edition_id = e.id
        WHERE e.slug = ?
        GROUP BY e.id
    """, (slug,))


# ---- Deck queries ----

def get_decks():
    return query_all("SELECT * FROM decks ORDER BY updated_at DESC")


def get_deck(deck_id):
    deck = query_one("SELECT * FROM decks WHERE id = ?", (deck_id,))
    if not deck:
        return None
    cards = query_all("""
        SELECT dc.quantity, c.*, e.title as edition_title, e.slug as edition_slug,
               r.name as race_name, r.slug as race_slug,
               t.name as type_name, t.slug as type_slug,
               ra.name as rarity_name
        FROM deck_cards dc
        JOIN cards c ON dc.card_id = c.id
        JOIN editions e ON c.edition_id = e.id
        LEFT JOIN races r ON c.race_id = r.id
        LEFT JOIN types t ON c.type_id = t.id
        LEFT JOIN rarities ra ON c.rarity_id = ra.id
        WHERE dc.deck_id = ?
        ORDER BY t.name, c.cost, c.name
    """, (deck_id,))
    deck["cards"] = cards
    return deck


def create_deck(name, race, format_type, cards):
    deck_id = execute_returning_id(
        "INSERT INTO decks (name, race, format) VALUES (?, ?, ?)",
        (name, race, format_type)
    )
    if cards:
        execute_many(
            "INSERT INTO deck_cards (deck_id, card_id, quantity) VALUES (?, ?, ?)",
            [(deck_id, c["card_id"], c["quantity"]) for c in cards]
        )
    return deck_id


def update_deck(deck_id, name=None, race=None, format_type=None, cards=None):
    if name:
        execute("UPDATE decks SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (name, deck_id))
    if race:
        execute("UPDATE decks SET race = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (race, deck_id))
    if format_type:
        execute("UPDATE decks SET format = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (format_type, deck_id))
    if cards is not None:
        execute("DELETE FROM deck_cards WHERE deck_id = ?", (deck_id,))
        if cards:
            execute_many(
                "INSERT INTO deck_cards (deck_id, card_id, quantity) VALUES (?, ?, ?)",
                [(deck_id, c["card_id"], c["quantity"]) for c in cards]
            )
        execute("UPDATE decks SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (deck_id,))


def delete_deck(deck_id):
    execute("DELETE FROM deck_cards WHERE deck_id = ?", (deck_id,))
    execute("DELETE FROM decks WHERE id = ?", (deck_id,))


def validate_deck(deck_id):
    """Validate a deck against format rules."""
    deck = get_deck(deck_id)
    if not deck:
        return {"valid": False, "errors": ["Mazo no encontrado"]}

    errors = []
    warnings = []

    cards = deck.get("cards", [])
    total_cards = sum(c["quantity"] for c in cards)
    race = deck.get("race", "")
    fmt = deck.get("format", "racial_edicion")

    # Total card count
    if total_cards < 40:
        errors.append(f"Mazo tiene {total_cards} cartas (minimo 40)")

    # Ally count
    ally_cards = [c for c in cards if c.get("type_slug") == "aliado"]
    ally_count = sum(c["quantity"] for c in ally_cards)
    if ally_count < 16:
        errors.append(f"Solo {ally_count} aliados (minimo 16)")

    # Race check for racial formats
    if fmt in ("racial_edicion", "racial_libre") and race:
        race_allies = [c for c in ally_cards if c.get("race_slug") == race]
        race_ally_count = sum(c["quantity"] for c in race_allies)
        # Allow Sin Raza allies too
        sin_raza_allies = [c for c in ally_cards if c.get("race_slug") == "noraza"]
        generic_ally_count = sum(c["quantity"] for c in sin_raza_allies)
        if race_ally_count + generic_ally_count < ally_count:
            non_race = ally_count - race_ally_count - generic_ally_count
            if non_race > 0:
                warnings.append(f"{non_race} aliados no son de raza {race} ni genericos")

    # Banlist check
    banlist = get_banlist(fmt)
    ban_map = {}
    for b in banlist:
        ban_map[b["card_name"].lower()] = b["restriction"]

    for card in cards:
        name_lower = card["name"].lower()
        qty = card["quantity"]
        restriction = ban_map.get(name_lower)
        if restriction == "prohibida" and qty > 0:
            errors.append(f"'{card['name']}' esta PROHIBIDA en este formato")
        elif restriction == "limitada_1" and qty > 1:
            errors.append(f"'{card['name']}' limitada a 1 copia (tienes {qty})")
        elif restriction == "limitada_2" and qty > 2:
            errors.append(f"'{card['name']}' limitada a 2 copias (tienes {qty})")
        elif qty > 3:
            errors.append(f"'{card['name']}' tiene {qty} copias (maximo 3)")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "card_count": total_cards,
        "ally_count": ally_count,
    }


# ---- Banlist queries ----

def get_banlist(fmt="racial_edicion"):
    return query_all(
        "SELECT * FROM banlist WHERE format = ? ORDER BY restriction, card_name",
        (fmt,)
    )


def check_banlist(card_name, fmt="racial_edicion"):
    return query_one(
        "SELECT * FROM banlist WHERE card_name = ? AND format = ?",
        (card_name, fmt)
    )


# ---- Simulator ----

def simulate_draw(deck_id=None, cards=None):
    import random
    if deck_id:
        deck = get_deck(deck_id)
        if not deck:
            return {"error": "Mazo no encontrado"}
        cards = deck.get("cards", [])
    elif not cards:
        return {"error": "Se necesita deck_id o cards"}

    # Build pool
    pool = []
    for c in cards:
        for _ in range(c.get("quantity", 1)):
            pool.append(c)

    if len(pool) < 7:
        return {"error": f"Mazo tiene {len(pool)} cartas, necesita al menos 7"}

    random.shuffle(pool)
    hand = pool[:7]
    remaining = len(pool) - 7

    # Compute probabilities
    from collections import Counter
    cost_dist = Counter()
    for c in pool:
        cost = c.get("cost") or 0
        cost_dist[cost] += 1

    total = len(pool)
    probabilities = {
        f"cost_{k}": round(v / total * 100, 1) for k, v in sorted(cost_dist.items())
    }

    return {
        "hand": [
            {
                "id": c["id"],
                "name": c["name"],
                "cost": c.get("cost"),
                "damage": c.get("damage"),
                "type_name": c.get("type_name"),
                "race_name": c.get("race_name"),
                "edition_title": c.get("edition_title"),
                "image_path": c.get("image_path"),
            }
            for c in hand
        ],
        "deck_size": total,
        "remaining": remaining,
        "probabilities": probabilities,
    }


# ---- Stats ----

def get_stats():
    stats = {}
    stats["total_cards"] = query_one("SELECT COUNT(*) as c FROM cards")["c"]
    stats["total_editions"] = query_one("SELECT COUNT(*) as c FROM editions")["c"]
    stats["total_decks"] = query_one("SELECT COUNT(*) as c FROM decks")["c"]
    stats["races"] = query_all("SELECT * FROM races ORDER BY name")
    stats["types"] = query_all("SELECT * FROM types ORDER BY name")
    stats["rarities"] = query_all("SELECT * FROM rarities ORDER BY name")
    return stats
