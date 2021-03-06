import os
import datetime
import calendar
import pandas as pd
from util import *


def read_sequence(file_dir):
    data = pd.DataFrame(columns=[YEAR, SUBJECT, TYPE, WEEK, ORDER, AFTER])
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
                for week in range(1, len(weeks_info) + 1):
                    order = 1
                    for lecture in weeks_info[week - 1].split(','):
                        n = lecture.count('-')
                        if n == 0:
                            data.loc[index] = pd.Series([year, subject, lecture, str(week), str(order), '-'],
                                                        index=[YEAR, SUBJECT, TYPE, WEEK, ORDER, AFTER])
                            index += 1
                            order += 1
                        else:
                            after = '-'
                            for lec in lecture.split('-'):
                                data.loc[index] = pd.Series([year, subject, lec, str(week), str(order), after],
                                                            index=[YEAR, SUBJECT, TYPE, WEEK, ORDER, AFTER])
                                after = str(order)
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
                groups, subjects_info = line.split(':')
                arr_groups = groups.split(',')
                for subject in subjects_info.split(';'):
                    sub, types = subject.split('/')
                    for i in range(len(arr_groups) - 1):
                        for type_ in types.split(','):
                            data.loc[index] = pd.Series([sub, type_, 'G' + arr_groups[i], 'G' + arr_groups[i + 1]],
                                                        index=[SUBJECT, TYPE, JOIN, WITH])
                            index += 1
    return data


def read_general_constraint(file_dir):
    data = pd.DataFrame(columns=[YEAR, WEEK, DAY, SLOT])
    index = 0
    first_day = None

    with open(file_dir, mode='r') as file:
        for line in file.readlines():
            if line.startswith('#'):
                continue
            if line.startswith('!'):
                line = line.replace(' ', '')
                line = line.replace('\n', '')
                day, month, year = line[1:].split('/')
                first_day = datetime.date(int(year), int(month), int(day))
            else:
                assert first_day is not None
                line = line.replace(' ', '')
                line = line.replace('\n', '')
                school_year, day_info = line.split(':')
                day_info, slot = day_info.split(';')
                day, month, year = day_info.split('/')

                if slot != '-':

                    date = datetime.date(int(year), int(month), int(day))
                    week = 1 + (date - first_day).days // 7
                    weekday = calendar.weekday(int(year), int(month), int(day))

                    data.loc[index] = pd.Series([school_year, str(week), str(weekday), slot],
                                                index=[YEAR, WEEK, DAY, SLOT])
                    index += 1

                else:

                    date = datetime.date(int(year), int(month), int(day))
                    week = 1 + (date - first_day).days // 7
                    weekday = calendar.weekday(int(year), int(month), int(day))

                    for sl in range(1, 7):
                        data.loc[index] = pd.Series([school_year, str(week), str(weekday), str(sl)],
                                                    index=[YEAR, WEEK, DAY, SLOT])
                        index += 1

    return data


def read_teacher_constraint(file_dir):
    data = pd.DataFrame(columns=[TEACHER, WEEK, DAY, SLOT])
    index = 0
    first_day = None

    with open(file_dir, mode='r') as file:
        for line in file.readlines():
            if line.startswith('#'):
                continue
            if line.startswith('!'):
                line = line.replace(' ', '')
                line = line.replace('\n', '')
                day, month, year = line[1:].split('/')
                first_day = datetime.date(int(year), int(month), int(day))
            else:
                assert first_day is not None
                line = line.replace(' ', '')
                line = line.replace('\n', '')
                teacher, day_info = line.split(':')
                day_info, slot = day_info.split(';')
                if day_info != '-':
                    day_map = {
                        'l': '0',
                        'm': '1',
                        'x': '2',
                        'j': '3',
                        'v': '4'
                    }
                    day = day_map[day_info]
                    if slot != '-':
                        data.loc[index] = pd.Series([teacher, '-', day, slot], index=[TEACHER, WEEK, DAY, SLOT])
                        index += 1
                    else:
                        for i in range(1, 7):
                            data.loc[index] = pd.Series([teacher, '-', day, str(i)],
                                                        index=[TEACHER, WEEK, DAY, SLOT])
                            index += 1
                else:
                    for i in range(0, 5):
                        data.loc[index] = pd.Series([teacher, '-', str(i), slot],
                                                    index=[TEACHER, WEEK, DAY, SLOT])
                        index += 1
    return data


def join_sequence_and_session(sequence, session):
    mapper = dict(zip(session[YEAR], session[SESSION]))
    sequence[SESSION] = sequence[YEAR].apply(lambda x: mapper[x])
    return sequence


def join_sequence_and_relation(sequence, relation):
    data = pd.DataFrame(columns=[YEAR, SESSION, SUBJECT, TYPE, ORDER, AFTER, WEEK,
                                 TEACHER, GROUP, JOIN])
    index = 0
    for i in sequence.index:
        year = sequence.loc[i][YEAR]
        session = sequence.loc[i][SESSION]
        subject = sequence.loc[i][SUBJECT]
        type_ = sequence.loc[i][TYPE]
        order = sequence.loc[i][ORDER]
        after = sequence.loc[i][AFTER]
        week = sequence.loc[i][WEEK]
        for j in relation.loc[(relation[YEAR] == year) &
                              (relation[SUBJECT] == subject) &
                              (relation[TYPE] == type_)].index:
            teacher = relation.loc[j][TEACHER]
            group = relation.loc[j][GROUP]
            data.loc[index] = pd.Series([year, session, subject, type_, order, after, week, teacher, group, '-'],
                                        index=[YEAR, SESSION, SUBJECT, TYPE, ORDER, AFTER, WEEK, TEACHER, GROUP, JOIN])
            index += 1
    return data


def join_sequence_and_union(sequence, union):
    for i in union.index:
        subject = union.loc[i][SUBJECT]
        type_ = union.loc[i][TYPE]
        group = union.loc[i][JOIN]
        con = union.loc[i][WITH]
        for j in sequence.loc[
            (sequence[SUBJECT] == subject) & (sequence[TYPE] == type_) & (sequence[GROUP] == group)].index:
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


def read_groups(file_dir):
    data = pd.DataFrame(columns=[GROUP, CAPACITY])
    index = 0

    with open(file_dir, mode='r') as file:
        for line in file.readlines():
            if line.startswith('#'):
                continue
            else:
                line = line.replace(' ', '')
                line = line.replace('\n', '')
                group, capacity = line.split(':')

                data.loc[index] = pd.Series(['G' + group, capacity], index=[GROUP, CAPACITY])
                index += 1
    return data


def read_classrooms(file_dir):
    data = pd.DataFrame(columns=[TYPE, ID, CAPACITY])
    index = 0

    with open(file_dir, mode='r') as file:
        for line in file.readlines():
            if line.startswith('#'):
                continue
            else:
                line = line.replace(' ', '')
                line = line.replace('\n', '')

                type_, class_info = line.split('/')
                id_, capacity = class_info.split(':')
                data.loc[index] = pd.Series([type_, id_, capacity], index=[TYPE, ID, CAPACITY])
                index += 1
    return data


def join_schedule_and_groups(schedule, groups):
    schedule[GROUP_COUNT] = pd.Series([None for _ in range(len(schedule))])
    schedule[JOIN_COUNT] = pd.Series([None for _ in range(len(schedule))])
    # Could I use join from pandas??
    for i in schedule.index:
        schedule.loc[i][GROUP_COUNT] = groups.loc[groups[GROUP] == schedule.loc[i][GROUP]][CAPACITY].values[0]
    for i in schedule.index:
        if schedule.loc[i][JOIN_COUNT] is None:
            if schedule.loc[i][JOIN] == '-':
                schedule.loc[i][JOIN_COUNT] = schedule.loc[i][GROUP_COUNT]
            else:
                initial = i
                done = False
                count = int(schedule.loc[i][GROUP_COUNT])
                while not done:
                    index = schedule.loc[(schedule[GROUP] == schedule.loc[initial][JOIN]) & \
                                         (schedule[SUBJECT] == schedule.loc[initial][SUBJECT]) & \
                                         (schedule[WEEK] == schedule.loc[initial][WEEK]) & \
                                         (schedule[ORDER] == schedule.loc[initial][ORDER])].index[0]
                    count += int(schedule.loc[index][GROUP_COUNT])
                    initial = index
                    if schedule.loc[index][JOIN] == '-':
                        done = True

                initial = i
                done = False
                while not done:
                    schedule.loc[initial][JOIN_COUNT] = str(count)
                    if schedule.loc[initial][JOIN] == '-':
                        done = True
                    else:
                        index = schedule.loc[(schedule[GROUP] == schedule.loc[initial][JOIN]) & \
                                             (schedule[SUBJECT] == schedule.loc[initial][SUBJECT]) & \
                                             (schedule[WEEK] == schedule.loc[initial][WEEK]) & \
                                             (schedule[ORDER] == schedule.loc[initial][ORDER])].index[0]
                        initial = index

    return schedule


def load_dir_files(config_dir):
    sequence_dir = os.path.join(config_dir, 'secuencia')
    session_dir = os.path.join(config_dir, 'sesion')
    relation_dir = os.path.join(config_dir, 'relacion')
    union_dir = os.path.join(config_dir, 'union')
    general_constraint_dir = os.path.join(config_dir, 'restriccion_general')
    teacher_constraint_dir = os.path.join(config_dir, 'restriccion_profesor')
    classrooms_dir = os.path.join(config_dir, 'aulas')
    groups_dir = os.path.join(config_dir, 'grupos')

    assert os.path.exists(sequence_dir)
    assert os.path.exists(session_dir)
    assert os.path.exists(relation_dir)
    assert os.path.exists(union_dir)
    assert os.path.exists(general_constraint_dir)
    assert os.path.exists(teacher_constraint_dir)
    assert os.path.exists(classrooms_dir)
    assert os.path.exists(groups_dir)

    schedule = read_schedule_data(sequence_dir, relation_dir, union_dir, session_dir)
    general_constraint = read_general_constraint(general_constraint_dir)
    teacher_constraint = read_teacher_constraint(teacher_constraint_dir)
    classrooms = read_classrooms(classrooms_dir)
    groups = read_groups(groups_dir)

    schedule = join_schedule_and_groups(schedule, groups)

    return schedule, general_constraint, teacher_constraint, classrooms
