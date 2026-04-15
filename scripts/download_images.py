"""Download card images from api.myl.cl."""
import sqlite3, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DB = Path(r"C:\Users\patriciods\myl-database\scraper\data\myl.db")
IMG_DIR = Path(r"C:\Users\patriciods\myl-database\scraper\data\images")
IMG_BASE = "https://api.myl.cl/static/cards"

conn = sqlite3.connect(str(DB))
rows = conn.execute(
    "SELECT c.edid, e.id FROM cards c JOIN editions e ON c.edition_id = e.id "
    "WHERE c.edid IS NOT NULL AND c.edid != ''"
).fetchall()
conn.close()

print(f"Descargando {len(rows)} imagenes...")

def dl(args):
    eid, edid = args
    dest = IMG_DIR / str(eid) / f"{edid}.png"
    if dest.exists():
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f"{IMG_BASE}/{eid}/{edid}.png"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MyL/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            with open(dest, "wb") as f:
                f.write(r.read())
        return True
    except:
        return False

tasks = [(eid, edid) for edid, eid in rows]
done = 0
fail = 0
batch = 200

for i in range(0, len(tasks), batch):
    chunk = tasks[i:i+batch]
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(dl, chunk))
    ok = sum(1 for r in results if r)
    done += ok
    fail += len(results) - ok
    print(f"  {done+fail}/{len(tasks)} ({done} OK, {fail} fail)")
    time.sleep(0.3)

print(f"\nTotal: {done} descargadas, {fail} fallidas de {len(tasks)}")

# Update image_path in DB
conn = sqlite3.connect(str(DB))
conn.execute(
    "UPDATE cards SET image_path = CAST(edition_id AS TEXT) || '/' || edid || '.png' "
    "WHERE edid IS NOT NULL AND edid != ''"
)
conn.commit()
count = conn.execute("SELECT COUNT(*) FROM cards WHERE image_path IS NOT NULL").fetchone()[0]
conn.close()
print(f"image_path actualizado ({count} cartas con imagen)")
