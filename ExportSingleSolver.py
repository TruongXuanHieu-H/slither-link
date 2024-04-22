import glob
import time
import os

import pandas as pd
from openpyxl import load_workbook
from pysat.solvers import Minisat22

from SlitherLinkAddAllLoop import SlitherLinkAddAllLoop
from SlitherLinkAddAllLoopWithEmpty import SlitherLinkAddAllLoopWithEmpty

test_folder = glob.glob("puzzle/*.txt", recursive=True)
number_solve_per_test = 10

first_solver_base_condition = []
first_solver_total_condition = []
first_solver_loop_count = []
first_solver_encode_time_elapse = []
first_solver_solve_time_elapsed = []
first_solver_time_elapsed = []


def get_first_solver():
    return SlitherLinkAddAllLoopWithEmpty(get_first_solver_params())


def get_first_solver_params():
    return Minisat22


def process(solver, solver_params, file_name, base_condition, total_condition, loop_count, encode_time_elapsed,
            solve_time_elapsed, time_elapsed):
    base_condition_list = []
    total_condition_list = []
    loop_count_list = []
    encode_time_elapsed_list = []
    solve_time_elapsed_list = []
    time_elapsed_list = []

    for i in range(number_solve_per_test):
        solver_instance = type(solver)(solver_params)

        start_encode_time = time.perf_counter()
        solver_instance.load_from_file(file_name)
        end_encode_time = time.perf_counter()

        start_solve_time = time.perf_counter()
        solver_instance.solve()
        end_solve_time = time.perf_counter()

        base_condition_list.append(len(solver_instance.base_cond))
        total_condition_list.append(len(solver_instance.cond))
        loop_count_list.append(solver_instance.num_loops)
        encode_time_elapsed_list.append(end_encode_time - start_encode_time)
        solve_time_elapsed_list.append(end_solve_time - start_solve_time)
        time_elapsed_list.append(encode_time_elapsed_list[-1] + solve_time_elapsed_list[-1])

    base_condition.append(sum(base_condition_list) / number_solve_per_test)
    total_condition.append(sum(total_condition_list) / number_solve_per_test)
    loop_count.append(sum(loop_count_list) / number_solve_per_test)
    encode_time_elapsed.append(sum(encode_time_elapsed_list) / number_solve_per_test)
    solve_time_elapsed.append(sum(solve_time_elapsed_list) / number_solve_per_test)
    time_elapsed.append(sum(time_elapsed_list) / number_solve_per_test)


for file_path in test_folder:
    print(f"{get_first_solver().__class__.__name__} - {file_path}")
    process(get_first_solver(), get_first_solver_params(), file_path,
            first_solver_base_condition, first_solver_total_condition,
            first_solver_loop_count, first_solver_encode_time_elapse,
            first_solver_solve_time_elapsed, first_solver_time_elapsed)

first_solver_base_condition.append(sum(first_solver_base_condition))
first_solver_total_condition.append(sum(first_solver_total_condition))
first_solver_loop_count.append(sum(first_solver_loop_count))
first_solver_encode_time_elapse.append(sum(first_solver_encode_time_elapse))
first_solver_solve_time_elapsed.append(sum(first_solver_solve_time_elapsed))
first_solver_time_elapsed.append(sum(first_solver_time_elapsed))

test_folder.append('total')

data = pd.DataFrame({"file_test": test_folder,
                     "base_condition": first_solver_base_condition,
                     "total_condition": first_solver_total_condition,
                     "loop_count": first_solver_loop_count,
                     "encode_time_elapse (ms)": first_solver_encode_time_elapse,
                     "solve_time_elapsed (ms)": first_solver_solve_time_elapsed,
                     "time_elapsed (ms)": first_solver_time_elapsed})


def df_style(x):
    return 'font-weight: bold'


output_file = (f"output/{get_first_solver().__class__.__name__} - "
               f"x{number_solve_per_test} - "
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

os.startfile(f"{os.getcwd()}/{output_file}")
