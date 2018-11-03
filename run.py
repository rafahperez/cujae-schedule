import sys
import pandas as pd
import pymzn
import argparse
from write_mzn import write_mzn_file
from xml_reader import xml_to_dataframe, read_general_constraints, read_teacher_constraints


schedule = xml_to_dataframe(sys.argv[1], sys.argv[2], sys.argv[3])
general_constraints = read_general_constraints(sys.argv[4])
teacher_constraints = read_teacher_constraints(sys.argv[5])
# Create the mzn file
write_mzn_file(schedule, general_constraints, teacher_constraints)

days_of_the_week = {0: 'Lunes', 1: 'Martes', 2: 'Miercoles', 3: 'Jueves', 4: 'Viernes'}
solution = pymzn.minizinc('test_file.mzn', data={'turnos': 30})
solved_ids_bitmap = solution[0]

print('GROUPS SCHEDULES')

groups = set(schedule['Grupo'])
groups_schedule = dict()
schedule_base = pd.read_excel('input/horario_base.xlsx')

for group in groups:
    groups_schedule[group] = schedule_base.copy()

for key, bit_map in solved_ids_bitmap.items():
    group_id, subject, order = key.split('_')
    year, group_number = int(group_id[-2]), int(group_id[-1])
    pos_in_bitmap = bit_map.index(1)
    day = days_of_the_week[pos_in_bitmap // 6]
    turn = pos_in_bitmap % 6
    groups_schedule[group_id][day][turn + 1] = subject + '_' + order

for group, group_schedule in groups_schedule.items():
    group_schedule.to_excel('output/' + str(group) + '.xlsx')
