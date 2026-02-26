"""
Runner script for ARC‑AGI‑3 games.

This script loads a game from the ARC‑AGI toolkit, instantiates your
custom agent, and steps through the environment until the agent
terminates the game or a maximum number of actions is reached.  It
uses the offline operation mode by default so that you do not need an
API key to experiment locally.

Usage:

    python run_agent.py --game ls20 --max-actions 80 --render-mode terminal

The game ID can be any ID returned from
`arc_agi.Arcade(operation_mode=OperationMode.OFFLINE).get_environments()`.  The
render mode can be `terminal`, `terminal-fast` or `human` (matplotlib).
"""

import argparse
import logging
from typing import Optional

from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

# Import your agent class from the agents package.  Feel free to
# rename MyAgent to something more descriptive in agents/my_agent.py.
from agents.my_agent import MyAgent


def run_game(
    game_id: str,
    max_actions: int = 80,
    render_mode: str = "terminal",
) -> None:
    """Run a single ARC‑AGI game with your custom agent.

    Args:
        game_id: Identifier of the game to play (e.g. "ls20").
        max_actions: Maximum number of actions the agent is allowed to take.
        render_mode: One of ``"terminal"``, ``"terminal-fast"`` or ``"human"``.
    """
    # Initialize the toolkit in OFFLINE mode (local games only).  The
    # OperationMode can be switched to ONLINE to play games via the API do not change it.
    arc = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arc.make(game_id, render_mode=render_mode)
    if env is None:
        raise RuntimeError(f"Game {game_id} could not be loaded. Ensure the environment files are available and the ID is correct.")

    # Reset the environment to start a new session.  The RESET action
    # returns the initial FrameDataRaw.  It is stored as the first
    # frame in the list for the agent's history.
    initial_frame = env.step(GameAction.RESET)
    frames = [initial_frame]
    agent = MyAgent()
    actions_taken = 0

    # Continue looping until the agent decides the game is done or the
    # maximum number of actions has been reached.
    while (
        not agent.is_done(frames, frames[-1])
        and actions_taken < max_actions
    ):
        latest_frame = frames[-1]
        action = agent.choose_action(frames, latest_frame)
        # Determine whether the action requires extra data (complex actions
        # like ACTION6 require x,y coordinates).
        data: Optional[dict[str, int]] = None
        try:
            if hasattr(action, "is_complex") and action.is_complex():
                # Try to extract the coordinates from the agent's action.
                # The action may expose a data attribute or an action_data
                # object with a model_dump() method.
                if hasattr(action, "action_data") and hasattr(action.action_data, "model_dump"):
                    data = action.action_data.model_dump()  # type: ignore[assignment]
                elif hasattr(action, "data") and isinstance(action.data, dict):
                    data = action.data  # type: ignore[assignment]
        except Exception:
            # If we cannot introspect the action, fall back to no data.
            data = None

        # Step the environment.  For simple actions data can be omitted.
        if data:
            obs = env.step(action, data=data)
        else:
            obs = env.step(action)

        frames.append(obs)
        actions_taken += 1
        # Log progress for debugging/analysis.
        try:
            state_name = obs.state.name if hasattr(obs.state, "name") else str(obs.state)
            levels_completed = obs.levels_completed
            win_levels = obs.win_levels
        except Exception:
            state_name = "Unknown"
            levels_completed = "?"
            win_levels = "?"
        logging.info(
            f"Step {actions_taken}: action={action.name}, state={state_name}, levels_completed={levels_completed}/{win_levels}"
        )

    # Print summary after loop finishes.
    final = frames[-1]
    try:
        final_state = final.state.name
        levels_completed = final.levels_completed
        win_levels = final.win_levels
    except Exception:
        final_state = str(final.state)
        levels_completed = "?"
        win_levels = "?"
    logging.info(
        f"Finished after {actions_taken} actions. Final state: {final_state}. Levels completed: {levels_completed}/{win_levels}."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run an ARC‑AGI‑3 environment with a custom agent."
    )
    parser.add_argument(
        "--game",
        type=str,
        default="ls20",
        help="Game ID to play (e.g., ls20)",
    )
    parser.add_argument(
        "--max-actions",
        type=int,
        default=10,
        help="Maximum number of actions to take",
    )
    parser.add_argument(
        "--render-mode",
        type=str,
        default="terminal-fast",
        choices=["terminal", "terminal-fast", "human"],
        help="Render mode: terminal, terminal-fast or human",
    )

    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    run_game(args.game, args.max_actions, args.render_mode)


if __name__ == "__main__":
    main()