import tkinter as tk
import re
import time
import random 
from tkinter import messagebox
from tkinter import ttk
import copy
import pygame 


class SudokuGenerator:
    def __init__(self):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]

    def is_valid(self, grid, row, col, num):
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
        #fills the whole grid
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
        #checks solutions
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

    def remove_numbers(self, grid, holes=40):
        #removes numbers
        grid = copy.deepcopy(grid)
        attempts = holes
        while attempts > 0:
            row, col = random.randint(0, 8), random.randint(0, 8)
            while grid[row][col] == 0:
                row, col = random.randint(0, 8), random.randint(0, 8)
            backup = grid[row][col]
            grid[row][col] = 0

            # Zkontroluj, že sudoku má stále JEDNO řešení
            if self.solve_count(grid) != 1:
                grid[row][col] = backup  # Vrať číslo zpět
                attempts -= 1
            else:
                attempts -= 1
        return grid

    def generate(self, holes=40):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.fill_grid(self.grid)
        self.full_solution = copy.deepcopy(self.grid)
        puzzle = self.remove_numbers(self.full_solution, holes)
        return puzzle




#GUI
class SudokuGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("SudokuGame")
        self.master.bind_all("<Key>", self.handle_key)
        self.master.bind("<Button-1>", self.global_click)
        self.master.bind("<Button-3>", self.clear_selection)


        # Game state variables
        self.currentNumber = None
        self.running = False
        self.startTime = 0
        self.pauseTime = 0
        self.cells = {}
        self.selectedCells = set()
        self.inputMode = "cell_first"
        self.pencilMode = False
        self.color = "#73AFCF"
        self.gameStarted = False
        self.generator = SudokuGenerator()
        self.difficulty = 0
        self.music = True
        self.volume = 0.5

        #music
        pygame.mixer.init()
        pygame.mixer.music.load("sudokuu.py/music.mp3")
        pygame.mixer.music.set_volume(self.volume)  # výchozí hlasitost 50 %
        pygame.mixer.music.play(-1)
        
        # Ttk styles
        self.style = ttk.Style()
        self.style.configure("numbers.TButton", padding=(0,32), width=6, relief="flat", background="#022132", fg= "#022132",font=("SF Pro Display", 22))
        self.style.configure("game.TButton", padding=6, relief="flat", background="#022132", fg= "#022132",font=("SF Pro Display", 18))
        self.style.configure("menu.TButton", padding=6, relief="flat", background="#022132", fg= "#022132",font=("SF Pro Display", 20))

        # Frames
        self.menu_frame = tk.Frame(self.master)
        self.game_frame = tk.Frame(self.master)

        # Menu
        self.create_main_menu()

    # Key binding
    def handle_key(self, event):
        key = event.char.lower()
        if key == "r":
            self.show_rules_popup()
        elif key == "p":
            self.toggle_pencilMode()
        elif key == "m":
            self.toggle_inputMode()
        elif key =="b":
            self.back_to_menu()


    # ---------------- MENU SCREEN ----------------
    def create_main_menu(self):
        self.menu_frame.config(bg=self.color)
        self.menu_frame.pack(expand=True, fill="both")

        title = tk.Label(
            self.menu_frame,
            text="🧩 Sudoku",
            fg= "#022132",
            background=self.color,
            font=("SF Pro Display", 38, "bold"),
            pady=30,
        )
        title.pack()

        ttk.Button(
            self.menu_frame,
            text="Play Basic",
            width=20,
            command=lambda: self.start_game("basic"),
            style="menu.TButton",
        ).pack(pady=10)

        ttk.Button(
            self.menu_frame,
            text="Play with Extra Rules",
            width=20,
            command=lambda: self.start_game("extra"),
            style="menu.TButton",
        ).pack(pady=10)

        ttk.Button(
            self.menu_frame,
            text="View Rules",
            width=20,
            command=self.show_rules_popup,
            style="menu.TButton",
        ).pack(pady=10)

        ttk.Button(
            self.menu_frame,
            text="Settings",
            width=20,
            command=self.settings_popup,
            style="menu.TButton",
        ).pack(pady=10)

        ttk.Button(
            self.menu_frame,
            text="Quit",
            width=20,
            command=self.master.destroy,
            style="menu.TButton",
        ).pack(pady=20)

    # ---------------- GAME SETUP ----------------
    def start_game(self, mode):
        if self.gameStarted == True:
            text = "Do you want to continue or start a new game?"
            buttons = {
                "Continue previous game": lambda:self.continue_game(),
                "Start a new game" : lambda:self.choose_difficulty()
            }
            self.popup("Start Game", text, buttons)

        else:
            self.mode = mode
            self.choose_difficulty()

    def continue_game(self):
        self.menu_frame.pack_forget()
        self.resume_timer()
        self.game_frame.pack(fill="both", expand=True)

    def choose_difficulty(self):
        text = "Which difficulty do you want?"
        buttons = {
            "Easy": lambda: self.start_with_difficulty(30),
            "Medium": lambda: self.start_with_difficulty(45),
            "Hard": lambda: self.start_with_difficulty(60)
        }
        self.popup("Choose Difficulty", text, buttons)
        
    def start_with_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.gameStarted = True
        self.setup_game_screen()


    def setup_game_screen(self):
        self.menu_frame.pack_forget()
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        self.game_frame.pack(fill="both", expand=True)
        self.game_frame.config(bg=self.color)
        
        # ---------------- Timer nahoře ----------------
        self.timer_label = tk.Label(
            self.game_frame, font=("SF Pro Display", 15), bg=self.color
        )
        self.timer_label.pack(pady=5)

        # Start timer
        self.running = True
        self.startTime = time.time()
        self.update_timer()
        
        controls0 = tk.Frame(self.game_frame, bg=self.color)
        controls0.pack(pady=10)

        ttk.Button(
            controls0,
            text="See Solved/Done",
            style="game.TButton",
            command=self.see_solution,
        ).grid(row=0, column=0, padx=10)
        ttk.Button(
            controls0,
            text="Check Numbers",
            style="game.TButton",
            command=self.check_numbers,
        ).grid(row=0, column=1, padx=10)
        ttk.Button(
            controls0,
            text="Start Over",
            style="game.TButton",
            command=self.start_over,
        ).grid(row=0, column=2, padx=10)


        # sudoku grid and numbers
        main_frame = tk.Frame(self.game_frame, bg=self.color)
        main_frame.pack(expand=True, anchor="n")


        # ---------------- Sudoku ----------------
        sudoku_frame = tk.Frame(main_frame, bg=self.color)
        sudoku_frame.grid(row=0, column=0, sticky="n")
        grid_frame = tk.Frame(sudoku_frame, bg=self.color)
        grid_frame.pack()
        
        self.cells = {}
        for row in range(9):
            for col in range(9):
                # Border logic for 3×3 boxes
                border_color = "black"
                top = 3 if row % 3 == 0 else 1
                left = 3 if col % 3 == 0 else 1
                bottom = 3 if row == 8 else 1
                right = 3 if col == 8 else 1

                frame = tk.Frame(
                    grid_frame,
                    highlightbackground=self.color,
                    highlightcolor=border_color,
                    bg=self.color
                )
                frame.grid(row=row, column=col, padx=(left, right), pady=(top, bottom))

                bg_color = "#FFFFFF" if (row // 3 + col // 3) % 2 == 0 else "#DCE6EB"
                cell = tk.Label(
                    frame,
                    text="",
                    width=2,
                    height=1,
                    font=("SF Pro Display", 25),
                    relief="solid",
                    borderwidth=1,
                    bg=bg_color,
                )
                cell.pack(fill="both", expand=True)
                cell.bind("<Button-1>", lambda e, r=row, c=col: self.cell_clicked(r, c))
                self.cells[(row, col)] = cell

        self.puzzle = self.generator.generate(holes = self.difficulty)
        self.generate_puzzle()


        # ---------------- Number pad and pencil and clear----------------
        pad_frame = tk.Frame(main_frame, bg=self.color,)
        pad_frame.grid(row=0, column=1, sticky="n", padx=10, pady=10)

        # Number pad
        self.create_number_pad(pad_frame)

        # Bind keyboard for number entry in cell-first mode
        self.master.bind("<Key>", self.handle_key_input)

        # Controls
        controls = tk.Frame(self.game_frame, bg=self.color)
        controls.pack(expand=True, fill="y",)

        ttk.Button(
            controls,
            text="Rules / Pause",
            style="game.TButton",
            command=self.show_rules_popup,
        ).grid(row=0, column=0, padx=10, sticky="n")

        ttk.Button(
            controls,
            text="Switch Input Mode",
            style="game.TButton",
            command=self.toggle_inputMode,
        ).grid(row=0, column=1, padx=10, sticky="n")

        ttk.Button(
            controls,
            text="Back to Menu",
            style="game.TButton",
            command=self.back_to_menu,
        ).grid(row=0, column=2, padx=10, sticky="n")

    # ---------------- TIMER ----------------
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

    # ---------------- INPUT MODES ----------------
    def toggle_inputMode(self):
        """Switch between number-first and cell-first input modes."""
        if self.inputMode == "number_first":
            self.inputMode = "cell_first" 
        else :
            self.inputMode = "number_first"
        self.clear_selection()

    def generate_puzzle(self):
        # === FILL GRID WITH GENERATED NUMBERS ===
        for row in range(9):
            for col in range(9):
                value = self.puzzle[row][col]
                if value != 0:
                    self.cells[(row, col)].config(text=str(value), fg="black")
                else:
                    self.cells[(row, col)].config(text="", fg="gray")

    # ---------------- NUMBER PAD ----------------
    def create_number_pad(self, frame):
        btn_frame = tk.Frame(frame, bg=self.color)
        btn_frame.pack()
        self.style.configure("numbers.TButton", padding=(0,32), width=6, relief="flat", background="#022132", fg= "#022132",font=("SF Pro Display", 22))

        for num in range(1, 10):
            btn = ttk.Button(
                btn_frame,
                text=str(num),
                
                style="numbers.TButton",
                command=lambda n=num: self.select_number(n),
            )
            btn.grid(row=(num - 1) // 3, column=(num - 1) % 3, padx=3, pady=3)

        action_frame = tk.Frame(frame, bg=self.color)
        action_frame.pack(pady=5)

        ttk.Button(
            action_frame,
            text="Clear Cell",
            style="game.TButton",
            command=lambda: self.select_number(0)
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            action_frame,
            text="Pencil Mode",
            style="game.TButton",
            command=self.toggle_pencilMode
        ).grid(row=0, column=1, padx=5)

    def select_number(self, num):
        if self.inputMode == "number_first":
            self.currentNumber = num
            self.master.config(cursor="hand2" if num else "X_cursor")

        elif self.inputMode == "cell_first":
            if not self.selectedCells:
                messagebox.showinfo("No Cell Selected", "Select a cell first!")
                return

            for (r, c) in self.selectedCells:
                if self.pencilMode and num != 0:
                    self.toggle_pencil_number(r, c, num)
                else:
                    self.place_number_in_selected(num)
            self.check_errors()

    #other button functions

    def see_solution(self):
        text = "Do you want to give up?"
        buttons = {
                "See Solution": lambda:self.solution(),
        }
        self.popup("See Solution", text, buttons)
        self.full_solution = self.generator.grid

    def solution(self):
        for row in range(9):
             for col in range(9):
                value =self.full_solution[row][col]
                if value != 0:
                    self.cells[(row, col)].config(text=str(value), fg="black")
                else:
                    self.cells[(row, col)].config(text="", fg="gray")

    def start_over(self):
        text = "Do you want to start this puzzle over or get a new one?"
        buttons = {
                "Erase My Numbers": lambda:self.generate_puzzle(),
                "New Game": lambda:self.setup_game_screen(),
        }
        self.popup("See Solution", text, buttons)
        self.full_solution = self.generator.grid

    def check_numbers(self):
        self.full_solution = self.generator.grid
        all_correct = True
        for row in range(9):
            for col in range(9):
                cell = self.cells[(row, col)]
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
            messagebox.showinfo("Check", "Every number is right so far!")
        else:
            messagebox.showinfo("Check", "Oh no! You made a mistake somewhere")



    # ---------------- PENCIL MODE ----------------
    def toggle_pencilMode(self):
        self.pencilMode = not self.pencilMode
        self.master.config(cursor="pencil" if self.pencilMode == True else "hand2")

    def toggle_pencil_number(self, row, col, num):
        """Toggle a pencil number in a cell. If num=0, clear all pencil marks."""
        cell = self.cells[(row, col)]
        if num == 0:
            cell.config(text="", font=("SF Pro Display", 25), width=2, height=1)
            return

        current_text = cell.cget("text")
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
                fg="black"
            )
        else:
            cell.config(
                text="",
                font=("SF Pro Display", 25),
                width=2, height=1,
                fg="black"
            )

    # ---------------- CELL ACTIONS ----------------
    def cell_clicked(self, row, col):
        if not self.running:
            messagebox.showinfo("Paused", "Timer is paused. Resume to play.")
            return

        cell = self.cells[(row, col)]

        if self.inputMode == "number_first":
            if self.currentNumber is None:
                messagebox.showinfo("No Number Selected", "Select a number first!")
                return

            if self.pencilMode and self.currentNumber != 0:
                self.toggle_pencil_number(row, col, self.currentNumber)
            else:
                if self.currentNumber == 0:
                    cell.config(text="", font=("SF Pro Display", 25))
                else:
                    cell.config(text=str(self.currentNumber), font=("SF Pro Display", 25),  width=2, height=1)
            self.check_errors()
        else:
            self.toggle_cell_selection(row, col)

    def toggle_cell_selection(self, row, col):
        """Toggle selection highlight for a cell."""
        cell = self.cells[(row, col)]
        if (row, col) in self.selectedCells:
            self.selectedCells.remove((row, col))
            cell.config(bg= "#FFFFFF" if (row // 3 + col // 3) % 2 == 0 else "#DCE6EB")
        else:
            self.selectedCells.add((row, col))
            cell.config(bg="#BCE7FF")

    def clear_selection(self, event=None):
        """Clear all highlighted cells."""
        for (r, c) in self.selectedCells:
            self.cells[(r, c)].config(bg = "#FFFFFF" if (r // 3 + c// 3) % 2 == 0 else "#DCE6EB")
        self.selectedCells.clear()

    def global_click(self, event):
        widget = event.widget
        if not isinstance(widget, (tk.Label, tk.Button, tk.Canvas, ttk.Button)):
            self.clear_selection()

    def place_number_in_selected(self, num):
        """Place a number in all selected cells."""
        for (r, c) in self.selectedCells:
            self.cells[(r, c)].config(text="" if num == 0 else str(num))

    def handle_key_input(self, event):
        if self.inputMode != "cell_first" or not self.running:
            return
        if event.char.isdigit() and event.char != "0":
            num = int(event.char)
            if self.pencilMode:
                for r, c in self.selectedCells:
                    self.toggle_pencil_number(r, c, num)
            else:
                self.place_number_in_selected(num)
        elif event.keysym in ("BackSpace", "Delete"):
            if self.pencilMode:
                for r, c in self.selectedCells:
                    self.toggle_pencil_number(r, c, 0)
            else:
                self.place_number_in_selected(0)
        self.check_errors()

    # ---------------- ERROR CHECK ----------------
    def check_errors(self):
        """Check all cells for conflicts. Pencil marks are handled separately."""
        for cell in self.cells.values():
            cell.config(fg="black")

        rows = {r: {} for r in range(9)}
        cols = {c: {} for c in range(9)}
        boxes = {(r // 3, c // 3): {} for r in range(9) for c in range(9)}

        for (r, c), cell in self.cells.items():
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
                if val not in "123456789":
                    continue
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
                        cell = self.cells[pos]
                        f = cell.cget("font")
                        font_size = f[1] if isinstance(f, tuple) else int(re.search(r'\d+', f).group())
                        if font_size >= 10:
                            cell.config(fg="red")

            if '_pencil' in group:
                for val, pos in group['_pencil']:
                    cell = self.cells[pos]
                    if val in group and any(
                        self.cells[p].cget("font")[1] >= 10 if isinstance(self.cells[p].cget("font"), tuple)
                        else int(re.search(r'\d+', self.cells[p].cget("font")).group()) >= 10
                        for p in group[val]
                    ):
                        cell.config(fg="red")

    # ---------------- GAME CONTROLS ----------------
    def back_to_menu(self):
        self.running = False
        self.clear_selection()
        self.game_frame.pack_forget()
        self.menu_frame.pack(expand=True, fill="both")

    # Settings
    def settings_popup(self):

        # --- Music toggle function ---
        def toggle_music():
            if self.music:
                pygame.mixer.music.pause()
                self.music = False
                toggle_btn.config(text="Turn Music On")
            else:
                pygame.mixer.music.unpause()
                self.music = True
                toggle_btn.config(text="Turn Music Off")

        # --- Volume control function ---
        def set_volume(val):
            volume = float(val)
            self.volume = volume/100
            pygame.mixer.music.set_volume(self.volume)

        # --- Create popup using your existing popup() function ---
        self.popup("Settings", "Settings:", close = False)

        # --- Access the last opened popup (your popup creates a new Toplevel) ---
        popup = self.master.winfo_children()[-1]

        # --- Find scroll_frame (3 layers deep inside popup structure) ---
        # container -> canvas -> scroll_frame
        container = popup.winfo_children()[0]
        canvas = container.winfo_children()[0]
        scroll_frame = canvas.winfo_children()[0]

        # --- On/Off button ---
        toggle_btn = ttk.Button(
            scroll_frame,
            text="Turn Music Off" if self.music else "Turn Music On",
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
            fg="white",
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
            text="Close",
            style="game.TButton",
            command=close_popup
        ).pack(pady=10)




    # ---------------- RULES POPUP ----------------
    def show_rules_popup(self):
        rules_text = (
            "🧩 Sudoku Rules:\n\n"
            "1. Each row, column, and 3x3 box must contain digits 1–9.\n"
            "2. No number repeats in any row, column, or box.\n\n"
            "Extra Rules Mode:\n"
            "Controls:\n"
            "• Switch Input Mode (press M) to change how you play.\n"
            "• Number-first: Select number, then click cells.\n"
            "• Cell-first: Select cell(s), then choose a number or type it.\n"
            "• You can select multiple cells at once in Cell-first mode.\n"
            "• Press R to see the rules or if you want to pause the timer.\n"
            "• Use ESC to exit fullscreen.\n"
        )
        self.popup("Rules", rules_text)
        self.pauseTimer()

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
            fg="white",
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
                    command=lambda c=command: [c(), popup.destroy()] if c else popup.destroy()
                ).pack( pady=10)
        
        def close_popup():
            popup.destroy()
            self.resume_timer()

        if close:
            ttk.Button(
                btn_frame,
                text="Close",
                style="game.TButton",
                command=close_popup
            ).pack(pady=10)


# ---------------- RUN GAME ----------------
if __name__ == "__main__":
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
    app = SudokuGUI(root)
    root.mainloop()

    # czech and special rules :))