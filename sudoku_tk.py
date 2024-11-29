from itertools import permutations
import time
from tkinter import Tk, Label, Entry, Button, END, CENTER, Checkbutton, BooleanVar

matrix = [[0] * 9 for _ in range(9)]
perms = {}
entries = []
labels = []
labels2 = []


# check if number has no conflicts - not present in a row, column or quadrant
def check(m, n, i, j):
    if n in m[i]:  # check a row
        return False
    if n in [r[j] for r in m]:  # check column
        return False
    # spot a quadrant in which the current cell is
    ii = (i // 3) * 3
    jj = (j // 3) * 3
    square = m[ii][jj : jj + 3] + m[ii + 1][jj : jj + 3] + m[ii + 2][jj : jj + 3]
    return n not in square  # check in it


# write numbers into the game matrix
def write_matrix(event, i, j):
    if event.keysym in ["Up", "Down", "Left", "Right", "Tab", "Return"]:
        # keyboard movements and controls
        match event.keysym:
            case "Up":
                if i:
                    entries[i - 1][j].focus()
                if not i:
                    entries[8][j].focus()
            case "Down":
                if i < 8:
                    entries[i + 1][j].focus()
                if i == 8:
                    entries[0][j].focus()
            case "Left":
                if j:
                    entries[i][j - 1].focus()
                if not j:
                    entries[i][8].focus()
            case "Right":
                if j < 8:
                    entries[i][j + 1].focus()
                if j == 8:
                    entries[i][0].focus()
            case "Return":
                solvebtn.focus()
        return True
    if entries[i][j].get():
        # clear the cell before entering the new number
        entries[i][j].delete(0, END)
    ch = event.char  # new number is the same
    if ch and ch in "123456789" and int(ch) == matrix[i][j]:
        return True
    if ch == "0":  # for "empty" cells
        entries[i][j].config(fg="black")
        window.update()
        matrix[i][j] = 0
        return False
    if ch and ch in "123456789" and check(matrix, int(ch), i, j):
        # new number has no conflicts
        entries[i][j].config(fg="black")
        window.update()
        matrix[i][j] = int(ch)
        return True
    # new number has conflicts
    entries[i][j].config(fg="red")
    window.update()
    matrix[i][j] = 0
    return False


def draw_find_perm(i):
    # show how many permutations for the row found
    labels[i].config(text=len(perms[i]))
    window.update()


def check_row(m, p, i):
    n = 0  # enumerator for a permutation
    for j in range(9):
        if m[i][j]:
            # permutation is a list not containing predefined numbers
            continue
        if not check(m, p[n], i, j):  # check each number in a permutation
            return False
        n += 1
    return True


def find_perm():
    start = time.time()
    msg.config(text="Searching combinations...")
    window.update()
    for i, row in enumerate(matrix):
        # find permutations for each row for not predefined numbers
        r = {1, 2, 3, 4, 5, 6, 7, 8, 9} - set(row)
        perms[i] = []
        for p in permutations(r, len(r)):
            if check_row(matrix, p, i):
                perms[i].append(p)
        draw_find_perm(i)
    search(start)


def set_p(m, i, p):
    # set permutation to the row for the further checking
    n = 0
    for j in range(9):
        if not m[i][j]:
            m[i][j] = p[n]
            n += 1
    return m


def show_solution(i, p, index):
    labels2[i].config(text=index + 1)
    n = 0
    for j in range(9):
        if matrix[i][j]:
            continue
        entries[i][j].delete(0, END)
        entries[i][j].insert(END, str(p[n]))
        entries[i][j].config(fg="blue")
        n += 1


def search(start):
    b_live = live.get()
    msg.config(text="Searching solution...")
    window.update()
    p_list = [len(pl) for pl in perms.values()]
    for leng in p_list:
        if not leng:
            # one of the rows does not have solutions
            msg.config(text="No solutions :(")
            return False
    i_list = [0] * 9  # index list to track solutions
    m = [row[:] for row in matrix]  # copy of matrix to test solutions
    i = 0  # row step counter
    while i < 9:
        if i_list[i] == p_list[i]:
            i_list[i] = 0
            i -= 1  # permutation does not fit, step back
            m[i] = matrix[i][:]
            if i < 0:  # step back is not possible
                msg.config(text="No solutions :(")
                return False
            i_list[i] += 1  # increment index for current row
            continue
        p = perms[i][i_list[i]]  # get a permutation for checking
        if not i or check_row(m, p, i):
            # for row 0 all permutations fit
            m = set_p(m, i, p)  # set permutation
            if b_live:  # show progress is checked
                show_solution(i, p, i_list[i])
                window.update()
            i += 1  # increment row counter
        else:
            # if does not fit, increment permutations index for current row
            i_list[i] += 1
    # if the loop ended successfully
    msg.config(text=f"Solution found! Time: {time.time() - start:.2f}s")
    if not b_live:
        for i in range(9):
            p = perms[i][i_list[i]]
            show_solution(i, p, i_list[i])
    return True


def reset(clean=False):
    # delete all numbers, and predefined if clean is True
    for i in range(9):
        labels[i].config(text="")
        labels2[i].config(text="")
        for j in range(9):
            entries[i][j].delete(0, END)
            text = matrix[i][j]
            if clean or text == 0:
                text = ""
                matrix[i][j] = 0
            entries[i][j].insert(END, text)
            msg.config(text="Enter initial values.")


# Tkinter GUI
window = Tk()
window.title("Sudoku Solver")
window.resizable(False, False)
window.config(padx=0)
window.columnconfigure(9, minsize=50)
window.columnconfigure(10, minsize=50)

for i in range(9):
    label = Label(text="")
    label.grid(padx=0, row=i, column=9)
    labels.append(label)
    label2 = Label(text="")
    label2.grid(padx=0, row=i, column=10)
    labels2.append(label2)
    row_entries = []
    for j in range(9):
        bg = "white"
        if (i in (0, 1, 2, 6, 7, 8) and j in (0, 1, 2, 6, 7, 8)) or (
            i in (3, 4, 5) and j in (3, 4, 5)
        ):
            bg = "yellow"
        entry = Entry(width=3, justify=CENTER, font=("Arial 16 bold"), bg=bg)
        entry.grid(row=i, column=j)
        entry.bind("<Key>", lambda event, i=i, j=j: write_matrix(event, i, j))
        row_entries.append(entry)
    entries.append(row_entries)
entries[0][0].focus()
msg = Label(text="Enter initial values.")
msg.grid(row=9, column=0, columnspan=9)
solvebtn = Button(
    pady=1,
    text="Solve",
    highlightthickness=0,
    fg="white",
    bg="#366036",
    activeforeground="white",
    activebackground="#369036",
    command=find_perm,
)
solvebtn.grid(row=9, column=9, rowspan=2, columnspan=2, sticky="ewns")
resetbtn = Button(
    pady=1,
    text="Reset",
    highlightthickness=0,
    fg="white",
    bg="#363636",
    activeforeground="white",
    activebackground="#6a502a",
    command=reset,
)
resetbtn.grid(row=10, column=6, columnspan=3, sticky="ew")
cleanbtn = Button(
    pady=1,
    text="Clean",
    highlightthickness=0,
    fg="white",
    bg="#603636",
    activeforeground="white",
    activebackground="#903636",
    command=lambda: reset(True),
)
cleanbtn.grid(row=10, column=3, columnspan=3, sticky="ew")
live = BooleanVar()
c_live = Checkbutton(text="Show progress", variable=live, onvalue=True)
c_live.grid(row=10, column=0, columnspan=3, sticky="w")

window.mainloop()
