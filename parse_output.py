import pandas as pd
import os
import datetime
from util import *
from schedule import DAYS_OF_WEEK, SLOTS_PER_DAY


def create_excels(scheduler, bitmaps, week):
    groups = set(scheduler.schedule[GROUP])
    groups_schedule = dict()
    schedule_base = pd.read_excel('input/horario_base.xlsx')

    for group in groups:
        groups_schedule[group] = schedule_base.copy()

    group_bitmaps = dict()
    classrooms_bitmaps = dict()
    for key, bit_map in bitmaps.items():
        if str(key).startswith('G'):
            group_bitmaps[key] = bit_map
        if str(key).startswith('A'):
            new_key = key[3:]
            if new_key in classrooms_bitmaps:
                classrooms_bitmaps[new_key] += [bit_map.index(1)]
            else:
                classrooms_bitmaps[new_key] = [bit_map.index(1)]
        else:
            continue

    classrooms_bitmaps = propagate_joins(scheduler, classrooms_bitmaps)

    for key, bit_map in group_bitmaps.items():
        group_id, subject, order = key.split('_')
        pos_in_bitmap = bit_map.index(1)
        pos_in_classroom = classrooms_bitmaps[key]
        classroom = scheduler.classrooms[ID][pos_in_classroom].tolist()
        day = DAYS_OF_WEEK[pos_in_bitmap // SLOTS_PER_DAY]
        slot = pos_in_bitmap % SLOTS_PER_DAY
        groups_schedule[group_id][day][slot + 1] = subject + ' (' + \
                                                   scheduler.schedule.loc[(scheduler.schedule[GROUP] == group_id)
                                                                          & (scheduler.schedule[SUBJECT] == subject)
                                                                          & (scheduler.schedule[ORDER] == order)].Tipo.values[0] + ')'

    now = datetime.datetime.now()
    dir_path = os.path.join(os.getcwd(), 'output')
    dir_path = os.path.join(dir_path, 'Week {} Generated {}'.format(week, now.strftime('%Y-%m-%d %H:%M')))
    os.makedirs(dir_path)
    os.chdir(dir_path)

    for group, group_schedule in groups_schedule.items():
        group_schedule.to_excel(str(group) + '.xlsx')


def propagate_joins(scheduler, classrooms_bitmaps):
    join = dict(scheduler.groups_to_join())
    final_join = dict()

    for g1, g2 in join.items():
        done = False
        looking = g2
        while not done:
            if looking in join:
                looking = join[looking]
            else:
                done = True
        final_join[g1] = looking

    for g1, g2 in final_join.items():
        classrooms_bitmaps[g1] = classrooms_bitmaps[g2]

    return classrooms_bitmaps
