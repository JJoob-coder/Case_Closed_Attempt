# visual_tron.py

"""
visual_tron.py

A simple terminal front-end for the Tron game.

- Agent 1 (your bot) is drawn in BLUE:
    head  = "◉"
    trail = "☼"

- Agent 2 (opponent) is drawn in ORANGE/YELLOW:
    head  = "@"
    trail = "$"

This file does NOT talk to the HTTP judge; it runs a local Game()
instance directly and uses your shared decision logic from brain.py
to choose moves so you can watch it play.
"""

import os
import time

from colorama import init, Fore, Style

from case_closed_game import Game, Direction, GameResult
from brain import choose_move

# Initialize colorama for Windows terminals
init(autoreset=True)

CELL_EMPTY = "."
AGENT1_TRAIL_CHAR = "☼"
AGENT2_TRAIL_CHAR = "$"
AGENT1_HEAD_CHAR = "◉"
AGENT2_HEAD_CHAR = "@"

def clear_screen() -> None:
    """Clear the terminal screen (Windows or Unix)."""
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def draw_board(game: Game) -> None:
    """Draw the current board with colored agents, heads, and trails."""
    board = game.board

    # Convert trails to plain Python lists of (x, y)
    a1_trail_list = list(game.agent1.trail)
    a2_trail_list = list(game.agent2.trail)

    # Heads: last element of each trail if present
    if a1_trail_list:
        h1x, h1y = int(a1_trail_list[-1][0]), int(a1_trail_list[-1][1])
    else:
        h1x = h1y = None

    if a2_trail_list:
        h2x, h2y = int(a2_trail_list[-1][0]), int(a2_trail_list[-1][1])
    else:
        h2x = h2y = None

    # Debug: show where the code *thinks* the heads are
    # (uncomment this if you want to see it)
    # print("HEADS:", (h1x, h1y), (h2x, h2y))

    for y in range(board.height):
        row_cells = []
        for x in range(board.width):
            # 1) HEADS FIRST (they are also in the trail, so they must win)
            if h1x is not None and x == h1x and y == h1y:
                # Try SIMPLE ASCII first to prove it works:
                # cell = Fore.BLUE + "H" + Style.RESET_ALL
                cell = Fore.BLUE + AGENT1_HEAD_CHAR + Style.RESET_ALL
            elif h2x is not None and x == h2x and y == h2y:
                # cell = Fore.YELLOW + "J" + Style.RESET_ALL
                cell = Fore.YELLOW + AGENT2_HEAD_CHAR + Style.RESET_ALL
            else:
                # 2) If not a head → maybe part of a trail?
                in_a1_trail = any((tx == x and ty == y) for (tx, ty) in a1_trail_list)
                in_a2_trail = any((tx == x and ty == y) for (tx, ty) in a2_trail_list)

                if in_a1_trail:
                    cell = Fore.BLUE + AGENT1_TRAIL_CHAR + Style.RESET_ALL
                elif in_a2_trail:
                    cell = Fore.YELLOW + AGENT2_TRAIL_CHAR + Style.RESET_ALL
                else:
                    cell = CELL_EMPTY

            row_cells.append(cell)

        print(" ".join(row_cells))


def build_state_from_game(game: Game, player_number: int) -> dict:
    """
    Construct a state dict similar to what the judge sends to /send-state.

    This lets us reuse the same choose_move() logic from brain.py
    in our visualizer.
    """
    agent1_trail = [[x, y] for (x, y) in game.agent1.trail]
    agent2_trail = [[x, y] for (x, y) in game.agent2.trail]

    state = {
        "board": game.board.grid,
        "agent1_trail": agent1_trail,
        "agent2_trail": agent2_trail,
        "agent1_length": game.agent1.length,
        "agent2_length": game.agent2.length,
        "agent1_alive": game.agent1.alive,
        "agent2_alive": game.agent2.alive,
        "agent1_boosts": game.agent1.boosts_remaining,
        "agent2_boosts": game.agent2.boosts_remaining,
        "turn_count": game.turns,
        "player_number": player_number,
    }
    return state


def move_str_to_direction_and_boost(move_str: str):
    """
    Convert a move string like "RIGHT" or "UP:BOOST" into
    (Direction enum, use_boost bool).
    """
    move_str = move_str.strip().upper()

    if ":BOOST" in move_str:
        dir_part, _ = move_str.split(":", 1)
        use_boost = True
    else:
        dir_part = move_str
        use_boost = False

    try:
        direction_enum = Direction[dir_part]  # "RIGHT" -> Direction.RIGHT
    except KeyError:
        # Fallback: if something goes wrong, just go RIGHT without boost
        direction_enum = Direction.RIGHT
        use_boost = False

    return direction_enum, use_boost


def main() -> None:
    print("USING visual_tron FROM:", __file__)
    time.sleep(1)
    game = Game()
    result = None  # GameResult or None

    while result is None:
        clear_screen()
        print(f"Turn: {game.turns}")
        draw_board(game)

        # ---------- Agent 1 (your bot) using brain.py ----------
        state1 = build_state_from_game(game, player_number=1)
        boosts1 = game.agent1.boosts_remaining
        move1_str = choose_move(state1, boosts1, player_number=1)
        dir1, boost1 = move_str_to_direction_and_boost(move1_str)

        # ---------- Agent 2 (opponent) also using brain.py ----------
        # This makes the opponent smarter too, instead of just going straight.
        state2 = build_state_from_game(game, player_number=2)
        boosts2 = game.agent2.boosts_remaining
        move2_str = choose_move(state2, boosts2, player_number=2)
        dir2, boost2 = move_str_to_direction_and_boost(move2_str)

        # Advance the game one step
        result = game.step(dir1, dir2, boost1, boost2)

        # Slow it down so the animation is visible
        time.sleep(0.15)

    # Final frame
    clear_screen()
    print(f"Final Turn: {game.turns}")
    draw_board(game)
    print("\nGame over!")
    print("Result:", result)


if __name__ == "__main__":
    main()