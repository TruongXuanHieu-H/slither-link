from SlitherLinkBase import SlitherLinkBase
from pysat.solvers import Minisat22
import time

class SlitherLinkOrigin(SlitherLinkBase):
    def loop_solve(self):
        while self.result and self.has_multi_loops():
            if len(self.list_nums) == 0:
                self.result = True
                self.model = self.list_loops[0]
                return

            valid_loops = []

            for curr_loop in self.list_loops:
                list_nums = set(self.list_nums)
                for edge in curr_loop:
                    neighbor_cells = self.converter.get_neighbor_cells(edge)
                    for cell in neighbor_cells:
                        if cell in list_nums:
                            is_side_cell = True
                            list_nums.remove(cell)
                if len(list_nums) > 0:
                    self.solver.add_clause([-i for i in curr_loop])
                    self.cond.append([-i for i in curr_loop])
                else:
                    valid_loops.append(curr_loop)

            if len(valid_loops) > 1:
                for curr_loop in valid_loops:
                    self.solver.add_clause([-i for i in curr_loop])
                    self.cond.append([-i for i in curr_loop])

            self.num_loops += 1
            self.result = self.solver.solve()
            self.model = self.solver.get_model()
            self.model_arr.append(self.model)
        pass

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

if __name__ == "__main__":
    solver = SlitherLinkOrigin(Minisat22)
    solver.load_from_file("puzzle/puzzle_50x40_1.txt")
    start_time = time.time()
    solver.solve()
    end_time = time.time()
    solver.show_result()
    print(end_time - start_time)