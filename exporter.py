import glob
import time

import pandas as pd
from openpyxl import load_workbook
from pysat.solvers import Minisat22

from SlitherLinkAddAllLoop import SlitherLinkAddAllLoop
from SlitherLinkAddAllLoopWithEmpty import SlitherLinkAddAllLoopWithEmpty

test_folder = glob.glob("puzzle/*.txt", recursive=True)

first_solver_base_condition = []
first_solver_total_condition = []
first_solver_loop_count = []
first_solver_encode_time_elapse = []
first_solver_solve_time_elapsed = []
first_solver_time_elapsed = []

second_solver_base_condition = []
second_solver_total_condition = []
second_solver_loop_count = []
second_solver_encode_time_elapse = []
second_solver_solve_time_elapsed = []
second_solver_time_elapsed = []


def get_first_solver():
    return SlitherLinkAddAllLoop(Minisat22)


def get_second_solver():
    return SlitherLinkAddAllLoopWithEmpty(Minisat22)


def process(solver, file_name, base_condition, total_condition, loop_count, encode_time_elapsed, solve_time_elapsed,
            time_elapsed):
    start_encode_time = time.perf_counter()
    solver.load_from_file(file_name)
    time_elapsed_encode = (time.perf_counter() - start_encode_time)
    start_solve_time = time.perf_counter()
    solver.solve()
    time_elapsed_solve = (time.perf_counter() - start_solve_time)
    base_condition.append(len(solver.base_cond))
    total_condition.append(len(solver.cond))
    loop_count.append(solver.num_loops)
    encode_time_elapsed.append(time_elapsed_encode)
    solve_time_elapsed.append(time_elapsed_solve)
    time_elapsed.append(time_elapsed_encode + time_elapsed_solve)
    return base_condition, total_condition, loop_count, encode_time_elapsed, solve_time_elapsed, time_elapsed


for file_path in test_folder:
    print(file_path)
    (first_solver_base_condition, first_solver_total_condition,
     first_solver_loop_count, first_solver_encode_time_elapse,
     first_solver_solve_time_elapsed, first_solver_time_elapsed) = process(
        get_first_solver(), file_path,
        first_solver_base_condition, first_solver_total_condition,
        first_solver_loop_count, first_solver_encode_time_elapse,
        first_solver_solve_time_elapsed, first_solver_time_elapsed)
    (second_solver_base_condition, second_solver_total_condition,
     second_solver_loop_count, second_solver_encode_time_elapse,
     second_solver_solve_time_elapsed, second_solver_time_elapsed) = process(
        get_second_solver(), file_path,
        second_solver_base_condition, second_solver_total_condition,
        second_solver_loop_count, second_solver_encode_time_elapse,
        second_solver_solve_time_elapsed, second_solver_time_elapsed)

first_solver_base_condition.append(sum(first_solver_base_condition))
first_solver_total_condition.append(sum(first_solver_total_condition))
first_solver_loop_count.append(sum(first_solver_loop_count))
first_solver_encode_time_elapse.append(sum(first_solver_encode_time_elapse))
first_solver_solve_time_elapsed.append(sum(first_solver_solve_time_elapsed))
first_solver_time_elapsed.append(sum(first_solver_time_elapsed))

second_solver_base_condition.append(sum(second_solver_base_condition))
second_solver_total_condition.append(sum(second_solver_total_condition))
second_solver_loop_count.append(sum(second_solver_loop_count))
second_solver_encode_time_elapse.append((sum(second_solver_encode_time_elapse)))
second_solver_solve_time_elapsed.append((sum(second_solver_solve_time_elapsed)))
second_solver_time_elapsed.append(sum(second_solver_time_elapsed))

test_folder.append('total')

data = pd.DataFrame({"file_test": test_folder,
                     "first_solver_base_condition": first_solver_base_condition,
                     "second_solver_base_condition": second_solver_base_condition,
                     "first_solver_total_condition": first_solver_total_condition,
                     "second_solver_total_condition": second_solver_total_condition,
                     "first_solver_loop_count": first_solver_loop_count,
                     "second_solver_loop_count": second_solver_loop_count,
                     "first_solver_encode_time_elapse": first_solver_encode_time_elapse,
                     "second_solver_encode_time_elapse": second_solver_encode_time_elapse,
                     "first_solver_solve_time_elapsed": first_solver_solve_time_elapsed,
                     "second_solver_solve_time_elapsed": second_solver_solve_time_elapsed,
                     "first_solver_time_elapsed": first_solver_time_elapsed,
                     "second_solver_time_elapsed": second_solver_time_elapsed})


def df_style(x):
    return 'font-weight: bold'


output_file = (f"{get_first_solver().__class__.__name__} VS "
               f"{get_second_solver().__class__.__name__} - "
               f"{time.strftime('%Y-%m-%d %H-%M-%S')}.xlsx")

last_row = pd.IndexSlice[data.index[-1], :]
writer = pd.ExcelWriter(output_file)
data.style.map(df_style, subset=last_row).to_excel(writer, sheet_name='sheet1', index=False, na_rep='NaN')

for column in data:
    column_length = max(data[column].astype(str).map(len).max(), len(column))
    col_idx = data.columns.get_loc(column)
    writer.sheets['sheet1'].set_column(col_idx, col_idx, column_length)

writer.close()

book = load_workbook(output_file)
sheet = book.active
sheet.freeze_panes = 'B2'
book.save(output_file)
