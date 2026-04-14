"""Database connection and queries for MyL card database."""
import sqlite3
import os
import logging
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_PATH = Path(os.environ.get("MYL_DB_PATH", str(Path(__file__).parent.parent / "scraper" / "data" / "myl.db")))
IMAGES_DIR = Path(os.environ.get("MYL_IMAGES_DIR", str(Path(__file__).parent.parent / "scraper" / "data" / "images")))


@contextmanager
def get_db():
    """Get database connection with row factory."""
    logger.debug("Opening DB connection: %s", DB_PATH)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()
        logger.debug("DB connection closed")


def query_one(sql, params=()):
    logger.debug("query_one | sql=%s | params=%s", sql.strip(), params)
    with get_db() as conn:
        cur = conn.execute(sql, params)
        row = cur.fetchone()
        result = dict(row) if row else None
        logger.debug("query_one → %s", result)
        return result


def query_all(sql, params=()):
    logger.debug("query_all | sql=%s | params=%s", sql.strip(), params)
    with get_db() as conn:
        cur = conn.execute(sql, params)
        rows = [dict(row) for row in cur.fetchall()]
        logger.debug("query_all → %d rows", len(rows))
        return rows


def execute(sql, params=()):
    logger.debug("execute | sql=%s | params=%s", sql.strip(), params)
    with get_db() as conn:
        conn.execute(sql, params)
        conn.commit()


def execute_many(sql, params_list):
    logger.debug("execute_many | sql=%s | %d rows", sql.strip(), len(params_list))
    with get_db() as conn:
        conn.executemany(sql, params_list)
        conn.commit()


def execute_returning_id(sql, params=()):
    logger.debug("execute_returning_id | sql=%s | params=%s", sql.strip(), params)
    with get_db() as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        logger.debug("execute_returning_id → lastrowid=%d", cur.lastrowid)
        return cur.lastrowid


# ---- Card queries ----

def get_cards(search=None, race=None, card_type=None, edition=None, rarity=None,
              cost_min=None, cost_max=None, damage_min=None, damage_max=None,
              sort="name", page=1, per_page=50):
    """Get cards grouped by name (one result per unique card, with printings list)."""
    from collections import OrderedDict
    logger.info(
        "get_cards | search=%r race=%r type=%r edition=%r rarity=%r "
        "cost=[%s,%s] damage=[%s,%s] sort=%r page=%d per_page=%d",
        search, race, card_type, edition, rarity,
        cost_min, cost_max, damage_min, damage_max,
        sort, page, per_page,
    )
    conditions = []
    params = []
    joins = ""

    if search:
        conditions.append("c.name LIKE ?")
        params.append(f"%{search}%")
    if race:
        joins += " JOIN races r2 ON c.race_id = r2.id"
        conditions.append("r2.name = ?")
        params.append(race)
    if card_type:
        joins += " JOIN types t2 ON c.type_id = t2.id"
        conditions.append("t2.name = ?")
        params.append(card_type)
    if edition:
        joins += " JOIN editions e2 ON c.edition_id = e2.id"
        conditions.append("e2.slug = ?")
        params.append(edition)
    if rarity:
        joins += " JOIN rarities ra2 ON c.rarity_id = ra2.id"
        conditions.append("ra2.name = ?")
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
    logger.debug("get_cards | conditions=%s | params=%s | joins=%r", conditions, params, joins)

    # Fetch all matching rows sorted by name (grouping happens in Python)
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
        ORDER BY c.name ASC, c.id ASC
    """
    logger.debug("get_cards data_sql: %s | params=%s", data_sql.strip(), params)
    all_rows = query_all(data_sql, params)
    logger.info("get_cards | fetched %d total rows before grouping", len(all_rows))

    # Group by name — preserve insertion order (already name-sorted)
    grouped: dict = OrderedDict()
    for card in all_rows:
        grouped.setdefault(card["name"], []).append(card)

    # Build canonical card list: pick the printing with most data, then highest id
    canonical_cards = []
    for name, printings in grouped.items():
        canonical = dict(max(printings, key=lambda c: (1 if c.get("ability") else 0, c["id"])))
        canonical["printings"] = printings
        canonical_cards.append(canonical)

    # Re-sort for non-name sorts (name order already correct from SQL)
    if sort == "cost":
        canonical_cards.sort(key=lambda c: (c["cost"] if c["cost"] is not None else 9999))
    elif sort == "damage":
        canonical_cards.sort(key=lambda c: (c["damage"] if c["damage"] is not None else -1), reverse=True)
    elif sort == "edition":
        canonical_cards.sort(key=lambda c: (c.get("edition_title") or ""))

    total = len(canonical_cards)
    offset = (page - 1) * per_page
    page_cards = canonical_cards[offset:offset + per_page]

    logger.info("get_cards | %d unique cards (page %d, returning %d)", total, page, len(page_cards))
    return {
        "cards": page_cards,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }


def get_card_by_id(card_id):
    logger.info("get_card_by_id | card_id=%d", card_id)
    result = query_one("""
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
    if result:
        logger.debug("get_card_by_id | found: %s", result.get("name"))
    else:
        logger.warning("get_card_by_id | card_id=%d not found", card_id)
    return result


def search_cards(q, limit=20):
    logger.info("search_cards | q=%r limit=%d", q, limit)
    results = query_all("""
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
    logger.info("search_cards | q=%r → %d resultados", q, len(results))
    return results


# ---- Edition queries ----

def get_editions():
    logger.info("get_editions")
    results = query_all("""
        SELECT e.id, e.slug, e.title, e.image, e.date_release, e.flags,
               COUNT(c.id) as card_count
        FROM editions e
        LEFT JOIN cards c ON c.edition_id = e.id
        GROUP BY e.id
        ORDER BY e.title
    """)
    logger.info("get_editions → %d ediciones", len(results))
    return results


def get_edition_by_slug(slug):
    logger.info("get_edition_by_slug | slug=%r", slug)
    result = query_one("""
        SELECT e.id, e.slug, e.title, e.image, e.date_release, e.flags,
               COUNT(c.id) as card_count
        FROM editions e
        LEFT JOIN cards c ON c.edition_id = e.id
        WHERE e.slug = ?
        GROUP BY e.id
    """, (slug,))
    if result:
        logger.debug("get_edition_by_slug | found: %s", result.get("title"))
    else:
        logger.warning("get_edition_by_slug | slug=%r not found", slug)
    return result


# ---- Deck queries ----

def get_decks():
    logger.info("get_decks")
    results = query_all("SELECT * FROM decks ORDER BY updated_at DESC")
    logger.info("get_decks → %d mazos", len(results))
    return results


def get_deck(deck_id):
    logger.info("get_deck | deck_id=%d", deck_id)
    deck = query_one("SELECT * FROM decks WHERE id = ?", (deck_id,))
    if not deck:
        logger.warning("get_deck | deck_id=%d not found", deck_id)
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
    logger.debug("get_deck | deck_id=%d name=%r cards=%d", deck_id, deck.get("name"), len(cards))
    return deck


def create_deck(name, race, format_type, cards):
    logger.info("create_deck | name=%r race=%r format=%r cards=%d", name, race, format_type, len(cards))
    deck_id = execute_returning_id(
        "INSERT INTO decks (name, race, format) VALUES (?, ?, ?)",
        (name, race, format_type)
    )
    if cards:
        execute_many(
            "INSERT INTO deck_cards (deck_id, card_id, quantity) VALUES (?, ?, ?)",
            [(deck_id, c["card_id"], c["quantity"]) for c in cards]
        )
    logger.info("create_deck → deck_id=%d", deck_id)
    return deck_id


def update_deck(deck_id, name=None, race=None, format_type=None, cards=None):
    logger.info("update_deck | deck_id=%d name=%r race=%r format=%r cards=%s",
                deck_id, name, race, format_type, len(cards) if cards is not None else "unchanged")
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
    logger.info("update_deck | deck_id=%d → OK", deck_id)


def delete_deck(deck_id):
    logger.info("delete_deck | deck_id=%d", deck_id)
    execute("DELETE FROM deck_cards WHERE deck_id = ?", (deck_id,))
    execute("DELETE FROM decks WHERE id = ?", (deck_id,))
    logger.info("delete_deck | deck_id=%d → OK", deck_id)


def validate_deck(deck_id):
    """Validate a deck against format rules."""
    logger.info("validate_deck | deck_id=%d", deck_id)
    deck = get_deck(deck_id)
    if not deck:
        logger.warning("validate_deck | deck_id=%d not found", deck_id)
        return {"valid": False, "errors": ["Mazo no encontrado"]}

    errors = []
    warnings = []

    cards = deck.get("cards", [])
    total_cards = sum(c["quantity"] for c in cards)
    race = deck.get("race", "")
    fmt = deck.get("format", "racial_edicion")

    logger.debug("validate_deck | deck_id=%d total_cards=%d race=%r format=%r", deck_id, total_cards, race, fmt)

    if total_cards < 40:
        errors.append(f"Mazo tiene {total_cards} cartas (minimo 40)")

    ally_cards = [c for c in cards if c.get("type_slug") == "aliado"]
    ally_count = sum(c["quantity"] for c in ally_cards)
    if ally_count < 16:
        errors.append(f"Solo {ally_count} aliados (minimo 16)")

    if fmt in ("racial_edicion", "racial_libre") and race:
        race_allies = [c for c in ally_cards if c.get("race_slug") == race]
        race_ally_count = sum(c["quantity"] for c in race_allies)
        sin_raza_allies = [c for c in ally_cards if c.get("race_slug") == "noraza"]
        generic_ally_count = sum(c["quantity"] for c in sin_raza_allies)
        if race_ally_count + generic_ally_count < ally_count:
            non_race = ally_count - race_ally_count - generic_ally_count
            if non_race > 0:
                warnings.append(f"{non_race} aliados no son de raza {race} ni genericos")

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

    result = {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "card_count": total_cards,
        "ally_count": ally_count,
    }
    logger.info("validate_deck | deck_id=%d → valid=%s errors=%d warnings=%d",
                deck_id, result["valid"], len(errors), len(warnings))
    return result


# ---- Banlist queries ----

def get_banlist(fmt="racial_edicion"):
    logger.info("get_banlist | format=%r", fmt)
    results = query_all(
        "SELECT * FROM banlist WHERE format = ? ORDER BY restriction, card_name",
        (fmt,)
    )
    logger.info("get_banlist | format=%r → %d entradas", fmt, len(results))
    return results


def check_banlist(card_name, fmt="racial_edicion"):
    logger.info("check_banlist | card_name=%r format=%r", card_name, fmt)
    result = query_one(
        "SELECT * FROM banlist WHERE card_name = ? AND format = ?",
        (card_name, fmt)
    )
    if result:
        logger.info("check_banlist | %r → restriction=%s", card_name, result.get("restriction"))
    else:
        logger.debug("check_banlist | %r → no restriction found", card_name)
    return result


# ---- Simulator ----

def simulate_draw(deck_id=None, cards=None):
    import random
    logger.info("simulate_draw | deck_id=%s cards_provided=%s", deck_id, cards is not None)
    if deck_id:
        deck = get_deck(deck_id)
        if not deck:
            logger.warning("simulate_draw | deck_id=%s not found", deck_id)
            return {"error": "Mazo no encontrado"}
        cards = deck.get("cards", [])

    elif not cards:
        logger.warning("simulate_draw | no deck_id and no cards provided")
        return {"error": "Se necesita deck_id o cards"}

    pool = []
    for c in cards:
        for _ in range(c.get("quantity", 1)):
            pool.append(c)

    logger.debug("simulate_draw | pool_size=%d", len(pool))

    if len(pool) < 7:
        logger.warning("simulate_draw | pool too small: %d cards", len(pool))
        return {"error": f"Mazo tiene {len(pool)} cartas, necesita al menos 7"}

    random.shuffle(pool)
    hand = pool[:7]
    remaining = len(pool) - 7

    from collections import Counter
    cost_dist = Counter()
    for c in pool:
        cost = c.get("cost") or 0
        cost_dist[cost] += 1

    total = len(pool)
    probabilities = {
        f"cost_{k}": round(v / total * 100, 1) for k, v in sorted(cost_dist.items())
    }

    logger.info("simulate_draw | hand=%d remaining=%d deck_size=%d", len(hand), remaining, total)

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
    logger.info("get_stats")
    stats = {}
    stats["total_cards"] = query_one("SELECT COUNT(*) as c FROM cards")["c"]
    stats["total_editions"] = query_one("SELECT COUNT(*) as c FROM editions")["c"]
    stats["total_decks"] = query_one("SELECT COUNT(*) as c FROM decks")["c"]
    stats["races"] = query_all("SELECT * FROM races ORDER BY name")
    stats["types"] = query_all("SELECT * FROM types ORDER BY name")
    stats["rarities"] = query_all("SELECT * FROM rarities ORDER BY name")
    logger.info("get_stats → cards=%d editions=%d decks=%d",
                stats["total_cards"], stats["total_editions"], stats["total_decks"])
    return stats
