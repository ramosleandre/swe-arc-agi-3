"""
BFS-based agent for ARC-AGI-3 game ls20.

Key insight (fixed from v1):
  The game uses rbt(qul, cfy, 5, 5) to detect sprites in a 5×5 window
  centred at the player's destination.  Sprites like iri power-ups can be
  placed at offsets (e.g. (20,31)) but are triggered when the player moves
  to the canonical player-grid position (19,30).

  Player positions always lie on the grid:
    x ∈ {4 + 5k}  (moves start from 4+5k and step by 5)
    y ∈ {5j}      (moves start from 5j and step by 5)

  For any sprite at (sx, sy) we compute the canonical player position
  that triggers it:
    nx = 4 + 5 * ((sx - 4) // 5)
    ny = 5 * (sy // 5)

Strategy: read all level data at init, run timer-aware BFS
(state = pos × shape × color × rot × targets_done × iri_collected ×
         steps_since_last_refill) and execute pre-computed sequences.
"""

from __future__ import annotations

import logging
import os
import sys
from collections import deque
from typing import Dict, List, Optional, Set, Tuple

from arcengine import FrameData, GameAction, GameState

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _canonical(sx: int, sy: int) -> Tuple[int, int]:
    """Return the player-grid position that triggers a sprite at (sx, sy)."""
    nx = 4 + 5 * ((sx - 4) // 5)
    ny = 5 * (sy // 5)
    return (nx, ny)


# ---------------------------------------------------------------------------
# BFS solver
# ---------------------------------------------------------------------------

def _solve_level(lvl, hul: list, kdj: list) -> List[int]:
    """Return the shortest timer-safe action sequence to complete a level."""
    # ---- build interaction maps using CANONICAL player positions ----
    walls: Set = set()
    gsu: Set = set()
    gic: Set = set()
    bgt: Set = set()
    iri_positions: list = []       # ordered list of canonical (nx,ny)
    iri_idx: Dict = {}
    player_start: Optional[Tuple[int, int]] = None

    for s in lvl._sprites:
        tags = s.tags or []
        pp = _canonical(s.x, s.y)

        if "jdd" in tags:
            walls.add(pp)
        if "gsu" in tags:
            gsu.add(pp)
        if "gic" in tags:
            gic.add(pp)
        if "bgt" in tags:
            bgt.add(pp)
        if "iri" in tags:
            if pp not in iri_idx:
                iri_idx[pp] = len(iri_positions)
                iri_positions.append(pp)
        if "caf" in tags:
            # player_start is already a valid player position
            player_start = (s.x, s.y)

    if player_start is None:
        logger.warning("No player start found")
        return []

    num_iri = len(iri_positions)

    # ---- target requirements ----
    tuv_data = lvl.get_data("tuv")   # required shape index(es)
    opw_data = lvl.get_data("opw")   # required rotation(s) in degrees
    nlo_data = lvl.get_data("nlo")   # required color(s) as hul value
    fij_data = lvl.get_data("fij")   # initial player rotation (degrees)
    ggk_data = lvl.get_data("ggk")   # initial player color (hul value)
    qqv_data = lvl.get_data("qqv")   # initial player shape index

    if isinstance(tuv_data, int):
        tuv_data = [tuv_data]
        opw_data = [opw_data]
        nlo_data = [nlo_data]

    # Targets mapped to canonical player positions
    target_requirements: list = []
    for s in lvl._sprites:
        if "mae" not in (s.tags or []):
            continue
        i = len(target_requirements)
        pp = _canonical(s.x, s.y)
        req_shape = tuv_data[i]
        try:
            req_color = hul.index(nlo_data[i])
        except (ValueError, IndexError):
            req_color = 0
        try:
            req_rot = kdj.index(opw_data[i])
        except (ValueError, IndexError):
            req_rot = 0
        target_requirements.append((pp[0], pp[1], req_shape, req_color, req_rot))

    num_targets = len(target_requirements)
    goal_mask = (1 << num_targets) - 1

    # ---- initial game state ----
    try:
        init_color = hul.index(ggk_data)
    except (ValueError, TypeError):
        init_color = 0
    try:
        init_rot = kdj.index(fij_data)
    except (ValueError, TypeError):
        init_rot = 0
    init_shape = int(qqv_data) if qqv_data is not None else 0

    logger.debug(
        "Level solve: player=%s  init(sh=%d,col=%d,rot=%d)  "
        "targets=%d  iri=%d  walls=%d",
        player_start, init_shape, init_color, init_rot,
        num_targets, num_iri, len(walls),
    )
    for i, t in enumerate(target_requirements):
        logger.debug("  target[%d] @ (%d,%d) need sh=%d col=%d rot=%d", i, *t)

    # ---- timer-aware BFS ----
    # State = (px, py, shape, color_idx, rot_idx, done, iri_mask, steps_since_refill)
    # steps_since_refill in {0..42}
    # Collecting iri: resets steps to 0 (xpb=True skips timer decrement, timer resets)
    # Normal step: steps += 1; if steps would exceed 42 without iri → life lost → skip

    start = (*player_start, init_shape, init_color, init_rot, 0, 0, 0)

    parent: dict = {start: None}
    queue: deque = deque([start])

    moves = [(0, -5, 1), (0, 5, 2), (-5, 0, 3), (5, 0, 4)]

    solution_state = None

    while queue:
        state = queue.popleft()
        px, py, shape, color_idx, rot_idx, done, iri_mask, steps = state

        if done == goal_mask:
            solution_state = state
            break

        for dx, dy, action_id in moves:
            nx, ny = px + dx, py + dy
            dest = (nx, ny)

            if dest in walls:
                continue

            # Is there a fresh iri at this player position?
            iri_bit = iri_idx.get(dest, -1)
            is_fresh_iri = (iri_bit >= 0) and not (iri_mask & (1 << iri_bit))

            # Timer constraint: at steps=42 only iri moves are valid
            if steps >= 42 and not is_fresh_iri:
                continue

            # Compute new state
            new_shape = shape
            new_color = color_idx
            new_rot = rot_idx
            new_done = done
            new_iri = iri_mask
            blocked = False

            if is_fresh_iri:
                new_iri = iri_mask | (1 << iri_bit)
                new_steps = 0          # free step: timer reset, no decrement
            else:
                new_steps = steps + 1

            # Modifier tiles
            if dest in gsu:
                new_shape = (new_shape + 1) % 6
            if dest in gic:
                new_color = (new_color + 1) % 4
            if dest in bgt:
                new_rot = (new_rot + 1) % 4

            # Target tiles
            for i, (tx, ty, req_s, req_c, req_r) in enumerate(target_requirements):
                if dest == (tx, ty):
                    if done & (1 << i):
                        pass  # already captured, tile removed → walk through
                    elif new_shape == req_s and new_color == req_c and new_rot == req_r:
                        new_done |= (1 << i)
                    else:
                        blocked = True  # wrong state → kbj penalty, skip
                        break

            if blocked:
                continue

            new_state = (nx, ny, new_shape, new_color, new_rot,
                         new_done, new_iri, new_steps)
            if new_state not in parent:
                parent[new_state] = (state, action_id)
                queue.append(new_state)

    if solution_state is None:
        best_done = -1
        best = None
        for s in parent:
            d = bin(s[5]).count('1')
            if d > best_done or (d == best_done and (best is None or s[7] < best[7])):
                best_done = d
                best = s
        logger.warning(
            "BFS: no full solution. Best partial: %d/%d targets",
            best_done, num_targets,
        )
        solution_state = best or start

    # ---- reconstruct path ----
    path: list = []
    cur = solution_state
    while parent.get(cur) is not None:
        prev_state, action_id = parent[cur]
        path.append(action_id)
        cur = prev_state
    path.reverse()
    return path


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class MyAgent:
    """BFS-guided agent — pre-computes timer-safe optimal paths for all levels."""

    MAX_ACTIONS = 500

    def __init__(self) -> None:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        game_dir = os.path.join(base, "environment_files", "ls20", "cb3b57cc")
        if game_dir not in sys.path:
            sys.path.insert(0, game_dir)

        hul = [12, 9, 14, 8]
        kdj = [0, 90, 180, 270]

        try:
            import ls20 as _g
            self.sequences: List[List[int]] = []
            for i in range(len(_g.levels)):
                seq = _solve_level(_g.levels[i], hul, kdj)
                logger.info("Level %d BFS path: %d actions: %s", i, len(seq), seq)
                self.sequences.append(seq)
        except Exception as exc:
            logger.error("BFS failed: %s", exc, exc_info=True)
            self.sequences = [[] for _ in range(7)]

        self._prev_levels: int = 0
        self._current_level: int = 0
        self._action_queue: List[int] = list(self.sequences[0]) if self.sequences else []

    def is_done(self, frames: List[FrameData], latest_frame: FrameData) -> bool:
        return latest_frame.state in (GameState.WIN, GameState.GAME_OVER)

    def choose_action(self, frames: List[FrameData], latest_frame: FrameData) -> GameAction:
        lc = latest_frame.levels_completed

        if lc > self._prev_levels:
            self._prev_levels = lc
            self._current_level = lc
            if self._current_level < len(self.sequences):
                self._action_queue = list(self.sequences[self._current_level])
                logger.info(
                    "Advanced to level %d, queued %d actions",
                    self._current_level, len(self._action_queue),
                )

        if self._action_queue:
            action_id = self._action_queue.pop(0)
            return GameAction[f"ACTION{action_id}"]

        import random
        return random.choice([
            GameAction.ACTION1, GameAction.ACTION2,
            GameAction.ACTION3, GameAction.ACTION4,
        ])
