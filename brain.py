"""
brain.py

This file contains the "brain" of your Tron agent: given a game state and some
metadata, decide what move to make.

Used by:
  - agent.py        (the HTTP API used by the judge)
  - visual_tron.py  (local visualizer to watch your bot play)
"""

from typing import Dict, Any, Tuple, List

# Directions as (dx, dy) in board coordinates (x to the right, y down)
DIRECTION_VECTORS = {
    "UP":    (0, -1),
    "DOWN":  (0,  1),
    "LEFT":  (-1, 0),
    "RIGHT": (1,  0),
}


def _get_head_position(state: Dict[str, Any], player_number: int) -> Tuple[int, int]:
    """Return (x, y) for the head of the given player from the state."""
    if player_number == 1:
        trail = state.get("agent1_trail", [])
    else:
        trail = state.get("agent2_trail", [])

    if not trail:
        return 0, 0

    head = trail[-1]  # last element is the head
    return int(head[0]), int(head[1])


def _get_board_size(board: List[List[int]]) -> Tuple[int, int]:
    """Return (width, height) of the board."""
    if not board or not board[0]:
        return 0, 0
    height = len(board)
    width = len(board[0])
    return width, height


def _is_cell_safe(board: List[List[int]], x: int, y: int) -> bool:
    """
    Check whether a cell is safe to move into.

    We treat 0 as empty, anything else as occupied/dangerous.
    We apply torus wrapping: going off an edge wraps around.
    """
    height = len(board)
    if height == 0:
        return True

    width = len(board[0])

    x = x % width
    y = y % height

    cell_value = board[y][x]
    return cell_value == 0  # EMPTY


def _choose_safe_direction(
    board: List[List[int]],
    head_x: int,
    head_y: int,
    preferred_order: List[str],
) -> str:
    """
    From a list of direction names, return the first one that leads to a safe cell.
    If none are safe, fall back to "RIGHT".
    """
    width, height = _get_board_size(board)
    if width == 0 or height == 0:
        return "RIGHT"

    for direction_name in preferred_order:
        dx, dy = DIRECTION_VECTORS[direction_name]
        new_x = (head_x + dx) % width
        new_y = (head_y + dy) % height

        if _is_cell_safe(board, new_x, new_y):
            return direction_name

    return "RIGHT"


def choose_move(state: Dict[str, Any], boosts_remaining: int, player_number: int) -> str:
    """
    Decide which move to make.

    Parameters
    ----------
    state : dict
        Should contain at least:
          - "board": 2D list of ints (0 = empty, non-zero = occupied)
          - "agent1_trail", "agent2_trail": lists of [x, y] pairs
          - "turn_count": int
    boosts_remaining : int
        Number of boosts this agent still has (not used yet).
    player_number : int
        1 if this agent is player 1, 2 if player 2.

    Returns
    -------
    move : str
        "UP", "DOWN", "LEFT", or "RIGHT"
        (You can later add ":BOOST" to use boost.)
    """
    board = state.get("board", [])
    if not board:
        return "RIGHT"

    head_x, head_y = _get_head_position(state, player_number)
    turn = state.get("turn_count", 0)

    # To make movement look less like a straight line and more "alive",
    # we change the preferred direction order depending on the turn.
    # This is just for visualization and basic behavior.
    pattern = turn % 4
    if pattern == 0:
        preferred_order = ["RIGHT", "DOWN", "UP", "LEFT"]
    elif pattern == 1:
        preferred_order = ["DOWN", "LEFT", "RIGHT", "UP"]
    elif pattern == 2:
        preferred_order = ["LEFT", "UP", "DOWN", "RIGHT"]
    else:
        preferred_order = ["UP", "RIGHT", "LEFT", "DOWN"]

    direction_name = _choose_safe_direction(board, head_x, head_y, preferred_order)

    move = direction_name  # no boost yet

    # Optional: debug print so you can see it changing in visual_tron
    # print(f"[BRAIN] turn={turn} head=({head_x},{head_y}) move={move}")

    return move