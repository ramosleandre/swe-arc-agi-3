# Checkpoint 01 – Environment Exploration

## What I tested
- Read `run_agent.py` and `agents/my_agent.py` (baseline random agent)
- Read `environment_files/ls20/cb3b57cc/ls20.py` (full game source)
- Ran `probe_01b.py` and `probe_02.py` to inspect FrameData and game state
- Ran `probe_03.py` to map all 7 levels

## Observed from logs/frames/source

### Game ID: ls20 – 7 levels, win on completing all 7

### Mechanics (from source code)
- Player sprite (tag "caf") moves in 4 directions (ACTION1=UP, ACTION2=DOWN, ACTION3=LEFT, ACTION4=RIGHT)
- Movement step = 5 world units per action
- Available actions are 1,2,3,4 (confirmed from metadata baseline_actions: 29,41,172,49,53,62,82 — these look like encoded action IDs)
- Walls (tag "jdd"): block movement entirely
- Shape changers (tag "gsu"): `snw = (snw+1) % 6` each visit
- Color changers (tag "gic"): `tmx = (tmx+1) % 4` each visit
- Rotation changers (tag "bgt"): `tuv = (tuv+1) % 4` each visit
- Power-ups (tag "iri"): refill timer to full (42), then removed
- Targets (tag "mae"): if `qhg(i)` = (snw==gfy[i] AND tmx==vxy[i] AND tuv==cjl[i]), capture it; else blocked+penalty
- Win condition: all targets in level captured → `next_level()` → after level 6, WIN
- Timer: 42 steps per life, 3 lives; on timer expiry → life lost, position/state reset
- Level 6: fog=True (visual only, no effect on logic)

### Level summaries
| Level | Start (world) | Targets | Changers needed |
|-------|--------------|---------|-----------------|
| 0 | (39,45) | 1 @ (34,10): sh=5,col=1,rot=0 | bgt (rot 3→0) |
| 1 | (29,40) | 1 @ (14,40): sh=5,col=1,rot=3 | bgt 3× (rot 0→3) |
| 2 | (9,45) | 1 @ (54,50): sh=5,col=1,rot=3 | gic 1×(col 0→1), bgt 3×(rot 0→3) |
| 3 | (54,5) | 1 @ (9,5): sh=5,col=1,rot=0 | gsu 1×(sh 4→5), gic 1×(col 2→1) |
| 4 | (54,50) | 1 @ (54,5): sh=5,col=1,rot=1 | gsu 1×(sh 4→5), gic 1×(col 0→1), bgt 1×(rot 0→1) |
| 5 | (24,50) | 2 targets: sh=5,col=1,rot=1 @ (54,50); sh=0,col=3,rot=1 @ (54,35) | multiple |
| 6 | (14,10) | 1 @ (29,50): sh=0,col=3,rot=2 | gsu 5×, gic 3×, bgt 2× |

### BFS state space
State = (px, py, shape_idx, color_idx, rot_idx, targets_done_bitmask)
- 12×12 grid × 6 shapes × 4 colors × 4 rotations × 2^targets ≤ 27,648 states per level
- BFS is tractable

### Key insight
- Fog in level 6 is visual-only
- Target tiles are "soft walls" (blocked if wrong state)
- Power-ups refill timer; not needed if path ≤ 42 steps

## What I changed next
- Writing probe_03.py to map all levels (linked above)
- Will implement BFS-based solver in agents/my_agent.py

## Probe scripts
- `probe_01.py`: FrameData attribute exploration
- `probe_01b.py`: Minimal probe for game internals
- `probe_02.py`: Direct game module import, level 0 data
- `probe_03.py`: All 7 level maps with grid visualization
