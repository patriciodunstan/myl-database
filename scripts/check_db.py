import sqlite3
conn = sqlite3.connect(r"C:\Users\patriciods\myl-database\scraper\data\myl.db")
schema = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='editions'").fetchone()
print("Editions schema:", schema[0])
cols = [r[1] for r in conn.execute("PRAGMA table_info(editions)").fetchall()]
print("Columns:", cols)
print()
# Test the query directly
try:
    rows = conn.execute("SELECT e.id, e.slug, e.title, e.image, e.date_release, e.flags, COUNT(c.id) as card_count FROM editions e LEFT JOIN cards c ON c.edition_id = e.id GROUP BY e.id ORDER BY e.order").fetchall()
    print(f"Query OK: {len(rows)} editions")
except Exception as ex:
    print(f"Query ERROR: {ex}")
    # Try without order
    try:
        rows = conn.execute("SELECT e.id, e.slug, e.title, COUNT(c.id) as card_count FROM editions e LEFT JOIN cards c ON c.edition_id = e.id GROUP BY e.id").fetchall()
        print(f"Without order: {len(rows)} editions")
    except Exception as ex2:
        print(f"Still ERROR: {ex2}")
conn.close()
