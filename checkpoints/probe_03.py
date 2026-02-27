"""
probe_03.py - Map each level's grid, find walls, special tiles, targets.
Linked to: note_01.md
"""
import sys
import logging
logging.disable(logging.CRITICAL)
sys.path.insert(0, '.')
sys.path.insert(0, 'environment_files/ls20/cb3b57cc')

import ls20 as game_module

def get_grid_pos(x, y):
    """Convert world coords to grid coords (steps of 5, offset by 4)."""
    return (x - 4) // 5, (y - 4) // 5

def world_pos(gx, gy):
    return gx * 5 + 4, gy * 5 + 4

def map_level(level_idx):
    game = game_module.Ls20()
    # Force advance to the right level
    # We need to set current_level - let's use the game's level-switching
    # The game starts at level 0. We can look at levels directly.
    lvl = game_module.levels[level_idx]

    print(f"\n{'='*60}")
    print(f"Level {level_idx}")
    print(f"  timer={lvl.get_data('vxy')}, fog={lvl.get_data('kdy')}")

    # Get sprites from level
    sprites_in_level = lvl._sprites

    # Map tag categories
    walls = set()
    shape_changers = []
    color_changers = []
    rotation_changers = []
    powerups = []
    targets = []
    players = []

    for s in sprites_in_level:
        tags = s.tags or []
        gx, gy = get_grid_pos(s.x, s.y)

        if "jdd" in tags:
            walls.add((gx, gy))
        if "gsu" in tags:
            shape_changers.append((gx, gy, s.x, s.y))
        if "gic" in tags:
            color_changers.append((gx, gy, s.x, s.y))
        if "bgt" in tags:
            rotation_changers.append((gx, gy, s.x, s.y))
        if "iri" in tags:
            powerups.append((gx, gy, s.x, s.y))
        if "mae" in tags:
            targets.append((gx, gy, s.x, s.y))
        if "caf" in tags:
            players.append((gx, gy, s.x, s.y))

    # Also check game state for initial values
    # We need to re-init game for each level to see its data properly
    # Let's just use level data
    try:
        tuv_data = lvl.get_data("tuv")  # target shape(s)
        opw_data = lvl.get_data("opw")  # target rotation(s)
        nlo_data = lvl.get_data("nlo")  # target color(s)
        fij_data = lvl.get_data("fij")  # initial player rotation
        ggk_data = lvl.get_data("ggk")  # initial player color
        qqv_data = lvl.get_data("qqv")  # initial player shape
    except:
        tuv_data = opw_data = nlo_data = fij_data = ggk_data = qqv_data = None

    hul = [12, 9, 14, 8]  # color palette
    kdj = [0, 90, 180, 270]  # rotations
    hep_names = ["opw", "lyd", "tmx", "nio", "dcb", "fij"]

    print(f"\n  Player start: {players}")
    print(f"  Targets (mae): {targets}")
    print(f"  Shape changers (gsu): {shape_changers}")
    print(f"  Color changers (gic): {color_changers}")
    print(f"  Rotation changers (bgt): {rotation_changers}")
    print(f"  Power-ups (iri): {powerups}")
    print(f"  Walls: {len(walls)} wall tiles")

    print(f"\n  Initial player state:")
    print(f"    shape={qqv_data} ({hep_names[qqv_data] if isinstance(qqv_data,int) else qqv_data})")
    try:
        color_idx = hul.index(ggk_data)
        print(f"    color={ggk_data} (idx={color_idx})")
    except:
        print(f"    color={ggk_data}")
    try:
        rot_idx = kdj.index(fij_data)
        print(f"    rotation={fij_data}° (idx={rot_idx})")
    except:
        print(f"    rotation={fij_data}")

    print(f"\n  Target requirements:")
    if isinstance(tuv_data, int):
        tuv_data = [tuv_data]
        opw_data = [opw_data]
        nlo_data = [nlo_data]
    if tuv_data:
        for i, (tgt, opw, nlo, (gx,gy,wx,wy)) in enumerate(zip(tuv_data, opw_data, nlo_data, targets)):
            try:
                color_idx = hul.index(nlo)
            except:
                color_idx = "?"
            try:
                rot_idx = kdj.index(opw)
            except:
                rot_idx = "?"
            print(f"    Target {i} at grid({gx},{gy}): shape={tgt}({hep_names[tgt] if isinstance(tgt,int) and 0<=tgt<len(hep_names) else tgt}), color={nlo}(idx={color_idx}), rotation={opw}°(idx={rot_idx})")

    # Print a text map (12x12 grid, 0 to 11)
    print(f"\n  Grid map (12x12, . = empty, W = wall, T = target, S = shape, C = color, R = rotation, P = player, I = powerup):")
    GRID_SIZE = 12
    grid_map = [['.' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    for (gx, gy) in walls:
        if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
            grid_map[gy][gx] = 'W'
    for (gx, gy, _, _) in targets:
        if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
            grid_map[gy][gx] = 'T'
    for (gx, gy, _, _) in shape_changers:
        if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
            grid_map[gy][gx] = 'S'
    for (gx, gy, _, _) in color_changers:
        if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
            grid_map[gy][gx] = 'C'
    for (gx, gy, _, _) in rotation_changers:
        if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
            grid_map[gy][gx] = 'R'
    for (gx, gy, _, _) in powerups:
        if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
            grid_map[gy][gx] = 'I'
    for (gx, gy, _, _) in players:
        if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
            grid_map[gy][gx] = 'P'

    print("    " + " ".join(str(i%10) for i in range(GRID_SIZE)))
    for gy in range(GRID_SIZE):
        print(f"  {gy:2d} " + " ".join(grid_map[gy]))

    return {
        "walls": walls,
        "targets": targets,
        "shape_changers": shape_changers,
        "color_changers": color_changers,
        "rotation_changers": rotation_changers,
        "powerups": powerups,
        "player": players[0] if players else None,
        "tuv": tuv_data,
        "opw": opw_data,
        "nlo": nlo_data,
        "fij": fij_data,
        "ggk": ggk_data,
        "qqv": qqv_data,
    }

for i in range(7):
    map_level(i)
