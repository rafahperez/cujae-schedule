import pandas as pd
import xml.etree.ElementTree as ET


def read_sequence(file_dir):
    '''

    :param file_dir: Name of the xml to read (Eg. 'secuencia.xml')
    :return: (pd.DataFrame) A DataFrame with the xml information
    '''

    root = ET.parse(file_dir).getroot()
    sequence = pd.DataFrame(columns=['Año', 'Sesion', 'Asignatura', 'Tipo', 'Orden'])
    index = 1
    for a in root:
        for asig in a:
            for c in asig:
                sequence.loc[index] = pd.Series([a.get('id'), a.get('sesion'), asig.get('nombre'), c.get('desc'), c.get('orden')],
                                                index=['Año', 'Sesion', 'Asignatura', 'Tipo', 'Orden'])
                index += 1
    return sequence


def read_relation(file_dir):
    '''

    :param file_dir:
    :return:
    '''

    root = ET.parse(file_dir).getroot()
    relation = pd.DataFrame(columns=['Asignatura', 'Tipo', 'Profesor', 'Grupo'])
    index = 1
    for a in root:
        for c in a:
            for g in c:
                relation.loc[index] = pd.Series([a.get('nombre'), c.get('desc'), c.get('profesor'), g.get('id')],
                                                index=['Asignatura', 'Tipo', 'Profesor', 'Grupo'])
                index += 1
    return relation


def read_union(file_dir):
    '''

    :param file_dir:
    :return:
    '''
    root = ET.parse(file_dir).getroot()
    union = pd.DataFrame(columns=['Asignatura', 'Tipo', 'Unir', 'Con'])
    index = 1
    for g in root:
        for c in g:
            union.loc[index] = pd.Series([c.get('de'), c.get('desc'), g.get('grupo'), g.get('con')], index=['Asignatura', 'Tipo', 'Unir', 'Con'])
            index += 1
    return union


def join_sequence_relation(sequence, relation):
    '''

    :param sequence:
    :param relation:
    :return:
    '''
    data = pd.DataFrame(columns=['Año', 'Sesion', 'Asignatura', 'Tipo', 'Orden', 'Profesor', 'Grupo', 'Unir'])
    k = 1
    for i in sequence.index:
        año = sequence.loc[i].Año
        sesion = sequence.loc[i].Sesion
        asig = sequence.loc[i].Asignatura
        tipo = sequence.loc[i].Tipo
        orden = sequence.loc[i].Orden
        for j in relation.loc[(relation.Asignatura == asig) & (relation.Tipo == tipo)].index:
            prof = relation.loc[j].Profesor
            grupo = relation.loc[j].Grupo
            data.loc[k] = pd.Series([año, sesion, asig, tipo, orden, prof, grupo, '-'], index=['Año', 'Sesion', 'Asignatura', 'Tipo', 'Orden', 'Profesor', 'Grupo', 'Unir'])
            k += 1
    return data


def join_union_with_data(data, union):
    for i in union.index:
        asig = union.loc[i].Asignatura
        tipo = union.loc[i].Tipo
        grupo = union.loc[i].Unir
        con = union.loc[i].Con
        for j in data.loc[(data.Asignatura == asig) & (data.Tipo == tipo) & (data.Grupo == grupo)].index:
            data.loc[j].Unir = con
    return data


def xml_to_dataframe(sequence_xml, relation_xml, union_xml):
    '''

    :param sequence_xml:
    :param relation_xml:
    :param union_xml:
    :return:
    '''

    sequence = read_sequence(sequence_xml)
    relation = read_relation(relation_xml)
    union = read_union(union_xml)
    sequence_relation = join_sequence_relation(sequence, relation)
    dataframe = join_union_with_data(sequence_relation, union)

    return dataframe


def read_general_constraints(file_dir):
    index = 1
    root = ET.parse(file_dir).getroot()
    general_constraints = pd.DataFrame(columns=['Año', 'Dia', 'Turno'])
    for constraint in root:
        day = int(constraint.get('dia')) - 1
        turno = int(constraint.get('turno'))
        año = constraint.get('año')
        general_constraints.loc[index] = pd.Series([año, day, turno], index=['Año', 'Dia', 'Turno'])
        index += 1
    return general_constraints


def read_teacher_constraints(file_dir):
    index = 1
    root = ET.parse(file_dir).getroot()
    teacher_constraints = pd.DataFrame(columns=['Profesor', 'Dia', 'Turno'])
    for constraint in root:
        prof = constraint.get('id')
        day = int(constraint.get('dia')) - 1
        turno = int(constraint.get('turno'))
        teacher_constraints.loc[index] = pd.Series([prof, day, turno], index=['Profesor', 'Dia', 'Turno'])
        index += 1
    return teacher_constraints

