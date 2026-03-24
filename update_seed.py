"""
Update the seed data to match the 'Counting Numbers 1-20' diagram.

Key changes from old spreadsheet:
1. Remove KC CNM-538 (not in diagram)
2. Schema CNM-5300 gets KCs 532-537 (was 413, 539, 601 — those become direct members of parent)
3. Remove schema CNM-5250 (not in diagram); its KCs (540, 602, 603, 604) become standalone
4. Adjust schema CNM-5300 parent to CNM-8300 (keep)
5. Adjust schema memberships for 5100, 8100, 8200, 8300 to match diagram
6. Re-derive edges from diagram

The diagram shows these schemas and their direct KC members:
  5010: {501, 502, 503, 504, 505}  parent=5100  (unchanged)
  5020: {512, 513, 514, 515, 516, 517}  parent=5100  (unchanged)
  5100: contains sub-schemas 5010, 5020; direct KCs: {400, 411}  parent=8100 (CHANGE: was parent=8100, but direct KCs 400,411 match - keep)
  5200: {522, 523, 524, 525, 526, 527}  parent=8200  (unchanged)
  5300: {532, 533, 534, 535, 536, 537}  parent=8300  (CHANGED: was {413, 539, 601})
  7100: {701, 702, 703}  parent=8100  (unchanged)
  7200: {711, 712, 713}  parent=8200  (unchanged)
  7300: {721, 722, 723}  parent=8300  (unchanged)
  8100: {518, 519, 811, 812, 813, 814}  parent=None  (unchanged, also contains 5100, 7100 as children)
  8200: {528, 529, 821, 822, 823, 824}  parent=None  (unchanged, also contains 5200, 7200 as children)
  8300: {825-836}  parent=None  (unchanged, also contains 5300, 7300 as children)

Standalone KCs visible in diagram (not in any leaf schema):
  412, 413, 539, 540, 601, 602, 603, 604

Schema 5250 is removed entirely (its KCs become standalone under 8300 or loose).

Edges from diagram — I'll trace each node's outgoing arrows:
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "living_map.db"


def update():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")

    # ── 1. Remove KC CNM-538 (not in diagram) ──
    print("Removing CNM-538...")
    conn.execute("DELETE FROM schema_kcs WHERE kc_id = 'CNM-538'")
    conn.execute("DELETE FROM kc_language_demands WHERE kc_id = 'CNM-538'")
    conn.execute("DELETE FROM kc_math_contexts WHERE kc_id = 'CNM-538'")
    conn.execute("DELETE FROM prerequisite_edges WHERE source_kc_id = 'CNM-538' OR target_kc_id = 'CNM-538'")
    conn.execute("DELETE FROM knowledge_components WHERE id = 'CNM-538'")

    # ── 2. Remove schema CNM-5250 (not in diagram) ──
    print("Removing schema CNM-5250...")
    conn.execute("DELETE FROM schema_kcs WHERE schema_id = 'CNM-5250'")
    conn.execute("DELETE FROM schemas WHERE id = 'CNM-5250'")

    # ── 3. Update schema CNM-5300 membership ──
    # Currently has {413, 539, 601}. Should have {532, 533, 534, 535, 536, 537}
    print("Updating schema CNM-5300 membership...")
    conn.execute("DELETE FROM schema_kcs WHERE schema_id = 'CNM-5300'")
    for kc_id in ["CNM-532", "CNM-533", "CNM-534", "CNM-535", "CNM-536", "CNM-537"]:
        conn.execute("INSERT INTO schema_kcs (schema_id, kc_id) VALUES (?, ?)", ("CNM-5300", kc_id))

    # ── 4. Update CNM-5100 direct KCs: should be {400, 411} — but diagram shows
    # 400 and 411 at bottom of 5100 box. Check current state:
    current_5100 = [r["kc_id"] for r in conn.execute(
        "SELECT kc_id FROM schema_kcs WHERE schema_id = 'CNM-5100'"
    )]
    print(f"  CNM-5100 current KCs: {current_5100}")
    # Already correct: {400, 411}

    # ── 5. Ensure 413, 539, 540, 601, 602, 603, 604 are standalone ──
    # They should NOT be in any schema (5300 was their old home)
    # 413, 539, 601 were in 5300; 540, 602, 603, 604 were in 5250
    # 5250 is now deleted, 5300 is updated. Let's verify they're not in any schema:
    for kc_id in ["CNM-413", "CNM-539", "CNM-540", "CNM-601", "CNM-602", "CNM-603", "CNM-604"]:
        rows = conn.execute("SELECT schema_id FROM schema_kcs WHERE kc_id = ?", (kc_id,)).fetchall()
        if rows:
            print(f"  {kc_id} still in schemas: {[r['schema_id'] for r in rows]}")
            # These should be standalone — but wait:
            # From diagram: 412, 413 appear between 5200 and 5300 as connectors
            # 539, 540 appear between 5300 and the right side
            # 601, 602, 603, 604 appear at far right
            # None of them are inside a schema box in the diagram
            # BUT: 413 is currently in 5300. We already deleted 5300's old members.
        else:
            print(f"  {kc_id} is standalone (good)")

    # ── 6. Now rebuild the CNM edges from the diagram ──
    # First, remove ALL existing CNM->CNM edges
    print("\nRebuilding CNM edges from diagram...")
    conn.execute(
        "DELETE FROM prerequisite_edges WHERE source_kc_id LIKE 'CNM%' AND target_kc_id LIKE 'CNM%'"
    )

    # Edges traced from diagram (source -> target means source is prerequisite of target):
    # Reading left to right, top to bottom in the diagram:
    diagram_edges = [
        # From 400 (bottom-left of 5010)
        ("CNM-400", "CNM-501"),
        ("CNM-400", "CNM-502"),
        ("CNM-400", "CNM-503"),
        ("CNM-400", "CNM-504"),
        ("CNM-400", "CNM-505"),
        ("CNM-400", "CNM-411"),

        # From 411 -> 5020 KCs
        ("CNM-411", "CNM-512"),
        ("CNM-411", "CNM-513"),
        ("CNM-411", "CNM-514"),
        ("CNM-411", "CNM-515"),
        ("CNM-411", "CNM-516"),
        ("CNM-411", "CNM-517"),

        # From 5010 KCs to 5020 KCs (internal 5100 edges)
        ("CNM-501", "CNM-512"),
        ("CNM-501", "CNM-515"),
        ("CNM-502", "CNM-513"),
        ("CNM-503", "CNM-514"),
        ("CNM-504", "CNM-516"),
        ("CNM-505", "CNM-517"),

        # From 5020 KCs outward
        ("CNM-512", "CNM-518"),
        ("CNM-512", "CNM-519"),
        ("CNM-512", "CNM-522"),
        ("CNM-512", "CNM-811"),
        ("CNM-512", "CNM-813"),
        ("CNM-513", "CNM-523"),
        ("CNM-513", "CNM-812"),
        ("CNM-513", "CNM-814"),
        ("CNM-514", "CNM-524"),
        ("CNM-514", "CNM-814"),
        ("CNM-515", "CNM-525"),
        ("CNM-516", "CNM-526"),
        ("CNM-517", "CNM-527"),

        # From 412 (connector between 5100 and 5200)
        ("CNM-412", "CNM-522"),
        ("CNM-412", "CNM-523"),
        ("CNM-412", "CNM-524"),
        ("CNM-412", "CNM-525"),
        ("CNM-412", "CNM-526"),
        ("CNM-412", "CNM-527"),
        ("CNM-412", "CNM-413"),

        # From 5200 KCs outward
        ("CNM-522", "CNM-528"),
        ("CNM-522", "CNM-529"),
        ("CNM-522", "CNM-532"),
        ("CNM-522", "CNM-601"),
        ("CNM-522", "CNM-821"),
        ("CNM-522", "CNM-823"),
        ("CNM-523", "CNM-533"),
        ("CNM-523", "CNM-534"),
        ("CNM-523", "CNM-535"),
        ("CNM-523", "CNM-536"),
        ("CNM-523", "CNM-822"),
        ("CNM-523", "CNM-824"),
        ("CNM-524", "CNM-824"),
        ("CNM-525", "CNM-537"),
        ("CNM-526", "CNM-537"),

        # From 413 (connector between 5200 and 5300)
        ("CNM-413", "CNM-532"),
        ("CNM-413", "CNM-533"),
        ("CNM-413", "CNM-534"),
        ("CNM-413", "CNM-535"),
        ("CNM-413", "CNM-536"),
        ("CNM-413", "CNM-537"),

        # From 5300 KCs outward
        ("CNM-532", "CNM-539"),
        ("CNM-532", "CNM-540"),
        ("CNM-532", "CNM-825"),
        ("CNM-532", "CNM-826"),
        ("CNM-532", "CNM-827"),
        ("CNM-532", "CNM-828"),
        ("CNM-533", "CNM-829"),
        ("CNM-533", "CNM-830"),
        ("CNM-534", "CNM-831"),
        ("CNM-535", "CNM-832"),
        ("CNM-536", "CNM-833"),
        ("CNM-537", "CNM-834"),

        # From 539, 540 (standalone, right of 5300)
        ("CNM-539", "CNM-601"),
        ("CNM-539", "CNM-604"),
        ("CNM-540", "CNM-602"),
        ("CNM-540", "CNM-603"),

        # From 601 -> 8300 area
        ("CNM-601", "CNM-602"),
        ("CNM-601", "CNM-825"),
        ("CNM-601", "CNM-826"),
        ("CNM-601", "CNM-828"),
        ("CNM-601", "CNM-831"),
        ("CNM-601", "CNM-833"),
        ("CNM-601", "CNM-835"),

        # From 602
        ("CNM-602", "CNM-603"),
        ("CNM-602", "CNM-827"),
        ("CNM-602", "CNM-829"),
        ("CNM-602", "CNM-832"),
        ("CNM-602", "CNM-834"),
        ("CNM-602", "CNM-836"),

        # From 603
        ("CNM-603", "CNM-604"),
        ("CNM-603", "CNM-832"),

        # From 7100 KCs
        ("CNM-701", "CNM-811"),
        ("CNM-701", "CNM-812"),
        ("CNM-701", "CNM-721"),
        ("CNM-701", "CNM-744"),
        ("CNM-701", "CNM-745"),
        ("CNM-702", "CNM-722"),
        ("CNM-703", "CNM-723"),
        ("CNM-703", "CNM-813"),
        ("CNM-703", "CNM-814"),

        # From 8100 KCs (811-814)
        # These don't seem to have outgoing edges in this subset of the diagram

        # From 7200 KCs
        ("CNM-711", "CNM-821"),
        ("CNM-711", "CNM-822"),
        ("CNM-711", "CNM-721"),
        ("CNM-711", "CNM-744"),
        ("CNM-711", "CNM-745"),
        ("CNM-712", "CNM-722"),
        ("CNM-713", "CNM-723"),
        ("CNM-713", "CNM-823"),
        ("CNM-713", "CNM-824"),

        # From 7300 KCs
        ("CNM-721", "CNM-825"),
        ("CNM-721", "CNM-828"),
        ("CNM-721", "CNM-829"),
        ("CNM-721", "CNM-830"),
        ("CNM-722", "CNM-833"),
        ("CNM-722", "CNM-834"),
        ("CNM-723", "CNM-835"),
        ("CNM-723", "CNM-836"),
    ]

    print(f"  Inserting {len(diagram_edges)} edges...")
    for src, tgt in diagram_edges:
        conn.execute(
            "INSERT INTO prerequisite_edges (source_kc_id, target_kc_id) VALUES (?, ?)",
            (src, tgt),
        )

    # ── 7. Also keep SUB edges unchanged (they weren't touched) ──
    sub_count = conn.execute(
        "SELECT COUNT(*) as c FROM prerequisite_edges WHERE source_kc_id LIKE 'SUB%'"
    ).fetchone()["c"]
    print(f"  SUB edges preserved: {sub_count}")

    conn.commit()

    # ── Verify ──
    total_kcs = conn.execute("SELECT COUNT(*) as c FROM knowledge_components").fetchone()["c"]
    total_edges = conn.execute("SELECT COUNT(*) as c FROM prerequisite_edges").fetchone()["c"]
    total_schemas = conn.execute("SELECT COUNT(*) as c FROM schemas").fetchone()["c"]

    print(f"\nAfter update:")
    print(f"  KCs: {total_kcs}")
    print(f"  Edges: {total_edges}")
    print(f"  Schemas: {total_schemas}")

    # Check schemas
    print("\nSchema memberships:")
    for s in conn.execute("SELECT id, name, parent_schema_id FROM schemas ORDER BY id"):
        kcs = [r["kc_id"] for r in conn.execute(
            "SELECT kc_id FROM schema_kcs WHERE schema_id = ? ORDER BY kc_id", (s["id"],)
        )]
        print(f"  {s['id']:15s} parent={str(s['parent_schema_id']):15s} KCs={kcs}")

    conn.close()
    print("\nDone!")


if __name__ == "__main__":
    update()
