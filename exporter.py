import glob
import time

import pandas as pd
from pysat.solvers import Minisat22

import SlitherLinkAddAllLoop
import SlitherLinkOrigin
import SlitherLinkPreloading

test_folder = glob.glob("puzzle/*.txt", recursive=True)

all_loop_base_condition = []
all_loop_total_condition = []
all_loop_loop_count = []
all_loop_time_elapsed = []

origin_base_condition = []
origin_total_condition = []
origin_loop_count = []
origin_time_elapsed = []

my_base_condition = []
my_total_condition = []
my_loop_count = []
my_time_elapsed = []


def process(solver, file, base_condition, total_condition, loop_count, time_elapsed):
    solver.load_from_file(file)
    start_time_origin = time.perf_counter()
    solver.solve()
    time_elapsed_origin = (time.perf_counter() - start_time_origin)
    base_condition.append(len(solver.base_cond))
    total_condition.append(len(solver.cond))
    loop_count.append(solver.num_loops)
    time_elapsed.append(time_elapsed_origin)
    return base_condition, total_condition, loop_count, time_elapsed


for file in test_folder:
    print(file)
    print("add (add all loops)")
    all_loop_base_condition, all_loop_total_condition, all_loop_loop_count, all_loop_time_elapsed = process(
        SlitherLinkAddAllLoop.SlitherLinkAddAllLoop(Minisat22), file, all_loop_base_condition,
        all_loop_total_condition,
        all_loop_loop_count, all_loop_time_elapsed)
    print("add my")
    my_base_condition, my_total_condition, my_loop_count, my_time_elapsed = process(
        SlitherLinkPreloading.SlitherLinkPreloading(Minisat22), file, my_base_condition, my_total_condition,
        my_loop_count, my_time_elapsed)
    print("add origin")
    origin_base_condition, origin_total_condition, origin_loop_count, origin_time_elapsed = process(
        SlitherLinkOrigin.SlitherLinkOrigin(Minisat22), file, origin_base_condition,
        origin_total_condition,
        origin_loop_count, origin_time_elapsed)

all_loop_base_condition.append(sum(all_loop_base_condition))
all_loop_total_condition.append(sum(all_loop_total_condition))
all_loop_loop_count.append(sum(all_loop_loop_count))
all_loop_time_elapsed.append(sum(all_loop_time_elapsed))

my_base_condition.append(sum(my_base_condition))
my_total_condition.append(sum(my_total_condition))
my_loop_count.append(sum(my_loop_count))
my_time_elapsed.append(sum(my_time_elapsed))

origin_base_condition.append(sum(origin_base_condition))
origin_total_condition.append(sum(origin_total_condition))
origin_loop_count.append(sum(origin_loop_count))
origin_time_elapsed.append(sum(origin_time_elapsed))

test_folder.append('total')
#print(len(test_folder), len(add_all_loop_base_condition))

data = pd.DataFrame({"file_test": test_folder,
                     "add_all_loop_base_condition": all_loop_base_condition, "origin_base_condition": origin_base_condition, "my_base_condition": my_base_condition,
                     "add_all_loop_total_condition": all_loop_total_condition, "origin_total_condition": origin_total_condition, "my_total_condition": my_total_condition,
                     "add_all_loop_loop_count": all_loop_loop_count, "origin_loop_count": origin_loop_count, "my_loop_count": my_loop_count,
                     "add_all_loop_time_elapsed": all_loop_time_elapsed, "origin_time_elapsed": origin_time_elapsed, "my_time_elapsed": my_time_elapsed})

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