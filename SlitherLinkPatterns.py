from pysat.solvers import Minisat22
import time

from SlitherLinkAddAllLoopWithEmpty import SlitherLinkAddAllLoopWithEmpty


class SlitherLinkPatterns(SlitherLinkAddAllLoopWithEmpty):
    def build_heuristic(self):
        super().build_heuristic()
        self.build_patterns()

    def build_patterns(self):
        self.build_pattern_3_in_corners()
        # self.build_pattern_3_cross_3()
        # self.build_pattern_3_adjacent_0()

    def build_pattern_3_in_corners(self):
        if self.board[0, 0] == 3:
            edges = self.converter.get_side_edges(0, 0)
            self.cond.append([edges[0]])
            self.cond.append([edges[2]])
        if self.board[0, self.board_col - 1] == 3:
            edges = self.converter.get_side_edges(0, self.board_col - 1)
            self.cond.append([edges[0]])
            self.cond.append([edges[3]])
        if self.board[self.board_row - 1, 0] == 3:
            edges = self.converter.get_side_edges(self.board_row - 1, 0)
            self.cond.append([edges[1]])
            self.cond.append([edges[2]])
        if self.board[self.board_row - 1, self.board_col - 1] == 3:
            edges = self.converter.get_side_edges(self.board_row - 1, self.board_col - 1)
            self.cond.append([edges[1]])
            self.cond.append([edges[3]])

    def build_pattern_3_cross_3(self):
        for cell_3 in self.list_cell_3:
            if cell_3[0] < self.board_row - 1:
                if cell_3[1] < self.board_col - 1:
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
                            or (cell_3[0] == self.board_row - 1 and neighbor[0] == self.board_row - 1)
                            or (cell_3[1] == 0 and neighbor[1] == 0)
                            or (cell_3[1] == self.board_col - 1 and neighbor[1] == self.board_col - 1)):
                        edges_3_0 = self.converter.get_side_edges(cell_3[0], cell_3[1])
                        edges_0_0 = self.converter.get_side_edges(neighbor[0], neighbor[1])
                        edge_adjacent_0 = list(set(edges_3_0) & set(edges_0_0))
                        edges_3_encode_0 = list(set(edges_3_0) ^ set(edge_adjacent_0))
                        edges_3_encode_0.append(edge_adjacent_0[0] - 1)
                        edges_3_encode_0.append(edge_adjacent_0[0] + 1)
                        for edge in edges_3_encode_0:
                            self.cond.append([edge])


if __name__ == "__main__":
    solver = SlitherLinkPatterns(Minisat22)
    solver.load_from_file("puzzle/test_3_adjacent_0.txt")
    start_time = time.time()
    solver.solve()
    end_time = time.time()
    solver.show_result()
    print(end_time - start_time)
