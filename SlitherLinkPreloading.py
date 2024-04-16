import numpy as np
import converter_2
from pysat.solvers import Minisat22
import time


class SlitherLinkPreloading():
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
        self.result_array = None
        self.row = None
        self.solver = solver()

    def load_from_file(self, filename):
        with open(filename) as f:
            self.row, self.col = map(int, f.readline().split())
            self.board = -np.ones(self.row * self.col, dtype=np.int32).reshape(self.row, self.col)
            while line := f.readline():
                x, y, k = map(int, line.split())
                self.board[x - 1, y - 1] = k
                if k == 2:
                    self.list_nums.append((x-1, y-1))
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
        self.loop_solve()

    def loop_solve(self):
        while self.result and self.loop_count != 1:
            self.num_loops += 1
            self.result = self.solver.solve()
            self.model = self.solver.get_model()
            self.model_arr.append(self.model)

    @property
    def loop_count(self):
        edges = {i for i in self.model if i > 0}
        clone_edges = {i for i in self.model if i > 0}
        visited_edges = {}

        def bfs(edge, count):
            queue = [edge]
            while len(queue) > 0:
                x = queue.pop()
                visited_edges[x] = count
                u = self.converter.get_two_vertices(x)
                neighbor_edges_1 = self.converter.get_neighbor_edges(u[0], u[1])
                neighbor_edges_2 = self.converter.get_neighbor_edges(u[2], u[3])
                for neighbor_edge in neighbor_edges_1 + neighbor_edges_2:
                    if neighbor_edge not in visited_edges and neighbor_edge in clone_edges:
                        queue.append(neighbor_edge)
                        clone_edges.remove(neighbor_edge)

        count = 0
        while len(clone_edges) > 0:
            edge = clone_edges.pop()
            if edge not in visited_edges:
                bfs(edge, count)
                count += 1

        if count == 1:
            return 1

        visited_cnt = []
        cnt_added = {}
        save = {}

        for i in range(count):
            cnt_added[i] = 0
            visited_cnt.append({x for x in edges if visited_edges[x] == i})
            save[i] = []

        for cell in self.list_nums:
            i, j = cell
            side_edges = self.converter.get_side_edges(i, j)
            val_edge = list({visited_edges[edge] for edge in side_edges if edge in visited_edges})
            if len(val_edge) == 2:
                cnt_added[val_edge[0]] += 1
                cnt_added[val_edge[1]] += 1
                save[val_edge[0]].append(val_edge[1])
                save[val_edge[1]].append(val_edge[0])

        for x in range(count):
            if cnt_added[x] == 0:
                self.solver.add_clause([-i for i in visited_cnt[x]])
                # self.cond.append([-i for i in visited_cnt[x]])
        sorted_cnt_added = sorted(cnt_added.items(), key=lambda l: (len(visited_cnt[l[0]]), -l[1]))
        for sorted_cnt_item in sorted_cnt_added:
            loop = sorted_cnt_item[0]
            if cnt_added[loop] == 0:
                continue

            for x in save[loop]:
                cnt_added[x] -= 1

            self.solver.add_clause([-i for i in visited_cnt[loop]])
            # self.cond.append([-i for i in visited_cnt[loop]])
        return count

    def show_result(self):
        if self.result:
            print("Result: SAT")
            print([i for i in self.model if i > 0])
        else:
            print("Result: UNSAT")

if __name__ == "__main__":
    solver = SlitherLinkPreloading(Minisat22)
    solver.load_from_file("puzzle/7x7_13.txt")
    start_time = time.time()
    solver.solve()
    end_time = time.time()
    solver.show_result()
    print(end_time - start_time)
