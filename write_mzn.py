import pandas as pd
import numpy as np
import pymzn
from schedule import *


CONSTRAINTS_FILE = 'test_file.mzn'


def write_mzn_file(schedule, general_constraints, teacher_constraints):
    '''

    :return:
    '''
    #utils
    bit_maps = create_bit_maps_ids(schedule)
    groups_to_join_ids = groups_to_join(schedule)
    ids_constraint_teacher = groups_with_teacher_constraint(schedule)
    ids_acts_different_days = activities_different_days(schedule)
    ids_acts_order = activities_order(schedule)
    index_general_const = index_general_constraints(general_constraints)
    bit_maps_per_years = create_bit_maps_per_year(schedule)
    index_general_const_per_years = index_general_constraints_per_years(general_constraints)
    teachers_with_constraints = pd.unique(teacher_constraints['Profesor'])
    bit_maps_per_teachers = create_bit_maps_ids_given_teacher_list(schedule, teachers_with_constraints)
    index_const_per_teachers = index_constraints_given_teacher_list(teacher_constraints, teachers_with_constraints)
    opposite_session_slots = count_opposite_session_slots(schedule, general_constraints)
    bit_maps_per_group = create_bit_maps_per_group(schedule)

    write_file_header()
    write_file_bit_maps(bit_maps)
    write_file_group_constraint(schedule, bit_maps)
    write_file_join_groups(groups_to_join_ids)
    write_file_groups_with_teacher_constraint(ids_constraint_teacher)
    write_file_activities_different_days(ids_acts_different_days)
    write_file_activities_order(ids_acts_order)
    write_general_constraint(bit_maps, index_general_const)
    write_general_constraint_per_year(bit_maps_per_years, index_general_const_per_years)
    write_constraints_per_teacher(bit_maps_per_teachers, index_const_per_teachers)
    write_break_index(bit_maps_per_group)
    write_opposite_session_constraint(bit_maps_per_group, opposite_session_slots)

    with open('test_file.mzn', mode='a') as file:
        file.write('\n')
        file.write('solve satisfy;')


def write_file_header():
    '''
    Escribe en el fichero el encabezado, asi como la variable turnos
    que va a ser el tamano de los mapas de bits

    :return:
    '''
    file = open('test_file.mzn', mode='w')
    file.write('include "globals.mzn";\n\n')
    file.write('int: turnos;\n\n')
    file.close()


def write_file_bit_maps(bit_maps):
    '''

    :param bit_maps:
    :return:
    '''
    file = open('test_file.mzn', mode='a')
    for i in bit_maps:
        file.write('array[1..turnos] of var 0..1: ' + i +';\nconstraint sum('+ i +') = 1;\n\n')
    file.close()


def write_file_group_constraint(schedule, bit_maps):
    '''

    :param schedule:
    :param bit_maps:
    :return:
    '''
    groups = pd.unique(schedule['Grupo'])
    for group in groups:
        constraint_group = 'constraint forall (i in 1..turnos) ('
        group_count=0
        for bit_map in bit_maps:
            if group in bit_map:
                constraint_group += bit_map + '[i]'
                group_count += 1
        constraint_group += ' <= 1);\n\n'
        constraint_group = constraint_group.replace(']',']+', group_count-1)
        file = open('test_file.mzn', mode='a')
        file.write(constraint_group)
        file.close()


def write_file_join_groups(join_groups_ids):
    '''

    :param join_groups_ids:
    :return:
    '''
    file = open('test_file.mzn', mode='a')
    file.write('predicate join_groups(array[int] of var int: g1, array[int] of var int: g2) = forall (i in 1..turnos) '
               '(g1[i] == g2[i]);\n\n')

    for g1, g2 in join_groups_ids:
        file.write('constraint join_groups(' + g1 + ', ' + g2 + ');\n')
    file.write('\n')
    file.close()


def write_file_groups_with_teacher_constraint(ids_constraint_teacher):
    '''

    :param ids_constraint_teacher:
    :return:
    '''
    for ids in ids_constraint_teacher:
        constraint = 'constraint forall(i in 1..turnos) ('
        for i in ids:
            constraint += i + '[i]'
        constraint += ' <= 1);\n\n'
        constraint = constraint.replace(']', ']+', len(ids) - 1)
        with open('test_file.mzn', mode='a') as file:
            file.write(constraint)


def write_file_activities_different_days(ids_acts_diff_days):
    '''

    :param ids_acts_diff_days:
    :return:
    '''
    with open('test_file.mzn', mode='a') as file:
        file.write('function var int: index(array[int] of var int: x) = sum([x[i]*i | i in 1..length(x)]);'+'\n\n')
        file.write('predicate diff_day(array[int] of var int: g1, array[int] of var int: g2) = '
                   '(index(g1) - 1) div 6 != (index(g2) - 1) div 6;'+'\n\n')
        for act1, act2 in ids_acts_diff_days:
            file.write('constraint diff_day(' + act1 + ',' + act2 + ');\n')


def write_file_activities_order(ids_acts_order):
    with open('test_file.mzn', mode='a') as file:
        file.write('\n')
        for act1, act2 in ids_acts_order:
            file.write('constraint index(' + act1 + ') < index(' + act2 + ');\n')


def write_general_constraint(bit_maps, index_general_const):
    with open('test_file.mzn', mode='a') as file:
        file.write('\n')
        for index in index_general_const:
            for bit_map in bit_maps:
                file.write('constraint ' + bit_map + '[' + str(index) + ']' + ' = 0;\n')


def write_general_constraint_per_year(bit_maps, index_general_const):
    with open('test_file.mzn', mode='a') as file:
        file.write('\n')
        for b, i in zip(bit_maps, index_general_const):
            if (len(b) != 0) & (len(i) != 0):
                for index in i:
                    for bit_map in b:
                        file.write('constraint ' + bit_map + '[' + str(index) + ']' + ' = 0;\n')


def write_constraints_per_teacher(bit_maps, index_general_const):
    with open('test_file.mzn', mode='a') as file:
        file.write('\n')
        for b, i in zip(bit_maps, index_general_const):
            if (len(b) != 0) & (len(i) != 0):
                for index in i:
                    for bit_map in b:
                        file.write('constraint ' + bit_map + '[' + str(index) + ']' + ' = 0;\n')


def close_opposite_session(schedule_data):
    for s, closed in zip(['M', 'T'], [AFTERNOON_CLOSED, MORNING_CLOSED]):
        bit_maps = create_bit_maps_ids_given_session(schedule_data, s)
        write_general_constraint(bit_maps, closed)


def write_break_index(bit_maps_per_group):
    with open(CONSTRAINTS_FILE, mode='a') as file:
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


def write_opposite_session_constraint(bit_maps_per_group, opposite_session_slots):
    with open(CONSTRAINTS_FILE, mode='a') as file:
        file.write('\n')
        for year, group, bit_maps in bit_maps_per_group:
            sess, needed_slots = opposite_session_slots[str(year)]
            indexes = AFTERNOON_CLOSED if sess == 'M' else MORNING_CLOSED

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
