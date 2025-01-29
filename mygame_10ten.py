import tkinter as tk
from tkinter import messagebox
import time
import json
import math
import tkinter.font as tkFont
from tkinter import simpledialog  # Correct import for simpledialog

class NumberPuzzleGUI:
    def __init__(self):
        self.size = 10  # Default size
        self.board = []
        self.current_number = 1
        self.game_over = False
        self.current_position = None
        self.buttons = []
        self.moves = []
        self.start_time = 0
        self.elapsed_time = 0
        self.scores_file = "scores.json"
        self.top_scores = self.load_scores()

        self.window = tk.Tk()
        self.window.title("Number Puzzle")
        self.window.resizable(False, False)

        # Font for numbers
        self.number_font = tkFont.Font(family="Helvetica", size=12, weight="bold")

        # Load configuration
        with open('config.json') as f:
            config = json.load(f)
            self.themes = config['themes']
            self.board_sizes = config['board_sizes']
        
        # Theme colors
        self.themes = {
            "dark": {
                "bg": "#333333",
                "fg": "white",
                "button_bg": "#555555",
                "button_fg": "white",
                "button_active_bg": "#777777",
            },
            "white": {
                "bg": "white",
                "fg": "black",
                "button_bg": "SystemButtonFace",
                "button_fg": "black",
                 "button_active_bg": "#e0e0e0",
            },
        }
        self.current_theme = "white"  # Default theme
        
        # Main Frame
        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Option Menu for Board Size
        self.size_var = tk.StringVar(value="Standard (10x10)")
        size_options = list(self.board_sizes.keys())
        size_menu = tk.OptionMenu(self.main_frame, self.size_var, *size_options, command=self.set_board_size)
        size_menu.pack(pady=10)


        # Info Label
        self.label_info = tk.Label(self.main_frame, text="Choose board size to start")
        self.label_info.pack(pady=10)

        # Time Label
        self.label_time = tk.Label(self.main_frame, text="Time: 0 s")
        self.label_time.pack(pady=5)

        # Move Counter
        self.move_counter = tk.Label(self.main_frame, text="Moves: 0")
        self.move_counter.pack(pady=5)

        # New Game Button
        self.btn_new_game = tk.Button(self.main_frame, text="New Game", command=self.start_new_game)
        self.btn_new_game.pack(pady=5)

        # Theme Switch Button
        self.btn_theme = tk.Button(self.main_frame, text="Dark Theme", command=self.switch_theme)
        self.btn_theme.pack(pady=10)

        # Board Frame
        self.board_frame = tk.Frame(self.main_frame)
        self.board_frame.pack()

        # Undo Button
        self.btn_undo = tk.Button(self.main_frame, text="Undo", command=self.undo_move, state=tk.DISABLED)
        self.btn_undo.pack(pady=5)

        # Score Sidebar
        self.score_frame = tk.Frame(self.window, width=250)
        self.score_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Score Lists Frame
        self.score_lists_frame = tk.Frame(self.score_frame)
        self.score_lists_frame.pack(fill=tk.BOTH, expand=True)

        # Top 10 10x10 Label
        tk.Label(self.score_lists_frame, text="Top 10 10x10 Scores", font="Helvetica 12 bold").pack(pady=5)

        # Listbox for 10x10 scores
        self.score_listbox_10x10 = tk.Listbox(self.score_lists_frame, width=40, height=10)
        self.score_listbox_10x10.pack(padx=15, pady=10, fill=tk.BOTH)

        # Top 10 5x5 Label
        tk.Label(self.score_lists_frame, text="Top 10 5x5 Scores", font="Helvetica 12 bold").pack(pady=10)

        # Listbox for 5x5 scores
        self.score_listbox_5x5 = tk.Listbox(self.score_lists_frame, width=40, height=10)
        self.score_listbox_5x5.pack(padx=15, pady=10, fill=tk.BOTH)
        
        self.update_score_list()
        self.create_board() # Generate initial board (10x10 by default)
        self.apply_theme()

    def set_board_size(self, option):
        if option == "Small (5x5)":
           self.size = 5
        elif option == "Standard (10x10)":
            self.size = 10
        
        self.create_board()
        self.start_new_game() # Start a new game with the new size.

    def create_board(self):
        # Clear old board buttons
        for row_buttons in self.buttons:
            for button in row_buttons:
                button.destroy()
        self.buttons = []

        # Clear old game board
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        
        #Create new board
        for row in range(self.size):
           button_row = []
           for col in range(self.size):
              button = tk.Button(self.board_frame, text=" ", width=4, height=2,
                                 command=lambda r=row, c=col: self.make_move(r, c), font=self.number_font)
              button.grid(row=row, column=col, padx=2, pady=2)
              button_row.append(button)
           self.buttons.append(button_row)
        self.apply_theme()
    
    def load_scores(self):
        try:
            with open(self.scores_file, "r") as f:
                scores = json.load(f)
                # Ensure that the scores dictionary has keys for both "10x10" and "5x5"
                if not isinstance(scores, dict):
                    scores = {}
                if "10x10" not in scores:
                    scores["10x10"] = []
                if "5x5" not in scores:
                    scores["5x5"] = []
                return scores
        except FileNotFoundError:
            return {"10x10": [], "5x5": []}

    def save_scores(self):
        with open(self.scores_file, "w") as f:
            json.dump(self.top_scores, f)

    def is_valid_position(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size

    def is_valid_move(self, next_row, next_col):
        if not self.is_valid_position(next_row, next_col):
            return False
        if self.board[next_row][next_col] != 0:
            return False
        return True

    def get_possible_moves(self):
        if self.current_position is None:
            return []

        row, col = self.current_position
        possible_moves = []
        #Straight
        moves_straight = [(0, -3), (0, 3), (-3, 0), (3, 0)]
        for dr, dc in moves_straight:
            next_row, next_col = row + dr, col + dc
            if self.is_valid_move(next_row, next_col):
              possible_moves.append((next_row, next_col))
        #Diagonal
        moves_diagonal = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        for dr, dc in moves_diagonal:
           next_row, next_col = row + dr, col + dc
           if self.is_valid_move(next_row, next_col):
                possible_moves.append((next_row, next_col))
        return possible_moves
    
    def make_move(self, row, col):
        if self.game_over:
            return
        if self.current_number == 1:
            self.start_time = time.time()
            self.board[row][col] = self.current_number
            self.current_position = (row, col)
            self.buttons[row][col].config(
                text=str(self.current_number), 
                fg=self.themes[self.current_theme]["button_fg"], 
                bg=self.get_color(self.current_number)
            )
            self.moves.append((row, col))
            self.current_number += 1
            self.label_info.config(text=f"Current Number: {self.current_number}")
            self.move_counter.config(text=f"Moves: {len(self.moves)}")
            self.highlight_valid_moves()
            self.update_timer()
            return

        if not self.is_valid_move(row, col):
            self.window.after(0, lambda: messagebox.showerror("Invalid Move", "Invalid move! Try again."))
            return
        
        possible_moves = self.get_possible_moves()
        if (row, col) not in possible_moves:
            self.window.after(0, lambda: messagebox.showerror("Invalid Move", "Invalid move! Try again."))
            return

        self.board[row][col] = self.current_number
        self.current_position = (row, col)
        self.buttons[row][col].config(
            text=str(self.current_number), 
            fg=self.themes[self.current_theme]["button_fg"], 
            bg=self.get_color(self.current_number)
        )
        self.moves.append((row, col))
        self.current_number += 1
        self.label_info.config(text=f"Current Number: {self.current_number}")
        self.move_counter.config(text=f"Moves: {len(self.moves)}")
        self.highlight_valid_moves()
        self.update_timer()

        if not self.get_possible_moves():
            self.end_game()

    def start_new_game(self):
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.current_number = 1
        self.game_over = False
        self.current_position = None
        self.moves = []
        self.start_time = 0
        self.elapsed_time = 0

        for row in range(self.size):
            for col in range(self.size):
                self.buttons[row][col].config(text=" ", bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"])
        self.btn_undo.config(state=tk.DISABLED)

        self.label_info.config(text="Click to start placing '1'")
        self.label_time.config(text="Time: 0 s")


    def update_timer(self):
        if not self.game_over and self.start_time != 0:
            self.elapsed_time = int(time.time() - self.start_time)
            self.label_time.config(text=f"Time: {self.elapsed_time} s")
            self.window.after(100, self.update_timer)

    def get_color(self, number):
        """Generate color gradient from cold blue to hot red"""
        max_value = self.size * self.size
        progress = (number - 1) / (max_value - 1) if max_value > 1 else 0
        
        # Color transition: blue (240°) to red (0°)
        hue = 240 - (progress * 240)
        saturation = 0.7 + (progress * 0.3)  # 70-100%
        value = 0.8 + (progress * 0.2)       # 80-100%
        
        # Convert HSV to RGB
        h = hue / 360
        i = math.floor(h * 6)
        f = h * 6 - i
        p = value * (1 - saturation)
        q = value * (1 - f * saturation)
        t = value * (1 - (1 - f) * saturation)

        i = i % 6
        if i == 0: r, g, b = value, t, p
        elif i == 1: r, g, b = q, value, p
        elif i == 2: r, g, b = p, value, t
        elif i == 3: r, g, b = p, q, value
        elif i == 4: r, g, b = t, p, value
        else: r, g, b = value, p, q

        # Convert to hex color
        return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'

    def end_game(self):
        self.game_over = True
        self.elapsed_time = int(time.time() - self.start_time)
        score = self.current_number - 1
        self.label_time.config(text=f"Time: {self.elapsed_time} s")
        self.window.after(0, lambda: self.check_high_score(score, self.elapsed_time))

    def check_high_score(self, score, elapsed_time):
        board_key = f"{self.size}x{self.size}"
        if not self.top_scores[board_key] or len(self.top_scores[board_key]) < 10 or score > self.top_scores[board_key][-1][1]:
            initials = simpledialog.askstring("High Score", "Enter your initials (3 chars):").upper()
            if initials and len(initials) == 3:
              self.top_scores[board_key].append((initials, score, elapsed_time))
              self.top_scores[board_key].sort(key=lambda item: item[1], reverse=True)
              self.top_scores[board_key] = self.top_scores[board_key][:10]
              self.save_scores()
              self.update_score_list()
              self.window.after(0, lambda: messagebox.showinfo("Game Over", f"New High Score!\n\nFinal Score: {score} (Time: {elapsed_time}s)"))
            elif initials:
                 self.window.after(0, lambda: messagebox.showerror("Initials Error","Please enter 3 initials."))
                 self.check_high_score(score, elapsed_time)

            else:
                 self.window.after(0, lambda: messagebox.showinfo("Game Over", f"Game Over!\n\nFinal Score: {score} (Time: {elapsed_time}s)\n"))
        else:
             self.window.after(0, lambda: messagebox.showinfo("Game Over", f"Game Over!\n\nFinal Score: {score} (Time: {elapsed_time}s)\n"))
    
    def update_score_list(self):
        self.score_listbox_10x10.delete(0, tk.END)
        self.score_listbox_5x5.delete(0, tk.END)
        
        if "10x10" in self.top_scores:
            for idx, (initials, score, time) in enumerate(self.top_scores["10x10"]):
                self.score_listbox_10x10.insert(tk.END, f"{idx+1}: {initials} - Score: {score} (Time: {time}s)")
        
        if "5x5" in self.top_scores:
            for idx, (initials, score, time) in enumerate(self.top_scores["5x5"]):
                self.score_listbox_5x5.insert(tk.END, f"{idx+1}: {initials} - Score: {score} (Time: {time}s)")

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        self.window.config(bg=theme["bg"])
        self.main_frame.config(bg=theme["bg"])
        self.board_frame.config(bg=theme["bg"])
        self.score_frame.config(bg=theme["bg"])
        self.score_lists_frame.config(bg=theme["bg"])
        self.label_info.config(bg=theme["bg"], fg=theme["fg"])
        self.label_time.config(bg=theme["bg"], fg=theme["fg"])
        self.btn_new_game.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["button_active_bg"])
        self.btn_theme.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["button_active_bg"])
        self.score_listbox_10x10.config(bg=theme["bg"], fg=theme["fg"])
        self.score_listbox_5x5.config(bg=theme["bg"], fg=theme["fg"])
        for row in self.buttons:
            for button in row:
                button.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["button_active_bg"])
                if button["text"] != " ":
                    button.config(fg=theme["button_fg"])

    def switch_theme(self):
        if self.current_theme == "white":
            self.current_theme = "dark"
            self.btn_theme.config(text="White Theme")
        else:
            self.current_theme = "white"
            self.btn_theme.config(text="Dark Theme")
        self.apply_theme()

    def run(self):
        self.window.mainloop()

    def highlight_valid_moves(self):
        valid_moves = self.get_possible_moves()
        for row in range(self.size):
            for col in range(self.size):
                if (row, col) in valid_moves:
                    self.buttons[row][col].config(bg="#90EE90")
                else:
                    self.buttons[row][col].config(bg=self.themes[self.current_theme]["button_bg"])
        self.btn_undo.config(state=tk.NORMAL if len(self.moves) > 1 else tk.DISABLED)

    def undo_move(self):
        if len(self.moves) > 1:
            # Remove last move
            last_row, last_col = self.moves.pop()
            self.board[last_row][last_col] = 0
            self.buttons[last_row][last_col].config(text=" ", 
                bg=self.themes[self.current_theme]["button_bg"])
            self.current_number -= 1
            
            # Update current position
            self.current_position = self.moves[-1] if self.moves else None
            
            # Update displays
            self.label_info.config(text=f"Current Number: {self.current_number}")
            self.move_counter.config(text=f"Moves: {len(self.moves)}")
            self.highlight_valid_moves()

if __name__ == "__main__":
    game = NumberPuzzleGUI()
    game.run()
