import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import time
from SlitherLinkPreloading import SlitherLinkPreloading
from SlitherLinkOrigin import SlitherLinkOrigin
from SlitherLinkAddAllLoop import SlitherLinkAddAllLoop
from SlitherLinkAddAllLoopWithEmpty import SlitherLinkAddAllLoopWithEmpty
from SlitherLinkPatterns import SlitherLinkPatterns
from pysat.solvers import Minisat22


class SlitherLinkApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        self.problem_Set = 0
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Slitherlink Solver")

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.selected_choice = ""
        self.name = ""

        self.frames = dict()

        for F in (LoadPage,):
            frame = F(self.container, self)
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoadPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def add_frame(self, cont):
        frame = cont(self.container, self)
        self.frames[cont] = frame

        frame.grid(row=0, column=0, sticky="nsew")


class LoadPage(tk.Frame):
    """This class creates a new frame in the app."""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        self.version_text = tk.StringVar()
        label0 = tk.Label(self, text="Version")
        label0.grid(row=0, column=0)
        self.version_choose = ttk.Combobox(self, textvariable=self.version_text)
        self.version_choose['values'] = ('Add All Loop', 'Origin', 'Preloading', 'Add All Loop With Empty', "Patterns")
        self.version_choose.current(4)
        self.version_choose["state"] = "readonly"
        self.version_choose.grid(row=0, column=1)

        label1 = tk.Label(self, text="Load file: ")
        label1.grid(row=1, column=0)
        self.filename = tk.StringVar()
        self.file_display = ttk.Label(self, textvariable=self.filename)
        self.file_display.grid(row=1, column=1)
        button1 = ttk.Button(self, text="Open", command=self.select_file)
        button1.grid(row=1, column=2)
        button2 = ttk.Button(self, text="Next", command=self.next)
        button2.grid(row=2, column=2)

    def close(self):
        app.quit()

    def select_file(self):
        filetypes = (
            ('text files', '*.txt'),
            ('All files', '*.*')
        )

        self.controller.filename = fd.askopenfilename(
            title='Open a file',
            filetypes=filetypes)

        self.filename.set(self.controller.filename)

    def next(self):
        if (self.controller.filename == None or self.controller.filename == ""):
            return
        self.controller.version_text = self.version_text.get()
        self.controller.add_frame(SlitherlinkUIPage)
        self.controller.show_frame(SlitherlinkUIPage)


class SlitherlinkUIPage(tk.Frame):
    """This class creates a new frame in the app. This class is responsible for generating the sudoku grid."""
    time_taken = time.time()

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.canvas = None
        self.controller = controller

        if self.controller.version_text == "Add All Loop":
            self.solver = SlitherLinkAddAllLoop(Minisat22)
        elif self.controller.version_text == "Origin":
            self.solver = SlitherLinkOrigin(Minisat22)
        elif self.controller.version_text == "Preloading":
            self.solver = SlitherLinkPreloading(Minisat22)
        elif self.controller.version_text == "Add All Loop With Empty":
            self.solver = SlitherLinkAddAllLoopWithEmpty(Minisat22)
        elif self.controller.version_text == "Patterns":
            self.solver = SlitherLinkPatterns(Minisat22)

        self.solver.load_from_file(self.controller.filename)

        self.entries = []

        self.create_can()

        self.num_conditions = tk.StringVar()
        self.run_time = tk.StringVar()
        self.num_variable = tk.StringVar()
        self.num_loops = tk.StringVar()
        self.label_version = ttk.Label(self, text='Version ' + self.controller.version_text, font=(("Bold", 20)))
        self.label_number_loop = ttk.Label(self, text="Number of loops: ")
        self.label_number_loop_value = ttk.Label(self, textvariable=self.num_loops)
        self.label_number_conditions = ttk.Label(self, text="Number of conditions: ")
        self.label_number_conditions_value = ttk.Label(self, textvariable=self.num_conditions)
        self.label_number_variables = ttk.Label(self, text="Number of variable: ")
        self.label_number_variables_value = ttk.Label(self, textvariable=self.num_variable)
        self.label_runtime = ttk.Label(self, text="Run time (seconds): ")
        self.label_runtime_value = ttk.Label(self, textvariable=self.run_time)
        self.button_resolve = ttk.Button(self, text="Resolve", command=self.solve)
        self.button_previous = ttk.Button(self, text="Previous", command=self.solve_prev)
        self.button_next = ttk.Button(self, text="Next", command=self.solve_next)
        self.button_previous['state'] = "disable"
        self.button_next['state'] = "disable"
        self.label_jump_to_loop = ttk.Label(self, text="Jump to loop: ")
        self.text_field_jump = tk.Entry(self)
        self.button_jump = ttk.Button(self, text="Jump", command=self.jump_to_loop)
        self.count = 0
        self.set_ui_tool_position()

    def set_ui_tool_position(self):
        self.label_version.place(x=1200, y=250)
        self.label_number_loop.place(x=1200, y=330)
        self.label_number_loop_value.place(x=1400, y=330)
        self.label_number_conditions.place(x=1200, y=360)
        self.label_number_conditions_value.place(x=1400, y=360)
        self.label_number_variables.place(x=1200, y=390)
        self.label_number_variables_value.place(x=1400, y=390)
        self.label_runtime.place(x=1200, y=420)
        self.label_runtime_value.place(x=1400, y=420)
        self.button_resolve.place(x=1200, y=300)
        self.button_previous.place(x=1300, y=300)
        self.button_next.place(x=1400, y=300)
        self.label_jump_to_loop.place(x=1200, y=450)
        self.text_field_jump.place(x=1300, y=450)
        self.button_jump.place(x=1450, y=450)

    def set_ui_tool_visibility(self):
        self.label_version.lift()
        self.label_number_loop.lift()
        self.label_number_loop_value.lift()
        self.label_number_conditions.lift()
        self.label_number_conditions_value.lift()
        self.label_number_variables.lift()
        self.label_number_variables_value.lift()
        self.label_runtime.lift()
        self.label_runtime_value.lift()
        self.button_resolve.lift()
        self.button_previous.lift()
        self.button_next.lift()

    def solve(self, *args):
        self.button_resolve['state'] = "disable"
        self.count = 0
        start_time = time.time()

        self.solver.solve()

        end_time = time.time()

        self.update_can()

        self.num_loops.set(self.solver.num_loops)

        self.num_conditions.set(str(len(self.solver.cond)))

        self.run_time.set(str(end_time - start_time))

        self.num_variable.set(str(len(self.solver.model)))

        self.count = len(self.solver.model_arr)

        self.button_previous['state'] = "enable"

    def solve_prev(self, *args):
        self.count -= 1
        if self.count == 1:
            self.button_previous['state'] = "disable"
        self.solver.model = self.solver.model_arr[self.count - 1]

        self.update_can()
        self.num_loops.set(str(self.count))

        self.button_next['state'] = "enable"

    def solve_next(self, *args):
        self.count += 1
        if self.count == len(self.solver.model_arr):
            self.button_next['state'] = "disable"
        self.solver.model = self.solver.model_arr[self.count - 1]

        self.update_can()
        self.num_loops.set(str(self.count))

        self.button_previous['state'] = "enable"

    def jump_to_loop(self, *args):
        loop_index = int(self.text_field_jump.get())
        if 0 < loop_index <= len(self.solver.model_arr):
            self.count = loop_index
            self.solver.model = self.solver.model_arr[self.count - 1]
            self.update_can()
            self.num_loops.set(str(self.count))
            if self.count == 1:
                self.button_previous['state'] = "disable"
            if self.count == len(self.solver.model_arr):
                self.button_next['state'] = "disable"

    def update_can(self):
        self.canvas.delete("all")
        self.create_can()
        if self.solver.result:
            edges = [self.solver.converter.get_two_vertices(i) for i in self.solver.model if i > 0]
            for edge in edges:
                x1, y1, x2, y2 = edge
                x1 = x1 * 20 + 10
                y1 = y1 * 20 + 10
                x2 = x2 * 20 + 10
                y2 = y2 * 20 + 10
                self.canvas.create_line(y1, x1, y2, x2, width=1)
        self.set_ui_tool_visibility()

    def create_can(self):

        self.canvas = tk.Canvas(self, height=self.solver.row * 20 + 30, width=self.solver.col * 20 + 30)

        for i in range(self.solver.col + 1):
            for j in range(self.solver.row + 1):
                x = i * 20 + 10
                y = j * 20 + 10
                self.canvas.create_oval(x - 1, y - 1, x + 1, y + 1, width=3)
        self.canvas.place(x=0, y=0)
        p, q = 14, 12

        for i in range(self.solver.row):
            for k in range(self.solver.col):
                x = self.solver.board[i][k]
                text_value = tk.StringVar()
                if x >= 0:
                    text_value.set(x)

                entry = tk.Label(self, textvariable=text_value, fg='black', font=("Normal", 6))
                entry.grid_slaves(row=i, column=k)
                entry.place(x=p, y=q)
                self.entries.append(text_value)
                p += 20.0
            q += 20
            p = 14


app = SlitherLinkApp()
width_value = app.winfo_screenwidth()
height_value = app.winfo_screenheight()
app.geometry("%dx%d+0+0" % (width_value, height_value))
app.mainloop()
