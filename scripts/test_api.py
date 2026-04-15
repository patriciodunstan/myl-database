"""Quick test of the MyL API."""
import urllib.request, json

def fetch(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())

# Card search
data = fetch("http://localhost:8000/api/cartas?race=dragon&type=aliado&per_page=5")
print("=== DRAGON ALIADOS ===")
print(f"Total: {data['total']} cartas")
for c in data["cards"][:5]:
    print(f"  {c['name']:40s} Cost:{c['cost']} Str:{c.get('damage','-')} [{c['edition_title']}]")

# Banlist
print()
data2 = fetch("http://localhost:8000/api/banlist?format=racial_edicion")
print("=== BANLIST RACIAL EDICION ===")
p = [b for b in data2["banlist"] if b["restriction"] == "prohibida"]
l1 = [b for b in data2["banlist"] if b["restriction"] == "limitada_1"]
l2 = [b for b in data2["banlist"] if b["restriction"] == "limitada_2"]
print(f"Prohibidas: {len(p)}, Limitadas 1: {len(l1)}, Limitadas 2: {len(l2)}")

# Create test deck
print()
deck = fetch("http://localhost:8000/api/mazos")
print(f"Mazos guardados: {len(deck.get('decks', []))}")

# Search
print()
data3 = fetch("http://localhost:8000/api/cartas/search?q=dragon+nival")
print(f"Busqueda 'dragon nival': {len(data3['results'])} resultados")
for r in data3["results"]:
    print(f"  {r['name']} ({r['edition_title']})")
