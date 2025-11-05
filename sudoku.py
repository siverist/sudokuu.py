import tkinter as tk
from tkinter import ttk, messagebox
from functools import partial
import random
import copy
import time
import re
import pygame
import sys
import os

# SUDOKU GENERATOR
class SudokuGenerator:
    def __init__(self):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]

    def is_valid(self, grid, row, col, num):
        """Check if num can be placed at grid[row][col]."""
        for i in range(9):
            if grid[row][i] == num or grid[i][col] == num:
                return False
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if grid[start_row + i][start_col + j] == num:
                    return False
        return True

    def fill_grid(self, grid):
        """Recursively fills the grid with a valid Sudoku solution."""
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for num in nums:
                        if self.is_valid(grid, row, col, num):
                            grid[row][col] = num
                            if self.fill_grid(grid):
                                return True
                            grid[row][col] = 0
                    return False
        return True

    def solve_count(self, grid):
        """Counts the number of solutions for a grid."""
        solutions = [0]

        def backtrack():
            for r in range(9):
                for c in range(9):
                    if grid[r][c] == 0:
                        for n in range(1, 10):
                            if self.is_valid(grid, r, c, n):
                                grid[r][c] = n
                                backtrack()
                                grid[r][c] = 0
                        return
            solutions[0] += 1
        backtrack()
        return solutions[0]

    def remove_numbers(self, grid, holes):
        """Remove numbers while keeping a unique solution."""
        grid = copy.deepcopy(grid)
        attempts = holes
        while attempts > 0:
            row, col = random.randint(0, 8), random.randint(0, 8)
            while grid[row][col] == 0:
                row, col = random.randint(0, 8), random.randint(0, 8)
            backup = grid[row][col]
            grid[row][col] = 0
            if self.solve_count(grid) != 1:
                grid[row][col] = backup
            attempts -= 1
        return grid

    def generate(self, holes):
        """Generate a puzzle with a given number of possible holes."""
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.fill_grid(self.grid)
        self.full_solution = copy.deepcopy(self.grid)
        puzzle = self.remove_numbers(self.full_solution, holes)
        return puzzle

# RESOURCE PATH
def resource_path(relative_path):
    """Get absolute path to resource, works for PyInstaller."""
    try:
        base_path = sys._MEIPASS 
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# GUI
class SudokuGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Sudoku")
        self.master.bind_all("<Key>", self.handle_key)
        self.master.bind("<Button-1>", self.global_click)
        self.master.bind("<Button-3>", self.clear_selection)
        self.master.bind("<Key>", self.handle_key_input)
        self.master.config(cursor="hand2")

        # Game state variables
        self.currentNumber = None
        self.running = False
        self.startTime = 0
        self.pauseTime = 0
        self.cells = {}
        self.selectedCells = set()
        self.inputMode = "cell_first"
        self.pencilMode = False
        self.clearMode = False
        self.color = "#73AFCF"
        self.color1 = "#ADD1E4"
        self.color3 = "#95C2DB"
        self.color4 = "#D1E8F5"
        self.color2 = "#042130"
        self.gameStarted = False
        self.generator = SudokuGenerator()
        self.difficulty = 0
        self.music = False
        self.volume = 0.5
        self.lang = "en"
        self.number_buttons = []


        # Music
        pygame.mixer.init()
        music_file = resource_path("music.mp3")
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(self.volume)  # výchozí hlasitost 50 %
        pygame.mixer.music.play(-1)
        pygame.mixer.music.pause()
        
        # Ttk styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("numbers.TButton", padding=(0,32), width=6, relief="flat", background=self.color1, foreground= self.color2,font=("SF Pro Display", 22))
        self.style.configure("game.TButton", padding=6, relief="flat", background=self.color1, foreground= self.color2,font=("SF Pro Display", 18))
        self.style.configure("menu.TButton", padding=6, relief="flat", background=self.color1, foreground= self.color2,font=("SF Pro Display", 20))
        
        layout  =[
            ("Button.border", {"sticky": "nswe", "children": [
                ("Button.padding", {"sticky": "nswe", "children": [
                    ("Button.label", {"sticky": "nswe"})
                ]})
            ]})
        ]
        self.style.layout("menu.TButton", layout)
        self.style.layout("game.TButton", layout)
        self.style.layout("numbers.TButton", layout)

        self.style.map("menu.TButton", background=[('pressed',self.color3),('active', self.color4)])
        self.style.map("game.TButton", background=[("selected",self.color3), ('pressed',self.color3),('active', self.color4)])
        self.style.map("numbers.TButton", background=[("selected",self.color3), ('pressed',self.color3),('active', self.color4)])
       
        # Frames
        self.menu_frame = tk.Frame(self.master)
        self.game_frame = tk.Frame(self.master)

        self.translations = {
            "en": {
                # --- Menu ---
                "button1": "Play Basic",
                "button2": "Play with Extra Rules",
                "button3": "Rules",
                "button4": "Settings",
                "button5": "Quit",

                # --- Difficulty & Game Start ---
                "popup_start_title": "Start Game",
                "popup_start_text": "Do you want to continue or start a new game?",
                "continue_game": "Continue previous game",
                "new_game": "Start a new game",
                "difficulty_title": "Choose Difficulty",
                "difficulty_text": "Which difficulty do you want?",
                "easy": "Easy",
                "medium": "Medium",
                "hard": "Hard",
                # --- In-game Buttons ---
                "button6": "See Solved/Done",
                "button7": "Check Numbers",
                "button8": "Start Over",
                "button9": "Rules / Pause",
                "button10": "Switch Input Mode",
                "button11": "Back to Menu",
                # --- Popups & Prompts ---
                "no_cell_selected": "Select a cell first!",
                "no_number_selected": "Select a number first!",
                "paused": "Timer is paused. Resume to play.",
                "check_ok": "Every number is right so far!",
                "check_fail": "Oh no! You made a mistake somewhere",
                "see_solution_title": "See Solution",
                "see_solution_text": "Do you want to give up?",
                "start_over_text": "Do you want to start this puzzle over or get a new one?",
                "erase_numbers": "Erase My Numbers",
                "new_puzzle": "New Game",
                # --- Settings ---
                "settings_title": "Settings",
                "music_on": "Turn Music On",
                "music_off": "Turn Music Off",
                "close": "Close",
                "lang": "Czech",
                # --- Rules ---
                "rules_title": "Rules",
                "rules_text": (
                    "🧩 Sudoku Rules:\n\n"
                    "1. Each row, column, and 3x3 box must contain digits 1–9.\n"
                    "2. No number repeats in any row, column, or box.\n\n"
                    "Extra Rules Mode:\n"
                    "Controls:\n"
                    "• Switch Input Mode (press M) to change how you play.\n"
                    "• Number-first: Select number, then click cells.\n"
                    "• Cell-first: Select cell(s), then choose a number or type it.\n"
                    "• You can select multiple cells at once in Cell-first mode.\n"
                    "• Press R to see the rules or pause the timer.\n"
                    "• Use ESC to exit fullscreen.\n"
                ),
                # --- Misc ---
                "pencil_mode": "Pencil Mode",
                "clear_cell": "Clear Cell",
            },
            "cz": {
                # --- Menu ---
                "button1": "Základní Sudoku",
                "button2": "Sudoku s Extra Pravidly",
                "button3": "Pravidla",
                "button4": "Nastavení",
                "button5": "Odejít",
                # --- Difficulty & Game Start ---
                "popup_start_title": "Spustit hru",
                "popup_start_text": "Chceš pokračovat nebo začít novou hru?",
                "continue_game": "Pokračovat v předchozí hře",
                "new_game": "Začít novou hru",
                "difficulty_title": "Zvol obtížnost",
                "difficulty_text": "Jakou obtížnost chceš?",
                "easy": "Lehká",
                "medium": "Střední",
                "hard": "Těžká",
                # --- In-game Buttons ---
                "button6": "Zobrazit řešení",
                "button7": "Zkontrolovat čísla",
                "button8": "Začít znovu",
                "button9": "Pravidla / Pauza",
                "button10": "Změnit režim zadávání",
                "button11": "Zpět do menu",
                # --- Popups & Prompts ---
                "no_cell_selected": "Nejprve vyber buňku!",
                "no_number_selected": "Nejprve vyber číslo!",
                "paused": "Časovač je pozastaven. Pokračuj ve hře.",
                "check_ok": "Všechna čísla jsou zatím správně!",
                "check_fail": "Někde máš chybu!",
                "see_solution_title": "Zobrazit řešení",
                "see_solution_text": "Chceš to vzdát?",
                "start_over_text": "Chceš začít toto sudoku znovu, nebo nové?",
                "erase_numbers": "Vymazat moje čísla",
                "new_puzzle": "Nová hra",
                # --- Settings ---
                "settings_title": "Nastavení",
                "music_on": "Zapnout hudbu",
                "music_off": "Vypnout hudbu",
                "close": "Zavřít",
                "lang": "Angličtina",
                # --- Rules ---
                "rules_title": "Pravidla",
                "rules_text": (
                    "🧩 Pravidla Sudoku:\n\n"
                    "1. Každý řádek, sloupec a 3x3 čtverec musí obsahovat čísla 1–9.\n"
                    "2. Žádné číslo se nesmí opakovat.\n\n"
                    "Extra pravidla:\n"
                    "Ovládání:\n"
                    "• Přepínej režim zadávání klávesou M.\n"
                    "• Režim číslo-první: Vyber číslo a klikni na buňky.\n"
                    "• Režim buňka-první: Vyber buňky a pak číslo.\n"
                    "• Můžeš vybrat více buněk najednou.\n"
                    "• Klávesou R otevřeš pravidla nebo pauzneš čas.\n"
                    "• Klávesou ESC ukončíš režim celé obrazovky.\n"
                ),
                # --- Misc ---
                "pencil_mode": "Poznámky",
                "clear_cell": "Vymazat buňku",
            },
        }
        self.create_main_menu()

    # Key binding
    def handle_key(self, event):
        key = event.char.lower()
        if key == "r":
            self.show_rules_popup()
        elif key == "p":
            self.toggle_Mode(True)
        elif key == "m":
            self.toggle_inputMode()
        elif key =="b":
            self.back_to_menu()

    # Language
    def t(self, key):
        return self.translations[self.lang].get(key, key)
    
    def toggle_lang(self):
        if self.lang == "cz":
            self.lang = "en"
        else :
            self.lang = "cz"
        for widget in self.menu_frame.winfo_children():
            widget.destroy()
        self.reopen_settings()
        self.create_main_menu()
    
# MENU
    def create_main_menu(self):
        self.menu_frame.config(bg=self.color)
        self.menu_frame.pack(expand=True, fill="both")

        title = tk.Label(
            self.menu_frame,
            text="🧩Sudoku",
            foreground= "#022132",
            background=self.color,
            font=("SF Pro Display", 38, "bold"),
            pady=30,
        )
        title.pack()

        ttk.Button(
            self.menu_frame,
            text=self.t("button1"),
            width=20,
            command=lambda: self.start_game("basic"),
            style="menu.TButton",
        ).pack(pady=10)

        ttk.Button(
            self.menu_frame,
            text=self.t("button2"),
            width=20,
            command=lambda: self.start_game("extra"),
            style="menu.TButton",
        ).pack(pady=10)

        ttk.Button(
            self.menu_frame,
            text=self.t("button3"),
            width=20,
            command=self.show_rules_popup,
            style="menu.TButton",
        ).pack(pady=10)

        ttk.Button(
            self.menu_frame,
            text=self.t("button4"),
            width=20,
            command=self.settings_popup,
            style="menu.TButton",
        ).pack(pady=10)

        ttk.Button(
            self.menu_frame,
            text=self.t("button5"),
            width=20,
            command=self.master.destroy,
            style="menu.TButton",
        ).pack(pady=20)

# GAME START
    def start_game(self, mode):
        if self.gameStarted == True:
            text = self.t("popup_start_text")
            buttons = {
                self.t("continue_game"): lambda:self.continue_game(),
                self.t("new_game") : lambda:self.choose_difficulty()
            }
            self.popup(self.t("popup_start_title"), text, buttons)
        else:
            self.choose_difficulty()

    def continue_game(self):
        self.menu_frame.pack_forget()
        self.resume_timer()
        self.game_frame.pack(fill="both", expand=True)

    def choose_difficulty(self):
        text = self.t("difficulty_text")
        buttons = {
            self.t("easy"): lambda: self.start_with_difficulty(30),
            self.t("medium"): lambda: self.start_with_difficulty(45),
            self.t("hard"): lambda: self.start_with_difficulty(60)
        }
        self.popup(self.t("difficulty_title"), text, buttons)
        
    def start_with_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.gameStarted = True
        self.setup_game_screen()

# GAME SCREEN
    def setup_game_screen(self):
        # Screen setup 
        self.menu_frame.pack_forget()
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        self.game_frame.pack(fill="both", expand=True)
        self.game_frame.config(bg=self.color)
        
        # Timer
        self.timer_label = tk.Label(
            self.game_frame, font=("SF Pro Display", 15), bg=self.color
        )
        self.timer_label.pack(pady=5)
        self.running = True
        self.startTime = time.time()
        self.update_timer()
        
        # Buttons
        controls0 = tk.Frame(self.game_frame, bg=self.color)
        controls0.pack(pady=10)

        ttk.Button(
            controls0,
            text=self.t("button6"),
            style="game.TButton",
            command=self.see_solution,
        ).grid(row=0, column=0, padx=10)

        ttk.Button(
            controls0,
            text=self.t("button7"),
            style="game.TButton",
            command=self.check_numbers,
        ).grid(row=0, column=1, padx=10)

        ttk.Button(
            controls0,
            text=self.t("button8"),
            style="game.TButton",
            command=self.start_over,
        ).grid(row=0, column=2, padx=10)

        # Sudoku grid and numbers
        main_frame = tk.Frame(self.game_frame, bg=self.color)
        main_frame.pack(expand=True, anchor="n")

        # Sudoku
        sudoku_frame = tk.Frame(main_frame, bg=self.color)
        sudoku_frame.grid(row=0, column=0, sticky="n")
        self.grid_frame = tk.Frame(sudoku_frame, bg=self.color)
        self.grid_frame.pack()
        self.puzzle = self.generator.generate(holes = self.difficulty)
        self.cells = {}
        self.generate_puzzle()

        # Number pad
        pad_frame = tk.Frame(main_frame, bg=self.color,)
        pad_frame.grid(row=0, column=1, sticky="n", padx=10, pady=10)
        self.create_number_pad(pad_frame)

        # Bottom buttons
        controls = tk.Frame(self.game_frame, bg=self.color)
        controls.pack(expand=True, fill="y",)

        ttk.Button(
            controls,
            text=self.t("button9"),
            style="game.TButton",
            command=self.show_rules_popup,
        ).grid(row=0, column=0, padx=10, sticky="n")

        ttk.Button(
            controls,
            text=self.t("button10"),
            style="game.TButton",
            command=self.toggle_inputMode,
        ).grid(row=0, column=1, padx=10, sticky="n")

        ttk.Button(
            controls,
            text=self.t("button11"),
            style="game.TButton",
            command=self.back_to_menu,
        ).grid(row=0, column=2, padx=10, sticky="n")

    # Timer
    def update_timer(self):
        if not self.running:
            return
        elapsed = int(time.time() - self.startTime)
        mins, secs = divmod(elapsed, 60)
        self.timer_label.config(text=f"Time: {mins:02}:{secs:02}")
        self.master.after(1000, self.update_timer)

    def pauseTimer(self):
        if self.running:
            self.running = False
            self.pauseTime = time.time() - self.startTime

    def resume_timer(self):
        if not self.running:
            self.running = True
            self.startTime = time.time() - self.pauseTime
            self.update_timer()

    # Grid generator
    def generate_puzzle(self):
        for row in range(9):
            for col in range(9):
                value = self.puzzle[row][col]
                cell_text = str(value) if value != 0 else ""
                border_color = "black"
                top = 3 if row % 3 == 0 else 1
                left = 3 if col % 3 == 0 else 1
                bottom = 3 if row == 8 else 1
                right = 3 if col == 8 else 1

                frame = tk.Frame(
                    self.grid_frame,
                    highlightbackground=self.color,
                    highlightcolor=border_color,
                    bg=self.color
                )
                frame.grid(row=row, column=col, padx=(left, right), pady=(top, bottom))
                bg_color = "#FFFFFF" if (row // 3 + col // 3) % 2 == 0 else "#DCE6EB"
                cell = tk.Label(
                    frame,
                    text=cell_text,
                    width=2,
                    height=1,
                    font=("SF Pro Display", 25),
                    relief="solid",
                    borderwidth=1,
                    bg=bg_color,
                )
                cell.pack(fill="both", expand=True)
                cell.bind("<Button-1>", lambda e, r=row, c=col: self.cell_clicked(r, c))
                self.cells[(row, col)] = {"label": cell, "fixed": value != 0}

    # Number pad
    def create_number_pad(self, frame):
        btn_frame = tk.Frame(frame, bg=self.color)
        btn_frame.pack()

        for num in range(1, 10):
            btn = ttk.Button(
                btn_frame,
                text=str(num),
                style="numbers.TButton",
            )
            btn.grid(row=(num - 1) // 3, column=(num - 1) % 3, padx=3, pady=3)
            btn.config(command=partial(self.select_number, num, btn))
            self.number_buttons.append(btn)

        action_frame = tk.Frame(frame, bg=self.color)
        action_frame.pack(pady=5)

        self.btn1 = ttk.Button(
            action_frame,
            text=self.t("clear_cell"),
            style="game.TButton",
            command=lambda: self.toggle_Mode(False),
        )
        self.btn1.grid(row=0, column=0, padx=5)

        self.btn2 = ttk.Button(
            action_frame,
            text=self.t("pencil_mode"),
            style="game.TButton",
            command=lambda: self.toggle_Mode(True)
        )
        self.btn2.grid(row=0, column=1, padx=5)

    def toggle_Mode(self, pencil):
        self.btn1.state(["!selected"])
        self.btn2.state(["!selected"])
        if pencil:
            self.pencilMode = not self.pencilMode
            if self.pencilMode:
                self.btn2.state(["selected"])
            self.clearMode = False
        else:
            self.clearMode = not self.clearMode
            if self.clearMode and self.inputMode == "number_first":
                self.btn1.state(["selected"])
            self.pencilMode = False
            self.select_number(0)
        self.toggle_Cursor()

    def toggle_Cursor(self):
        self.master.config(cursor="hand2")
        if self.inputMode == "number_first":
            if self.pencilMode:
                self.master.config(cursor="pencil")
            elif self.clearMode:
                self.master.config(cursor="X_cursor")
                for b in self.number_buttons:
                    b.state(["!selected"])
        else:
            for b in self.number_buttons:
                b.state(["!selected"])

    def select_number(self, num, btn=None):
        if self.inputMode == "number_first":
            self.currentNumber = num
            for b in self.number_buttons:
                b.state(["!selected"])
            if btn:
                btn.state(["selected"])
                self.clearMode=False
                self.btn1.state(["!selected"])
                self.toggle_Cursor()
        elif self.inputMode == "cell_first":
            if not self.selectedCells:
                messagebox.showinfo("No Cell Selected", self.t("no_cell_selected"))
                return

            for (r, c) in self.selectedCells:
                if self.pencilMode and num != 0:
                    self.toggle_pencil_number(r, c, num)
                else:
                    if self.cells[(r, c)]["fixed"]:
                        return
                    self.place_number_in_selected(num)
        self.check_errors()

    # Top buttons
    def see_solution(self):
        text = self.t("see_solution_text")
        buttons = {
                self.t("see_solution_title"): lambda:self.solution(),
        }
        self.popup(self.t("see_solution_title"), text, buttons)
        self.full_solution = self.generator.grid

    def solution(self):
        for row in range(9):
             for col in range(9):
                value =self.full_solution[row][col]
                self.cells[(row, col)]["label"].config(text=str(value), foreground="black")
             
    def start_over(self):
        text = self.t("start_over_text")
        buttons = {
                self.t("erase_numbers"): lambda:self.generate_puzzle(),
                self.t("new_puzzle"): lambda:self.setup_game_screen(),
        }
        self.popup(self.t("see_solution_title"), text, buttons)
        self.full_solution = self.generator.grid

    def check_numbers(self):
        self.full_solution = self.generator.grid
        all_correct = True
        for row in range(9):
            for col in range(9):
                cell = self.cells[(row, col)]["label"]
                cell_text = cell.cget("text").strip()
                # ignore empty cells
                if not cell_text or cell_text == "0":
                    continue   
                font = cell.cget("font")
                if isinstance(font, tuple):
                    font_size = font[1]
                else:
                    font_size = int(re.search(r'\d+', font).group())
                # ignore pencil marks
                if font_size < 10:
                    continue
                try:
                    value = int(cell_text)
                except ValueError:
                    continue
                if value != self.full_solution[row][col]:
                    all_correct = False
                    break
            if not all_correct:
                break
        if all_correct:
            messagebox.showinfo("Check", self.t("check_ok"))
        else:
            messagebox.showinfo("Check", self.t("check_fail"))

    # Pencil
    def toggle_pencil_number(self, row, col, num):
        """Toggle a pencil number in a cell. If num=0, clear all pencil marks."""
        cell = self.cells[(row, col)]["label"]
        if num == 0:
            cell.config(text="", font=("SF Pro Display", 25), width=2, height=1)
            return

        current_text = cell.cget("text")
        font = cell.cget("font")
        if isinstance(font, tuple):
            font_size = font[1]
        else:
            font_size = int(re.search(r'\d+', font).group())
        if font_size > 10 and current_text!="":
            return
        pencil_numbers = set(current_text.replace("\n", " ").split()) if current_text else set()
        num_str = str(num)

        if num_str in pencil_numbers:
            pencil_numbers.remove(num_str)
        else:
            pencil_numbers.add(num_str)

        sorted_numbers = sorted(pencil_numbers)
        lines = [" ".join(sorted_numbers[i:i+3]) for i in range(0, len(sorted_numbers), 3)]
        formatted_text = "\n".join(lines)

        if pencil_numbers:
            cell.config(
                text=formatted_text,
                font=("SF Pro Display", 7),
                width=6, height=3,
                foreground="black"
            )
        else:
            cell.config(
                text="",
                font=("SF Pro Display", 25),
                width=2, height=1,
                foreground="black"
            )
        self.check_errors

    # Cell actions
    def cell_clicked(self, row, col):
        if not self.running:
            messagebox.showinfo("Paused", self.t("paused"))
            return
        cell_data = self.cells[(row, col)]
        if cell_data["fixed"]:
            return

        cell = self.cells[(row, col)]["label"]
        if self.inputMode == "number_first":
            if self.currentNumber is None:
                messagebox.showinfo("No Number Selected", "Select a number first!")
                return

            if self.pencilMode and self.currentNumber != 0:
                self.toggle_pencil_number(row, col, self.currentNumber)
            else:
                cell.config(font=("SF Pro Display", 25), width=2, height=1)
                if self.currentNumber == 0:
                    cell.config(text="")
                else:
                    cell.config(text=str(self.currentNumber))
        else:
            self.toggle_cell_selection(row, col)
        self.check_errors()

    def toggle_cell_selection(self, row, col):
        """Toggle selection highlight for a cell."""
        cell = self.cells[(row, col)]["label"]
        if (row, col) in self.selectedCells:
            self.selectedCells.remove((row, col))
            cell.config(bg= "#FFFFFF" if (row // 3 + col // 3) % 2 == 0 else "#DCE6EB")
        else:
            self.selectedCells.add((row, col))
            cell.config(bg="#BCE7FF")

    def clear_selection(self, event=None):
        """Clear all highlighted cells."""
        for (r, c) in self.selectedCells:
            self.cells[(r, c)]["label"].config(bg = "#FFFFFF" if (r // 3 + c// 3) % 2 == 0 else "#DCE6EB")
        self.selectedCells.clear()

    def global_click(self, event):
        widget = event.widget
        if not isinstance(widget, (tk.Label, tk.Button, tk.Canvas, ttk.Button)):
            self.clear_selection()

    def place_number_in_selected(self, num):
        """Place a number in all selected cells."""
        for (r, c) in self.selectedCells:
            if self.cells[(r, c)]["fixed"]:
                return
            self.cells[(r, c)]["label"].config(font=("SF Pro Display", 25), width=2, height=1)
            self.cells[(r, c)]["label"].config(text="" if num == 0 else str(num))

    def handle_key_input(self, event):
        if not self.running:
            return
        if self.inputMode == "number_first":
            if event.char.isdigit() and event.char != "0":
                num = int(event.char)
                self.select_number(num, btn=self.number_buttons[num-1])
            elif event.keysym in ("BackSpace", "Delete"):
                self.toggle_Mode(False)           
        else:
            if event.char.isdigit() and event.char != "0":
                num = int(event.char)
                if self.pencilMode:
                    for r, c in self.selectedCells:
                        self.toggle_pencil_number(r, c, num)
                else:
                    self.place_number_in_selected(num)
            elif event.keysym in ("BackSpace", "Delete"):
                self.place_number_in_selected(0)
        self.check_errors()

    # Errors
    def check_errors(self):
        """Check all cells for conflicts. Pencil marks are handled separately."""
        for cell_data in self.cells.values():
            cell_data["label"].config(foreground="black")

        rows = {r: {} for r in range(9)}
        cols = {c: {} for c in range(9)}
        boxes = {(r // 3, c // 3): {} for r in range(9) for c in range(9)}

        for (r, c), cell_data in self.cells.items():
            cell = cell_data["label"]
            text = cell.cget("text").strip()
            if not text:
                continue

            f = cell.cget("font")
            if isinstance(f, tuple):
                font_size = f[1]
            else:
                m = re.search(r'\d+', f)
                font_size = int(m.group()) if m else 20

            is_pencil = font_size < 10
            values = text.split()
            for val in values:
                if not is_pencil:
                    rows[r].setdefault(val, []).append((r, c))
                    cols[c].setdefault(val, []).append((r, c))
                    boxes[(r // 3, c // 3)].setdefault(val, []).append((r, c))
                else:
                    rows[r].setdefault('_pencil', []).append((val, (r, c)))
                    cols[c].setdefault('_pencil', []).append((val, (r, c)))
                    boxes[(r // 3, c // 3)].setdefault('_pencil', []).append((val, (r, c)))

        self.mark_conflicts(rows)
        self.mark_conflicts(cols)
        self.mark_conflicts(boxes)

    def mark_conflicts(self, structure):
        for group in structure.values():
            for val, positions in group.items():
                if val == '_pencil':
                    continue
                if len(positions) > 1:
                    for pos in positions:
                        if self.cells[pos]["fixed"]:
                            continue
                        cell = self.cells[pos]["label"]
                        f = cell.cget("font")
                        font_size = f[1] if isinstance(f, tuple) else int(re.search(r'\d+', f).group())
                        if font_size >= 10:
                            cell.config(foreground="red")

            if '_pencil' in group:
                for val, pos in group['_pencil']:
                    cell = self.cells[pos]["label"]
                    if val in group and any(
                        self.cells["label"][p].cget("font")[1] >= 10 if isinstance(self.cells["label"][p].cget("font"), tuple)
                        else int(re.search(r'\d+', self.cells["label"][p].cget("font")).group()) >= 10
                        for p in group[val]
                    ):
                        cell.config(foreground="red")

    # Bottom buttons
        # Leave game
    def back_to_menu(self):
        self.running = False
        self.clear_selection()
        self.game_frame.pack_forget()
        self.menu_frame.pack(expand=True, fill="both")

        # Input modes
    def toggle_inputMode(self):
        """Switches between number-first and cell-first input modes."""
        if self.inputMode == "number_first":
            self.inputMode = "cell_first" 
        else :
            self.inputMode = "number_first"
        self.toggle_Cursor()
        self.clear_selection()

# POPUPS
    def popup(self, title, message, buttons=None, close = True):
        popup = tk.Toplevel(self.master)
        popup.title(title)
        popup.geometry("600x400")
        popup.config(bg=self.color)

        container = tk.Frame(popup, bg=self.color)
        container.pack(fill="both", expand=True)

        # Canvas + Scrollbar
        canvas = tk.Canvas(container, bg=self.color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.color)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Scroll mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Text 
        label = tk.Label(
            scroll_frame,
            text=message,
            bg=self.color,
            foreground="white",
            font=("SF Pro Display", 14),
            wraplength=550,
            justify="left",
        )
        label.pack(padx=20, pady=20, fill="both", expand=True)

        # buttons
        btn_frame = tk.Frame(scroll_frame, bg=self.color)
        btn_frame.pack( side="top")

        if buttons:
            for text, command in buttons.items():
                ttk.Button(
                    btn_frame,
                    text=text,
                    style="game.TButton",
                    command=lambda c=command: [popup.destroy(), c()] if c else popup.destroy()
                ).pack( pady=10)
        
        def close_popup():
            popup.destroy()
            self.resume_timer()

        if close:
            ttk.Button(
                btn_frame,
                text=self.t("close"),
                style="game.TButton",
                command=close_popup
            ).pack(pady=10)

            # --- Center on screen ---
        self.center_popup(popup, 600, 400)

    def center_popup(self, popup, width=600, height=400):
        popup.update_idletasks()  # aktualizuj rozměry
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        popup.geometry(f"{width}x{height}+{x}+{y}")

    # Rules
    def show_rules_popup(self):
        self.popup(self.t("rules_title"), self.t("rules_text"))
        self.pauseTimer()

    # Settings
    def settings_popup(self):

        # --- Music toggle function ---
        def toggle_music():
            if self.music:
                pygame.mixer.music.pause()
                self.music = False
                toggle_btn.config(text=self.t("music_on"))
            else:
                pygame.mixer.music.unpause()
                self.music = True
                toggle_btn.config(text=self.t("music_off"))

        # --- Volume control function ---
        def set_volume(val):
            volume = float(val)
            self.volume = volume/100
            pygame.mixer.music.set_volume(self.volume)

        # --- Create popup using your existing popup() function ---
        self.popup(self.t("settings_title"), self.t("settings_title")+":", close = False)

        # --- Access the last opened popup (your popup creates a new Toplevel) ---
        popup = self.master.winfo_children()[-1]

        # --- Find scroll_frame (3 layers deep inside popup structure) ---
        # container -> canvas -> scroll_frame
        container = popup.winfo_children()[0]
        canvas = container.winfo_children()[0]
        scroll_frame = canvas.winfo_children()[0]

        ttk.Button(
            scroll_frame,
            text=self.t("lang"),
            style="game.TButton",
            command=self.toggle_lang
        ).pack(pady=10)

        # --- On/Off button ---
        toggle_btn = ttk.Button(
            scroll_frame,
            text=self.t("music_off") if self.music else self.t("music_on"),
            style="game.TButton",
            command=toggle_music
        )
        toggle_btn.pack(pady=10)

        # --- Volume slider ---
        volume_slider = tk.Scale(
            scroll_frame,
            from_=0,
            to=100,
            orient="horizontal",
            resolution=0.05,
            length=250,
            bg=self.color,
            foreground="white",
            highlightthickness=0,
            troughcolor="#022132",
            command=set_volume
        )
        volume_slider.set(self.volume*100)
        volume_slider.pack(pady=5)

        def close_popup():
            popup.destroy()
            self.resume_timer()

    
        ttk.Button(
            scroll_frame,
            text=self.t("close"),
            style="game.TButton",
            command=close_popup
        ).pack(pady=10)

    def reopen_settings(self):
    # Destroy current settings popup if it exists
        for widget in self.master.winfo_children():
            if isinstance(widget, tk.Toplevel) and widget.title() in ("Settings","Nastavení"):
                widget.destroy()

        # Recreate it
        self.settings_popup()

# RUN GAME
if __name__ == "__main__":
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
    app = SudokuGUI(root)
    root.mainloop()

    # czech and special rules :))