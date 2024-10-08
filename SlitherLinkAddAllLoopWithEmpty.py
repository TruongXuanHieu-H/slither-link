import numpy as np
import converter_2
from pysat.solvers import Minisat22
import time

from SlitherLinkAddAllLoop import  SlitherLinkAddAllLoop


class SlitherLinkAddAllLoopWithEmpty(SlitherLinkAddAllLoop):
    def __init__(self, sat_solver):
        super().__init__(sat_solver)
        self.list_cell_empty = []
        self.list_cell_0 = []
        self.list_cell_1 = []
        self.list_cell_2 = []
        self.list_cell_3 = []

    def load_from_file(self, filename):
        super().load_from_file(filename)
        for i in range(self.board_row):
            for j in range(self.board_col):
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

    def build_heuristic(self):
        self.build_special_loops()

    def build_special_loops(self):
        self.build_empty_single_cell()
        self.build_empty_single_cell_adjacent_3()
        self.build_empty_couple_cells()
        # self.build_double_cells_3()

    def build_empty_single_cell(self):
        for emptyCell in self.list_cell_empty:
            edges = self.converter.get_side_edges(emptyCell[0], emptyCell[1])
            self.cond.append([-edges[0], -edges[1], -edges[2], -edges[3]])

    def build_empty_single_cell_adjacent_3(self):
        for emptyCell in self.list_cell_empty:
            neighbors = self.converter.get_neighbor_cells_of_cell(emptyCell)
            for neighbor in neighbors:
                if self.board[neighbor[0], neighbor[1]] == 3:
                    cellEdges = self.converter.get_side_edges(emptyCell[0], emptyCell[1])
                    neighborEdges = self.converter.get_side_edges(neighbor[0], neighbor[1])
                    borders = list(set(cellEdges) ^ set(neighborEdges))
                    self.cond.append([-border for border in borders])

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

    def build_double_cells_3(self):
        for cell_3 in self.list_cell_3:
            neighbors = self.converter.get_neighbor_cells_of_cell(cell_3)
            coupleNeighbors = list(
                neighbor for neighbor in neighbors if neighbor[0] >= cell_3[0] and neighbor[1] >= cell_3[1])
            for coupleNeighbor in coupleNeighbors:
                neighborValue = self.board[coupleNeighbor[0], coupleNeighbor[1]]
                if neighborValue == -1:
                    cellEdges = self.converter.get_side_edges(cell_3[0], cell_3[1])
                    neighborEdges = self.converter.get_side_edges(coupleNeighbor[0], coupleNeighbor[1])
                    borders = list(set(cellEdges) ^ set(neighborEdges))  # Guarantee 6 elements
                    self.cond.append([-border for border in borders])

    def build_cond(self):
        super().build_cond()
        self.build_heuristic()


if __name__ == "__main__":
    solver = SlitherLinkAddAllLoopWithEmpty(Minisat22)
    solver.load_from_file("puzzle/50x40_1.txt")
    start_time = time.time()
    solver.solve()
    end_time = time.time()
    solver.show_result()
    print(end_time - start_time)
