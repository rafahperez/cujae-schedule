import logging
from util import *
from schedule import *

LOG = logging.getLogger(__name__)
CONSTRAINTS_FILE = 'schedule.mzn'


class MinizincWriter:

    def __init__(self, file):
        self.file = file

    def write_file(self, scheduler):
        LOG.info('Started writing the mzn file.')
        self.write_header()
        self.write_classrooms_capacity(scheduler)
        self.write_classrooms_cost(scheduler)
        self.write_bit_maps(scheduler)
        self.write_classrooms_bit_maps(scheduler)
        self.write_group_constraint(scheduler)
        self.write_file_join_groups(scheduler)
        self.write_same_teacher_activities(scheduler)
        self.write_activities_order(scheduler)
        self.write_next_to_lectures(scheduler)
        self.write_general_constraint(scheduler)
        self.write_general_constraint_per_year(scheduler)
        self.write_teacher_constraints(scheduler)
        self.write_break_index(scheduler)
        self.write_opposite_session_constraint(scheduler)
        self.write_classrooms_amount_constraint(scheduler)
        self.write_classrooms_capacity_constraint(scheduler)
        self.write_locked_classrooms(scheduler)
        self.write_objective_function(scheduler)
        LOG.info('Finished writing the mzn file.')

    def write_header(self):
        with open(self.file, mode='w') as file:
            file.write('include "globals.mzn";\n')
            file.write('int: turnos;\n')
        LOG.info('Finished writing the mzn file header.')

    def write_classrooms_capacity(self, scheduler):
        capacities = scheduler.get_classroom_capacities()
        length = len(capacities)
        with open(self.file, mode='a') as file:
            file.write('\n')
            file.write('int: aulas = {};\n'.format(length))
            file.write('array[1..aulas] of var 0..200: capacity = [')
            for i in range(length):
                file.write(capacities[i])
                if i == length - 1:
                    continue
                else:
                    file.write(', ')
            file.write('];\n')
        LOG.info('Finished writing the classroom capacities.')

    def write_classrooms_cost(self, scheduler):
        cost = scheduler.get_classrooms_cost()
        length = len(cost)
        with open(self.file, mode='a') as file:
            file.write('\n')
            file.write('array[1..aulas] of var 0..100: costs = [')
            for i in range(length):
                file.write(cost[i])
                if i == length - 1:
                    continue
                else:
                    file.write(', ')
            file.write('];\n')
        LOG.info('Finished writing the classroom costs.')

    def write_bit_maps(self, scheduler):
        bit_maps = scheduler.get_bit_maps()
        with open(self.file, mode='a') as file:
            file.write('\n')
            file.write('% Bit maps\n')
            for bm in bit_maps:
                file.write('\n')
                file.write('array[1..turnos] of var 0..1: ' + bm + ';\n')
                file.write('constraint sum(' + bm + ') = 1;\n')
        LOG.info('Finished writing the bit maps.')

    def write_classrooms_bit_maps(self, scheduler):
        bit_maps = scheduler.get_classrooms_bit_maps()
        with open(self.file, mode='a') as file:
            file.write('\n')
            file.write('% Classrooms bit maps\n')
            for bm in bit_maps.keys():
                file.write('\n')
                file.write('array[1..aulas] of var 0..1: ' + bm + ';\n')
                file.write('constraint sum(' + bm + ') = 1;\n')
                file.write('int: C_{} = {};\n'.format(bm, bit_maps[bm]))
        LOG.info('Finished writing the classrooms bit maps.')

    def write_group_constraint(self, scheduler):
        groups = scheduler.get_unique_groups()
        with open(self.file, mode='a') as file:
            file.write('\n')
            file.write('% A group can only have one lecture per slot\n')
            file.write('\n')
            for group in groups:
                file.write('constraint forall (i in 1..turnos) (')
                bit_maps = scheduler.get_bit_maps_given_group(group)
                length = len(bit_maps)
                for i in range(length):
                    file.write(bit_maps[i] + '[i]')
                    if i == length - 1:
                        continue
                    else:
                        file.write(' + ')
                file.write(' <= 1);\n')
        LOG.info('Finished writing group constraints.')

    def write_file_join_groups(self, scheduler):
        join_groups_ids = scheduler.groups_to_join()
        with open(self.file, mode='a') as file:
            file.write('\n')
            file.write('% Groups to join\n')
            file.write('\n')
            for g1, g2 in join_groups_ids:
                file.write('constraint join_groups(' + g1 + ', ' + g2 + ');\n')
        LOG.info('Finished writing groups to join.')

    def write_same_teacher_activities(self, scheduler):
        ids_constraint_teacher = scheduler.groups_with_teacher_constraint()
        with open(self.file, mode='a') as file:
            file.write('\n')
            file.write('% Activities with same teacher\n')
            file.write('\n')
            for ids in ids_constraint_teacher:
                file.write('constraint forall(i in 1..turnos) (')
                length = len(ids)
                for i in range(length):
                    file.write(ids[i] + '[i]')
                    if i == length - 1:
                        continue
                    else:
                        file.write(' + ')
                file.write(' <= 1);\n')
        LOG.info('Finished writing same teacher activities.')

    def write_activities_order(self, scheduler):
        ids_acts_order = scheduler.get_pairs_activities_order()
        with open(self.file, mode='a') as file:
            file.write('\n')
            file.write('% Activities order\n')
            file.write('\n')
            for act1, act2 in ids_acts_order:
                file.write('constraint day(' + act1 + ') < day(' + act2 + ');\n')
        LOG.info('Finished writing activities order.')

    def write_next_to_lectures(self, scheduler):
        ids_next_to = scheduler.get_pairs_next_to_activities()
        with open(self.file, mode='a') as file:
            file.write('\n')
            file.write('% Contiguous lectures\n')
            file.write('\n')
            if len(ids_next_to) > 0:
                for act1, act2 in ids_next_to:
                    file.write('constraint index(' + act1 + ') - index(' + act2 + ') = -1;\n')
                    file.write('constraint day(' + act1 + ') = day(' + act2 + ');\n')
            else:
                file.write('% NONE\n')
        LOG.info('Finished writing contiguous lectures.')

    def write_general_constraint(self, scheduler):
        bit_maps = scheduler.get_bit_maps()
        index_general_const = scheduler.index_general_constraints()
        with open(self.file, mode='a') as file:
            file.write('\n')
            for index in index_general_const:
                for bit_map in bit_maps:
                    file.write('constraint ' + bit_map + '[' + str(index) + ']' + ' = 0;\n')

    def write_general_constraint_per_year(self, scheduler):
        bit_maps_per_years = scheduler.create_bit_maps_per_year()
        index_general_const_per_years = scheduler.index_general_constraints_per_years()
        with open(self.file, mode='a') as file:
            file.write('\n')
            for b, i in zip(bit_maps_per_years, index_general_const_per_years):
                if (len(b) != 0) & (len(i) != 0):
                    for index in i:
                        for bit_map in b:
                            file.write('constraint ' + bit_map + '[' + str(index) + ']' + ' = 0;\n')

    def write_teacher_constraints(self, scheduler):
        teachers_with_constraints = pd.unique(scheduler.teacher_constraint[TEACHER])
        with open(self.file, mode='a') as file:
            file.write('\n')
            file.write('% Teacher constraints\n')
            file.write('\n')

            for teacher in teachers_with_constraints:
                bit_maps = scheduler.get_bit_maps_given_teacher(teacher)
                index = scheduler.get_index_constraints_given_teacher(teacher)
                if (len(bit_maps) != 0) & (len(index) != 0):
                    for i in index:
                        for b in bit_maps:
                            file.write('constraint ' + b + '[' + str(i) + ']' + ' = 0;\n')

    def write_break_index(self, scheduler):
        bit_maps_per_group = scheduler.create_bit_maps_per_group()

        with open(self.file, mode='a') as file:
            file.write('\n')
            for top, bottom in BREAK_INDEX:
                for year, group, bit_maps in bit_maps_per_group:
                    file.write('constraint ')
                    len_bit_maps = len(bit_maps)
                    for i in range(len_bit_maps):
                        bit_map = bit_maps[i]
                        file.write(bit_map + '[' + str(top) + '] + ' + bit_map + '[' + str(bottom) + ']')
                        if i == len_bit_maps - 1:
                            file.write('')
                        else:
                            file.write(' + ')
                    file.write(' <= 1;\n')

    def write_opposite_session_constraint(self, scheduler):
        bit_maps_per_group = scheduler.create_bit_maps_per_group()
        opposite_session_slots = scheduler.count_opposite_session_slots()
        with open(self.file, mode='a') as file:
            file.write('\n')
            for year, group, bit_maps in bit_maps_per_group:
                sess, needed_slots = opposite_session_slots[str(year)]
                indexes = AFTERNOON_CLOSED if sess == MORNING_SESSION else MORNING_CLOSED

                len_bit_maps = len(bit_maps)
                len_indexes = len(indexes)

                file.write('constraint ')

                for i in range(len_bit_maps):
                    bit_map = bit_maps[i]

                    for j in range(len_indexes):
                        index = indexes[j]

                        file.write(bit_map + '[' + str(index) + ']')

                        if (i == len_bit_maps - 1) & (j == len_indexes - 1):
                            file.write('')
                        else:
                            file.write(' + ')
                file.write(' = ' + str(needed_slots) + ';\n')

    def write_classrooms_amount_constraint(self, scheduler):
        bit_maps = scheduler.get_classrooms_bit_maps()
        with open(self.file, mode='a') as file:
            file.write('\n')
            file.write('% Classrooms amount constraint\n')
            file.write('constraint forall (i,j in 1..turnos where j<=aulas) (')
            keys = list(bit_maps.keys())
            length = len(keys)
            for i in range(length):
                file.write('{}[i] * {}[j]'.format(keys[i][3:], keys[i]))
                if i == length - 1:
                    continue
                else:
                    file.write(' + ')
            file.write(' <= 1);\n')
        LOG.info('Finished writing the classrooms amount constraint.')

    def write_classrooms_capacity_constraint(self, scheduler):
        bit_maps = scheduler.get_classrooms_bit_maps()
        with open(self.file, mode='a') as file:
            file.write('\n')
            file.write('% Classrooms capacity constraints\n')
            for bm in bit_maps.keys():
                file.write('constraint forall (i in 1..aulas) ({}[i] * C_{} <= capacity[i]);\n'.format(bm, bm))
        LOG.info('Finished writing the classrooms capacity contraint.')

    def write_locked_classrooms(self, scheduler):
        locked = scheduler.get_locked_classrooms()
        with open(self.file, mode='a') as file:
            file.write('\n')
            file.write('% Classrooms locked\n')
            for key, values in locked.items():
                if len(values) > 0:
                    for element in values:
                        file.write('constraint {}[{}] = 0;\n'.format(key, element))
        LOG.info('Finished writing the locked classrooms by type.')

    def write_objective_function(self, scheduler):
        bit_maps_subject_order = scheduler.get_optimization_bit_maps_same_subject_and_order()
        length_so = len(bit_maps_subject_order)

        bit_maps_subject_group = scheduler.get_optimization_bit_maps_same_subject_and_group()
        length_sg = len(bit_maps_subject_group)

        bit_maps_first_order = scheduler.get_optimization_bit_maps_first_order()
        length_fo = len(bit_maps_first_order)

        classrooms_bit_maps = scheduler.get_classrooms_bit_maps()

        with open(self.file, mode='a') as file:
            file.write('\n')
            file.write('predicate join_groups(array[int] of var int: g1, array[int] of var int: g2) = '
                       'forall (i in 1..turnos) (g1[i] == g2[i]);\n')

            file.write('\n')
            file.write('function var int: index(array[int] of var int: x) = sum([x[i]*i | i in 1..length(x)]);\n')

            file.write('\n')
            file.write('function var int: day(array[int] of var int: x) = (index(x) - 1) div 6;\n')

            file.write('\n')
            file.write('function var int: day_distance(array[int] of var int: x, array[int] of var int: y) = '
                       'abs(day(x) - day(y));\n')

            file.write('\n')
            file.write('function var int: cost(array[int] of var int: x) = sum([x[i]*costs[i] | i in 1..length(x)]);\n')

            file.write('\n')
            file.write('solve minimize ')

            for i in range(length_so):
                bm_1, bm_2 = bit_maps_subject_order[i]
                file.write('5*day_distance(' + bm_1 + ', ' + bm_2 + ')')
                file.write(' + ')

            for k in range(length_fo):
                bm = bit_maps_first_order[k]
                file.write('day(' + bm + ')')
                file.write(' + ')

            for c in classrooms_bit_maps.keys():
                file.write('cost(' + c + ')')
                file.write(' + ')

            for j in range(length_sg):
                bm_1, bm_2 = bit_maps_subject_group[j]
                file.write('(-1)*day_distance(' + bm_1 + ', ' + bm_2 + ')')
                if j == length_sg - 1:
                    continue
                else:
                    file.write(' + ')

            file.write(';')

        LOG.info('Finished writing the objective function.')
