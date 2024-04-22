import numpy as np
import converter_2
from pysat.solvers import Minisat22
import time


class SlitherLinkPatterns:
    def __init__(self, sat_solver):
        self.base_cond = []
        self.board = None
        self.col = None
        self.cond = []
        self.converter = None
        self.edges = None
        self.list_cell_empty = []
        self.list_cell_0 = []
        self.list_cell_1 = []
        self.list_cell_2 = []
        self.list_cell_3 = []
        self.list_loops = None
        self.list_nums = []
        self.model = None
        self.model_arr = []
        self.num_loops = 1
        self.result = None
        self.row = None
        self.solver = sat_solver()

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
                    self.list_nums.append((i - 1, j - 1))
        for i in range(self.row):
            for j in range(self.col):
                if self.board[i, j] == -1:
                    self.list_cell_empty.append((i, j))
                elif self.board[i, j] == 0:
                    self.list_cell_0.append((i, j))
                elif self.board[i, j] == 1:
                    self.list_cell_1.append((i, j))
                elif self.board[i, j] == 2:
                    self.list_cell_2.append((i, j))
                elif self.board[i, j] == 3:
                    self.list_cell_3.append((i, j))
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

    def build_heuristic(self):
        # self.build_empty_cells()
        self.build_patterns()

    def build_empty_cells(self):
        self.build_empty_single_cell()
        self.build_empty_couple_cells()

    def build_empty_single_cell(self):
        for emptyCell in self.list_cell_empty:
            neighbors = self.converter.get_neighbor_cells_of_cell(emptyCell)
            neighborValues = [self.board[x, y] for x, y in neighbors]
            if all(neighborValue == -1 for neighborValue in neighborValues):
                edges = self.converter.get_side_edges(emptyCell[0], emptyCell[1])
                self.cond.append([-edges[0], -edges[1], -edges[2], -edges[3]])

    def build_empty_couple_cells(self):
        for emptyCell in self.list_cell_empty:
            neighbors = self.converter.get_neighbor_cells_of_cell(emptyCell)
            coupleNeighbors = list(
                neighbor for neighbor in neighbors if neighbor[0] >= emptyCell[0] and neighbor[1] >= emptyCell[1])
            for coupleNeighbor in coupleNeighbors:
                neighborValue = self.board[coupleNeighbor[0], coupleNeighbor[1]]
                if neighborValue == -1:
                    cellEdges = self.converter.get_side_edges(emptyCell[0], emptyCell[1])
                    neighborEdges = self.converter.get_side_edges(coupleNeighbor[0], coupleNeighbor[1])
                    borders = list(set(cellEdges) ^ set(neighborEdges))  # Guarantee 6 elements
                    self.cond.append([-border for border in borders])

    def build_patterns(self):
        self.build_pattern_3_in_corners()
        self.build_pattern_3_cross_3()
        self.build_pattern_3_adjacent_0()

    def build_pattern_3_in_corners(self):
        if self.board[0, 0] == 3:
            edges = self.converter.get_side_edges(0, 0)
            self.cond.append([edges[0], edges[2]])
        if self.board[0, self.col - 1] == 3:
            edges = self.converter.get_side_edges(0, self.col - 1)
            self.cond.append([edges[0], edges[3]])
        if self.board[self.row - 1, 0] == 3:
            edges = self.converter.get_side_edges(self.row - 1, 0)
            self.cond.append([edges[1], edges[2]])
        if self.board[self.row - 1, self.col - 1] == 3:
            edges = self.converter.get_side_edges(self.row - 1, self.col - 1)
            self.cond.append([edges[1], edges[3]])

    def build_pattern_3_cross_3(self):
        for cell_3 in self.list_cell_3:
            if cell_3[0] < self.row - 1:
                if cell_3[1] < self.col - 1:
                    cross_cell_3_up = [cell_3[0] + 1, cell_3[1] + 1]
                    if self.board[cross_cell_3_up[0], cross_cell_3_up[1]] == 3:
                        up_edges = self.converter.get_side_edges(cell_3[0], cell_3[1])
                        up_cross_edges = self.converter.get_side_edges(cross_cell_3_up[0], cross_cell_3_up[1])
                        self.cond.append([up_edges[0], up_edges[2], up_cross_edges[1], up_cross_edges[3]])
                if cell_3[1] > 0:
                    cross_cell_3_down = [cell_3[0] + 1, cell_3[1] - 1]
                    if self.board[cross_cell_3_down[0], cross_cell_3_down[1]] == 3:
                        down_edges = self.converter.get_side_edges(cell_3[0], cell_3[1])
                        down_cross_edges = self.converter.get_side_edges(cross_cell_3_down[0], cross_cell_3_down[1])
                        self.cond.append([down_edges[0], down_edges[3], down_cross_edges[1], down_cross_edges[2]])

    def build_pattern_3_adjacent_0(self):
        for cell_3 in self.list_cell_3:
            neighbors = self.converter.get_neighbor_cells_of_cell(cell_3)
            for neighbor in neighbors:
                if self.board[neighbor[0], neighbor[1]] == 0:
                    if not ((cell_3[0] == 0 and neighbor[0] == 0)
                            or (cell_3[0] == self.row - 1 and neighbor[0] == self.row - 1)
                            or (cell_3[1] == 0 and neighbor[1] == 0)
                            or (cell_3[1] == self.col - 1 and neighbor[1] == self.col - 1)):
                        edges_3 = self.converter.get_side_edges(cell_3[0], cell_3[1])
                        edges_0 = self.converter.get_side_edges(neighbor[0], neighbor[1])
                        edge_adjacent = list(set(edges_3) & set(edges_0))
                        edges_3_encode = list(set(edges_3) ^ set(edge_adjacent))
                        edges_3_encode.append(edge_adjacent[0] - 1)
                        edges_3_encode.append(edge_adjacent[0] + 1)
                        self.cond.append([edge for edge in edges_3_encode])

    def build_cond(self):
        self.build_neighbor_rule()
        self.build_cell_rule()
        self.build_heuristic()

    def solve(self):
        self.build_cond()
        self.num_loops = 1
        for cond in self.cond:
            self.solver.add_clause(cond)
        self.base_cond = [x for x in self.cond]
        self.result = self.solver.solve()
        self.model = self.solver.get_model()
        self.model_arr.append(self.model)
        if len(self.list_nums) > 0:
            self.loop_solve()

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
            print("Result: UN SAT")


if __name__ == "__main__":
    solver = SlitherLinkPatterns(Minisat22)
    solver.load_from_file("puzzle/test_3_adjacent_0.txt")
    start_time = time.time()
    solver.solve()
    end_time = time.time()
    solver.show_result()
    print(end_time - start_time)
