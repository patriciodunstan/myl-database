"""MyL Primer Bloque Extendido - FastAPI Backend."""
import os
from pathlib import Path
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import database as db
import httpx

app = FastAPI(title="MyL Primer Bloque - Base de Datos", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
STATIC_DIR = Path(__file__).parent / "static"
IMAGES_DIR = Path(__file__).parent.parent / "scraper" / "data" / "images"


# ---- Static files ----
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/images/{path:path}")
async def serve_image(path: str):
    img_path = IMAGES_DIR / path
    if img_path.exists():
        return FileResponse(str(img_path))
    # Proxy from api.myl.cl
    remote_url = f"https://api.myl.cl/static/cards/{path}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(remote_url)
            if resp.status_code == 200:
                return Response(content=resp.content, media_type="image/png")
        except httpx.HTTPError:
            pass
    raise HTTPException(status_code=404, detail="Imagen no encontrada")


# ---- Cards ----
from typing import Optional

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
    d_min = _int_or_none(damage_min) or _int_or_none(power_min)
    d_max = _int_or_none(damage_max) or _int_or_none(power_max)
    return db.get_cards(
        search=_str_or_none(search), race=_str_or_none(race),
        card_type=_str_or_none(type), edition=_str_or_none(edition),
        rarity=_str_or_none(rarity),
        cost_min=_int_or_none(cost_min), cost_max=_int_or_none(cost_max),
        damage_min=d_min, damage_max=d_max,
        sort=_str_or_none(sort) or "name", page=page, per_page=per_page,
    )


@app.get("/api/cartas/search")
async def search_cartas(q: str = Query(..., min_length=1), limit: int = Query(20)):
    return {"results": db.search_cards(q, limit)}


@app.get("/api/cartas/{card_id}")
async def get_carta(card_id: int):
    card = db.get_card_by_id(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Carta no encontrada")
    return card


# ---- Editions ----
@app.get("/api/ediciones")
async def list_ediciones():
    return {"editions": db.get_editions()}


@app.get("/api/ediciones/{slug}")
async def get_edicion(slug: str):
    edition = db.get_edition_by_slug(slug)
    if not edition:
        raise HTTPException(status_code=404, detail="Edicion no encontrada")
    return edition


# ---- Decks ----
@app.get("/api/mazos")
async def list_mazos():
    return {"decks": db.get_decks()}


@app.post("/api/mazos")
async def create_mazo(body: dict):
    if not body.get("name"):
        raise HTTPException(status_code=400, detail="Nombre requerido")
    deck_id = db.create_deck(
        name=body["name"],
        race=body.get("race", ""),
        format_type=body.get("format", "racial_edicion"),
        cards=body.get("cards", []),
    )
    return {"id": deck_id, "message": "Mazo creado"}


@app.get("/api/mazos/{deck_id}")
async def get_mazo(deck_id: int):
    deck = db.get_deck(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Mazo no encontrado")
    return deck


@app.put("/api/mazos/{deck_id}")
async def update_mazo(deck_id: int, body: dict):
    existing = db.get_deck(deck_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Mazo no encontrado")
    db.update_deck(
        deck_id=deck_id,
        name=body.get("name"),
        race=body.get("race"),
        format_type=body.get("format"),
        cards=body.get("cards"),
    )
    return {"message": "Mazo actualizado"}


@app.delete("/api/mazos/{deck_id}")
async def delete_mazo(deck_id: int):
    db.delete_deck(deck_id)
    return {"message": "Mazo eliminado"}


@app.get("/api/mazos/{deck_id}/validate")
async def validate_mazo(deck_id: int):
    result = db.validate_deck(deck_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Mazo no encontrado")
    return result


# ---- Banlist ----
@app.get("/api/banlist")
async def get_banlist(format: str = Query("racial_edicion")):
    return {"banlist": db.get_banlist(format)}


@app.get("/api/banlist/check/{card_name}")
async def check_ban(card_name: str, format: str = Query("racial_edicion")):
    result = db.check_banlist(card_name, format)
    if result:
        return result
    return {"card_name": card_name, "restriction": "none", "message": "Sin restricciones"}


# ---- Simulator ----
@app.post("/api/simular")
async def simular(body: dict):
    deck_id = body.get("deck_id")
    cards = body.get("cards")
    result = db.simulate_draw(deck_id=deck_id, cards=cards)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---- Stats ----
@app.get("/api/stats")
async def stats():
    return db.get_stats()


# ---- Run ----
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
