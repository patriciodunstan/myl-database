"""MyL Primer Bloque Extendido - FastAPI Backend."""
import os
import logging
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import database as db
import httpx
import config

settings = config.get_settings()

NOTION_TOKEN = settings.notion_token
NOTION_FEEDBACK_DB_ID = settings.notion_feedback_db_id

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up... initializing database tables")
    await db.init_db()
    logger.info("Database tables initialized")
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(title="MyL Primer Bloque - Base de Datos", version="1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
# Images are served from remote URL (proxy fallback) - no local storage needed
IMAGES_DIR = Path(__file__).parent.parent / "scraper" / "data" / "images"  # For backward compatibility, not used


@app.get("/images/{path:path}")
async def serve_image(path: str):
    img_path = IMAGES_DIR / path
    if img_path.exists():
        logger.debug("GET /images/%s → local file", path)
        return FileResponse(str(img_path))
    remote_url = f"https://api.myl.cl/static/cards/{path}"
    logger.info("GET /images/%s → not found locally, proxying from %s", path, remote_url)
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(remote_url)
            if resp.status_code == 200:
                logger.debug("GET /images/%s → proxy OK (%d bytes)", path, len(resp.content))
                return Response(content=resp.content, media_type="image/png")
            logger.warning("GET /images/%s → proxy returned status %d", path, resp.status_code)
        except httpx.HTTPError as exc:
            logger.error("GET /images/%s → proxy error: %s", path, exc)
    raise HTTPException(status_code=404, detail="Imagen no encontrada")


# ---- Cards ----

def _int_or_none(val):
    """Convert empty strings to None, then to int."""
    if val is None or val == "":
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None

def _str_or_none(val):
    """Convert empty strings to None."""
    if val is None or val == "":
        return None
    return val


@app.get("/api/cartas")
async def list_cartas(
    search: Optional[str] = Query(None),
    race: Optional[str] = Query(None),
    type: Optional[str] = Query(None, alias="type"),
    edition: Optional[str] = Query(None),
    rarity: Optional[str] = Query(None),
    cost_min: Optional[str] = Query(None),
    cost_max: Optional[str] = Query(None),
    damage_min: Optional[str] = Query(None),
    damage_max: Optional[str] = Query(None),
    power_min: Optional[str] = Query(None),
    power_max: Optional[str] = Query(None),
    sort: Optional[str] = Query("name"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
):
    logger.info(
        "GET /api/cartas | search=%r race=%r type=%r edition=%r rarity=%r "
        "cost=[%s,%s] damage=[%s,%s] power=[%s,%s] sort=%r page=%d per_page=%d",
        search, race, type, edition, rarity,
        cost_min, cost_max, damage_min, damage_max, power_min, power_max,
        sort, page, per_page,
    )
    d_min = _int_or_none(damage_min) or _int_or_none(power_min)
    d_max = _int_or_none(damage_max) or _int_or_none(power_max)
    result = await db.get_cards(
        search=_str_or_none(search), race=_str_or_none(race),
        card_type=_str_or_none(type), edition=_str_or_none(edition),
        rarity=_str_or_none(rarity),
        cost_min=_int_or_none(cost_min), cost_max=_int_or_none(cost_max),
        damage_min=d_min, damage_max=d_max,
        sort=_str_or_none(sort) or "name", page=page, per_page=per_page,
    )
    logger.info("GET /api/cartas → total=%d page=%d/%d", result["total"], page, result["total_pages"])
    return result


@app.get("/api/cartas/search")
async def search_cartas(q: str = Query(..., min_length=1), limit: int = Query(20)):
    logger.info("GET /api/cartas/search | q=%r limit=%d", q, limit)
    results = await db.search_cards(q, limit)
    logger.info("GET /api/cartas/search → %d resultados", len(results))
    return {"results": results}


@app.get("/api/cartas/{card_id}")
async def get_carta(card_id: int):
    logger.info("GET /api/cartas/%d", card_id)
    card = await db.get_card_by_id(card_id)
    if not card:
        logger.warning("GET /api/cartas/%d → 404 not found", card_id)
        raise HTTPException(status_code=404, detail="Carta no encontrada")
    logger.debug("GET /api/cartas/%d → encontrada: %s", card_id, card.get("name"))
    return card


# ---- Editions ----

@app.get("/api/ediciones")
async def list_ediciones():
    logger.info("GET /api/ediciones")
    editions = await db.get_editions()
    logger.info("GET /api/ediciones → %d ediciones", len(editions))
    return {"editions": editions}

@app.get("/api/ediciones/{slug}")
async def get_edicion(slug: str):
    logger.info("GET /api/ediciones/%s", slug)
    edition = await db.get_edition_by_slug(slug)
    if not edition:
        logger.warning("GET /api/ediciones/%s → 404 not found", slug)
        raise HTTPException(status_code=404, detail="Edicion no encontrada")
    logger.debug("GET /api/ediciones/%s → %s", slug, edition.get("title"))
    return edition


# ---- Decks ----

@app.get("/api/mazos")
async def list_mazos():
    logger.info("GET /api/mazos")
    decks = await db.get_decks()
    logger.info("GET /api/mazos → %d mazos", len(decks))
    return {"decks": decks}

@app.post("/api/mazos")
async def create_mazo(body: dict):
    logger.info("POST /api/mazos | name=%r race=%r format=%r cards=%d",
                body.get("name"), body.get("race"), body.get("format"), len(body.get("cards", [])))
    if not body.get("name"):
        logger.warning("POST /api/mazos → 400 nombre requerido")
        raise HTTPException(status_code=400, detail="Nombre requerido")
    deck_id = await db.create_deck(
        name=body["name"],
        race=body.get("race", ""),
        format_type=body.get("format", "racial_edicion"),
        cards=body.get("cards", []),
    )
    logger.info("POST /api/mazos → creado deck_id=%d", deck_id)
    return {"id": deck_id, "message": "Mazo creado"}

@app.get("/api/mazos/{deck_id}")
async def get_mazo(deck_id: int):
    logger.info("GET /api/mazos/%d", deck_id)
    deck = await db.get_deck(deck_id)
    if not deck:
        logger.warning("GET /api/mazos/%d → 404 not found", deck_id)
        raise HTTPException(status_code=404, detail="Mazo no encontrado")
    logger.debug("GET /api/mazos/%d → %s (%d cartas)", deck_id, deck.get("name"), len(deck.get("cards", [])))
    return deck

@app.put("/api/mazos/{deck_id}")
async def update_mazo(deck_id: int, body: dict):
    logger.info("PUT /api/mazos/%d | body=%r", deck_id, {k: v for k, v in body.items() if k != "cards"})
    existing = await db.get_deck(deck_id)
    if not existing:
        logger.warning("PUT /api/mazos/%d → 404 not found", deck_id)
        raise HTTPException(status_code=404, detail="Mazo no encontrado")
    await db.update_deck(
        deck_id=deck_id,
        name=body.get("name"),
        race=body.get("race"),
        format_type=body.get("format"),
        cards=body.get("cards"),
    )
    logger.info("PUT /api/mazos/%d → actualizado", deck_id)
    return {"message": "Mazo actualizado"}

@app.delete("/api/mazos/{deck_id}")
async def delete_mazo(deck_id: int):
    logger.info("DELETE /api/mazos/%d", deck_id)
    await db.delete_deck(deck_id)
    logger.info("DELETE /api/mazos/%d → eliminado", deck_id)
    return {"message": "Mazo eliminado"}

@app.get("/api/mazos/{deck_id}/validate")
async def validate_mazo(deck_id: int):
    logger.info("GET /api/mazos/%d/validate", deck_id)
    result = await db.validate_deck(deck_id)
    if result is None:
        logger.warning("GET /api/mazos/%d/validate → 404 not found", deck_id)
        raise HTTPException(status_code=404, detail="Mazo no encontrado")
    logger.info("GET /api/mazos/%d/validate → valid=%s errors=%d warnings=%d",
                deck_id, result.get("valid"), len(result.get("errors", [])), len(result.get("warnings", [])))
    return result


# ---- Banlist ----

@app.get("/api/banlist")
async def get_banlist(format: str = Query("racial_edicion")):
    logger.info("GET /api/banlist | format=%r", format)
    banlist = await db.get_banlist(format)
    logger.info("GET /api/banlist → %d entradas", len(banlist))
    return {"banlist": banlist}

@app.get("/api/banlist/check/{card_name}")
async def check_ban(card_name: str, format: str = Query("racial_edicion")):
    logger.info("GET /api/banlist/check/%s | format=%r", card_name, format)
    result = await db.check_banlist(card_name, format)
    if result:
        logger.info("GET /api/banlist/check/%s → restriction=%s", card_name, result.get("restriction"))
        return result
    logger.debug("GET /api/banlist/check/%s → sin restricciones", card_name)
    return {"card_name": card_name, "restriction": "none", "message": "Sin restricciones"}

# ---- Simulator ----

@app.post("/api/simular")
async def simular(body: dict):
    deck_id = body.get("deck_id")
    cards = body.get("cards")
    logger.info("POST /api/simular | deck_id=%s cards_count=%s", deck_id, len(cards) if cards else None)
    result = await db.simulate_draw(deck_id=deck_id, cards=cards)
    if "error" in result:
        logger.warning("POST /api/simular → error: %s", result["error"])
        raise HTTPException(status_code=400, detail=result["error"])
    logger.info("POST /api/simular → hand=%d cartas, deck_size=%d", len(result.get("hand", [])), result.get("deck_size", 0))
    return result

# ---- Contacto ----

@app.post("/api/contacto")
async def create_contacto(body: dict):
    nombre = (body.get("nombre") or "").strip()
    email = (body.get("email") or "").strip() or None
    tipo = body.get("tipo") or "Otro"
    mensaje = (body.get("mensaje") or "").strip()

    if not nombre or not mensaje:
        raise HTTPException(status_code=400, detail="Nombre y mensaje son requeridos")
    if not NOTION_TOKEN:
        raise HTTPException(status_code=503, detail="Servicio de contacto no configurado")

    payload = {
        "parent": {"database_id": NOTION_FEEDBACK_DB_ID},
        "properties": {
            "Nombre": {"title": [{"text": {"content": nombre}}]},
            "Tipo": {"select": {"name": tipo}},
            "Mensaje": {"rich_text": [{"text": {"content": mensaje}}]},
            "Estado": {"select": {"name": "Nuevo"}},
        },
    }
    if email:
        payload["properties"]["Email"] = {"email": email}

    logger.info("POST /api/contacto | nombre=%r tipo=%r", nombre, tipo)
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            "https://api.notion.com/v1/pages",
            headers={
                "Authorization": f"Bearer {NOTION_TOKEN}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json",
            },
            json=payload,
        )
    if resp.status_code != 200:
        logger.error("Notion API error %d: %s", resp.status_code, resp.text)
        raise HTTPException(status_code=502, detail="Error al guardar el contacto")

    logger.info("POST /api/contacto → guardado en Notion OK")
    return {"message": "Mensaje enviado correctamente"}


# ---- Stats ----

@app.get("/api/stats")
async def stats():
    logger.info("GET /api/stats")
    result = await db.get_stats()
    logger.info("GET /api/stats → total_cards=%d total_editions=%d",
                result.get("total_cards", 0), result.get("total_editions", 0))
    return result


# ---- Run ----
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
