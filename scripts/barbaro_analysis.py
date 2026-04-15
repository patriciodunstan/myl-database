# -*- coding: utf-8 -*-
"""
Bárbaro Aggro - Gap Analysis
Cruza el mazo competitivo vs lo que el usuario tiene (toolkits + mazo dragón)
"""
import json

# ============================================================
# MAZO BARBARO AGGRO (50 cartas)
# Fuente: blog.myl.cl/decks-para-torneos-kit-de-superacion-barbaro-aggro/
# Formato: Racial Edición - Primer Bloque
# ============================================================

MAZO = {
    "nombre": "Bárbaro Aggro - Kit de Superación",
    "formato": "Racial Edición - Primer Bloque",
    "raza": "Bárbaro",
    "cartas": {
        # ALIADOS (23) - Raza Bárbaro, de Hijos de Daana / Dinastía del Dragón
        "Genseric": {"qty": 3, "type": "Aliado", "race": "Bárbaro", "source": "Dinastía del Dragón / Kit Racial Bárbaro", "edition": "Hijos de Daana"},
        "Medea": {"qty": 3, "type": "Aliado", "race": "Bárbaro", "source": "Dinastía del Dragón / Kit Racial Bárbaro", "edition": "Hijos de Daana"},
        "Viriato": {"qty": 3, "type": "Aliado", "race": "Bárbaro", "source": "Dinastía del Dragón / Kit Racial Bárbaro", "edition": "Hijos de Daana"},
        "Alboin": {"qty": 3, "type": "Aliado", "race": "Bárbaro", "source": "Dinastía del Dragón / Kit Racial Bárbaro", "edition": "Hijos de Daana"},
        "Odoacro": {"qty": 3, "type": "Aliado", "race": "Bárbaro", "source": "Dinastía del Dragón / Kit Racial Bárbaro", "edition": "Hijos de Daana"},
        "Tamora": {"qty": 2, "type": "Aliado", "race": "Bárbaro", "source": "Dinastía del Dragón / Kit Racial Bárbaro", "edition": "Hijos de Daana"},
        "Admeto": {"qty": 2, "type": "Aliado", "race": "Bárbaro", "source": "Dinastía del Dragón / Kit Racial Bárbaro", "edition": "Hijos de Daana"},
        "Charlotte de Berry": {"qty": 2, "type": "Aliado", "race": "Bárbaro", "source": "Dinastía del Dragón / Kit Racial Bárbaro", "edition": "Hijos de Daana"},
        "Ermanaric": {"qty": 2, "type": "Aliado", "race": "Bárbaro", "source": "Dinastía del Dragón / Kit Racial Bárbaro", "edition": "Hijos de Daana"},
        
        # TALISMANES (13)
        "Compitalia": {"qty": 3, "type": "Talismán", "race": "Sin Raza", "source": "Hijos de Daana / Tierras Altas", "edition": "Hijos de Daana"},
        "Teurgia": {"qty": 2, "type": "Talismán", "race": "Sin Raza", "source": "Hijos de Daana / Tierras Altas", "edition": "Hijos de Daana"},
        "Maldición de la Tormenta": {"qty": 2, "type": "Talismán", "race": "Sin Raza", "source": "Hijos de Daana / Tierras Altas", "edition": "Hijos de Daana"},
        "Poltergeist": {"qty": 2, "type": "Talismán", "race": "Sin Raza", "source": "Hijos de Daana / Tierras Altas", "edition": "Hijos de Daana"},
        "Rey Roble": {"qty": 1, "type": "Talismán", "race": "Sin Raza", "source": "Hijos de Daana / Tierras Altas", "edition": "Hijos de Daana"},
        "Carpa Dragón": {"qty": 1, "type": "Talismán", "race": "Sin Raza", "source": "Hijos de Daana / Tierras Altas", "edition": "Hijos de Daana"},
        "Maldición Gitana": {"qty": 1, "type": "Talismán", "race": "Sin Raza", "source": "Hijos de Daana / Tierras Altas", "edition": "Hijos de Daana"},
        "Caminar el Tablón": {"qty": 1, "type": "Talismán", "race": "Sin Raza", "source": "Hijos de Daana / Tierras Altas", "edition": "Hijos de Daana"},
        
        # OROS (13 - incluyendo oro inicial)
        "Oro Inicial": {"qty": 1, "type": "Oro", "race": "Sin Raza", "source": "Genérico", "edition": "Todos"},
        "Murti": {"qty": 2, "type": "Oro", "race": "Sin Raza", "source": "Dominios de Ra / Tierras Altas", "edition": "Dominios de Ra"},
        "Santa Diestra": {"qty": 3, "type": "Oro", "race": "Sin Raza", "source": "Hijos de Daana / Tierras Altas", "edition": "Hijos de Daana"},
        "Arca del Pacto": {"qty": 2, "type": "Oro", "race": "Sin Raza", "source": "Hijos de Daana / Tierras Altas", "edition": "Hijos de Daana"},
        "Cofre de Davy Jones": {"qty": 2, "type": "Oro", "race": "Sin Raza", "source": "Hijos de Daana / Tierras Altas", "edition": "Hijos de Daana"},
        "San Pancracio": {"qty": 1, "type": "Oro", "race": "Sin Raza", "source": "Hijos de Daana / Tierras Altas", "edition": "Hijos de Daana"},
        "Espejo Negro": {"qty": 1, "type": "Oro", "race": "Sin Raza", "source": "Hijos de Daana / Tierras Altas", "edition": "Hijos de Daana"},
        "Udjat": {"qty": 1, "type": "Oro", "race": "Sin Raza", "source": "Dominios de Ra", "edition": "Dominios de Ra"},
        
        # TÓTEM (1)
        "Baobab": {"qty": 1, "type": "Tótem", "race": "Sin Raza", "source": "Hijos de Daana / Tierras Altas", "edition": "Hijos de Daana"},
        
        # MONUMENTO (1)
        "Santuario Yoruba": {"qty": 1, "type": "Monumento", "race": "Sin Raza", "source": "Hijos de Daana / Tierras Altas", "edition": "Hijos de Daana"},
    }
}

# ============================================================
# PRODUCTOS QUE EL USUARIO TIENE
# ============================================================

# Toolkit Fe sin Límite (ed_id=81) - OLD toolkit
TOOLKIT_FE_SIN_LIMITE = {
    "espada larga", "hacha de batalla", "aceite de oliva", "biblioteca eterna",
    "caja de pandora", "letania", "fe sin limite", "relampago arcano",
    "bola de fuego", "capa de invisibilidad", "juramento feerico",
    "revivir a osiris", "traicion de seth", "ira gnea", "avalon"
}

# Toolkit Dragón Dorado (ed_id=82) - OLD toolkit
TOOLKIT_DRAGON_DORADO = {
    "martillo pesado", "carmix", "carnwennan", "gaitas", "dragon dorado",
    "la traicion de macalpin", "morir de pie", "jinetes de fuego",
    "red de plata", "alas de horus", "aplastar fomor", "despertar oscuro",
    "forma de toro", "micenas", "totem de nwyre"
}

# Toolkit Fuerza y Destino (ed_id=117) - OLD toolkit
TOOLKIT_FUERZA_DESTINO = {
    "espada larga", "martillo de hefestos", "ave de hera", "caja de pandora",
    "carnwennan", "corona de arturo", "figuras negras", "fe sin limite",
    "luz de prometeo", "toque de persival", "aliado feerico", "bola de fuego",
    "producir terremoto", "siete contra tebas", "guardia gozosa"
}

# Toolkit Magia y Divinidad (ed_id=118) - OLD toolkit
TOOLKIT_MAGIA_DIVINIDAD = {
    "fragarach", "martillo pesado", "glas gaibhenenn", "jeroglificos",
    "manzana sidhe", "papiros de lahun", "revivir a osiris", "forma de lince",
    "morir de pie", "destrozar la mente", "traicion de seth", "aplastar fomor",
    "ojo asesino", "caravana de los muertos", "duat"
}

# Toolkit Desafío 2026 - NEW (Espada Sagrada + Helénica)
TOOLKIT_DESAFIO_2026 = {
    # NEW cards
    "desafiar a arturo", "galatine", "cinturon de lady ann",
    "robar el vellocino", "carro de medea", "diente de la bestia",
    # REWORK cards
    "totem del errante", "atenas",
    # REPRINT cards (not confirmed, likely staples)
    "herrero",
}

# Toolkit Amatista 2026 - NEW (Hijos de Daana + Dominios de Ra)
TOOLKIT_AMATISTA_2026 = {
    # NEW cards
    "magia amatista", "loch lein", "torc fianna",
    "nombre de ra", "templo de isis", "nudo de isis",
    # REWORK cards
    "crear talisman", "carro real",
}

# Mazo preconstruido Dragón (contenido genérico, cartas comunes de dragón)
MAZO_DRAGON_PRECON = {
    # Raciales PB Dragón aliados
    "dragon demonio", "cultistas del dragon", "org el hechicero",
    "cria de wyrm", "dragon cobrizo", "drig ifanc",
    "dragon de bronce", "dragon de magma", "dragon nube",
    "dragon de luz", "dragon de plata",
    # Otros cartas comunes dragón
    "dragon dorado",  # del toolkit
}

# ============================================================
# ANÁLISIS
# ============================================================

print("=" * 70)
print("MAZO BÁRBARO AGGRO - ANÁLISIS COMPLETO")
print("=" * 70)

# 1. Verificar total del mazo
total = sum(c["qty"] for c in MAZO["cartas"].values())
print(f"\n📊 Total cartas mazo: {total}")
by_type = {}
for name, data in MAZO["cartas"].items():
    t = data["type"]
    by_type[t] = by_type.get(t, 0) + data["qty"]
for t, qty in sorted(by_type.items(), key=lambda x: -x[1]):
    print(f"   {t}: {qty}")

# 2. Chequeo de banlist (Abril 2026)
BANLIST_PROHIBIDAS = {
    "ataque a traicion", "juglares", "felipe ii", "dragon dorado", "joyero",
    "curandera", "caballo lunar", "hogar de demonios", "red de aracne",
    "romulo y remo", "rayos", "eolo", "forma de toro", "furias", "urisk",
    "traficante de esclavos", "la traicion de macalpin", "guiza",
    "vuelta a lo primordial", "nuh", "daga de bote", "bas-pef",
    "kernuac el cazador", "fergus"
}

BANLIST_LIMITADA_1 = {
    "totem de nwyre", "dragon nival", "la llama fria", "antorcha olimpica",
    "cesar augusto", "aceite de oliva", "leucrota", "yelmo alejandrino",
    "gaitas", "carmix", "druida maldito", "ulster", "rito de aton",
    "beni hassam", "pwyll", "jinetes de fuego", "cathbadh el druida",
    "montuhopet ii", "fergus", "jeroglificos", "avalon", "ptolomeo ii",
    "furia irracional", "tebas", "baal-zaphon", "bennu", "qer-her",
    "marmita druida", "kobold"
}

BANLIST_LIMITADA_2 = {
    "ma'arrat an-numan", "fe sin limite", "idmon el adivino",
    "alejandro magno", "afrodita", "corona del dia", "haquika", "zagreus",
    "papiros de lahum", "morir de pie", "helios", "amergin el druida",
    "red de plata", "cantobele", "la iliada", "kamose el guerrero",
    "qadesh", "panteon", "mineros de lapislazuli", "amosis i"
}

print(f"\n📋 CHEQUEO BANLIST (Abril 2026):")
banlist_issues = []
for name, data in MAZO["cartas"].items():
    name_lower = name.lower()
    if name_lower in BANLIST_PROHIBIDAS:
        banlist_issues.append(f"  ⛔️ PROHIBIDA: {name} x{data['qty']}")
    elif name_lower in BANLIST_LIMITADA_1 and data["qty"] > 1:
        banlist_issues.append(f"  ⚠️ LIMITADA 1: {name} x{data['qty']} (max 1)")
    elif name_lower in BANLIST_LIMITADA_2 and data["qty"] > 2:
        banlist_issues.append(f"  ⚠️ LIMITADA 2: {name} x{data['qty']} (max 2)")

if banlist_issues:
    for issue in banlist_issues:
        print(issue)
else:
    print("  ✅ Todas las cartas OK - sin restricciones violadas")

# 3. Gap Analysis vs Toolkits
print(f"\n{'=' * 70}")
print("GAP ANALYSIS - CARTAS QUE YA TIENES vs NECESITAS")
print(f"{'=' * 70}")

# Combined inventory from all toolkits user might have
all_toolkits_old = TOOLKIT_FE_SIN_LIMITE | TOOLKIT_DRAGON_DORADO | TOOLKIT_FUERZA_DESTINO | TOOLKIT_MAGIA_DIVINIDAD
all_toolkits_2026 = TOOLKIT_DESAFIO_2026 | TOOLKIT_AMATISTA_2026
all_inventory = all_toolkits_old | all_toolkits_2026 | MAZO_DRAGON_PRECON

# Check overlap
have_from_toolkits = []
need_to_buy = []

for name, data in MAZO["cartas"].items():
    name_lower = name.lower()
    if name_lower in all_inventory:
        have_from_toolkits.append(f"  ✅ {name} x{data['qty']} - YA LO TIENES")
    else:
        need_to_buy.append((name, data))

print(f"\n📦 CARTAS DEL MAZO QUE YA TIENES ({len(have_from_toolkits)}):")
if have_from_toolkits:
    for item in have_from_toolkits:
        print(item)
else:
    print("  Ninguna carta del mazo está en los toolkits")

print(f"\n🛒 CARTAS QUE NECESITAS COMPRAR ({len(need_to_buy)}):")
for name, data in need_to_buy:
    print(f"  ❌ {name} x{data['qty']} ({data['type']}) - de {data['source']}")

# 4. Cartas utiles de los toolkits para el mazo (aunque no estén en el decklist)
print(f"\n{'=' * 70}")
print("CARTAS ÚTILES DE TUS TOOLKITS PARA BÁRBARO")
print(f"{'=' * 70}")

# Useful cards from toolkits that could substitute or support
useful_from_toolkits = {
    # Oros útiles
    "aceite de oliva": {"from": "Toolkit Fe sin Límite", "note": "Oro - limitada 1, ramp genérico"},
    "biblioteca eterna": {"from": "Toolkit Fe sin Límite", "note": "Oro - ramp genérico"},
    "caja de pandora": {"from": "Toolkit Fe sin Límite / Fuerza y Destino", "note": "Oro - ramp genérico"},
    "carnwennan": {"from": "Toolkit Dragón Dorado / Fuerza y Destino", "note": "Oro - genérico útil"},
    "gaitas": {"from": "Toolkit Dragón Dorado", "note": "Oro - LIMITADA 1, muy buena"},
    "jeroglificos": {"from": "Toolkit Magia y Divinidad", "note": "Oro - LIMITADA 1, ramp"},
    "papiros de lahun": {"from": "Toolkit Magia y Divinidad", "note": "Oro - LIMITADA 2, robo"},
    # Talismanes útiles
    "fe sin limite": {"from": "Toolkit Fe sin Límite / Fuerza y Destino", "note": "Talismán - LIMITADA 2, protege aliados"},
    "morir de pie": {"from": "Toolkit Dragón Dorado / Magia y Divinidad", "note": "Talismán - LIMITADA 2, recursion"},
    "aplastar fomor": {"from": "Toolkit Dragón Dorado / Magia y Divinidad", "note": "Talismán - removal"},
    "bola de fuego": {"from": "Toolkit Fe sin Límite / Fuerza y Destino", "note": "Talismán - daño directo"},
    # Tótems útiles
    "avalon": {"from": "Toolkit Fe sin Límite", "note": "Tótem - LIMITADA 1, ventaja de cartas"},
}

for name, info in useful_from_toolkits.items():
    print(f"  💎 {name}")
    print(f"     Fuente: {info['from']}")
    print(f"     Uso: {info['note']}")

# 5. PRODUCTOS RECOMENDADOS
print(f"\n{'=' * 70}")
print("PRODUCTOS RECOMENDADOS PARA COMPLETAR EL MAZO")
print(f"{'=' * 70}")

products = [
    {
        "name": "Kit Racial Bárbaro (2020 - original)",
        "price": "$14,990 - $19,990 CLP",
        "includes": [
            "Siegfried (reprint foil)",
            "Atalanta (reprint foil)", 
            "Medea (reprint foil)",
            "Viriato (reprint foil)",
            "Gaitas SP (reprint foil)",
            "Palnatoke (reprint)",
            "Brynhildr (reprint + remake)",
            "12 sobres de Dinastía del Dragón"
        ],
        "cards_needed": ["Medea x1 (de las 3 que necesitas)", "Viriato x1 (de las 3)"],
        "difficulty": "Difícil de encontrar - producto de 2020, probablemente discontinuado",
        "priority": "BAJA - si lo encuentras barato, cómpralo"
    },
    {
        "name": "Toolkit Amatista 2026 (Hijos de Daana + Dominios de Ra)",
        "price": "$29,990 CLP",
        "includes": [
            "Magia Amatista (talismán nuevo)",
            "Loch Lein (tótem nuevo)", 
            "Torc Fianna (oro nuevo)",
            "Nombre de Ra (talismán nuevo)",
            "Templo de Isis (tótem nuevo)",
            "Nudo de Isis (oro nuevo)",
            "Crear Talismán (rework)",
            "Carro Real (rework)",
            "8 reprint + 8 sobres Dominios de Ra Aniversario"
        ],
        "cards_needed": [],
        "difficulty": "Disponible en preventa/tiendas",
        "priority": "ALTA - soporte directo para Hijos de Daana"
    },
    {
        "name": "Sobres de Dinastía del Dragón",
        "price": "~$1,500 - $2,500 CLP cada sobre",
        "includes": [
            "Aliados Bárbaros (Genseric, Alboin, Odoacro, etc.)",
            "Talismanes de soporte",
            "Oros con habilidades"
        ],
        "cards_needed": ["LA FUENTE PRINCIPAL de aliados Bárbaro"],
        "difficulty": "Disponible en tiendas pero necesitas varios para completar",
        "priority": "CRÍTICA - de aquí salen la mayoría de los aliados"
    },
    {
        "name": "Lootbox Racial Bárbaro (La Guarida)",
        "price": "$11,990 CLP",
        "includes": [
            "30 cartas holográficas (configurables: 20 aliados Bárbaro + 10 soporte)",
            "30 cartas adicionales (cortesanos + vasallos)",
            "1-3 sobres de Leyendas PB 2.0",
            "Posibilidad de cartas raras"
        ],
        "cards_needed": ["Altamente configurable para Bárbaro"],
        "difficulty": "Disponible en laguarida.store",
        "priority": "ALTA - mejor relación precio/cartas para Bárbaro"
    },
    {
        "name": "Sobres de Hijos de Daana / Tierras Altas",
        "price": "~$2,000 - $3,500 CLP cada sobre",
        "includes": [
            "Talismanes (Compitalia, Teurgia, etc.)",
            "Oros (Santa Diestra, Arca del Pacto, etc.)",
            "Tótems (Baobab)",
            "Aliados Desafiante/Defensor/Sombra (no Bárbaro directamente)"
        ],
        "cards_needed": ["Fuente de talismanes, oros y tótems del mazo"],
        "difficulty": "Disponible en tiendas",
        "priority": "MEDIA - para completar soporte"
    },
]

for p in products:
    print(f"\n  📦 {p['name']}")
    print(f"     Precio: {p['price']}")
    print(f"     Cartas incluidas:")
    for card in p['includes']:
        print(f"       • {card}")
    if p['cards_needed']:
        print(f"     Cubre del mazo: {', '.join(p['cards_needed'])}")
    print(f"     Disponibilidad: {p['difficulty']}")
    print(f"     ⭐ PRIORIDAD: {p['priority']}")

# 6. RESUMEN FINAL
print(f"\n{'=' * 70}")
print("RESUMEN FINAL")
print(f"{'=' * 70}")

total_cards_needed = sum(d["qty"] for _, d in need_to_buy)
print(f"\n  Mazo total: {total} cartas (49 + 1 oro inicial)")
print(f"  Cartas que YA tienes (de toolkits): {total - total_cards_needed}")
print(f"  Cartas que NECESITAS: {total_cards_needed}")

print(f"\n  🎯 PLAN DE ACCIÓN RECOMENDADO (prioridad rapidez > costo):")
print(f"     1. Comprar 6-10 sobres de Dinastía del Dragón ($9,000-$25,000)")
print(f"        → Fuente principal de aliados Bárbaro (Genseric, Alboin, Odoacro, etc.)")
print(f"     2. Comprar Lootbox Racial Bárbaro ($11,990)")
print(f"        → 20 aliados Bárbaro configurables + soporte")
print(f"     3. Comprar 3-5 sobres de Hijos de Daana ($6,000-$17,500)")
print(f"        → Talismanes (Compitalia, Teurgia) y Oros (Santa Diestra)")
print(f"     4. CONSIDERAR: Toolkit Amatista 2026 ($29,990)")
print(f"        → Nuevas cartas de soporte Hijos de Daana + 8 sobres")
print(f"\n  💰 Costo estimado total: $27,000 - $84,000 CLP")
print(f"     (dependiendo de suerte con sobres y si compras lootbox vs toolkit)")
