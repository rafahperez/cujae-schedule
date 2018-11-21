import pandas as pd
from util import *
from schedule import DAYS_OF_WEEK, SLOTS_PER_DAY


def create_excels(schedule, bitmaps):
    groups = set(schedule['Grupo'])
    groups_schedule = dict()
    schedule_base = pd.read_excel('input/horario_base.xlsx')

    for group in groups:
        groups_schedule[group] = schedule_base.copy()

    for key, bit_map in bitmaps.items():
        group_id, subject, order = key.split('_')
        year, group_number = int(group_id[-2]), int(group_id[-1])
        pos_in_bitmap = bit_map.index(1)
        day = DAYS_OF_WEEK[pos_in_bitmap // SLOTS_PER_DAY]
        slot = pos_in_bitmap % SLOTS_PER_DAY
        groups_schedule[group_id][day][slot + 1] = subject + ' (' + schedule.loc[(schedule[GROUP] == group_id) &
                                                                                 (schedule[SUBJECT] == subject) &
                                                                                 (schedule[ORDER] == order)].Tipo.values[0] + ')'

    for group, group_schedule in groups_schedule.items():
        group_schedule.to_excel('output/' + str(group) + '.xlsx')