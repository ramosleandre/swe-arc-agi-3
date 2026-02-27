# Checkpoint 02 – BFS Bug: Wrong Grid Mapping + Timer Fix

## What I tested
- Implemented initial BFS in agents/my_agent.py using exact sprite world positions
- Ran: `python3 run_agent.py --game ls20 --max-actions 200`
- Observed: levels 0 and 1 completed (WIN on 0/1), GAME_OVER at level 2 step 184

## Observed problem
Level 2 path was 46 steps but timer = 42 → life lost mid-level.
Adding timer-aware BFS (with iri power-up state tracking) still failed for levels 2, 4, 5, 6.
BFS reported "no full solution" for level 2 even though iri tiles exist.

## Root cause found (probe_04.py)
The game's `rbt(qul, cfy, 5, 5)` checks sprites within a **5×5 window** at the destination, NOT at the exact destination position.

Example: iri power-up sprite is at world **(20, 31)** but is collected when player moves to **(19, 30)** (the nearest player-grid position that covers it):
- Player x positions: `{4 + 5k}` = {4, 9, 14, 19, 24, …}
- Player y positions: `{5j}` = {0, 5, 10, 15, 20, 25, 30, …}
- From (20, 31): `nx = 4 + 5*((20-4)//5) = 19`, `ny = 5*(31//5) = 30` → triggered at **(19, 30)**

My BFS was checking `(19, 30) in iri_idx` where `iri_idx = {(20,31): 0}` → MISS!

## Fix applied
Added `_canonical(sx, sy)` function that maps any sprite world position to the canonical player-grid position that triggers it:
```python
def _canonical(sx, sy):
    nx = 4 + 5 * ((sx - 4) // 5)
    ny = 5 * (sy // 5)
    return (nx, ny)
```
All interaction maps (gsu, gic, bgt, iri, mae) now use canonical positions.
Timer-aware BFS state: `(px, py, shape, color, rot, done, iri_mask, steps_since_refill)`.

## Results after fix
| Level | BFS path (steps) | Power-up needed? | Status |
|-------|-----------------|-----------------|--------|
| 0     | 14              | No              | ✓      |
| 1     | 41              | No              | ✓      |
| 2     | 48              | Yes (1 iri)     | ✓      |
| 3     | 41              | No              | ✓      |
| 4     | 45              | Yes (1 iri)     | ✓      |
| 5     | 54              | Yes (1+ iri)    | ✓      |
| 6     | 45              | Yes (1 iri)     | ✓      |

**Final result: 100% win rate, 288 actions per run (4/4 runs)**

## Probe scripts used
- `probe_04.py`: Verified sprite tags in levels 2,4,5,6 and confirmed iri tiles exist at offset positions
