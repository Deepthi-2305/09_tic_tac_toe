"""
GameEngine: owns the board, turn state, round-end logic,
scoreboard, first-player choice, and restart controls.
"""

from game.rules import check_winner, is_board_full
from game.renderer import board_pos_to_cell
from game.ai import choose_move

HUMAN_SYMBOL = 'X'
COMPUTER_SYMBOL = 'O'


class GameEngine:
    def __init__(self):
        # Board and round state
        self.board = [[None] * 3 for _ in range(3)]
        self.round_over = False
        self.winner = None

        # The player can choose which symbol starts.
        self.starting_symbol = HUMAN_SYMBOL

        # Current turn
        self.current_player = self.starting_symbol

        # Persistent scoreboard
        self.x_wins = 0
        self.o_wins = 0
        self.draws = 0

        # If O starts, the computer should move immediately.
        self._maybe_take_computer_turn()

    def handle_click(self, pos):
        # Don't allow moves after the round has ended.
        if self.round_over:
            return

        # The human can only make a move when X is the current player.
        if self.current_player != HUMAN_SYMBOL:
            return

        cell = board_pos_to_cell(pos)

        if cell is None:
            return

        row, col = cell

        # Task 3: reject an occupied cell.
        if self.board[row][col] is not None:
            return

        # Place X.
        self.board[row][col] = HUMAN_SYMBOL

        self.check_round_end()

        if self.round_over:
            return

        self.current_player = COMPUTER_SYMBOL

        self._maybe_take_computer_turn()

    def _maybe_take_computer_turn(self):
        """
        Let the computer make a move whenever O is the current player.

        This also handles the case where O is selected as the
        starting symbol.
        """

        if self.round_over:
            return

        if self.current_player != COMPUTER_SYMBOL:
            return

        move = choose_move(self.board)

        if move is None:
            return

        row, col = move

        # Place O.
        self.board[row][col] = COMPUTER_SYMBOL

        self.check_round_end()

        if self.round_over:
            return

        self.current_player = HUMAN_SYMBOL

    def handle_keydown(self, key):
        import pygame

        # Choose X as the starting player.
        if key == pygame.K_x:
            self.starting_symbol = HUMAN_SYMBOL
            return

        # Choose O as the starting player.
        if key == pygame.K_o:
            self.starting_symbol = COMPUTER_SYMBOL
            return

        # R = restart current round.
        # Scoreboard remains unchanged.
        if key == pygame.K_r:
            self.start_new_round()
            return

        # M = reset the entire match.
        # Scoreboard is cleared.
        if key == pygame.K_m:
            self.reset_match()
            return

    def start_new_round(self):
        """
        Start a fresh round while keeping the scoreboard.

        The currently selected starting symbol is used for
        the new round.
        """

        self.board = [[None] * 3 for _ in range(3)]
        self.round_over = False
        self.winner = None
        self.current_player = self.starting_symbol

        # If O was selected to start, the computer moves immediately.
        self._maybe_take_computer_turn()

    def reset_match(self):
        """
        Reset the complete match.

        This clears both the board and scoreboard.
        """

        self.x_wins = 0
        self.o_wins = 0
        self.draws = 0

        self.start_new_round()

    def check_round_end(self):
        # Winner always has priority over draw.
        winner = check_winner(self.board)

        if winner:
            self.round_over = True
            self.winner = winner

            if winner == HUMAN_SYMBOL:
                self.x_wins += 1
            elif winner == COMPUTER_SYMBOL:
                self.o_wins += 1

            return

        # Only check for draw if nobody has won.
        if is_board_full(self.board):
            self.round_over = True
            self.winner = None
            self.draws += 1

    def draw(self, surface, font):
        from game import renderer

        renderer.draw_board(surface, self.board)

        # Scoreboard
        renderer.draw_scoreboard(
            surface,
            font,
            self.x_wins,
            self.o_wins,
            self.draws
        )

        # Current starting-player selection
        renderer.draw_text(
            surface,
            font,
            f"Starts next round: {self.starting_symbol}",
            (10, 45)
        )

        # Current turn
        if self.current_player == HUMAN_SYMBOL:
            turn_label = "Your turn (X)"
        else:
            turn_label = "Computer's turn (O)"

        renderer.draw_text(
            surface,
            font,
            turn_label,
            (10, 70)
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
                f"{text} Press R for new round."
            )