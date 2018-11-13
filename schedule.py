import pandas as pd

AFTERNOON_CLOSED = [4, 5, 6, 10, 11, 12, 16, 17, 18, 22, 23, 24, 28, 29, 30]
MORNING_CLOSED = [1, 2, 3, 7, 8, 9, 13, 14, 15, 19, 20, 21, 25, 26, 27]
BREAK_INDEX = [(3, 4), (9, 10), (15, 16), (21, 22), (27, 28)]

STANDARD_WEEK_SLOTS = 15
SLOTS_PER_WEEK = 30
SLOTS_PER_DAY = 6
MORNING_SESSION = 'm'
DAYS_OF_WEEK = {0: 'Lunes', 1: 'Martes', 2: 'Miercoles', 3: 'Jueves', 4: 'Viernes'}


def create_bit_maps_ids(schedule_data):
    """

    :param schedule_data:
    :return: (list) Ids(Grupo_Asignatura_Orden) one per row in the schedule
    """
    return [schedule_data.loc[i]['Grupo'] + '_' + schedule_data.loc[i]['Asignatura'] + '_' +
            schedule_data.loc[i]['Orden'] for i in schedule_data.index]


def create_bit_maps_per_year(schedule_data):
    return [create_bit_maps_ids_given_year(schedule_data, str(year)) for year in range(1, 6)]


def create_bit_maps_per_group(schedule_data):
    bit_maps = list()
    for year in schedule_data.groupby(['Año']).count().index:
        for group in schedule_data.loc[schedule_data['Año'] == year].groupby(['Grupo']).count().index:
            bit_maps.append((year, group, create_bit_maps_ids(schedule_data.loc[schedule_data['Grupo'] == group])))
    return bit_maps


def create_bit_maps_ids_given_year(schedule_data, year):
    """

    :param schedule_data:
    :return: (list) Ids(Grupo_Asignatura_Orden) one per row in the schedule per year
    """
    return [schedule_data.loc[i]['Grupo'] + '_' + schedule_data.loc[i]['Asignatura'] + '_' +
            schedule_data.loc[i]['Orden'] for i in schedule_data.loc[schedule_data['Año'].astype(object) == year].index]


def create_bit_maps_ids_given_teacher(schedule_data, teacher):
    '''

    :param schedule_data:
    :param teacher:
    :return:
    '''
    return [schedule_data.loc[i]['Grupo'] + '_' + schedule_data.loc[i]['Asignatura'] + '_' +
            schedule_data.loc[i]['Orden'] for i in schedule_data.loc[schedule_data['Profesor'] == teacher].index]


def create_bit_maps_ids_given_teacher_list(schedule_data, teachers):
    return [create_bit_maps_ids_given_teacher(schedule_data, teacher) for teacher in teachers]


def create_bit_maps_ids_given_session(schedule_data, session):
    '''

    :param schedule_data:
    :param session:
    :return:
    '''
    return [schedule_data.loc[i]['Grupo'] + '_' + schedule_data.loc[i]['Asignatura'] + '_' +
            schedule_data.loc[i]['Orden'] for i in schedule_data.loc[schedule_data['Sesion'] == session].index]


def index_general_constraints(constraint_data):
    '''

    :param constraint_data:
    :return:
    '''
    return [int(constraint_data.loc[i]['Dia']) * 6 + int(constraint_data.loc[i]['Turno'])
            for i in constraint_data.loc[constraint_data['Año'] == '-'].index]


def index_general_constraints_per_years(constraint_data):
    return [index_general_constraints_given_year(constraint_data, str(year)) for year in range(1, 6)]


def index_general_constraints_given_year(constraint_data, year):
    '''

    :param constraint_data:
    :param year:
    :return:
    '''
    return [int(constraint_data.loc[i]['Dia']) * 6 + int(constraint_data.loc[i]['Turno'])
            for i in constraint_data.loc[constraint_data['Año'] == year].index]


def index_constraints_given_teacher(constraint_data, teacher):
    '''

    :param constraint_data:
    :param teacher:
    :return:
    '''
    return [int(constraint_data.loc[i]['Dia']) * 6 + int(constraint_data.loc[i]['Turno'])
            for i in constraint_data.loc[constraint_data['Profesor'] == teacher].index]


def index_constraints_given_teacher_list(constraint_data, teachers):
    '''

    :param constraint_data:
    :param teachers:
    :return:
    '''
    return [index_constraints_given_teacher(constraint_data, teacher) for teacher in teachers]


def groups_to_join(schedule_data):
    """

    :param schedule_data:
    :return: (list) Tuples with groups to join in a specific class
    """
    groups_to_join_ids = list()
    for i in schedule_data.index:
        if schedule_data.loc[i]['Unir'] != '-':
            ids = schedule_data.loc[i]['Grupo'] + '_' + schedule_data.loc[i]['Asignatura'] + '_' + schedule_data.loc[i][
                'Orden'], \
                  schedule_data.loc[i]['Unir'] + '_' + schedule_data.loc[i]['Asignatura'] + '_' + schedule_data.loc[i][
                      'Orden']
            groups_to_join_ids.append(ids)

    return groups_to_join_ids


def groups_constraint_by_teacher(schedule_data, teacher):
    """

    :param schedule_data:
    :param teacher:
    """

    schedule_teacher = schedule_data.loc[(schedule_data['Profesor'] == teacher)
                                         & (schedule_data['Unir'] == '-')].reset_index(drop='index')

    if len(schedule_teacher) != 1:
        return [schedule_teacher.loc[activity]['Grupo'] + '_' + schedule_teacher.loc[activity]['Asignatura']
                + '_' + schedule_teacher.loc[activity]['Orden'] for activity in schedule_teacher.index]


def groups_with_teacher_constraint(schedule_data):
    '''

    :param schedule_data:
    :return: (list) Ids (Grupo_Asignatura_Orden) that can't be together at the same
                    time in the schedule because are taught by the same teacher
    '''

    teachers = pd.unique(schedule_data['Profesor'])
    ids_constraint_teacher = list()
    for teacher in teachers:
        ids = groups_constraint_by_teacher(schedule_data, teacher)
        if ids is not None:
            ids_constraint_teacher.append(ids)
    return ids_constraint_teacher


def activities_different_days(schedule_data):
    '''

    :param schedule_data:
    :return:
    '''
    groups = set(schedule_data['Grupo'])
    ids_act_diff_days = []
    for group in groups:
        group_activities = schedule_data.loc[schedule_data['Grupo'] == group].reset_index(drop='index')
        subjects_of_group = set(group_activities['Asignatura'])
        for subject in subjects_of_group:
            group_subject = group_activities.loc[group_activities['Asignatura'] == subject].reset_index(drop='index')
            for g_s in range(len(group_subject)):
                for g_s2 in range(g_s + 1, len(group_subject)):
                    ids_act_diff_days.append(
                        (group_subject.loc[g_s]['Grupo'] + '_' + group_subject.loc[g_s]['Asignatura']
                         + '_' + group_subject.loc[g_s]['Orden'],
                         group_subject.loc[g_s2]['Grupo'] + '_' + group_subject.loc[g_s2]['Asignatura']
                         + '_' + group_subject.loc[g_s2]['Orden']))
    return ids_act_diff_days


def activities_order(schedule_data):
    groups = set(schedule_data['Grupo'])
    ids_act_order = []
    for group in groups:
        group_activities = schedule_data.loc[schedule_data['Grupo'] == group].reset_index(drop='index')
        subjects_of_group = set(group_activities['Asignatura'])
        for subject in subjects_of_group:
            group_subject = group_activities.loc[group_activities['Asignatura'] == subject].sort_values(
                by='Orden').reset_index(drop='index')
            for g_s in range(len(group_subject) - 1):
                ids_act_order.append(
                    (group_subject.loc[g_s]['Grupo'] + '_' + group_subject.loc[g_s]['Asignatura']
                     + '_' + group_subject.loc[g_s]['Orden'],
                     group_subject.loc[g_s + 1]['Grupo'] + '_' + group_subject.loc[g_s + 1]['Asignatura']
                     + '_' + group_subject.loc[g_s + 1]['Orden']))
    return ids_act_order


def count_classes_per_year(schedule_data):
    classes_per_year = list()

    for year in range(1, 6):
        data = schedule_data.loc[schedule_data['Año'] == str(year)]
        count = 0
        if len(data) > 0:
            n_groups = len(data.groupby(['Grupo']).count().index)
            count = int(data.groupby(['Grupo', 'Asignatura']).count()['Tipo'].sum() / n_groups)
        classes_per_year.append((year, count))

    return classes_per_year


def count_available_slots_per_year(general_constraint):
    available_slots_per_year = list()
    count_gen_const = len(general_constraint.loc[general_constraint['Año'] == '-'])

    for year in range(1, 6):
        count_year = len(general_constraint.loc[general_constraint['Año'] == str(year)])
        available_slots_per_year.append((year, STANDARD_WEEK_SLOTS - count_gen_const - count_year))

    return available_slots_per_year


def count_opposite_session_slots(schedule_data, general_constraints):
    classes_per_year = count_classes_per_year(schedule_data)
    available_slots_per_year = count_available_slots_per_year(general_constraints)
    opposite_session_need = dict()

    for c, a in zip(classes_per_year, available_slots_per_year):
        year, classes = c
        same_year, available = a
        if year == same_year:
            sess = get_session_given_year(schedule_data, year)
            need = classes - available
            opposite_session_need[str(year)] = (sess, 0 if need < 0 else need)
        else:
            raise Exception('Exception while counting opposite session slots')

    return opposite_session_need


def get_session_given_year(schedule_data, year):
    session = None
    data = schedule_data.loc[schedule_data['Año'] == str(year)]['Sesion'].reset_index(drop='index')
    if len(data) != 0:
        session = data[0]
    return session


def get_optimization_bit_maps_same_subject_and_order(schedule_data):
    pairs = list()
    for year in schedule_data.groupby('Año').count().index:
        for subject in schedule_data.loc[schedule_data['Año'] == year].groupby('Asignatura').count().index:
            for order in schedule_data.loc[(schedule_data['Año'] == year) &
                    (schedule_data['Asignatura'] == subject)].groupby('Orden').count().index:
                data = schedule_data.loc[(schedule_data['Año'] == year) &
                                         (schedule_data['Asignatura'] == subject) &
                                         (schedule_data['Orden'] == order) &
                                         (schedule_data['Unir'] == '-')].reset_index(drop='index')
                length = len(data)
                for i in range(length):
                    for j in range(i+1, length):
                        pairs.append((data.loc[i]['Grupo'] + '_' + data.loc[i]['Asignatura'] + '_'
                                      + data.loc[i]['Orden'],
                                      data.loc[j]['Grupo'] + '_' + data.loc[j]['Asignatura'] + '_'
                                      + data.loc[j]['Orden']))
    return pairs


def get_optimization_bit_maps_same_subject_and_group(schedule_data):
    pairs = list()
    for year in pd.unique(schedule_data['Año']):
        for group in pd.unique(schedule_data.loc[schedule_data['Año'] == year]['Grupo']):
            for subject in pd.unique(schedule_data.loc[(schedule_data['Año'] == year) &
                    (schedule_data['Grupo'] == group)]['Asignatura']):
                data = schedule_data.loc[(schedule_data['Año'] == year) &
                                         (schedule_data['Asignatura'] == subject) &
                                         (schedule_data['Grupo'] == group)].reset_index(drop='index')
                length = len(data)
                for i in range(length-1):
                    pairs.append((data.loc[i]['Grupo'] + '_' + data.loc[i]['Asignatura'] + '_' + data.loc[i]['Orden'],
                                  data.loc[i+1]['Grupo'] + '_' + data.loc[i+1]['Asignatura'] + '_' + data.loc[i+1]['Orden']))
    return pairs


def get_optimization_bit_maps_first_order(schedule_data):
    arr = list()
    for i in schedule_data.loc[schedule_data['Orden'] == '1'].index:
        arr.append(schedule_data.loc[i]['Grupo'] + '_' + schedule_data.loc[i]['Asignatura'] + '_' +
                   schedule_data.loc[i]['Orden'])
    return arr
