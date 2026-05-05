import tkinter as tk
from tkinter import ttk
import random
import copy


# ===================== CONSTANTS =====================

ANIMATION_DELAY = 800
BUTTON_WIDTH = 4
BUTTON_HEIGHT = 2


# ===================== CORE LOGIC =====================

class PegSolitaire:

    def __init__(self, size=7, board_type="cross"):
        self.size = size
        self.board_type = board_type
        self.board = []

        self.initialize_board()

    def initialize_board(self):

        self.board = [
            [1 for _ in range(self.size)]
            for _ in range(self.size)
        ]

        mid = self.size // 2
        self.board[mid][mid] = 0

        if self.board_type == "cross":

            remove = self.size // 3

            for r in range(self.size):
                for c in range(self.size):

                    if (
                        (r < remove or r >= self.size - remove)
                        and
                        (c < remove or c >= self.size - remove)
                    ):
                        self.board[r][c] = None

    def is_valid_move(
        self,
        r1, c1,
        r2, c2
    ):

        if not (
            0 <= r2 < self.size
            and
            0 <= c2 < self.size
        ):
            return False

        if (
            self.board[r1][c1] != 1
            or
            self.board[r2][c2] != 0
        ):
            return False

        dr = r2 - r1
        dc = c2 - c1

        valid_distance = (
            (abs(dr) == 2 and dc == 0)
            or
            (abs(dc) == 2 and dr == 0)
            or
            (abs(dr) == 2 and abs(dc) == 2)
        )

        if not valid_distance:
            return False

        mid_r = r1 + dr // 2
        mid_c = c1 + dc // 2

        return self.board[mid_r][mid_c] == 1

    def make_move(
        self,
        r1, c1,
        r2, c2
    ):

        dr = r2 - r1
        dc = c2 - c1

        mid_r = r1 + dr // 2
        mid_c = c1 + dc // 2

        self.board[r1][c1] = 0
        self.board[mid_r][mid_c] = 0
        self.board[r2][c2] = 1

    def has_valid_moves(self):

        for r in range(self.size):
            for c in range(self.size):

                if self.board[r][c] == 1:

                    for dr in [-2, 0, 2]:
                        for dc in [-2, 0, 2]:

                            if dr == 0 and dc == 0:
                                continue

                            if self.is_valid_move(
                                r, c,
                                r + dr,
                                c + dc
                            ):
                                return True

        return False

    def count_pegs(self):

        return sum(
            row.count(1)
            for row in self.board
            if row
        )


# ===================== GAME TYPES =====================

class BaseGame(PegSolitaire):

    def is_game_over(self):

        return (
            self.count_pegs() == 1
            or
            not self.has_valid_moves()
        )


class ManualGame(BaseGame):
    pass


class AutomatedGame(BaseGame):

    def make_auto_move(self):

        possible_moves = []

        for r in range(self.size):
            for c in range(self.size):

                if self.board[r][c] == 1:

                    for dr in [-2, 0, 2]:
                        for dc in [-2, 0, 2]:

                            if dr == 0 and dc == 0:
                                continue

                            r2 = r + dr
                            c2 = c + dc

                            if self.is_valid_move(
                                r, c,
                                r2, c2
                            ):
                                possible_moves.append(
                                    (r, c, r2, c2)
                                )

        if possible_moves:
            return random.choice(
                possible_moves
            )

        return None


# ===================== RECORDING =====================

class GameRecorder:

    def __init__(self):

        self.actions = []
        self.is_recording = False

    def start(self):

        self.actions = []
        self.is_recording = True

    def stop(self):

        self.is_recording = False

    def add_move(
        self,
        r1, c1,
        r2, c2
    ):

        if self.is_recording:

            self.actions.append(
                (
                    "move",
                    r1, c1,
                    r2, c2
                )
            )

    def add_randomize(
        self,
        board_snapshot
    ):

        if self.is_recording:

            self.actions.append(
                (
                    "randomize",
                    copy.deepcopy(
                        board_snapshot
                    )
                )
            )

    def save(
        self,
        filename="game_record.txt"
    ):

        with open(
            filename,
            "w"
        ) as file:

            for action in self.actions:

                file.write(
                    repr(action)
                    + "\n"
                )

    def load(
        self,
        filename="game_record.txt"
    ):

        try:

            with open(
                filename,
                "r"
            ) as file:

                lines = []

                for line in file.readlines():
                    lines.append(
                        eval(line.strip())
                    )

                return lines

        except FileNotFoundError:
            return []


# ===================== GUI =====================

class PegSolitaireGUI:

    def __init__(self, root):

        self.root = root
        self.root.title(
            "Peg Solitaire"
        )

        self.selected = None

        self.recorder = GameRecorder()

        self.size_var = tk.IntVar(
            value=7
        )

        self.type_var = tk.StringVar(
            value="cross"
        )

        self.mode_var = tk.StringVar(
            value="manual"
        )

        self.build_ui()

        self.new_game()

    def build_ui(self):

        control_frame = tk.Frame(
            self.root
        )
        control_frame.pack(
            pady=10
        )

        ttk.Label(
            control_frame,
            text="Board Size:"
        ).pack(side=tk.LEFT)

        ttk.Combobox(
            control_frame,
            textvariable=self.size_var,
            values=[5, 7, 9],
            width=5,
            state="readonly"
        ).pack(side=tk.LEFT)

        ttk.Label(
            control_frame,
            text="Board Type:"
        ).pack(side=tk.LEFT)

        ttk.Combobox(
            control_frame,
            textvariable=self.type_var,
            values=["cross", "full"],
            width=8,
            state="readonly"
        ).pack(side=tk.LEFT)

        ttk.Label(
            control_frame,
            text="Mode:"
        ).pack(side=tk.LEFT)

        ttk.Combobox(
            control_frame,
            textvariable=self.mode_var,
            values=[
                "manual",
                "automated"
            ],
            width=10,
            state="readonly"
        ).pack(side=tk.LEFT)

        button_config = [
            ("New Game", self.new_game),
            ("Autoplay", self.auto_play),
            ("Randomize", self.randomize_board),
            ("Record", self.toggle_record),
            ("Replay", self.replay_game)
        ]

        for text, command in button_config:

            ttk.Button(
                control_frame,
                text=text,
                command=command
            ).pack(side=tk.LEFT)

        self.status_label = tk.Label(
            self.root,
            text=""
        )
        self.status_label.pack()

        self.board_frame = tk.Frame(
            self.root
        )
        self.board_frame.pack()

    def update_status(
        self,
        message=""
    ):

        status = (
            f"Pegs Remaining: "
            f"{self.game.count_pegs()}"
        )

        if message:
            status += f" | {message}"

        self.status_label.config(
            text=status
        )

    def toggle_record(self):

        if not self.recorder.is_recording:

            self.recorder.start()

            self.update_status(
                "Recording Started"
            )

        else:

            self.recorder.stop()

            self.recorder.save()

            self.update_status(
                "Recording Saved"
            )

    def new_game(self):

        if (
            self.mode_var.get()
            == "manual"
        ):

            self.game = ManualGame(
                self.size_var.get(),
                self.type_var.get()
            )

        else:

            self.game = AutomatedGame(
                self.size_var.get(),
                self.type_var.get()
            )

        self.selected = None

        self.draw_board()

    def execute_move(
        self,
        r1, c1,
        r2, c2
    ):

        if self.game.is_valid_move(
            r1, c1,
            r2, c2
        ):

            self.game.make_move(
                r1, c1,
                r2, c2
            )

            self.recorder.add_move(
                r1, c1,
                r2, c2
            )

            self.draw_board()

            return True

        return False

    def randomize_board(self):

        for r in range(
            self.game.size
        ):
            for c in range(
                self.game.size
            ):

                if (
                    self.game.board[r][c]
                    is not None
                ):

                    self.game.board[r][c] = (
                        random.choice(
                            [0, 1]
                        )
                    )

        self.recorder.add_randomize(
            self.game.board
        )

        self.draw_board()

    def draw_board(self):

        for widget in (
            self.board_frame
            .winfo_children()
        ):
            widget.destroy()

        for r in range(
            self.game.size
        ):
            for c in range(
                self.game.size
            ):

                cell = (
                    self.game.board[r][c]
                )

                if cell is None:

                    tk.Label(
                        self.board_frame
                    ).grid(
                        row=r,
                        column=c
                    )

                else:

                    color = (
                        "blue"
                        if cell == 1
                        else "white"
                    )

                    if (
                        self.selected
                        == (r, c)
                    ):
                        color = "red"

                    tk.Button(
                        self.board_frame,
                        bg=color,
                        width=BUTTON_WIDTH,
                        height=BUTTON_HEIGHT,
                        command=lambda r=r, c=c:
                            self.cell_clicked(
                                r, c
                            )
                    ).grid(
                        row=r,
                        column=c
                    )

    def cell_clicked(
        self,
        r, c
    ):

        if not isinstance(
            self.game,
            ManualGame
        ):
            return

        if self.selected is None:

            if (
                self.game.board[r][c]
                == 1
            ):

                self.selected = (
                    r, c
                )

                self.draw_board()

            return

        r1, c1 = self.selected

        if self.execute_move(
            r1, c1,
            r, c
        ):

            self.selected = None

        elif (
            self.game.board[r][c]
            == 1
        ):

            self.selected = (
                r, c
            )

        self.draw_board()

    def auto_play(self):

        if not isinstance(
            self.game,
            AutomatedGame
        ):
            return

        def step():

            move = (
                self.game
                .make_auto_move()
            )

            if move:

                self.execute_move(
                    *move
                )

                self.root.after(
                    ANIMATION_DELAY,
                    step
                )

        step()

    def replay_game(self):

        lines = (
            self.recorder
            .load()
        )

        if not lines:

            self.update_status(
                "No replay data found"
            )

            return

        self.new_game()

        def step(index):

            if (
                index
                >= len(lines)
            ):

                self.update_status(
                    "Replay Finished"
                )

                return

            action = lines[index]

            if action[0] == "move":

                try:

                    r1, c1, r2, c2 = action[1:]

                except Exception:

                    self.update_status(
                        "Corrupt replay file"
                    )

                    return

                self.execute_move(
                    r1, c1,
                    r2, c2
                )

            elif (
                action[0]
                == "randomize"
            ):

                self.game.board = copy.deepcopy(
                    action[1]
                )

                self.draw_board()

            self.root.after(
                ANIMATION_DELAY,
                lambda:
                    step(
                        index + 1
                    )
            )

        step(0)


# ===================== RUN =====================

if __name__ == "__main__":

    root = tk.Tk()

    app = PegSolitaireGUI(
        root
    )

    root.mainloop()