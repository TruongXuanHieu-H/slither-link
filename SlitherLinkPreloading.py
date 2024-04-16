from SlitherLinkBase import SlitherLinkBase
from pysat.solvers import Minisat22
import time


class SlitherLinkPreloading(SlitherLinkBase):
    def loop_solve(self):
        while self.result and self.loop_count != 1:
            self.num_loops += 1
            self.result = self.solver.solve()
            self.model = self.solver.get_model()
            self.model_arr.append(self.model)
        pass

    @property
    def loop_count(self):
        edges = {i for i in self.model if i > 0}
        clone_edges = {i for i in self.model if i > 0}
        visited = {}

        def bfs(x_0, cnt):
            queue = [x_0]
            while len(queue) > 0:
                x = queue.pop()
                visited[x] = cnt
                u = self.converter.get_two_vertices(x)
                neighbor_edges_1 = self.converter.get_neighbor_edges(u[0], u[1])
                neighbor_edges_2 = self.converter.get_neighbor_edges(u[2], u[3])
                for neighbor_edge in neighbor_edges_1 + neighbor_edges_2:
                    if neighbor_edge not in visited and neighbor_edge in clone_edges:
                        queue.append(neighbor_edge)
                        clone_edges.remove(neighbor_edge)

        count = 0
        while len(clone_edges) > 0:
            edge = clone_edges.pop()
            if edge not in visited:
                bfs(edge, count)
                count += 1

        if count == 1:
            return 1

        visited_cnt = []
        cnt_added = {}
        save = {}

        for i in range(count):
            cnt_added[i] = 0
            visited_cnt.append({x for x in edges if visited[x] == i})
            save[i] = []

        for cell in self.list_nums:
            i, j = cell
            side_edges = self.converter.get_side_edges(i, j)
            val_edge = list({visited[edge] for edge in side_edges if edge in visited})
            if len(val_edge) == 2:
                cnt_added[val_edge[0]] += 1
                cnt_added[val_edge[1]] += 1
                save[val_edge[0]].append(val_edge[1])
                save[val_edge[1]].append(val_edge[0])

        for x in range(count):
            if cnt_added[x] == 0:
                self.solver.add_clause([-i for i in visited_cnt[x]])
                # self.cond.append([-i for i in visited_cnt[x]])
        # print(cnt_added)
        g = sorted(cnt_added.items(), key=lambda l: (len(visited_cnt[l[0]]), -l[1]))
        # print(g)
        for y in g:
            loop = y[0]
            if cnt_added[loop] == 0:
                continue

            for x in save[loop]:
                cnt_added[x] -= 1

            self.solver.add_clause([-i for i in visited_cnt[loop]])
            # self.cond.append([-i for i in visited_cnt[loop]])
        return count


if __name__ == "__main__":
    solver = SlitherLinkPreloading(Minisat22)
    solver.load_from_file("puzzle/puzzle_50x40_1.txt")
    start_time = time.time()
    solver.solve()
    end_time = time.time()
    solver.show_result()
    print(end_time - start_time)
