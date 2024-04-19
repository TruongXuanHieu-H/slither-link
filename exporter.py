import glob
import time

import pandas as pd
from openpyxl import load_workbook
from pysat.solvers import Minisat22

import SlitherLinkAddAllLoop
import SlitherLinkAddAllLoopWithEmpty

test_folder = glob.glob("puzzle/*.txt", recursive=True)

all_loop_base_condition = []
all_loop_total_condition = []
all_loop_loop_count = []
all_loop_time_elapsed = []

all_loop_with_empty_base_condition = []
all_loop_with_empty_total_condition = []
all_loop_with_empty_loop_count = []
all_loop_with_empty_time_elapsed = []


def process(solver, file_path, base_condition, total_condition, loop_count, time_elapsed):
    solver.load_from_file(file_path)
    start_time_origin = time.perf_counter()
    solver.solve()
    time_elapsed_origin = (time.perf_counter() - start_time_origin)
    base_condition.append(len(solver.base_cond))
    total_condition.append(len(solver.cond))
    loop_count.append(solver.num_loops)
    time_elapsed.append(time_elapsed_origin)
    return base_condition, total_condition, loop_count, time_elapsed


for file_path in test_folder:
    print(file_path)
    print("add (add all loops)")
    (all_loop_base_condition, all_loop_total_condition,
     all_loop_loop_count, all_loop_time_elapsed) = process(
        SlitherLinkAddAllLoop.SlitherLinkAddAllLoop(Minisat22), file_path,
        all_loop_base_condition, all_loop_total_condition,
        all_loop_loop_count, all_loop_time_elapsed)
    print("add (add all loop with empty)")
    (all_loop_with_empty_base_condition, all_loop_with_empty_total_condition,
     all_loop_with_empty_loop_count, all_loop_with_empty_time_elapsed) = process(
        SlitherLinkAddAllLoopWithEmpty.SlitherLinkAddAllLoop(Minisat22), file_path,
        all_loop_with_empty_base_condition, all_loop_with_empty_total_condition,
        all_loop_with_empty_loop_count, all_loop_with_empty_time_elapsed)

all_loop_base_condition.append(sum(all_loop_base_condition))
all_loop_total_condition.append(sum(all_loop_total_condition))
all_loop_loop_count.append(sum(all_loop_loop_count))
all_loop_time_elapsed.append(sum(all_loop_time_elapsed))

all_loop_with_empty_base_condition.append(sum(all_loop_with_empty_base_condition))
all_loop_with_empty_total_condition.append(sum(all_loop_with_empty_total_condition))
all_loop_with_empty_loop_count.append(sum(all_loop_with_empty_loop_count))
all_loop_with_empty_time_elapsed.append(sum(all_loop_with_empty_time_elapsed))

test_folder.append('total')

data = pd.DataFrame({"file_test": test_folder,
                     "add_all_loop_base_condition": all_loop_base_condition,
                     "add_all_loop_with_empty_base_condition": all_loop_with_empty_base_condition,
                     "add_all_loop_total_condition": all_loop_total_condition,
                     "add_all_loop_with_empty_total_condition": all_loop_with_empty_total_condition,
                     "add_all_loop_loop_count": all_loop_loop_count,
                     "add_all_loop_with_empty_loop_count": all_loop_with_empty_loop_count,
                     "add_all_loop_time_elapsed": all_loop_time_elapsed,
                     "add_all_loop_with_empty_time_elapsed": all_loop_with_empty_time_elapsed})


def df_style(x):
    return 'font-weight: bold'


last_row = pd.IndexSlice[data.index[-1], :]
writer = pd.ExcelWriter('output.xlsx')
data.style.map(df_style, subset=last_row).to_excel(writer, sheet_name='sheet1', index=False, na_rep='NaN')

for column in data:
    column_length = max(data[column].astype(str).map(len).max(), len(column))
    col_idx = data.columns.get_loc(column)
    writer.sheets['sheet1'].set_column(col_idx, col_idx, column_length)

writer.close()

book = load_workbook('output.xlsx')
sheet = book.active
sheet.freeze_panes = 'B2'
book.save('output.xlsx')
