import pandas as pd
from util import *
import xml.etree.ElementTree as et


def read_sequence(sequence_xml_dir):
    """

    :param sequence_xml_dir: Path of the sequence.xml to read (Eg. 'secuencia.xml')
    :return: (pd.DataFrame) A DataFrame with the sequence.xml information
    """

    root = et.parse(sequence_xml_dir).getroot()
    sequence = pd.DataFrame(columns=[YEAR, SESSION, SUBJECT, TYPE, ORDER])
    index = 1
    for year in root:
        for subject in year:
            for c in subject:
                sequence.loc[index] = pd.Series([year.get('id'), year.get('sesion'), subject.get('nombre'),
                                                 c.get('desc'), c.get('orden')],
                                                index=[YEAR, SESSION, SUBJECT, TYPE, ORDER])
                index += 1
    return sequence


def read_relation(relation_xml_dir):
    """

    :param relation_xml_dir: Path of the relation.xml to read (Eg. 'relacion.xml')
    :return: (pd.DataFrame) A DataFrame with the relation.xml information
    """

    root = et.parse(relation_xml_dir).getroot()
    relation = pd.DataFrame(columns=[YEAR, SUBJECT, TYPE, TEACHER, GROUP])
    index = 1
    for year in root:
        for subject in year:
            for c in subject:
                for group in c:
                    relation.loc[index] = pd.Series([year.get('id'), subject.get('nombre'), c.get('desc'), c.get('profesor'),
                                                     group.get('id')], index=[YEAR, SUBJECT, TYPE, TEACHER, GROUP])
                    index += 1
    return relation


def read_union(union_xml_dir):
    """

    :param union_xml_dir: Path of the union.xml to read (Eg. 'union.xml')
    :return: (pd.DataFrame) A DataFrame with the union.xml information
    """

    root = et.parse(union_xml_dir).getroot()
    union = pd.DataFrame(columns=[SUBJECT, TYPE, JOIN, WITH])
    index = 1
    for groups in root:
        for c in groups:
            union.loc[index] = pd.Series([c.get('de'), c.get('desc'), groups.get('grupo'), groups.get('con')],
                                         index=[SUBJECT, TYPE, JOIN, WITH])
            index += 1
    return union


def read_general_constraints(general_constr_xml_dir):
    """

    :param general_constr_xml_dir: Path of the general_constraint.xml to read (Eg. 'restriccion_general.xml')
    :return: (pd.DataFrame) A DataFrame with the general_constraint.xml information
    """

    index = 1
    root = et.parse(general_constr_xml_dir).getroot()
    general_constraints = pd.DataFrame(columns=[YEAR, DAY, SLOT])
    for constraint in root:
        day = int(constraint.get('dia')) - 1
        turn = int(constraint.get('turno'))
        year = constraint.get('año')
        general_constraints.loc[index] = pd.Series([year, day, turn], index=[YEAR, DAY, SLOT])
        index += 1
    return general_constraints


def read_teacher_constraints(teacher_constr_xml_dir):
    """

    :param teacher_constr_xml_dir: Path of the teacher_constraint.xml to read (Eg. 'restriccion_profesor.xml')
    :return: (pd.DataFrame) A DataFrame with the teacher_constraint.xml information
    """
    index = 1
    root = et.parse(teacher_constr_xml_dir).getroot()
    teacher_constraints = pd.DataFrame(columns=[TEACHER, DAY, SLOT])
    for constraint in root:
        teacher_id = constraint.get('id')
        day = int(constraint.get('dia')) - 1
        turn = int(constraint.get('turno'))
        teacher_constraints.loc[index] = pd.Series([teacher_id, day, turn], index=[TEACHER, DAY, SLOT])
        index += 1
    return teacher_constraints


def join_sequence_relation(sequence, relation):
    '''

    :param sequence: DataFrame with the sequence information
    :param relation: DataFrame with the relation information
    :return: (pd.DataFrame) DataFrame obtained after joining sequence DataFrame and relation DataFrame
    '''
    sequence_relation = pd.DataFrame(columns=[YEAR, SESSION, SUBJECT, TYPE, ORDER,
                                              TEACHER, GROUP, JOIN])
    index = 1
    for i in sequence.index:
        year = sequence.loc[i][YEAR]
        session = sequence.loc[i][SESSION]
        subject = sequence.loc[i][SUBJECT]
        type = sequence.loc[i][TYPE]
        order = sequence.loc[i][ORDER]
        for j in relation.loc[(relation[YEAR] == year) &
                (relation[SUBJECT] == subject) &
                (relation[TYPE] == type)].index:
            teacher = relation.loc[j][TEACHER]
            group = relation.loc[j][GROUP]
            sequence_relation.loc[index] = pd.Series([year, session, subject, type, order, teacher, group, '-'],
                                                     index=[YEAR, SESSION, SUBJECT, TYPE, ORDER,
                                                            TEACHER, GROUP, JOIN])
            index += 1
    return sequence_relation


def join_union_with_sequence_relation(sequence_relation, union):
    """

    :param sequence_relation: DataFrame with the joined information of sequence and relation
    :param union: DataFrame with the union information
    :return: (pd.DataFrame) DataFrame obtained after joining sequence_relation DataFrame and union DataFrame
    """
    for i in union.index:
        subject = union.loc[i][SUBJECT]
        type_ = union.loc[i][TYPE]
        group = union.loc[i][JOIN]
        con = union.loc[i][WITH]
        for j in sequence_relation.loc[(sequence_relation[SUBJECT] == subject)
                                       & (sequence_relation[TYPE] == type_)
                                       & (sequence_relation[GROUP] == group)].index:
            sequence_relation.loc[j][JOIN] = con
    return sequence_relation


def xml_to_dataframe(sequence_xml, relation_xml, union_xml):
    '''

    :param sequence_xml: Path of the sequence.xml to read (Eg. 'secuencia.xml')
    :param relation_xml: Path of the relation.xml to read (Eg. 'relacion.xml')
    :param union_xml: Path of the union.xml to read (Eg. 'union.xml')
    :return: (pd.DataFrame) Final DataFrame with all the joined information.
    '''

    sequence = read_sequence(sequence_xml)
    relation = read_relation(relation_xml)
    union = read_union(union_xml)
    sequence_relation = join_sequence_relation(sequence, relation)
    dataframe = join_union_with_sequence_relation(sequence_relation, union)

    return dataframe




