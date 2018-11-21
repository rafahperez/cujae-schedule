import time
import argparse
import logging
import pymzn
import multiprocessing
import minizinc
from schedule import SLOTS_PER_WEEK, WeekScheduler
from util import *
from parse_output import create_excels
from parse_input import load_dir_files

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

ap = argparse.ArgumentParser()
ap.add_argument('-w', '--week', required=True, help='Schedule week')
ap.add_argument('-c', '--config', required=True, help='Path to schedule config files')
ap.add_argument('-t', '--time', required=True, help='Optimization time in minutes')
ap.add_argument('-p', '--cores', required=True, help='Number of parallel threads')
args = ap.parse_args()

schedule, general_constraint, teacher_constraint = load_dir_files(args.config)

week = str(args.week)
week_schedule = schedule.loc[schedule[WEEK] == week].reset_index(drop='index').copy()
assert len(week_schedule) > 0

week_general_const = general_constraint.loc[general_constraint[WEEK] == week].reset_index(drop='index').copy()
week_teacher_const = teacher_constraint.loc[teacher_constraint[WEEK] == week].reset_index(drop='index').copy()

scheduler = WeekScheduler(week_schedule, week_general_const, week_teacher_const)

time_to_run = int(args.time)
time_to_run *= SECONDS_IN_MINUTE

if time_to_run == -1:
    time_to_run = None

cores = int(args.cores)

machine_cores = multiprocessing.cpu_count()
if cores == -1:
    cores = multiprocessing.cpu_count()
elif machine_cores < cores:
    cores = machine_cores

mw = minizinc.MinizincWriter(minizinc.CONSTRAINTS_FILE)
mw.write_file(scheduler)

start_time = time.time()

LOG.info('Started optimizing the schedule.')
solution = pymzn.minizinc(minizinc.CONSTRAINTS_FILE, data={'turnos': SLOTS_PER_WEEK}, timeout=time_to_run, parallel=cores)
LOG.info('Finished the optimization.')

final_time = time.time()
running_time = final_time - start_time

LOG.info('Process finished in {} minutes.'.format(int(running_time / SECONDS_IN_MINUTE)))

solved_ids_bitmap = solution[0]

create_excels(schedule, solved_ids_bitmap)
