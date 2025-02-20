import os
import sys

# Try to find Python's TCL/TK libraries
python_path = os.path.dirname(sys.executable)
tcl_path = os.path.join(python_path, "tcl", "tcl8.6")
tk_path = os.path.join(python_path, "tcl", "tk8.6")
if os.path.exists(tcl_path) and os.path.exists(tk_path):
    os.environ["TCL_LIBRARY"] = tcl_path
    os.environ["TK_LIBRARY"] = tk_path
else:
    # Fallback: update these absolute paths to where Tcl/Tk is installed on your system
    os.environ["TCL_LIBRARY"] = r"C:\Users\Dell\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"
    os.environ["TK_LIBRARY"] = r"C:\Users\Dell\AppData\Local\Programs\Python\Python313\tcl\tk8.6"

import tkinter as tk
from tkinter import messagebox
import time
import json
import math
import tkinter.font as tkFont
from tkinter import simpledialog  # Correct import for simpledialog
from collections import defaultdict
import statistics
import pygame  # Added for simple music playback

class MoveAnalyzer:
    def __init__(self):
        self.move_history = defaultdict(list)
        self.board_size = None
        self.log_file = "autoplay_logs.json"
        self.load_history()

    def load_history(self):
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Initialize empty logs file
            empty_logs = []
            with open(self.log_file, 'w') as f:
                json.dump(empty_logs, f)
            return empty_logs

    def analyze_position(self, position, turn):
        if position not in self.move_history:
            return None
        
        relevant_moves = [m for m in self.move_history[position] if abs(m["turn"] - turn) <= 5]
        if not relevant_moves:
            return None

        avg_score = statistics.mean(m["score"] for m in relevant_moves if "score" in m)
        avg_future_moves = statistics.mean(m["future_moves"] for m in relevant_moves if "future_moves" in m)
        success_rate = len([m for m in relevant_moves if m.get("score", 0) > 0]) / len(relevant_moves)

        return {
            "position": position,
            "avg_score": avg_score,
            "avg_future_moves": avg_future_moves,
            "success_rate": success_rate,
            "sample_size": len(relevant_moves)
        }

class NumberPuzzleGUI:
    def __init__(self):
        self.size = 10  # Default size
        self.board_sizes = {"Small (5x5)": 5, "Standard (10x10)": 10}  # Added board sizes
        
        # Define themes
        self.themes = {
            "white": {
                "bg": "#FFFFFF",
                "fg": "#000000",
                "button_bg": "#F0F0F0",
                "button_fg": "#000000",
                "button_active_bg": "#E0E0E0"
            },
            "dark": {
                "bg": "#2D2D2D",
                "fg": "#FFFFFF",
                "button_bg": "#404040",
                "button_fg": "#FFFFFF",
                "button_active_bg": "#505050"
            }
        }
        self.current_theme = "white"
        
        self.window = tk.Tk()
        self.window.title("Number Puzzle 10x10")
        # Bind keyboard events:
        self.bind_keys()
        
        # Initialize and play background music
        try:
            pygame.mixer.init()
            music_file = os.path.join(os.path.dirname(__file__), "background.mp3")
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play(-1)  # Loop indefinitely
        except Exception as e:
            print("Error playing music:", e)
        
        # Make window resizable
        self.window.resizable(True, True)
        
        # Set minimum window size
        self.window.minsize(400, 450)
        
        # Define font for numbers
        self.number_font = tkFont.Font(size=10, weight="bold")

        # Configure grid weights for main window
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Main Frame
        self.main_frame = tk.Frame(self.window)
        self.main_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
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

        
        # Main Frame
        self.main_frame = tk.Frame(self.window)
        self.main_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        # Configure grid weights for main frame
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.number_font = tkFont.Font(family="Helvetica", size=12, weight="bold")

        self.current_theme = "white"
        self.themes = {
            "white": {
                "bg": "white",
                "fg": "black",
                "button_bg": "#f0f0f0",
                "button_fg": "black",
                "button_active_bg": "#e0e0e0"
            },
            "dark": {
                "bg": "#2e2e2e",
                "fg": "#f0f0f0",
                "button_bg": "#424242",
                "button_fg": "#f0f0f0",
                "button_active_bg": "#5c5c5c"
            }
        }
        
        self.board_sizes = {
            "Small (5x5)": 5,
            "Standard (10x10)": 10
        }
        
        # Option Menu for Board Size
        self.size_var = tk.StringVar(value="Standard (10x10)")
        size_options = list(self.board_sizes.keys())
        self.size_menu = tk.OptionMenu(self.main_frame, self.size_var, *size_options, command=self.set_board_size)
        self.size_menu.grid(row=1, column=0, pady=10, sticky='ew')

        # Info Label
        self.label_info = tk.Label(self.main_frame, text="Choose board size to start")
        self.label_info.grid(row=2, column=0, pady=10, sticky='ew')

        # Time Label
        self.label_time = tk.Label(self.main_frame, text="Time: 0 s")
        self.label_time.grid(row=3, column=0, pady=5, sticky='ew')

        # Move Counter
        self.move_counter = tk.Label(self.main_frame, text="Moves: 0")
        self.move_counter.grid(row=4, column=0, pady=5, sticky='ew')

        # New Game Button
        self.btn_new_game = tk.Button(self.main_frame, text="New Game", command=self.start_new_game)
        self.btn_new_game.grid(row=5, column=0, pady=5, sticky='ew')

        # Theme Switch Button
        self.btn_theme = tk.Button(self.main_frame, text="Dark Theme", command=self.switch_theme)
        self.btn_theme.grid(row=6, column=0, pady=10, sticky='ew')

        # Board Frame: use pack instead of grid
        self.board_frame = tk.Frame(self.main_frame)
        self.board_frame.grid(row=7, column=0, sticky='nsew')
        
        # Configure grid weights for board frame
        for i in range(self.size):
            self.board_frame.grid_columnconfigure(i, weight=1)
            self.board_frame.grid_rowconfigure(i, weight=1)

        # Undo Button
        self.btn_undo = tk.Button(self.main_frame, text="Undo", command=self.undo_move, state=tk.DISABLED)
        self.btn_undo.grid(row=8, column=0, pady=5, sticky='ew')

        # Auto Play Button
        self.auto_playing = False
        self.btn_auto = tk.Button(self.main_frame, text="Auto Play", command=self.toggle_auto_play)
        self.btn_auto.grid(row=9, column=0, pady=5, sticky='ew')

        # Instead of pack(), use grid for score sidebar:
        self.score_frame = tk.Frame(self.window, width=250)
        self.score_frame.grid(row=0, column=1, sticky='ns')

        # Score Lists Frame
        self.score_lists_frame = tk.Frame(self.score_frame)
        self.score_lists_frame.grid(row=0, column=0, sticky='nsew')

        # Top 10 10x10 Label
        tk.Label(self.score_lists_frame, text="Top 10 10x10 Scores", font="Helvetica 12 bold").grid(row=0, column=0, pady=5)

        # Listbox for 10x10 scores
        self.score_listbox_10x10 = tk.Listbox(self.score_lists_frame, width=40, height=10)
        self.score_listbox_10x10.grid(row=1, column=0, padx=15, pady=10, sticky='nsew')

        # Top 10 5x5 Label
        tk.Label(self.score_lists_frame, text="Top 10 5x5 Scores", font="Helvetica 12 bold").grid(row=2, column=0, pady=10)

        # Listbox for 5x5 scores
        self.score_listbox_5x5 = tk.Listbox(self.score_lists_frame, width=40, height=10)
        self.score_listbox_5x5.grid(row=3, column=0, padx=15, pady=10, sticky='nsew')
        
        self.update_score_list()
        self.create_board() # Generate initial board (10x10 by default)
        self.apply_theme()

        self.move_analyzer = MoveAnalyzer()
        self.game_history = []
        
        # Add Strategy Display
        self.strategy_label = tk.Label(self.main_frame, text="Strategy Tips:", wraplength=200, justify=tk.LEFT)
        self.strategy_label.pack(pady=5)

    def bind_keys(self):
        self.window.bind("<KeyPress>", self.handle_keypress)

    def handle_keypress(self, event):
        # Map arrow keys to moves
        if event.keysym == "Up":
            self.move_by_key(-3, 0)
        elif event.keysym == "Down":
            self.move_by_key(3, 0)
        elif event.keysym == "Left":
            self.move_by_key(0, -3)
        elif event.keysym == "Right":
            self.move_by_key(0, 3)
        # Map Q, W, A, S for diagonal moves
        elif event.char == "q":
            self.move_by_key(-2, -2)
        elif event.char == "w":
            self.move_by_key(-2, 2)
        elif event.char == "a":
            self.move_by_key(2, -2)
        elif event.char == "s":
            self.move_by_key(2, 2)

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
              button.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
              button_row.append(button)
           self.buttons.append(button_row)
        self.apply_theme()
        self.label_info.config(text="Game will start with '1' in top-left corner")
    
    def load_scores(self):
        try:
            with open(self.scores_file, "r") as f:
                scores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            scores = {}
        
        # Ensure both board size categories exist
        if "10x10" not in scores:
            scores["10x10"] = []
        if "5x5" not in scores:
            scores["5x5"] = []
        
        # Save initialized structure
        with open(self.scores_file, "w") as f:
            json.dump(scores, f)
            
        return scores

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
    
    def move_by_key(self, dr, dc):
        if self.game_over or self.current_position is None:
            return
        row, col = self.current_position
        next_row = row + dr
        next_col = col + dc
        if self.is_valid_move(next_row, next_col):
            self.make_move(next_row, next_col)

    def make_move(self, row, col):
        if self.game_over:
            return

        # Log the state before the move
        current_state = {
            "turn": self.current_number,
            "board": [row[:] for row in self.board],
            "position": (row, col),
            "timestamp": time.time()
        }

        # Execute the move with existing logic
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
            self.game_history.append(current_state)
            self.analyze_and_update_strategy()
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
        self.game_history.append(current_state)
        self.analyze_and_update_strategy()

        if not self.get_possible_moves():
            self.end_game()

    def start_new_game(self):
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.current_number = 1
        self.game_over = False
        self.moves = []
        self.start_time = 0
        self.elapsed_time = 0
        self.auto_playing = False
        self.btn_auto.config(text="Auto Play")

        # Reset all buttons
        for row in range(self.size):
            for col in range(self.size):
                self.buttons[row][col].config(text=" ", bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"])
        
        self.btn_undo.config(state=tk.DISABLED)
        self.label_time.config(text="Time: 0 s")

        # Automatically place 1 in the top-left corner (0,0)
        self.make_move(0, 0)

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
        self.auto_playing = False
        self.elapsed_time = int(time.time() - self.start_time)
        score = self.current_number - 1
        
        # Save game history - updated logging to write a valid JSON list
        game_summary = {
            "size": self.size,
            "score": score,
            "time": self.elapsed_time,
            "moves": [(state["position"], state["turn"]) for state in self.game_history]
        }
        
        try:
            # Read existing logs
            if os.path.exists("game_history.json"):
                with open("game_history.json", "r") as f:
                    existing_logs = json.load(f)
            else:
                existing_logs = []
            # Append new game summary
            existing_logs.append(game_summary)
            # Write back the updated logs
            with open("game_history.json", "w") as f:
                json.dump(existing_logs, f, indent=2)
        except Exception as e:
            print(f"Error saving game history: {e}")
        
        self.label_time.config(text=f"Time: {self.elapsed_time} s")
        self.window.after(0, lambda: self.check_high_score(score, self.elapsed_time))
        self.btn_auto.config(text="Auto Play")

    def toggle_auto_play(self):
        if self.game_over:
            return
        self.auto_playing = not self.auto_playing
        if self.auto_playing:
            self.btn_auto.config(text="Stop Auto Play")
            self.make_auto_move()
        else:
            self.btn_auto.config(text="Auto Play")

    def make_auto_move(self):
        if not self.auto_playing or self.game_over:
            return

        possible_moves = self.get_possible_moves()
        if not possible_moves:
            self.end_game()
            return

        # Enhanced move analysis using historical data
        move_analyses = []
        for move in possible_moves:
            historical_analysis = self.move_analyzer.analyze_position(move, self.current_number)
            current_analysis = {
                "position": move,
                "future_moves": self.count_future_moves(move),
                "board_coverage": self.calculate_board_coverage(move),
                "corner_proximity": self.is_corner_move(*move)
            }
            
            # Combine historical and current analysis
            score = (
                (historical_analysis["success_rate"] * 20 if historical_analysis else 0) +
                current_analysis["future_moves"] * 10 +
                (10 - current_analysis["corner_proximity"]) * 2 +
                current_analysis["board_coverage"] * 5
            )
            
            move_analyses.append({**current_analysis, "score": score})

        # Choose best move
        best_move = max(move_analyses, key=lambda x: x["score"])
        self.make_move(*best_move["position"])
        
        if self.auto_playing:
            self.window.after(500, self.make_auto_move)

    def calculate_board_coverage(self, move):
        """Calculate how well a move contributes to board coverage"""
        row, col = move
        coverage = 0
        for r in range(max(0, row-2), min(self.size, row+3)):
            for c in range(max(0, col-2), min(self.size, row+3)):
                if self.board[r][c] == 0:
                    coverage += 1
        return coverage / (self.size * self.size)

    def is_corner_move(self, row, col):
        """Determine if a move is near a corner"""
        corner_distance = min(
            abs(row) + abs(col),
            abs(row) + abs(col - self.size + 1),
            abs(row - self.size + 1) + abs(col),
            abs(row - self.size + 1) + abs(col - self.size + 1)
        )
        return 1 if corner_distance <= 2 else 0

    def calculate_quadrant_progress(self, quadrant):
        """Calculate progress in completing current quadrant"""
        row_start = quadrant[0] * (self.size//2)
        col_start = quadrant[1] * (self.size//2)
        filled = 0
        total = (self.size//2) ** 2
        
        for r in range(row_start, row_start + self.size//2):
            for c in range(col_start, col_start + self.size//2):
                if self.board[r][c] != 0:
                    filled += 1
        return filled / total

    def calculate_buffer_score(self, row, col):
        """Calculate buffer zone status score"""
        # Buffer zones are every 10th row
        buffer_rows = [i for i in range(0, self.size, 10)]
        if row in buffer_rows:
            # Prefer moves that don't block buffer rows
            return -1 if self.current_number < 90 else 1
        return 0

    def calculate_transition_score(self, row, col):
        """Calculate transition lane availability score"""
        # Transition lanes are vertical columns spaced every 5 columns
        transition_cols = [i for i in range(0, self.size, 5)]
        if col in transition_cols:
            # Prefer moves that preserve transition lanes
            return 1 if self.current_number < 80 else -1
        return 0

    def log_move_analysis(self, analysis_data):
        """Log move analysis data to JSON file"""
        log_file = "autoplay_logs.json"
        try:
            # Convert board state to serializable format
            analysis_data["board_state"] = [
                [int(cell) for cell in row] 
                for row in analysis_data["board_state"]
            ]
            
            # Load existing logs
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                logs = []
                
            # Add new analysis
            logs.append(analysis_data)
            
            # Save updated logs
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"Error logging move analysis: {e}")

    def count_future_moves(self, position):
        """Count how many moves would be available after making this move"""
        row, col = position
        temp_board = [row[:] for row in self.board]
        temp_board[row][col] = self.current_number
        
        # Calculate possible moves from this new position
        future_moves = []
        # Straight moves
        moves_straight = [(0, -3), (0, 3), (-3, 0), (3, 0)]
        for dr, dc in moves_straight:
            next_row, next_col = row + dr, col + dc
            if self.is_valid_position(next_row, next_col) and temp_board[next_row][next_col] == 0:
                future_moves.append((next_row, next_col))
        # Diagonal moves
        moves_diagonal = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        for dr, dc in moves_diagonal:
            next_row, next_col = row + dr, dc + col
            if self.is_valid_position(next_row, next_col) and temp_board[next_row][next_col] == 0:
                future_moves.append((next_row, next_col))
        
        return len(future_moves)

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
           future_moves_count = self.count_future_moves((row, col))
           if not hasattr(self, 'min_future_moves_valid_moves'):
            self.min_future_moves_valid_moves = {}
           self.min_future_moves_valid_moves[(row, col)] = future_moves_count

        if valid_moves:
         min_future_moves = min(self.min_future_moves_valid_moves.values())
         for row in range(self.size):
          for col in range(self.size):
           if (row, col) in valid_moves and self.min_future_moves_valid_moves[(row, col)] == min_future_moves:
            self.buttons[row][col].config(bg="#FFA500") # Highlight color for fewest options
           elif (row, col) in valid_moves:
            self.buttons[row][col].config(bg="#90EE90") # Original valid move color
           else:
            self.buttons[row][col].config(bg=self.themes[self.current_theme]["button_bg"])
        self.btn_undo.config(state=tk.NORMAL if len(self.moves) > 1 else tk.DISABLED)

    def highlight_analyzed_moves(self, analyzed_moves, best_move):
        if not analyzed_moves:
            return self.highlight_valid_moves()
        valid_moves = self.get_possible_moves()
        for row in range(self.size):
            for col in range(self.size):
                if (row, col) not in valid_moves:
                    self.buttons[row][col].config(bg=self.themes[self.current_theme]["button_bg"])
                    continue
                move_analysis = next((m for m in analyzed_moves if m["position"] == (row, col)), None)
                if move_analysis:
                    if move_analysis["position"] == best_move["position"]:
                        self.buttons[row][col].config(bg="#0000FF")  # Bright blue for best move
                    elif move_analysis["success_rate"] > 0.6:
                        self.buttons[row][col].config(bg="#90EE90")  # Light green for good moves
                    else:
                        self.buttons[row][col].config(bg="#FFA500")  # Orange for other moves
                else:
                    self.buttons[row][col].config(bg="#FFA500")

    def analyze_and_update_strategy(self):
        if len(self.game_history) < 2:
            return

        possible_moves = self.get_possible_moves()
        move_analyses = []
        for move in possible_moves:
            analysis = self.move_analyzer.analyze_position(move, self.current_number)
            if analysis:
                move_analyses.append(analysis)
        if move_analyses:
            # Compute best move using weighted criteria:
            best_move = max(move_analyses, key=lambda m: m["success_rate"] * 100 + m["avg_future_moves"])
            # For strategy tips, sort by success rate and average future moves
            move_analyses.sort(key=lambda x: (x["success_rate"], x["avg_future_moves"]), reverse=True)
            best_moves = move_analyses[:3]
            tips = ["Strategy Tips:"]
            for i, move in enumerate(best_moves, 1):
                row, col = move["position"]
                tips.append(f"{i}. Consider ({row},{col}): {move['success_rate']:.2%} success rate")
                tips.append(f"   Avg future moves: {move['avg_future_moves']:.1f}")
            self.strategy_label.config(text="\n".join(tips))
            self.highlight_analyzed_moves(move_analyses, best_move)

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
