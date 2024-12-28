import tkinter as tk
import time
from tkinter import messagebox
import random
import heapq

# ...existing code...
class SudokuUI:
    def __init__(self, root):
        self.root = root
        self.entries = [[tk.Entry(self.root) for _ in range(9)] for _ in range(9)]
        self.solution_found = False
        self.solving = False  # Initialize solving flag
        self.setup_ui()

        # Add clock frame at the top
        self.clock_frame = tk.Frame(self.root)
        self.clock_frame.pack(side=tk.TOP, pady=10)

        self.clock_label = tk.Label(self.clock_frame, text="Time:")
        self.clock_label.pack(side=tk.LEFT, padx=5)

        self.time_var = tk.StringVar()
        self.time_var.set("00:00.00")
        self.time_display = tk.Label(self.clock_frame, textvariable=self.time_var, font=("Helvetica", 12))
        self.time_display.pack(side=tk.LEFT)

        self.start_time = None
        self.running = False

    def start_timer(self):
        self.start_time = time.time()
        self.running = True
        self.update_timer()

    def update_timer(self):
        if self.running:
            if self.start_time is not None:
                elapsed = time.time() - self.start_time
            else:
                elapsed = 0
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            hundredths = int((elapsed - int(elapsed)) * 100)
            self.time_var.set(f"{minutes:02d}:{seconds:02d}.{hundredths:02d}")
            self.root.after(100, self.update_timer)

    def stop_timer(self):
        self.running = False

    def reset_timer(self):
        self.time_var.set("00:00.00")
        self.start_time = None
        self.running = False

    def setup_ui(self):
        self.root.title("Sudoku Solver")
        main_frame = tk.Frame(self.root, bd=2, relief='solid')
        main_frame.pack()
        
        vcmd = (self.root.register(self.validate_digit), '%P')
        
        for box_r in range(3):
            for box_c in range(3):
                frame = tk.Frame(main_frame, bd=1, relief='solid')
                frame.grid(row=box_r, column=box_c, padx=2, pady=2)
                
                for i in range(3):
                    for j in range(3):
                        r = box_r * 3 + i
                        c = box_c * 3 + j
                        entry = tk.Entry(frame, width=2, font=('Arial', 18), justify='center', fg='black',
                                         validate='key', validatecommand=vcmd)
                        entry.grid(row=i, column=j, padx=1, pady=1)
                        entry.bind("<FocusOut>", self.mark_user_entry)
                        entry.bind("<Up>", lambda e, r=r, c=c: self.move_focus(r-1, c))
                        entry.bind("<Down>", lambda e, r=r, c=c: self.move_focus(r+1, c))
                        entry.bind("<Left>", lambda e, r=r, c=c: self.move_focus(r, c-1))
                        entry.bind("<Right>", lambda e, r=r, c=c: self.move_focus(r, c+1))
                        self.entries[r][c] = entry
                        
        button_frame = tk.Frame(self.root)  # New frame for buttons and delay box
        button_frame.pack(pady=5)
        
        random_button = tk.Button(button_frame, text="Random!", command=self.fill_random)
        random_button.pack(side=tk.LEFT, padx=5)

        solve_button = tk.Button(button_frame, text="Solve", command=self.solve_sudoku)
        solve_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = tk.Button(button_frame, text="Clear", command=self.clear_grid)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        delay_frame = tk.Frame(button_frame)  # Move delay_frame into button_frame
        delay_frame.pack(side=tk.LEFT, padx=5)
        
        delay_label = tk.Label(delay_frame, text="Delay (ms):")
        delay_label.pack(side=tk.LEFT)
        
        self.delay_entry = tk.Entry(delay_frame, width=5)
        self.delay_entry.insert(0, "50")
        self.delay_entry.pack(side=tk.LEFT)

    def clear_grid(self):
        self.reset_timer()
        self.solving = False  # Stop solving
        for r in range(9):
            for c in range(9):
                if self.entries[r][c] is not None:
                    self.entries[r][c].delete(0, tk.END)

    def mark_user_entry(self, event):
        entry = event.widget
        value = entry.get()
        row, col = self.get_entry_position(entry)
        
        if value == "":
            entry.config(bg='white', fg='black')
        elif not value.isdigit() or not 1 <= int(value) <= 9:
            entry.config(bg='red', fg='black')
        else:
            if self.has_conflict(row, col, int(value)):
                entry.config(bg='red', fg='black')
            else:
                entry.config(bg='white', fg='green')
        
        self.validate_entries()  # Re-validate all entries to update their colors

    def get_entry_position(self, entry):
        for r in range(9):
            for c in range(9):
                if self.entries[r][c] == entry:
                    return r, c
        return None, None

    def has_conflict(self, row, col, num):
        # Check row
        for c in range(9):
            if c != col:
                existing = self.get_entry_value(row, c)
                if existing == num:
                    return True
        # Check column
        for r in range(9):
            if r != row:
                existing = self.get_entry_value(r, col)
                if existing == num:
                    return True
        # Check 3x3 subgrid
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                if (r != row or c != col):
                    existing = self.get_entry_value(r, c)
                    if existing == num:
                        return True
        return False

    def get_entry_value(self, row, col):
        value = self.entries[row][col].get()
        return int(value) if value.isdigit() else None

    def get_puzzle(self):
        puzzle = []
        for r in range(9):
            row = []
            for c in range(9):
                if self.entries[r][c] is not None:
                    val = self.entries[r][c].get()
                    row.append(int(val) if val.isdigit() else 0)
                    if val.isdigit():
                        self.entries[r][c].config(fg='red')  # Set user-entered numbers to red
                    else:
                        self.entries[r][c].config(fg='black')
                else:
                    row.append(0)
            puzzle.append(row)
        return puzzle

    def solve_sudoku(self):
        self.root.focus_set()
        self.solution_found = False
        if not self.validate_entries():
            messagebox.showerror("Invalid Input", "Please correct the highlighted cells before solving.")
            return
        self.start_timer()
        self.solving = True  # Start solving

        puzzle = self.get_puzzle()
        possibilities = self.build_possibilities(puzzle)
        self.backtrack(puzzle, possibilities)
        self.stop_timer()
        if not self.solution_found:
            messagebox.showinfo("Sodoku Solver", "NO SOLUTION!")
        else:
            messagebox.showinfo("Sodoku Solver", "SOLUTION FOUND!")

        self.solving = False  # Solving finished

    def validate_entries(self):
        if self.solving:
            return True  # Allow programmatic changes
        valid = True
        for r in range(9):
            for c in range(9):
                value = self.entries[r][c].get()
                if value == "":
                    self.entries[r][c].config(bg='white', fg='black')
                    continue
                if not value.isdigit() or not 1 <= int(value) <= 9:
                    self.entries[r][c].config(bg='red', fg='black')
                    valid = False
                elif self.has_conflict(r, c, int(value)):
                    self.entries[r][c].config(bg='red', fg='black')
                    valid = False
                else:
                    self.entries[r][c].config(bg='white', fg='green')
        return valid

    def build_possibilities(self, puzzle):
        possibilities = {}
        for r in range(9):
            for c in range(9):
                if puzzle[r][c] == 0:
                    valid_nums = set(range(1, 10))
                    # Eliminate based on row
                    valid_nums -= set(puzzle[r])
                    # Eliminate based on column
                    valid_nums -= {puzzle[i][c] for i in range(9)}
                    # Eliminate based on subgrid
                    start_row, start_col = 3 * (r // 3), 3 * (c // 3)
                    subgrid = {puzzle[i][j] for i in range(start_row, start_row + 3)
                                        for j in range(start_col, start_col + 3)}
                    valid_nums -= subgrid
                    possibilities[(r, c)] = valid_nums
        return possibilities

    def get_next_cell_optimized(self, puzzle, possibilities):
        # Implement Cross-Hatching by selecting the cell with fewest possibilities
        min_count = 10
        best_cell = None
        for cell, nums in possibilities.items():
            count = len(nums)
            if count < min_count:
                min_count = count
                best_cell = cell
            if count == 1:
                break
        return best_cell if best_cell else (None, None)

    def backtrack(self, puzzle, possibilities):
        if not self.solving:
            return False
        row, col = self.get_next_cell_optimized(puzzle, possibilities)
        if row is None:
            self.solution_found = True
            return True

        for num in sorted(possibilities[(row, col)]):
            if self.is_safe(puzzle, row, col, num):
                puzzle[row][col] = num
                self.entries[row][col].delete(0, tk.END)
                self.entries[row][col].insert(0, str(num))
                self.entries[row][col].config(fg='black')
                self.root.update()
                try:
                    delay = int(self.delay_entry.get()) / 1000
                except ValueError:
                    delay = 0.05
                time.sleep(delay)

                new_possibilities = self.build_possibilities(puzzle)
                if self.backtrack(puzzle, new_possibilities):
                    return True

                puzzle[row][col] = 0
                self.entries[row][col].delete(0, tk.END)
        return False

    def is_safe(self, puzzle, row, col, num):
        if any(puzzle[row][i] == num for i in range(9)):
            return False
        if any(puzzle[i][col] == num for i in range(9)):
            return False
        br, bc = (row//3)*3, (col//3)*3
        for r in range(br, br+3):
            for c in range(bc, bc+3):
                if puzzle[r][c] == num:
                    return False
        return True

    def validate_digit(self, P):
        if P == "":
            return True
        if len(P) > 1:
            return False
        if P.isdigit() and 1 <= int(P) <= 9:
            return True
        return False

    def move_focus(self, row, col):
        if 0 <= row < 9 and 0 <= col < 9:
            self.entries[row][col].focus_set()

    def fill_random(self):
        for r in range(9):
            for c in range(9):
                choice = random.randint(0, 15)
                if choice != 0:
                    continue  # Skip filling this cell
                
                if self.entries[r][c].get() == "":
                    num = random.randint(1, 9)
                    attempts = 0
                    while self.has_conflict(r, c, num) and attempts < 10:
                        num = random.randint(1, 9)
                        attempts += 1
                    if not self.has_conflict(r, c, num):
                        self.entries[r][c].insert(0, str(num))
                        self.entries[r][c].config(bg='white', fg='green')
        
        self.validate_entries()

def main():
    root = tk.Tk()
    app = SudokuUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()