"""
probe_02.py - Access the game engine directly to inspect level internals
without terminal rendering spam.
Linked to: note_01.md
"""
import sys
import logging
logging.disable(logging.CRITICAL)

# Patch stdout to suppress render output
import io

# We need to directly import the game environment
sys.path.insert(0, '.')
sys.path.insert(0, 'environment_files/ls20/cb3b57cc')

import ls20 as game_module

game = game_module.Ls20()

print("=== Level count ===")
print(f"  Total levels: {len(game_module.levels)}")

print("\n=== Level 0 data ===")
lvl = game_module.levels[0]
for key in ["vxy", "kdy", "tuv", "opw", "nlo", "fij", "ggk", "qqv"]:
    try:
        val = lvl.get_data(key)
        print(f"  {key}: {repr(val)[:150]}")
    except Exception as e:
        print(f"  {key}: ERROR({e})")

print("\n=== Sprites in level 0 ===")
try:
    sprites = lvl._sprites
    print(f"  Total sprites: {len(sprites)}")
    # Group by tags
    tagged = {}
    for s in sprites:
        tags = tuple(s.tags) if s.tags else ("(no tag)",)
        for t in tags:
            if t not in tagged:
                tagged[t] = []
            tagged[t].append((s.x, s.y, s.name if hasattr(s, 'name') else ''))
    for tag, items in sorted(tagged.items()):
        print(f"  tag={tag}: {items[:10]}")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback; traceback.print_exc()

# Check game state after initialization
print("\n=== Game after init ===")
print(f"  current_level idx: {game.current_level_index if hasattr(game, 'current_level_index') else 'N/A'}")
try:
    print(f"  mgu pos: ({game.mgu.x}, {game.mgu.y})")
    print(f"  snw={game.snw}, tmx={game.tmx}, tuv={game.tuv}")
    print(f"  lbq (lives)={game.lbq}")
    print(f"  gfy={game.gfy}")
    print(f"  vxy={game.vxy}")
    print(f"  cjl={game.cjl}")
    print(f"  hul={game.hul}")
    print(f"  kdj={game.kdj}")
    print(f"  qqv positions: {[(s.x, s.y) for s in game.qqv]}")
    print(f"  pca positions: {[(s.x, s.y) for s in game.pca]}")
    print(f"  rzt (completed): {game.rzt}")
    # Shape changer tiles
    gsu_sprites = game.current_level.get_sprites_by_tag("gsu")
    print(f"\n  gsu (shape changers): {[(s.x, s.y) for s in gsu_sprites]}")
    gic_sprites = game.current_level.get_sprites_by_tag("gic")
    print(f"  gic (color changers): {[(s.x, s.y) for s in gic_sprites]}")
    bgt_sprites = game.current_level.get_sprites_by_tag("bgt")
    print(f"  bgt (rotation changers): {[(s.x, s.y) for s in bgt_sprites]}")
    iri_sprites = game.current_level.get_sprites_by_tag("iri")
    print(f"  iri (power-ups): {[(s.x, s.y) for s in iri_sprites]}")
    jdd_sprites = game.current_level.get_sprites_by_tag("jdd")
    print(f"  jdd (walls): {len(jdd_sprites)} walls, first few: {[(s.x, s.y) for s in jdd_sprites[:5]]}")
    mae_sprites = game.current_level.get_sprites_by_tag("mae")
    print(f"  mae (target tiles): {[(s.x, s.y) for s in mae_sprites]}")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback; traceback.print_exc()

print("\n=== All levels overview ===")
for i, lvl in enumerate(game_module.levels):
    try:
        vxy_val = lvl.get_data("vxy")
        kdy_val = lvl.get_data("kdy")
        print(f"  Level {i}: timer={vxy_val}, has_fog={kdy_val}")
    except:
        print(f"  Level {i}: error reading data")
