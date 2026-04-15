"""Database connection and queries for MyL card database using SQLAlchemy 2.0 async."""
import logging
from collections import OrderedDict
from typing import Optional, Dict, List, Any

from sqlalchemy import select, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

import config
import models

from models import Base, Card, Edition, Race, Type, Rarity, Banlist, Deck, DeckCard


logger = logging.getLogger(__name__)

settings = config.get_settings()

# Convert postgresql:// to postgresql+asyncpg:// for async
database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

# Async engine and session factory
engine = create_async_engine(
    database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


from typing import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    logger.debug("Opening DB connection")
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            logger.debug("DB connection closed")


async def init_db():
    """Initialize database tables."""
    logger.info("Creating database tables if they don't exist...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


def _model_to_dict(model, *, join_data=None):
    """Convert SQLAlchemy model to dict with optional join data."""
    result = {c.name: getattr(model, c.name) for c in model.__table__.columns}
    if join_data:
        result.update(join_data)
    return result


# ---- Card queries ----

async def get_cards(
    search=None,
    race=None,
    card_type=None,
    edition=None,
    rarity=None,
    cost_min=None,
    cost_max=None,
    damage_min=None,
    damage_max=None,
    sort="name",
    page=1,
    per_page=50,
):
    """Get cards grouped by name (one result per unique card, with printings list)."""
    logger.info(
        "get_cards | search=%r race=%r type=%r edition=%r rarity=%r "
        "cost=[%s,%s] damage=[%s,%s] sort=%r page=%d per_page=%d",
        search, race, card_type, edition, rarity,
        cost_min, cost_max, damage_min, damage_max,
        sort, page, per_page,
    )

    conditions = []
    params = {}
    joins = []

    if search:
        conditions.append(Card.name.like(f"%{search}%"))
    if race:
        joins.append((Race, Card.race_id == Race.id))
        conditions.append(Race.name == race)
    if card_type:
        joins.append((Type, Card.type_id == Type.id))
        conditions.append(Type.name == card_type)
    if edition:
        joins.append((Edition, Card.edition_id == Edition.id))
        conditions.append(Edition.slug == edition)
    if rarity:
        joins.append((Rarity, Card.rarity_id == Rarity.id))
        conditions.append(Rarity.name == rarity)
    if cost_min is not None:
        conditions.append(Card.cost >= cost_min)
    if cost_max is not None:
        conditions.append(Card.cost <= cost_max)
    if damage_min is not None:
        conditions.append(Card.damage >= damage_min)
    if damage_max is not None:
        conditions.append(Card.damage <= damage_max)

    async with async_session_factory() as session:
        query = select(Card)
        for join_table, condition in joins:
            query = query.join(join_table, condition)

        if conditions:
            query = query.where(*conditions)

        query = query.options(
            selectinload(Card.edition),
            selectinload(Card.race),
            selectinload(Card.type),
            selectinload(Card.rarity),
        )

        query = query.order_by(Card.name.asc(), Card.id.asc())

        result = await session.execute(query)
        all_rows = result.scalars().all()
        logger.info("get_cards | fetched %d total rows before grouping", len(all_rows))

        # Convert to dicts
        cards_data = []
        for card in all_rows:
            card_dict = _model_to_dict(
                card,
                join_data={
                    "edition_title": card.edition.title if card.edition else None,
                    "edition_slug": card.edition.slug if card.edition else None,
                    "race_name": card.race.name if card.race else None,
                    "race_slug": card.race.slug if card.race else None,
                    "type_name": card.type.name if card.type else None,
                    "type_slug": card.type.slug if card.type else None,
                    "rarity_name": card.rarity.name if card.rarity else None,
                    "rarity_slug": card.rarity.slug if card.rarity else None,
                }
            )
            cards_data.append(card_dict)

    # Group by name — preserve insertion order (already name-sorted)
    grouped: OrderedDict[str, List[Dict[str, Any]]] = OrderedDict()
    for card in cards_data:
        grouped.setdefault(card["name"], []).append(card)

    # Build canonical card list: pick printing with most data, then highest id
    canonical_cards = []
    for name, printings in grouped.items():
        canonical: Dict[str, Any] = dict(max(printings, key=lambda c: (1 if c.get("ability") else 0, c["id"])))
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


async def get_card_by_id(card_id):
    """Get a single card by ID with joins."""
    logger.info("get_card_by_id | card_id=%d", card_id)

    async with async_session_factory() as session:
        query = (
            select(Card)
            .options(
                selectinload(Card.edition),
                selectinload(Card.race),
                selectinload(Card.type),
                selectinload(Card.rarity),
            )
            .where(Card.id == card_id)
        )
        result = await session.execute(query)
        card = result.scalar_one_or_none()

    if card:
        card_dict = _model_to_dict(
            card,
            join_data={
                "edition_title": card.edition.title if card.edition else None,
                "edition_slug": card.edition.slug if card.edition else None,
                "race_name": card.race.name if card.race else None,
                "race_slug": card.race.slug if card.race else None,
                "type_name": card.type.name if card.type else None,
                "type_slug": card.type.slug if card.type else None,
                "rarity_name": card.rarity.name if card.rarity else None,
                "rarity_slug": card.rarity.slug if card.rarity else None,
            }
        )
        logger.debug("get_card_by_id | found: %s", card_dict.get("name"))
        return card_dict
    else:
        logger.warning("get_card_by_id | card_id=%d not found", card_id)
        return None


async def search_cards(q, limit=20):
    """Search cards by name."""
    logger.info("search_cards | q=%r limit=%d", q, limit)

    async with async_session_factory() as session:
        query = (
            select(Card)
            .options(
                selectinload(Card.edition),
                selectinload(Card.race),
                selectinload(Card.type),
                selectinload(Card.rarity),
            )
            .where(Card.name.like(f"%{q}%"))
            .order_by(Card.name)
            .limit(limit)
        )
        result = await session.execute(query)
        cards = result.scalars().all()

    results = []
    for card in cards:
        results.append(_model_to_dict(
            card,
            join_data={
                "edition_title": card.edition.title if card.edition else None,
                "edition_slug": card.edition.slug if card.edition else None,
                "race_name": card.race.name if card.race else None,
                "type_name": card.type.name if card.type else None,
                "rarity_name": card.rarity.name if card.rarity else None,
            }
        ))

    logger.info("search_cards | q=%r → %d resultados", q, len(results))
    return results


# ---- Edition queries ----

async def get_editions():
    """Get all editions with card count."""
    logger.info("get_editions")

    async with async_session_factory() as session:
        query = (
            select(
                Edition.id,
                Edition.slug,
                Edition.title,
                Edition.image,
                Edition.date_release,
                Edition.flags,
                func.count(Card.id).label("card_count"),
            )
            .outerjoin(Card, Card.edition_id == Edition.id)
            .group_by(Edition.id)
            .order_by(Edition.title)
        )
        result = await session.execute(query)
        editions = [dict(row._mapping) for row in result.all()]

    logger.info("get_editions → %d ediciones", len(editions))
    return editions


async def get_edition_by_slug(slug):
    """Get a single edition by slug with card count."""
    logger.info("get_edition_by_slug | slug=%r", slug)

    async with async_session_factory() as session:
        query = (
            select(
                Edition.id,
                Edition.slug,
                Edition.title,
                Edition.image,
                Edition.date_release,
                Edition.flags,
                func.count(Card.id).label("card_count"),
            )
            .outerjoin(Card, Card.edition_id == Edition.id)
            .where(Edition.slug == slug)
            .group_by(Edition.id)
        )
        result = await session.execute(query)
        edition = result.one_or_none()

    if edition:
        edition_dict = dict(edition._mapping)
        logger.debug("get_edition_by_slug | found: %s", edition_dict.get("title"))
        return edition_dict
    else:
        logger.warning("get_edition_by_slug | slug=%r not found", slug)
        return None


# ---- Deck queries ----

async def get_decks():
    """Get all decks."""
    logger.info("get_decks")

    async with async_session_factory() as session:
        query = select(Deck).order_by(Deck.updated_at.desc())
        result = await session.execute(query)
        decks = [_model_to_dict(deck) for deck in result.scalars().all()]

    logger.info("get_decks → %d mazos", len(decks))
    return decks


async def get_deck(deck_id):
    """Get a single deck with its cards."""
    logger.info("get_deck | deck_id=%d", deck_id)

    async with async_session_factory() as session:
        deck = await session.get(Deck, deck_id)
        if not deck:
            logger.warning("get_deck | deck_id=%d not found", deck_id)
            return None

        # Get deck cards
        query = (
            select(DeckCard, Card, Edition, Race, Type, Rarity)
            .join(Card, DeckCard.card_id == Card.id)
            .join(Edition, Card.edition_id == Edition.id)
            .outerjoin(Race, Card.race_id == Race.id)
            .outerjoin(Type, Card.type_id == Type.id)
            .outerjoin(Rarity, Card.rarity_id == Rarity.id)
            .where(DeckCard.deck_id == deck_id)
            .order_by(Type.name, Card.cost, Card.name)
        )
        result = await session.execute(query)
        deck_cards_data = []

        for deck_card, card, edition, race, type_, rarity in result.all():
            cards_data = _model_to_dict(deck_card)
            cards_data.update(_model_to_dict(
                card,
                join_data={
                    "edition_title": edition.title if edition else None,
                    "edition_slug": edition.slug if edition else None,
                    "race_name": race.name if race else None,
                    "race_slug": race.slug if race else None,
                    "type_name": type_.name if type_ else None,
                    "type_slug": type_.slug if type_ else None,
                    "rarity_name": rarity.name if rarity else None,
                }
            ))
            deck_cards_data.append(cards_data)

        deck_dict = _model_to_dict(deck)
        deck_dict["cards"] = deck_cards_data
        logger.debug("get_deck | deck_id=%d name=%r cards=%d", deck_id, deck_dict.get("name"), len(deck_cards_data))
        return deck_dict


async def create_deck(name, race, format_type, cards):
    """Create a new deck with cards."""
    logger.info("create_deck | name=%r race=%r format=%r cards=%d", name, race, format_type, len(cards))

    async with async_session_factory() as session:
        deck = Deck(name=name, race=race, format=format_type)
        session.add(deck)
        await session.flush()
        deck_id = deck.id

        for card_entry in cards:
            deck_card = DeckCard(deck_id=deck_id, card_id=card_entry["card_id"], quantity=card_entry["quantity"])
            session.add(deck_card)

        await session.commit()
        logger.info("create_deck → deck_id=%d", deck_id)
        return deck_id


async def update_deck(deck_id, name=None, race=None, format_type=None, cards=None):
    """Update a deck."""
    logger.info("update_deck | deck_id=%d name=%r race=%r format=%r cards=%s",
                deck_id, name, race, format_type, len(cards) if cards is not None else "unchanged")

    async with async_session_factory() as session:
        deck = await session.get(Deck, deck_id)
        if not deck:
            logger.warning("update_deck | deck_id=%d not found", deck_id)
            return

        if name:
            deck.name = name
        if race:
            deck.race = race
        if format_type:
            deck.format = format_type
        deck.updated_at = func.now()

        if cards is not None:
            # Delete existing deck cards
            await session.execute(delete(DeckCard).where(DeckCard.deck_id == deck_id))
            # Insert new cards
            for card_entry in cards:
                deck_card = DeckCard(deck_id=deck_id, card_id=card_entry["card_id"], quantity=card_entry["quantity"])
                session.add(deck_card)
            deck.updated_at = func.now()

        await session.commit()
        logger.info("update_deck | deck_id=%d → OK", deck_id)


async def delete_deck(deck_id):
    """Delete a deck and its cards."""
    logger.info("delete_deck | deck_id=%d", deck_id)

    async with async_session_factory() as session:
        await session.execute(delete(DeckCard).where(DeckCard.deck_id == deck_id))
        await session.execute(delete(Deck).where(Deck.id == deck_id))
        await session.commit()
        logger.info("delete_deck | deck_id=%d → OK", deck_id)


async def validate_deck(deck_id):
    """Validate a deck against format rules."""
    logger.info("validate_deck | deck_id=%d", deck_id)
    deck = await get_deck(deck_id)
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

    banlist = await get_banlist(fmt)
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

async def get_banlist(fmt="racial_edicion"):
    """Get banlist entries for a format."""
    logger.info("get_banlist | format=%r", fmt)

    async with async_session_factory() as session:
        query = (
            select(Banlist)
            .where(Banlist.format == fmt)
            .order_by(Banlist.restriction, Banlist.card_name)
        )
        result = await session.execute(query)
        banlist_entries = [_model_to_dict(b) for b in result.scalars().all()]

    logger.info("get_banlist | format=%r → %d entradas", fmt, len(banlist_entries))
    return banlist_entries


async def check_banlist(card_name, fmt="racial_edicion"):
    """Check if a card is on the banlist."""
    logger.info("check_banlist | card_name=%r format=%r", card_name, fmt)

    async with async_session_factory() as session:
        query = select(Banlist).where(Banlist.card_name == card_name, Banlist.format == fmt)
        result = await session.execute(query)
        ban_entry = result.scalar_one_or_none()

    if ban_entry:
        result_dict = _model_to_dict(ban_entry)
        logger.info("check_banlist | %r → restriction=%s", card_name, result_dict.get("restriction"))
        return result_dict
    else:
        logger.debug("check_banlist | %r → no restriction found", card_name)
        return None


# ---- Simulator ----

async def simulate_draw(deck_id=None, cards=None):
    """Simulate a card draw from a deck."""
    import random
    logger.info("simulate_draw | deck_id=%s cards_provided=%s", deck_id, cards is not None)

    if deck_id:
        deck = await get_deck(deck_id)
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
                "edition_id": c.get("edition_id"),
                "edid": c.get("edid"),
            }
            for c in hand
        ],
        "deck_size": total,
        "remaining": remaining,
        "probabilities": probabilities,
    }


# ---- Stats ----

async def get_stats():
    """Get database statistics."""
    logger.info("get_stats")

    async with async_session_factory() as session:
        total_cards = await session.scalar(select(func.count(Card.id)))
        total_editions = await session.scalar(select(func.count(Edition.id)))
        total_decks = await session.scalar(select(func.count(Deck.id)))

        races_result = await session.execute(select(Race).order_by(Race.name))
        races = [_model_to_dict(r) for r in races_result.scalars().all()]

        types_result = await session.execute(select(Type).order_by(Type.name))
        types = [_model_to_dict(t) for t in types_result.scalars().all()]

        rarities_result = await session.execute(select(Rarity).order_by(Rarity.name))
        rarities = [_model_to_dict(r) for r in rarities_result.scalars().all()]

    stats = {
        "total_cards": total_cards,
        "total_editions": total_editions,
        "total_decks": total_decks,
        "races": races,
        "types": types,
        "rarities": rarities,
    }

    logger.info("get_stats → cards=%d editions=%d decks=%d",
                stats["total_cards"], stats["total_editions"], stats["total_decks"])
    return stats
