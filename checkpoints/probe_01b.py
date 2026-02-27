"""
probe_01b.py - Minimal probe: just print game internals without render output.
Linked to: note_01.md
"""
import sys
import logging
import os

# suppress all logging
logging.disable(logging.CRITICAL)

# Redirect stderr to suppress terminal render output
import io
old_stderr = sys.stderr
sys.stderr = io.StringIO()

from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

arc = Arcade(operation_mode=OperationMode.OFFLINE)
env = arc.make("ls20", render_mode="terminal-fast")
frame = env.step(GameAction.RESET)

# Restore stderr
sys.stderr = old_stderr

print("=== FrameData attributes ===")
for attr in sorted(dir(frame)):
    if not attr.startswith("_"):
        try:
            val = getattr(frame, attr)
            if not callable(val):
                print(f"  {attr}: {repr(val)[:120]}")
        except Exception as e:
            print(f"  {attr}: ERROR({e})")

print("\n=== available_actions ===")
try:
    print(repr(frame.available_actions))
except:
    print("N/A")

print(f"\nlevels_completed={frame.levels_completed}, win_levels={frame.win_levels}, state={frame.state}")

print("\n=== env._game attributes (game internals) ===")
try:
    game = env._game
    print(f"  game class: {type(game).__name__}")
    for attr in sorted(["mgu", "snw", "tmx", "tuv", "lbq", "rzt", "pca", "qqv", "gfy", "vxy", "cjl", "qee", "hul", "kdj", "hep", "xhp", "kbj", "opw", "nlo", "ggk"]):
        try:
            val = getattr(game, attr)
            print(f"  {attr}: {repr(val)[:200]}")
        except Exception as e:
            print(f"  {attr}: not found")
except Exception as e:
    print(f"  ERROR: {e}")

# Try mgu position
try:
    game = env._game
    mgu = game.mgu
    print(f"\n=== Player (mgu) position ===")
    print(f"  mgu.x={mgu.x}, mgu.y={mgu.y}")

    print(f"\n=== Target spots (qqv) ===")
    for i, spot in enumerate(game.qqv):
        print(f"  qqv[{i}]: x={spot.x}, y={spot.y}, tags={spot.tags}")

    print(f"\n=== Target shape/color/rotation requirements ===")
    print(f"  gfy (shape indices): {game.gfy}")
    print(f"  vxy (color indices): {game.vxy}")
    print(f"  cjl (rotation indices): {game.cjl}")
    print(f"  hul (colors): {game.hul}")
    print(f"  kdj (rotations): {game.kdj}")

    print(f"\n=== Current state ===")
    print(f"  snw (current shape): {game.snw}")
    print(f"  tmx (current color idx): {game.tmx}")
    print(f"  tuv (current rotation idx): {game.tuv}")
    print(f"  lbq (lives): {game.lbq}")
    print(f"  rzt (completed targets): {game.rzt}")

    print(f"\n=== Power-up sprites ===")
    try:
        gsu_sprites = game.current_level.get_sprites_by_tag("gsu")
        print(f"  gsu (shape changers): {[(s.x, s.y) for s in gsu_sprites]}")
    except Exception as e:
        print(f"  gsu: {e}")
    try:
        gic_sprites = game.current_level.get_sprites_by_tag("gic")
        print(f"  gic (color changers): {[(s.x, s.y) for s in gic_sprites]}")
    except Exception as e:
        print(f"  gic: {e}")
    try:
        bgt_sprites = game.current_level.get_sprites_by_tag("bgt")
        print(f"  bgt (rotation changers): {[(s.x, s.y) for s in bgt_sprites]}")
    except Exception as e:
        print(f"  bgt: {e}")
    try:
        iri_sprites = game.current_level.get_sprites_by_tag("iri")
        print(f"  iri (power-ups): {[(s.x, s.y) for s in iri_sprites]}")
    except Exception as e:
        print(f"  iri: {e}")
    try:
        jdd_sprites = game.current_level.get_sprites_by_tag("jdd")
        print(f"  jdd (walls): {len(jdd_sprites)} walls")
    except Exception as e:
        print(f"  jdd: {e}")
    try:
        mae_sprites = game.current_level.get_sprites_by_tag("mae")
        print(f"  mae (target tiles): {[(s.x, s.y) for s in mae_sprites]}")
    except Exception as e:
        print(f"  mae: {e}")

except Exception as e:
    print(f"\nERROR accessing game internals: {e}")
    import traceback
    traceback.print_exc()
