"""
GameEngine: owns the board, turn state, round-end logic, and scoreboard.

The player always plays X and the computer always plays O.
The scoreboard persists across rounds.
"""

from game.rules import check_winner, is_board_full
from game.renderer import board_pos_to_cell
from game.ai import choose_move

HUMAN_SYMBOL = 'X'
COMPUTER_SYMBOL = 'O'


class GameEngine:
    def __init__(self):
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = HUMAN_SYMBOL
        self.round_over = False
        self.winner = None

        # Persistent match scoreboard.
        self.x_wins = 0
        self.o_wins = 0
        self.draws = 0

    def handle_click(self, pos):
        # Do nothing after the round has ended.
        if self.round_over:
            return

        # Only the human player can make a mouse move.
        if self.current_player != HUMAN_SYMBOL:
            return

        cell = board_pos_to_cell(pos)

        if cell is None:
            return

        row, col = cell

        # TASK 3:
        # Reject clicks on cells that are already occupied.
        if self.board[row][col] is not None:
            return

        # Place the human player's symbol.
        self.board[row][col] = self.current_player

        self.check_round_end()

        # If the move ended the round, do not change the turn
        # or let the computer make another move.
        if self.round_over:
            return

        self.current_player = (
            COMPUTER_SYMBOL
            if self.current_player == HUMAN_SYMBOL
            else HUMAN_SYMBOL
        )

        self._maybe_take_computer_turn()

    def _maybe_take_computer_turn(self):
        if self.round_over or self.current_player != COMPUTER_SYMBOL:
            return

        move = choose_move(self.board)

        if move is None:
            return

        row, col = move

        self.board[row][col] = self.current_player

        self.check_round_end()

        if self.round_over:
            return

        self.current_player = (
            COMPUTER_SYMBOL
            if self.current_player == HUMAN_SYMBOL
            else HUMAN_SYMBOL
        )

    def handle_keydown(self, key):
        import pygame

        if key == pygame.K_r:
            self.start_new_round()

    def start_new_round(self):
        """
        Start a new round while keeping the scoreboard.
        """

        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = HUMAN_SYMBOL
        self.round_over = False
        self.winner = None

    def reset_match(self):
        """
        Reset the entire match, including the scoreboard.

        The separate control for this belongs to Task 4.
        """

        self.x_wins = 0
        self.o_wins = 0
        self.draws = 0

        self.start_new_round()

    def check_round_end(self):
        # Check winner first.
        winner = check_winner(self.board)

        if winner:
            self.round_over = True
            self.winner = winner

            if winner == HUMAN_SYMBOL:
                self.x_wins += 1
            elif winner == COMPUTER_SYMBOL:
                self.o_wins += 1

            return

        # Check for draw only when there is no winner.
        if is_board_full(self.board):
            self.round_over = True
            self.winner = None
            self.draws += 1

    def draw(self, surface, font):
        from game import renderer

        renderer.draw_board(surface, self.board)

        # Persistent scoreboard.
        renderer.draw_scoreboard(
            surface,
            font,
            self.x_wins,
            self.o_wins,
            self.draws
        )

        turn_label = (
            "Your turn (X)"
            if self.current_player == HUMAN_SYMBOL
            else "Computer's turn (O)"
        )

        renderer.draw_text(
            surface,
            font,
            turn_label,
            (10, 50)
        )

        if self.round_over:
            text = (
                f"{self.winner} wins!"
                if self.winner
                else "Draw!"
            )

            renderer.draw_banner(
                surface,
                font,
                f"{text} Press R for a new round."
            )