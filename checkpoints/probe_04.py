"""
probe_04.py - Debug BFS failure: check sprite tags in levels 2,4,5,6.
Linked to: note_02.md
"""
import sys
import logging
logging.disable(logging.CRITICAL)
sys.path.insert(0, '.')
sys.path.insert(0, 'environment_files/ls20/cb3b57cc')

import ls20 as game_module

for level_idx in [2, 4, 5, 6]:
    lvl = game_module.levels[level_idx]
    print(f"\n=== Level {level_idx} sprite tags ===")

    # Check iri, gsu, gic, bgt tags
    for s in lvl._sprites:
        tags = s.tags or []
        if any(t in tags for t in ["iri", "gsu", "gic", "bgt", "mae", "caf"]):
            print(f"  ({s.x},{s.y}) name={s.name!r} tags={tags}")

    # Also check by just listing all unique tag sets
    print(f"\n  All unique tags:")
    all_tags = set()
    for s in lvl._sprites:
        tags = tuple(s.tags) if s.tags else ("(none)",)
        for t in tags:
            all_tags.add(t)
    print(f"  {sorted(all_tags)}")

# Also test what the LIVE game exposes after init
print("\n\n=== Live game for level 2 (index 2) ===")
game = game_module.Ls20()
# The game starts at level 0. We need to manually advance to level 2.
# Actually, let's just check what's in level 2 via the live game's level data
from arcengine import Level
lvl2 = game_module.levels[2]
print("Sprites tagged iri:", [(s.x, s.y, s.tags) for s in lvl2._sprites if "iri" in (s.tags or [])])
print("Sprites tagged gsu:", [(s.x, s.y, s.tags) for s in lvl2._sprites if "gsu" in (s.tags or [])])
print("Sprites tagged gic:", [(s.x, s.y, s.tags) for s in lvl2._sprites if "gic" in (s.tags or [])])
print("Sprites tagged bgt:", [(s.x, s.y, s.tags) for s in lvl2._sprites if "bgt" in (s.tags or [])])
print("Sprites tagged mae:", [(s.x, s.y, s.tags) for s in lvl2._sprites if "mae" in (s.tags or [])])
print("Sprites tagged caf:", [(s.x, s.y, s.tags) for s in lvl2._sprites if "caf" in (s.tags or [])])
print("Sprites tagged jdd:", len([(s.x, s.y) for s in lvl2._sprites if "jdd" in (s.tags or [])]), "walls")
