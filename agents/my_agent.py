"""
Baseline agent implementation for ARC‑AGI‑3 games.

This file provides a minimal agent class that can interact with
ARC‑AGI‑3 environments.  It defines two methods you should override:

* ``is_done(frames, latest_frame)`` — return ``True`` when the agent
  should stop playing.  A reasonable default is to stop when the
  environment reports a win or game over state.
* ``choose_action(frames, latest_frame)`` — return a ``GameAction``
  indicating the next action to take.  Complex actions (e.g. ``ACTION6``)
  require x/y coordinates (0–63) via ``action.set_data({...})``.  See
  https://docs.arcprize.org/actions for details.

The provided implementation picks actions at random and serves as a
template for you to build more capable agents.  You can import any
Python libraries needed to implement your logic, keep state across
calls, or store memory in ``frames``.
"""

from __future__ import annotations

import random
from typing import List

from arcengine import FrameData, GameAction, GameState


class MyAgent:
    """A simple baseline agent that selects actions randomly.

    Modify this class to implement your own strategy.  At each step the
    framework passes in a history of frames and the most recent frame.
    You can examine ``latest_frame.state``, ``latest_frame.levels_completed``,
    ``latest_frame.win_levels`` and ``latest_frame.available_actions`` to make
    informed decisions.

    Attributes:
        MAX_ACTIONS: A hint for the runner (unused here) about how
            many actions this agent expects to take.
    """

    MAX_ACTIONS = 80

    def is_done(self, frames: List[FrameData], latest_frame: FrameData) -> bool:
        """Determine whether the agent has finished playing.

        The default behaviour stops when the game is won or a game
        over condition is reached.  You can override this method to
        implement your own termination conditions (e.g. after some
        number of levels are complete or after a timeout).
        """
        return latest_frame.state in (GameState.WIN, GameState.GAME_OVER)

    def choose_action(self, frames: List[FrameData], latest_frame: FrameData) -> GameAction:
        """Choose the next action for the agent.

        This implementation chooses a random action from the full set
        of game actions.  If the game has not started (``NOT_PLAYED``)
        or has ended (``GAME_OVER``) it returns ``RESET`` to start a
        new episode.  For complex actions requiring coordinates the
        method selects random values for ``x`` and ``y`` in the range
        0–63.

        Replace this logic with your own to improve performance.

        Args:
            frames: A list of all frames seen so far (oldest first).
            latest_frame: The most recent frame returned from the environment.

        Returns:
            A ``GameAction`` instance representing the desired action.
        """
        # If the game is not started or has ended, reset it.  Otherwise
        # choose a random action other than RESET.
        if latest_frame.state in (GameState.NOT_PLAYED, GameState.GAME_OVER):
            action = GameAction.RESET
        else:
            # Build a list of all possible actions excluding RESET
            candidates = [a for a in GameAction if a is not GameAction.RESET]
            action = random.choice(candidates)

        # If the chosen action requires coordinates (ACTION6), assign
        # random x and y values in the allowed range.  The action
        # object exposes a ``set_data`` method in the ARC‑AGI API.  If
        # this fails (e.g. older API), fall back to setting a
        # ``data`` attribute directly.
        if hasattr(action, "is_complex") and action.is_complex():
            x = random.randint(0, 63)
            y = random.randint(0, 63)
            try:
                action.set_data({"x": x, "y": y})  # type: ignore[arg-type]
            except Exception:
                # Fallback for API versions that do not support set_data
                action.data = {"x": x, "y": y}  # type: ignore[attr-defined]

        return action