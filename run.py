import sys
import time
import logging
import pandas as pd
import pymzn
import multiprocessing
import write_mzn
from schedule import DAYS_OF_WEEK, SLOTS_PER_DAY, SLOTS_PER_WEEK
from util import *
from parse_input import load_dir_files

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

dir_files = sys.argv[1]

schedule, general_constraint, teacher_constraint = load_dir_files(dir_files)

week = str(sys.argv[2])
week_schedule = schedule.loc[schedule[WEEK] == week].reset_index(drop='index').copy()
assert len(week_schedule) > 0

time_to_run = int(sys.argv[3])
time_to_run *= SECONDS_IN_MINUTE

if time_to_run == -1:
    time_to_run = None

cores = int(sys.argv[4])

machine_cores = multiprocessing.cpu_count()
if cores == -1:
    cores = multiprocessing.cpu_count()
elif machine_cores < cores:
    cores = machine_cores

write_mzn.write_file(week_schedule, general_constraint, teacher_constraint)

start_time = time.time()

LOG.info('Started optimizing the schedule.')
solution = pymzn.minizinc('test_file.mzn', data={'turnos': SLOTS_PER_WEEK}, timeout=time_to_run, parallel=cores)
LOG.info('Finished the optimization.')

final_time = time.time()
running_time = final_time - start_time

LOG.info('Process finished in {} minutes.'.format(int(running_time / SECONDS_IN_MINUTE)))

solved_ids_bitmap = solution[0]
groups = set(schedule['Grupo'])
groups_schedule = dict()
schedule_base = pd.read_excel('input/horario_base.xlsx')

for group in groups:
    groups_schedule[group] = schedule_base.copy()

for key, bit_map in solved_ids_bitmap.items():
    group_id, subject, order = key.split('_')
    year, group_number = int(group_id[-2]), int(group_id[-1])
    pos_in_bitmap = bit_map.index(1)
    day = DAYS_OF_WEEK[pos_in_bitmap // SLOTS_PER_DAY]
    slot = pos_in_bitmap % SLOTS_PER_DAY
    groups_schedule[group_id][day][slot + 1] = subject + ' (' + \
                                               schedule.loc[(schedule[GROUP] == group_id) &
                                                            (schedule[SUBJECT] == subject) &
                                                            (schedule[ORDER] == order)].Tipo.values[0] + \
                                               ')'

for group, group_schedule in groups_schedule.items():
    group_schedule.to_excel('output/' + str(group) + '.xlsx')
