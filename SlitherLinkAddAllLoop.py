import numpy as np

import converter_2
from pysat.solvers import Minisat22
import time


class SlitherLinkAddAllLoop():
    def __init__(self, solver):
        self.base_cond = []
        self.board = None
        self.col = None
        self.cond = []
        self.converter = None
        self.edges = None
        self.list_loops = None
        self.list_nums = []
        self.model = None
        self.model_arr = []
        self.num_loops = 1
        self.result = None
        self.row = None
        self.solver = solver()

    def load_from_file(self, filename):
        with open(filename, 'rt') as file:
            lines = file.readlines()
        assert len(lines[0].split()) == 2, "Invalid"
        self.row, self.col = [int(x) for x in lines[0].split()]
        self.board = -np.ones(self.row * self.col, dtype=np.int32).reshape(self.row, self.col)
        for i in range(1, len(lines)):
            if len(lines[i].split()) == 3:
                i, j, k = [int(x) for x in lines[i].split()]
                self.board[i - 1, j - 1] = int(k)
                if k > 0:
                    self.list_nums.append((i-1, j-1))
        self.converter = converter_2.Converter(self.row, self.col)

    def build_cell_rule(self):
        for i in range(self.row):
            for j in range(self.col):
                if self.board[i, j] >= 0:
                    side_edges = self.converter.get_side_edges(i, j)
                    self.build_cell_condition(side_edges, self.board[i, j])

    def build_cell_condition(self, edges, k):
        e1, e2, e3, e4 = edges
        if k == 0:
            self.cond.append([-e1])
            self.cond.append([-e2])
            self.cond.append([-e3])
            self.cond.append([-e4])
        elif k == 1:
            self.cond.append([e1, e2, e3, e4])
            self.cond.append([-e1, -e2])
            self.cond.append([-e1, -e3])
            self.cond.append([-e1, -e4])
            self.cond.append([-e2, -e3])
            self.cond.append([-e2, -e4])
            self.cond.append([-e3, -e4])
        elif k == 2:
            self.cond.append([e1, e2, e3])
            self.cond.append([e1, e2, e4])
            self.cond.append([e1, e3, e4])
            self.cond.append([e2, e3, e4])
            self.cond.append([-e1, -e2, -e3])
            self.cond.append([-e1, -e2, -e4])
            self.cond.append([-e1, -e3, -e4])
            self.cond.append([-e2, -e3, -e4])
        elif k == 3:
            self.cond.append([-e1, -e2, -e3, -e4])
            self.cond.append([e1, e2])
            self.cond.append([e1, e3])
            self.cond.append([e1, e4])
            self.cond.append([e2, e3])
            self.cond.append([e2, e4])
            self.cond.append([e3, e4])
        elif k == 4:
            self.cond.append([e1])
            self.cond.append([e2])
            self.cond.append([e3])
            self.cond.append([e4])
        else:
            raise ValueError

    def build_neighbor_rule(self):
        for i in range(self.row + 1):
            for j in range(self.col + 1):
                neighbor_edges = self.converter.get_neighbor_edges(i, j)
                self.build_neighbor_condition(neighbor_edges)

    def build_neighbor_condition(self, edges):
        if len(edges) == 2:
            self.build_two_neighbor(edges)
        elif len(edges) == 3:
            self.build_three_neighbor(edges)
        elif len(edges) == 4:
            self.build_four_neighbor(edges)
        else:
            raise ValueError

    def build_two_neighbor(self, edges):
        e1 = edges[0]
        e2 = edges[1]
        self.cond.append([-e1, e2])
        self.cond.append([e1, -e2])

    def build_three_neighbor(self, edges):
        e1 = edges[0]
        e2 = edges[1]
        e3 = edges[2]
        self.cond.append([-e1, e2, e3])
        self.cond.append([e1, -e2, e3])
        self.cond.append([e1, e2, -e3])
        self.cond.append([-e1, -e2, -e3])

    def build_four_neighbor(self, edges):
        e1 = edges[0]
        e2 = edges[1]
        e3 = edges[2]
        e4 = edges[3]
        self.cond.append([-e1, -e2, -e3])
        self.cond.append([-e1, -e2, -e4])
        self.cond.append([-e1, -e3, -e4])
        self.cond.append([-e2, -e3, -e4])
        self.cond.append([-e1, e2, e3, e4])
        self.cond.append([e1, -e2, e3, e4])
        self.cond.append([e1, e2, -e3, e4])
        self.cond.append([e1, e2, e3, -e4])

    def build_cond(self):
        self.build_neighbor_rule()
        self.build_cell_rule()

    def solve(self):
        self.build_cond()
        self.num_loops = 1
        for cond in self.cond:
            self.solver.add_clause(cond)
        self.base_cond = [x for x in self.cond]
        self.result = self.solver.solve()
        self.model = self.solver.get_model()
        self.model_arr.append(self.model)
        self.loop_solve();

    def loop_solve(self):
        while self.result and self.has_multi_loops():
            if len(self.list_nums) == 0:
                self.result = True
                self.model = self.list_loops[0]
                return

            for curr_loop in self.list_loops:
                self.solver.add_clause([-i for i in curr_loop])
                self.cond.append([-i for i in curr_loop])

            self.num_loops += 1
            self.result = self.solver.solve()
            self.model = self.solver.get_model()
            self.model_arr.append(self.model)

    def has_multi_loops(self):
        self.list_loops = []
        self.edges = {i for i in self.model if i > 0}
        first_edge = self.edges.pop()
        curr_loop = [first_edge]
        x, y = self.converter.get_vertice(first_edge)

        while len(self.edges) > 0:
            is_continue = True
            neighbor_edges = self.converter.get_neighbor_edges(x, y)
            for neighbor_edge in neighbor_edges:
                if neighbor_edge in self.edges:
                    self.edges.remove(neighbor_edge)
                    curr_loop.append(neighbor_edge)
                    x, y = self.converter.get_next_vertice(x, y, neighbor_edge)
                    is_continue = False
                    break
            if is_continue:
                self.list_loops.append(curr_loop)
                if len(self.edges) > 0:
                    first_edge = self.edges.pop()
                    curr_loop = [first_edge]
                    x, y = self.converter.get_vertice(first_edge)

        self.list_loops.append(curr_loop)
        if len(self.list_loops) == 1:
            return False
        return True

    def show_result(self):
        if self.result:
            print("Result: SAT")
            print([i for i in self.model if i > 0])
        else:
            print("Result: UNSAT")

if __name__ == "__main__":
    solver = SlitherLinkAddAllLoop(Minisat22)
    solver.load_from_file("puzzle/puzzle_50x40_1.txt")
    start_time = time.time()
    solver.solve()
    end_time = time.time()
    solver.show_result()
    print(end_time - start_time)
