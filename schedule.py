import pandas as pd
from util import *

AFTERNOON_CLOSED = [4, 5, 6, 10, 11, 12, 16, 17, 18, 22, 23, 24, 28, 29, 30]
MORNING_CLOSED = [1, 2, 3, 7, 8, 9, 13, 14, 15, 19, 20, 21, 25, 26, 27]
BREAK_INDEX = [(3, 4), (9, 10), (15, 16), (21, 22), (27, 28)]

STANDARD_WEEK_SLOTS = 15
SLOTS_PER_WEEK = 30
SLOTS_PER_DAY = 6
MORNING_SESSION = 'm'
DAYS_OF_WEEK = {0: 'Lunes', 1: 'Martes', 2: 'Miercoles', 3: 'Jueves', 4: 'Viernes'}


class WeekScheduler:

    def __init__(self, schedule, general_constraint, teacher_constraint):
        self.schedule = schedule
        self.general_constraint = general_constraint
        self.teacher_constraint = teacher_constraint

    def get_unique_groups(self):
        return pd.unique(self.schedule[GROUP])

    def get_bit_maps(self):
        return [self.schedule.loc[i][GROUP] + '_' + self.schedule.loc[i][SUBJECT] + '_' +
                self.schedule.loc[i][ORDER] for i in self.schedule.index]

    def create_bit_maps_per_year(self):
        return [self.create_bit_maps_ids_given_year(str(year)) for year in range(1, 6)]

    def create_bit_maps_per_group(self):
        bit_maps = list()
        for year in self.schedule.groupby([YEAR]).count().index:
            for group in self.schedule.loc[self.schedule[YEAR] == year].groupby([GROUP]).count().index:
                bit_maps.append((year, group, self.create_bit_maps_ids(self.schedule.loc[self.schedule[GROUP] == group])))
        return bit_maps

    def create_bit_maps_ids(self, schedule_data):
        return [schedule_data.loc[i][GROUP] + '_' + schedule_data.loc[i][SUBJECT] + '_' +
                schedule_data.loc[i][ORDER] for i in schedule_data.index]

    def create_bit_maps_ids_given_year(self, year):
        return [self.schedule.loc[i][GROUP] + '_' + self.schedule.loc[i][SUBJECT] + '_' +
                self.schedule.loc[i][ORDER] for i in self.schedule.loc[self.schedule[YEAR].astype(object) == year].index]

    def get_bit_maps_given_teacher(self, teacher):
        arr = list()
        for i in self.schedule.index:
            if teacher in self.schedule.loc[i][TEACHER].split(','):
                arr.append(self.schedule.loc[i][GROUP] + '_' + self.schedule.loc[i][SUBJECT] + '_' +
                           self.schedule.loc[i][ORDER])

        return arr

    def get_bit_maps_given_group(self, group):
        arr = list()
        for i in self.schedule.index:
            if group == self.schedule.loc[i][GROUP]:
                arr.append(self.schedule.loc[i][GROUP] + '_' + self.schedule.loc[i][SUBJECT] + '_' +
                           self.schedule.loc[i][ORDER])

        return arr

    def create_bit_maps_ids_given_session(self, session):
        return [self.schedule.loc[i][GROUP] + '_' + self.schedule.loc[i][SUBJECT] + '_' +
                self.schedule.loc[i][ORDER] for i in self.schedule.loc[self.schedule[SESSION] == session].index]

    def index_general_constraints(self):
        return [int(self.general_constraint.loc[i][DAY]) * 6 + int(self.general_constraint.loc[i][SLOT])
                for i in self.general_constraint.loc[self.general_constraint[YEAR] == '-'].index]

    def index_general_constraints_per_years(self):
        return [self.index_general_constraints_given_year(str(year)) for year in range(1, 6)]

    def index_general_constraints_given_year(self, year):
        return [int(self.general_constraint.loc[i][DAY]) * 6 + int(self.general_constraint.loc[i][SLOT])
                for i in self.general_constraint.loc[self.general_constraint[YEAR] == year].index]

    def get_index_constraints_given_teacher(self, teacher):
        return [int(self.teacher_constraint.loc[i][DAY]) * 6 + int(self.teacher_constraint.loc[i][SLOT])
                for i in self.teacher_constraint.loc[self.teacher_constraint[TEACHER] == teacher].index]

    def groups_to_join(self):
        groups_to_join_ids = list()
        for i in self.schedule.index:
            if self.schedule.loc[i][JOIN] != '-':
                ids = self.schedule.loc[i][GROUP] + '_' + self.schedule.loc[i][SUBJECT] + '_' + self.schedule.loc[i][
                    ORDER], \
                      self.schedule.loc[i][JOIN] + '_' + self.schedule.loc[i][SUBJECT] + '_' + self.schedule.loc[i][
                          ORDER]
                groups_to_join_ids.append(ids)
        return groups_to_join_ids

    def groups_constraint_by_teacher(self, teacher):
        arr = list()
        for i in self.schedule.index:
            if (teacher in self.schedule.loc[i][TEACHER].split(',')) & (self.schedule.loc[i][JOIN] == '-'):
                arr.append(self.schedule.loc[i][GROUP] + '_' + self.schedule.loc[i][SUBJECT] + '_' + self.schedule.loc[i][ORDER])

        return arr

    def get_teacher_list(self):
        arr = list()
        for i in self.schedule.index:
            arr.extend(self.schedule.loc[i][TEACHER].split(','))
        return pd.unique(arr)

    def groups_with_teacher_constraint(self):
        teachers = self.get_teacher_list()
        ids_constraint_teacher = list()
        for teacher in teachers:
            ids = self.groups_constraint_by_teacher(teacher)
            if len(ids) > 1:
                ids_constraint_teacher.append(ids)
        return ids_constraint_teacher

    def get_pairs_activities_order(self):
        pairs_acts = list()
        for year in pd.unique(self.schedule[YEAR]):
            for subject in pd.unique(self.schedule.loc[self.schedule[YEAR] == year][SUBJECT]):
                data = self.schedule.loc[(self.schedule[YEAR] == year) & (self.schedule[SUBJECT] == subject)].sort_values(ORDER).reset_index(drop='index')
                for i in range(len(data)-1):
                    for j in range(i+1, len(data)):
                        if data.loc[j][AFTER] == '-':
                            if int(data.loc[j][ORDER]) - int(data.loc[i][ORDER]) == 1:
                                pairs_acts.append((data.loc[i][GROUP] + '_' + data.loc[i][SUBJECT] + '_' + data.loc[i][ORDER],
                                                   data.loc[j][GROUP] + '_' + data.loc[j][SUBJECT] + '_' + data.loc[j][ORDER]))
        return pairs_acts

    def get_pairs_next_to_activities(self):
        pairs_acts = list()
        for i in self.schedule.loc[self.schedule[AFTER] != '-'].index:
            pairs_acts.append((self.schedule.loc[i][GROUP] + '_' + self.schedule.loc[i][SUBJECT] + '_' + self.schedule.loc[i][AFTER],
                               self.schedule.loc[i][GROUP] + '_' + self.schedule.loc[i][SUBJECT] + '_' + self.schedule.loc[i][ORDER]))
        return pairs_acts

    def count_classes_given_year(self, year):
        data = self.schedule.loc[self.schedule[YEAR] == year]
        count = 0
        if len(data) > 0:
            n_groups = len(data.groupby([GROUP]).count().index)
            count = int(data.groupby([GROUP, SUBJECT]).count()[TYPE].sum() / n_groups)
        return count

    def count_available_slot_given_year(self, year, session):
        count_morning = len(self.general_constraint.loc[(self.general_constraint[YEAR] == '-') & (self.general_constraint[SLOT] < '4')])
        count_afternoon = len(self.general_constraint.loc[(self.general_constraint[YEAR] == '-') & (self.general_constraint[SLOT] > '3')])
        count_year = len(self.general_constraint.loc[self.general_constraint[YEAR] == year])
        if session == 'm':
            return STANDARD_WEEK_SLOTS - count_morning - count_year
        else:
            return STANDARD_WEEK_SLOTS - count_afternoon - count_year

    def count_opposite_session_slots(self):
        opposite_session_need = dict()

        for year in pd.unique(self.schedule[YEAR]):
            session = self.get_session_given_year(year)
            n_classes = self.count_classes_given_year(year)
            n_slots = self.count_available_slot_given_year(year, session)
            need = n_classes - n_slots
            opposite_session_need[str(year)] = (session, 0 if need < 0 else need)

        return opposite_session_need

    def get_session_given_year(self, year):
        session = self.schedule.loc[self.schedule[YEAR] == year][SESSION].values[0]
        return session

    def get_optimization_bit_maps_same_subject_and_order(self):
        pairs = list()
        for year in self.schedule.groupby(YEAR).count().index:
            for subject in self.schedule.loc[self.schedule[YEAR] == year].groupby(SUBJECT).count().index:
                for order in self.schedule.loc[(self.schedule[YEAR] == year) &
                        (self.schedule[SUBJECT] == subject)].groupby(ORDER).count().index:
                    data = self.schedule.loc[(self.schedule[YEAR] == year) &
                                             (self.schedule[SUBJECT] == subject) &
                                             (self.schedule[ORDER] == order) &
                                             (self.schedule[JOIN] == '-')].reset_index(drop='index')
                    length = len(data)
                    for i in range(length):
                        for j in range(i+1, length):
                            pairs.append((data.loc[i][GROUP] + '_' + data.loc[i][SUBJECT] + '_'
                                          + data.loc[i][ORDER],
                                          data.loc[j][GROUP] + '_' + data.loc[j][SUBJECT] + '_'
                                          + data.loc[j][ORDER]))
        return pairs

    def get_optimization_bit_maps_same_subject_and_group(self):
        pairs = list()
        for year in pd.unique(self.schedule[YEAR]):
            for group in pd.unique(self.schedule.loc[self.schedule[YEAR] == year][GROUP]):
                for subject in pd.unique(self.schedule.loc[(self.schedule[YEAR] == year) &
                        (self.schedule[GROUP] == group)][SUBJECT]):
                    data = self.schedule.loc[(self.schedule[YEAR] == year) &
                                             (self.schedule[SUBJECT] == subject) &
                                             (self.schedule[GROUP] == group)].reset_index(drop='index')
                    length = len(data)
                    for i in range(length-1):
                        pairs.append((data.loc[i][GROUP] + '_' + data.loc[i][SUBJECT] + '_' + data.loc[i][ORDER],
                                      data.loc[i+1][GROUP] + '_' + data.loc[i+1][SUBJECT] + '_' + data.loc[i+1][ORDER]))
        return pairs

    def get_optimization_bit_maps_first_order(self):
        arr = list()
        for i in self.schedule.loc[self.schedule[ORDER] == '1'].index:
            arr.append(self.schedule.loc[i][GROUP] + '_' + self.schedule.loc[i][SUBJECT] + '_' +
                       self.schedule.loc[i][ORDER])
        return arr
