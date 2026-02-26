# Simple ARC‑AGI‑3 Code Agent POC

This repository contains a minimal setup to experiment with
[ARC‑AGI‑3](https://docs.arcprize.org/) environments in an offline,
local setting.  It is designed for quick iteration with code assistants
like Claude Code, Codex, Cursor or Copilot: you modify a single
agent file (`agents/my_agent.py`), run the environment, inspect
the logs and iterate.  Everything here is intentionally lightweight
so you can drop it into a new directory and start experimenting
immediately.

## Contents

* `run_agent.py` — a simple runner script that loads a specified game,
  invokes your agent for a limited number of actions, logs progress
  and prints the final outcome.
* `agents/my_agent.py` — a skeleton agent that you can extend.  Modify
  the `choose_action` and `is_done` methods to control how the agent
  behaves.  The provided implementation picks random actions.
* `agents/__init__.py` — exposes your agent class for import.
* `requirements.txt` — Python dependencies for this proof‑of‑concept
  (primarily `arc‑agi`).

## Getting started

1. **Install dependencies.**  The
   [ARC‑AGI toolkit](https://pypi.org/project/arc-agi/) is required
   and available on PyPI.  Create a virtual environment if desired
   and install the dependencies with:

   ```bash
   pip install -r requirements.txt
   ```

   Alternatively you can install directly with:

   ```bash
   pip install arc-agi
   ```

2. **Explore available games (optional).**  To see which games are
   available in your local environment, run the following in a
   Python REPL:

   ```python
   import arc_agi
   arc = arc_agi.Arcade(operation_mode=arc_agi.OperationMode.OFFLINE)
   for info in arc.get_environments():
       print(info.game_id, info.title)
   ```

   If you have not downloaded any environment files yet, the toolkit
   will automatically fetch them the first time you load a game (see
   the next step).  An internet connection is required for this
   initial download.

3. **Run a game with your agent.**  Use the runner script to play a
   game.  The `--game` argument defaults to `ls20` and `--max-actions`
   controls how many moves the agent is allowed to take:

   ```bash
   python run_agent.py --game ls20 --max-actions 10
   ```

   The script will load the game locally, reset it, then repeatedly
   call your agent’s `choose_action` method until the game ends or
   the action limit is reached.  Progress is logged to the console
   including the action taken, the current state (e.g. `WIN` or
   `GAME_OVER`) and how many levels have been completed.

4. **Edit your agent.**  Open `agents/my_agent.py` and implement
   smarter logic in `choose_action` and `is_done`.  The
   `latest_frame` passed to these methods is an instance of
   `arcengine.FrameData` and contains properties such as `state`,
   `levels_completed`, `win_levels` and `available_actions` that you
   can inspect to make decisions.  For games that support
   coordinate‑based actions (`ACTION6`), use `action.set_data({"x": x,
   "y": y})` to supply the coordinates.

5. **Iterate with your code assistant.**  Using your preferred tool
   (Claude Code, Codex, Cursor, Copilot, etc.), instruct it to modify
   `agents/my_agent.py`, run the script, inspect the output, and
   repeat.  Because everything is local, you can iterate quickly
   without hitting API rate limits.  When you’re satisfied, you can
   switch the `operation_mode` in `run_agent.py` to `ONLINE` and
   provide an `ARC_API_KEY` to get official scorecards and shareable
   replays.

## Notes

* This proof‑of‑concept runs games **offline** by default.  To use the
  online API (for example, to record scorecards and replays), set
  `operation_mode=arc_agi.OperationMode.ONLINE` in `run_agent.py` and
  provide a valid API key via the `ARC_API_KEY` environment variable.
* Complex actions (`ACTION6`) require `(x, y)` coordinates in the
  0–63 range.  The skeleton agent chooses random coordinates when
  necessary.  You may want to implement a smarter sampling strategy
  based on the game state.
* The `arc-agi` toolkit will automatically download environment
  description files on first use.  After that, you can work
  completely offline.