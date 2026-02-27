"""
probe_01.py - Explore the FrameData structure, game state, and level layout.
Linked to: note_01.md
"""
import sys
import logging
logging.basicConfig(level=logging.WARNING)  # suppress info spam

from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

arc = Arcade(operation_mode=OperationMode.OFFLINE)
env = arc.make("ls20", render_mode="terminal-fast")

frame = env.step(GameAction.RESET)

print("=== FrameData attributes ===")
for attr in dir(frame):
    if not attr.startswith("_"):
        try:
            val = getattr(frame, attr)
            if not callable(val):
                print(f"  {attr}: {val}")
        except Exception as e:
            print(f"  {attr}: ERROR({e})")

print("\n=== available_actions ===")
print(frame.available_actions)

print("\n=== state ===")
print(frame.state)
print(f"levels_completed: {frame.levels_completed}")
print(f"win_levels: {frame.win_levels}")

print("\n=== grid/frame shape ===")
try:
    g = frame.grid
    print(f"  grid type: {type(g)}, shape: {getattr(g, 'shape', 'N/A')}")
except Exception as e:
    print(f"  grid: ERROR({e})")

# Try to access the underlying game object
print("\n=== env attributes ===")
for attr in dir(env):
    if not attr.startswith("_"):
        try:
            val = getattr(env, attr)
            if not callable(val):
                print(f"  {attr}: {type(val).__name__} = {repr(val)[:100]}")
        except Exception as e:
            print(f"  {attr}: ERROR")

# Take a few actions and inspect the frame
print("\n=== Taking actions 1-4 ===")
for action in [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]:
    f = env.step(action)
    print(f"  {action.name}: state={f.state.name}, levels={f.levels_completed}")

# Try to access game internals via the env
print("\n=== env._game attributes ===")
try:
    game = env._game
    print(f"  game type: {type(game).__name__}")
    for attr in ["mgu", "snw", "tmx", "tuv", "lbq", "rzt", "pca", "qqv", "gfy", "vxy", "cjl"]:
        try:
            val = getattr(game, attr)
            print(f"  {attr}: {repr(val)[:200]}")
        except Exception as e:
            print(f"  {attr}: ERROR({e})")
except Exception as e:
    print(f"  ERROR accessing _game: {e}")
