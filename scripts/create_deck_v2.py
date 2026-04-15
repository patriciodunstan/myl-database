# -*- coding: utf-8 -*-
"""Create Barbaro proxy deck via Railway API with proper URL encoding."""
import json
import urllib.request
import urllib.parse
import urllib.error

RAILWAY = "https://myl-database-production.up.railway.app"

def api_get(path, params=None):
    url = f"{RAILWAY}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "MyL-DeckBuilder/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def api_post(path, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(f"{RAILWAY}{path}", data=body, headers={
        "User-Agent": "MyL-DeckBuilder/1.0", "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def find_card(name):
    """Find a card by exact or partial name match."""
    try:
        result = api_get("/api/cartas", {"search": name, "per_page": "10"})
        cards = result.get("cards", [])
        if cards:
            # Prefer exact match
            for c in cards:
                if c["name"].lower() == name.lower():
                    return c
            # Return first partial match
            return cards[0]
    except:
        pass
    return None

# Deck plan: 50 cards total
# Using available cards since Bárbaro-specific aliados aren't in DB
# This is a PROXY deck using Desafiante race until Bárbaro cards are added
deck_plan = [
    # ALIADOS (23) - Desafiante race from HdD/TA editions
    ("ashrays", 3),           # cost 1, dmg 3 - FAST
    ("tutatis", 2),           # cost 1, dmg 4 - FAST
    ("tuatha de danaan", 3),  # cost 2, dmg 2
    ("epona", 3),             # cost 2, dmg 2
    ("rhiannon", 3),          # cost 2, dmg 2
    ("boobrie", 3),           # cost 2, dmg 3
    ("sidhe guerrero", 3),    # cost 2, dmg 3
    ("aine", 2),              # cost 3, dmg 3
    ("lugh", 1),              # cost 4, dmg 4 - finisher

    # TALISMANES (13) - from toolkits and editions
    ("fe sin limite", 2),
    ("morir de pie", 2),
    ("aplastar fomor", 3),
    ("bola de fuego", 3),
    ("relampago arcano", 1),
    ("destrozar la mente", 2),

    # OROS (12) - from toolkits (1 oro inicial = 49 + 1)
    ("aceite de oliva", 1),
    ("biblioteca eterna", 2),
    ("caja de pandora", 2),
    ("carnwennan", 2),
    ("gaitas", 1),
    ("papiros de lahun", 2),
    ("jeroglificos", 1),
    ("ojo udjat", 1),

    # TÓTEM (1)
    ("avalon", 1),
]

# Find all cards
print("Resolviendo cartas...")
deck_cards = []
not_found = []

for name, qty in deck_plan:
    card = find_card(name)
    if card:
        deck_cards.append({"card_id": card["id"], "quantity": qty})
        print(f"  OK: {card['name']} (id={card['id']}) x{qty} | {card.get('type_name')} | {card.get('race_name', '?')}")
    else:
        not_found.append((name, qty))
        print(f"  MISSING: {name} x{qty}")

total = sum(c["quantity"] for c in deck_cards)
print(f"\nTotal cartas encontradas: {total}")
if not_found:
    print(f"Faltantes: {len(not_found)}")
    for n, q in not_found:
        print(f"  - {n} x{q}")

if total >= 40:
    print(f"\nCreando mazo en Railway...")
    try:
        result = api_post("/api/mazos", {
            "name": "Barbaro Aggro (Proxy - Desafiante base)",
            "race": "desafiante",
            "format": "racial_edicion",
            "cards": deck_cards
        })
        deck_id = result.get("id")
        print(f"  MAZO CREADO! ID: {deck_id}")
        print(f"  URL: {RAILWAY}/api/mazos/{deck_id}")
        
        # Validate
        validation = api_get(f"/api/mazos/{deck_id}/validate")
        print(f"  Valido: {validation.get('valid')}")
        if validation.get('errors'):
            for e in validation['errors']:
                print(f"    ERROR: {e}")
        if validation.get('warnings'):
            for w in validation['warnings']:
                print(f"    WARN: {w}")
        print(f"  Total cartas: {validation.get('card_count')}")
        print(f"  Total aliados: {validation.get('ally_count')}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  Error {e.code}: {body}")
    except Exception as e:
        print(f"  Error: {e}")
else:
    print(f"\nNo hay suficientes cartas ({total}) para crear mazo (min 40)")
