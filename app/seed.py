#!/usr/bin/env python3
"""
MyL Database Seed Script
Populates PostgreSQL with cards from api.myl.cl.
Run with: python -m seed
"""

import asyncio
import sys

import httpx
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

import config

from models import Base, Edition, Race, Type, Rarity, Card, Banlist


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


# Edition slugs to download
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

# Banlist for racial_edicion format (Abril 2026)
BANLIST = {
    "prohibida": [
        "ataque a traicion", "juglares", "felipe ii", "dragon dorado", "joyero",
        "curandera", "caballo lunar", "hogar de demonios", "red de aracne",
        "romulo y remo", "rayos", "eolo", "forma de toro", "furias", "urisk",
        "traficante de esclavos", "la traicion de macalpin", "guiza",
        "vuelta a lo primordial", "nuh", "daga de bote", "bas-pef",
        "kernuac el cazador", "fergus", "hechiceros del caos", "carro celta",
    ],
    "limitada_1": [
        "totem de nwyre", "dragon nival", "la llama fria", "antorcha olimpica",
        "cesar augusto", "aceite de oliva", "leucrota", "yelmo alejandrino",
        "gaitas", "carmix", "druida maldito", "ulster", "rito de aton",
        "beni hassam", "pwyll", "jinetes de fuego", "cathbadh el druida",
        "montuhopet ii", "jeroglificos", "avalon", "ptolomeo ii",
        "furia irracional", "tebas", "baal-zaphon", "bennu", "qer-her",
        "marmita druida", "kobold", "montuhopet i", "amosis i", "canopic",
        "djed", "gato egipcio",
    ],
    "limitada_2": [
        "ma'arrat an-numan", "fe sin limite", "idmon el adivino",
        "alejandro magno", "afrodita", "corona del dia", "haquika", "zagreus",
        "papiros de lahun", "morir de pie", "helios", "amergin el druida",
        "red de plata", "cantobele", "la iliada", "kamose el guerrero",
        "qadesh", "panteon", "mineros de lapislazuli", "amosis i",
    ],
}

API_BASE = "https://api.myl.cl"


async def fetch_json(client: httpx.AsyncClient, url: str, retries: int = 3) -> dict | None:
    """Fetch JSON from URL with retry logic (async, non-blocking)."""
    for attempt in range(retries):
        try:
            resp = await client.get(url, timeout=30.0)
            resp.raise_for_status()
            return resp.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            wait = 2 ** attempt
            print(f"    Retry {attempt+1}/{retries} after error: {e} (waiting {wait}s)")
            await asyncio.sleep(wait)
    return None


async def insert_reference_data(session, data):
    """Insert races, types, rarities from API response."""
    for race in data.get("races", []):
        stmt = insert(Race).values(
            id=int(race["id"]),
            slug=race["slug"],
            name=race["name"]
        ).on_conflict_do_nothing(
            index_elements=[Race.id]
        )
        await session.execute(stmt)

    for t in data.get("types", []):
        stmt = insert(Type).values(
            id=int(t["id"]),
            slug=t["slug"],
            name=t["name"]
        ).on_conflict_do_nothing(
            index_elements=[Type.id]
        )
        await session.execute(stmt)

    for r in data.get("rarities", []):
        stmt = insert(Rarity).values(
            id=int(r["id"]),
            slug=r.get("slug", ""),
            name=r["name"]
        ).on_conflict_do_nothing(
            index_elements=[Rarity.id]
        )
        await session.execute(stmt)

    await session.commit()
    races = data.get("races", [])
    types = data.get("types", [])
    rarities = data.get("rarities", [])
    print(f"  Reference data: {len(races)} races, "
          f"{len(types)} types, "
          f"{len(rarities)} rarities")


async def insert_edition(session, edition_data):
    """Insert edition record."""
    stmt = insert(Edition).values(
        id=int(edition_data["id"]),
        slug=edition_data["slug"],
        title=edition_data["title"],
        image=edition_data.get("image", ""),
        date_release=edition_data.get("date_release", ""),
        flags=int(edition_data.get("flags", 0)),
    ).on_conflict_do_nothing(index_elements=[Edition.id])
    await session.execute(stmt)
    await session.commit()


async def insert_cards(session, cards, edition_id):
    """Insert card records for an edition. Uses Card.id (PK) for conflict resolution."""
    inserted = 0
    failed = 0

    for card in cards:
        try:
            cost = int(card["cost"]) if card.get("cost") else None
        except (ValueError, TypeError):
            cost = None

        try:
            damage = int(card["damage"]) if card.get("damage") else None
        except (ValueError, TypeError):
            damage = None

        try:
            stmt = insert(Card).values(
                id=int(card["id"]),
                edid=card.get("edid", ""),
                slug=card["slug"],
                name=card["name"],
                edition_id=edition_id,
                race_id=int(card["race"]) if card.get("race") else None,
                type_id=int(card["type"]) if card.get("type") else None,
                rarity_id=int(card["rarity"]) if card.get("rarity") else None,
                cost=cost,
                damage=damage,
                ability=card.get("ability", ""),
                flavour=card.get("flavour", ""),
                keywords=card.get("keywords", ""),
                image_path=None,
            ).on_conflict_do_nothing(index_elements=[Card.id])
            await session.execute(stmt)
            inserted += 1
        except Exception as e:
            failed += 1
            print(f"    ERROR inserting card {card.get('name', '?')} (id={card.get('id')}): {e}")

    await session.commit()
    if failed > 0:
        print(f"    WARNING: {failed} cards failed to insert")
    return inserted


async def insert_banlist(session):
    """Insert banlist data."""
    for restriction, cards in BANLIST.items():
        for card_name in cards:
            stmt = insert(Banlist).values(
                card_name=card_name,
                format="racial_edicion",
                restriction=restriction
            ).on_conflict_do_nothing(index_elements=[Banlist.card_name, Banlist.format])
            await session.execute(stmt)
    await session.commit()
    total = sum(len(cards) for cards in BANLIST.values())
    print(f"  Banlist inserted: {total} entries")


async def main():
    """Main seed function."""
    print("=" * 60)
    print("MyL Database Seed - PostgreSQL")
    print("=" * 60)

    settings = config.get_settings()
    db_display = settings.database_url[:50] + "..." if settings.database_url else "(empty)"
    print(f"Database URL: {db_display}")

    # Create tables
    print("\nCreating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created.")

    # Check if already seeded — use CARD count, not edition count
    async with async_session_factory() as session:
        card_count = await session.scalar(select(func.count(Card.id)))
        if card_count and card_count > 100:
            print(f"\nDatabase already has {card_count} cards. Skipping seed.")
            return

    # Download and insert data using async httpx client
    total_cards = 0
    ref_data_loaded = False

    async with httpx.AsyncClient(
        headers={"User-Agent": "MyL-Seed/2.0"},
        follow_redirects=True,
    ) as client:
        for i, slug in enumerate(EDITION_SLUGS):
            print(f"\n[{i+1}/{len(EDITION_SLUGS)}] Downloading: {slug}")

            url = f"{API_BASE}/cards/edition/{slug}"
            data = await fetch_json(client, url)

            if not data or data.get("code") != 200:
                print(f"  ERROR: Could not fetch {slug}")
                continue

            cards = data.get("cards", [])
            if not cards:
                print(f"  NO CARDS: {slug} (0 cards)")
                continue

            edition_data = data.get("edition", {})
            edition_id = int(edition_data["id"])
            title = edition_data.get("title", slug)

            async with async_session_factory() as session:
                # Insert reference data from first successful response
                if not ref_data_loaded:
                    await insert_reference_data(session, data)
                    ref_data_loaded = True

                await insert_edition(session, edition_data)
                inserted = await insert_cards(session, cards, edition_id)
                print(f"  {title}: {inserted} cards inserted")

            total_cards += inserted

    # Insert banlist
    print("\nInserting banlist for Racial Edicion (Abril 2026)...")
    async with async_session_factory() as session:
        await insert_banlist(session)

    # Final stats
    async with async_session_factory() as session:
        edition_count = await session.scalar(select(func.count(Edition.id)))
        cards_count = await session.scalar(select(func.count(Card.id)))
        banlist_count = await session.scalar(select(func.count(Banlist.id)))

    print("\n" + "=" * 60)
    print("SEED COMPLETE")
    print("=" * 60)
    print(f"  Editions processed: {len(EDITION_SLUGS)}")
    print(f"  Editions in DB:      {edition_count}")
    print(f"  Cards in DB:         {cards_count}")
    print(f"  Banlist entries:     {banlist_count}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\nFATAL: Seed failed with error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
