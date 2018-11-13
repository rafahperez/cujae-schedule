import os
import pandas as pd
from util import *


def read_sequence(file_dir):
    data = pd.DataFrame(columns=[YEAR, SUBJECT, TYPE, WEEK, ORDER])
    index = 0

    with open(file_dir, mode='r') as file:
        year = None
        for line in file.readlines():
            if line.startswith('#'):
                continue
            elif line.startswith('-'):
                line = line.replace(' ', '')
                year = line[1]
            else:
                line = line.replace(' ', '')
                line = line.replace('\n', '')
                subject, sequence_info = line.split(':')
                weeks_info = sequence_info.split('/')
                for week in range(1, len(weeks_info)+1):
                    order = 1
                    for lecture in weeks_info[week-1].split(','):
                        data.loc[index] = pd.Series([year, subject, lecture, str(week), str(order)],
                                                    index=[YEAR, SUBJECT, TYPE, WEEK, ORDER])
                        index += 1
                        order += 1

    return data


def read_relation(file_dir):
    data = pd.DataFrame(columns=[YEAR, SUBJECT, TYPE, TEACHER, GROUP])
    index = 0

    with open(file_dir, mode='r') as file:
        year = None
        subject = None
        for line in file.readlines():
            if line.startswith('#'):
                continue
            elif line.startswith('-'):
                line = line.replace(' ', '')
                year = line[1]
            elif line.startswith('!'):
                line = line.replace(' ', '')
                line = line.replace('\n', '')
                subject = line[1:]
            else:
                line = line.replace(' ', '')
                line = line.replace('\n', '')
                teacher, relation_info = line.split(':')

                for types in relation_info.split(';'):
                    type_, groups = types.split('/')

                    for group in groups.split(','):
                        data.loc[index] = pd.Series([year, subject, type_, teacher, 'G' + group],
                                                    index=[YEAR, SUBJECT, TYPE, TEACHER, GROUP])
                        index += 1

    return data


def read_session(file_dir):
    data = pd.DataFrame(columns=[YEAR, SESSION])
    index = 0

    with open(file_dir, mode='r') as file:
        for line in file.readlines():
            if line.startswith('#'):
                continue
            else:
                line = line.replace(' ', '')
                line = line.replace('\n', '')
                year, session = line.split(':')
                data.loc[index] = pd.Series([year, session], index=[YEAR, SESSION])
                index += 1

    return data


def read_union(file_dir):
    data = pd.DataFrame(columns=[SUBJECT, TYPE, JOIN, WITH])
    index = 0

    with open(file_dir, mode='r') as file:
        for line in file.readlines():
            if line.startswith('#'):
                continue
            else:
                line = line.replace(' ', '')
                line = line.replace('\n', '')
                groups, subject_info = line.split(':')
                g1, g2 = groups.split(',')
                subject, types = subject_info.split('/')
                for type_ in types.split(','):
                    data.loc[index] = pd.Series([subject, type_, 'G' + g1, 'G' + g2], index=[SUBJECT, TYPE, JOIN, WITH])
                    index += 1
    return data


def read_general_constraint(file_dir):
    data = pd.DataFrame(columns=[YEAR, DAY, SLOT])
    index = 0

    with open(file_dir, mode='r') as file:
        for line in file.readlines():
            if line.startswith('#'):
                continue
            else:
                line = line.replace(' ', '')
                line = line.replace('\n', '')
                year, day_info = line.split(':')
                day, slot = day_info.split('/')
                day = str(int(day) - 1)
                data.loc[index] = pd.Series([year, day, slot], index=[YEAR, DAY, SLOT])
                index += 1
    return data


def read_teacher_constraint(file_dir):
    data = pd.DataFrame(columns=[TEACHER, DAY, SLOT])
    index = 0

    with open(file_dir, mode='r') as file:
        for line in file.readlines():
            if line.startswith('#'):
                continue
            else:
                line = line.replace(' ', '')
                line = line.replace('\n', '')
                teacher, day_info = line.split(':')
                day, slot = day_info.split('/')
                day = str(int(day)-1)
                data.loc[index] = pd.Series([teacher, day, slot], index=[TEACHER, DAY, SLOT])
                index += 1
    return data


def join_sequence_and_session(sequence, session):
    mapper = dict(zip(session[YEAR], session[SESSION]))
    sequence[SESSION] = sequence[YEAR].apply(lambda x: mapper[x])
    return sequence


def join_sequence_and_relation(sequence, relation):
    data = pd.DataFrame(columns=[YEAR, SESSION, SUBJECT, TYPE, ORDER, WEEK,
                                 TEACHER, GROUP, JOIN])
    index = 0
    for i in sequence.index:
        year = sequence.loc[i][YEAR]
        session = sequence.loc[i][SESSION]
        subject = sequence.loc[i][SUBJECT]
        type_ = sequence.loc[i][TYPE]
        order = sequence.loc[i][ORDER]
        week = sequence.loc[i][WEEK]
        for j in relation.loc[(relation[YEAR] == year) &
                 (relation[SUBJECT] == subject) &
                 (relation[TYPE] == type_)].index:
            teacher = relation.loc[j][TEACHER]
            group = relation.loc[j][GROUP]
            data.loc[index] = pd.Series([year, session, subject, type_, order, week, teacher, group, '-'],
                                        index=[YEAR, SESSION, SUBJECT, TYPE, ORDER, WEEK, TEACHER, GROUP, JOIN])
            index += 1
    return data


def join_sequence_and_union(sequence, union):
    for i in union.index:
        subject = union.loc[i][SUBJECT]
        type_ = union.loc[i][TYPE]
        group = union.loc[i][JOIN]
        con = union.loc[i][WITH]
        for j in sequence.loc[(sequence[SUBJECT] == subject) & (sequence[TYPE] == type_) & (sequence[GROUP] == group)].index:
            sequence.loc[j][JOIN] = con
    return sequence


def read_schedule_data(sequence_dir, relation_dir, union_dir, session_dir):
    session = read_session(session_dir)
    sequence = read_sequence(sequence_dir)
    relation = read_relation(relation_dir)
    union = read_union(union_dir)

    sequence = join_sequence_and_session(sequence, session)
    sequence = join_sequence_and_relation(sequence, relation)
    schedule = join_sequence_and_union(sequence, union)

    return schedule


def load_dir_files(config_dir):

    sequence_dir = os.path.join(config_dir, 'secuencia.txt')
    session_dir = os.path.join(config_dir, 'sesion.txt')
    relation_dir = os.path.join(config_dir, 'relacion.txt')
    union_dir = os.path.join(config_dir, 'union.txt')
    general_constraint_dir = os.path.join(config_dir, 'restriccion_general.txt')
    teacher_constraint_dir = os.path.join(config_dir, 'restriccion_profesor.txt')

    assert os.path.exists(sequence_dir)
    assert os.path.exists(session_dir)
    assert os.path.exists(relation_dir)
    assert os.path.exists(union_dir)
    assert os.path.exists(general_constraint_dir)
    assert os.path.exists(teacher_constraint_dir)

    schedule = read_schedule_data(sequence_dir, relation_dir, union_dir, session_dir)
    general_constraint = read_general_constraint(general_constraint_dir)
    teacher_constraint = read_teacher_constraint(teacher_constraint_dir)

    return schedule, general_constraint, teacher_constraint
