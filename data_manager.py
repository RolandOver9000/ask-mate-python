from time import time
import connection
import util
from psycopg2 import sql
from datetime import datetime


@connection.connection_handler
def get_all_questions(cursor, order_by, order):
    """
    :param cursor: SQL cursor from @connection.connection_handler
    :param order_by:
    :param order:
    :return:
    """
    cursor.execute(
            sql.SQL("""
                    SELECT * FROM question
                    ORDER BY {order_by} {order}
                   """).format(order_by=sql.Identifier(order_by), order=sql.SQL(order)))
    questions = cursor.fetchall()
    # calling this function will add a new key to the questions that contains the amount of answers
    add_answer_count_to_question(questions)
    return questions


@connection.connection_handler
def get_single_question(cursor, question_id):
    cursor.execute(
        """
        SELECT * FROM question
        WHERE id = %(question_id)s
        """,
        {'question_id': question_id}
    )
    question = cursor.fetchone()
    return question


@connection.connection_handler
def get_answers_for_question(cursor, question_id):
    cursor.execute(
        """
        SELECT * FROM answer
        WHERE question_id = %(question_id)s
        ORDER BY id;
        """,
        {'question_id': question_id}
    )
    answers_for_question = cursor.fetchall()
    return answers_for_question


@connection.connection_handler
def delete_question(cursor, question_id):
    cursor.execute(
        """
        DELETE FROM answer
        WHERE question_id = %(question_id)s;
        """,
        {'question_id': question_id}
    )
    cursor.execute(
        """
        DELETE FROM question
        WHERE id = %(question_id)s;
        """,
        {'question_id': question_id}
    )


@connection.connection_handler
def insert_question(cursor, question_data):
    question_data['submission_time'] = datetime.now().replace(microsecond=0)
    question_data['view_number'] = 0
    question_data['vote_number'] = 0
    cursor.execute(
        """
        INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
        VALUES (%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s);
        """,
        question_data
    )


@connection.connection_handler
def get_latest_id(cursor, table):
    cursor.execute(sql.SQL("SELECT id FROM {} ORDER BY id DESC LIMIT 1;").format(
        sql.Identifier(table)
    ))
    entry_data = cursor.fetchone()
    return entry_data['id']


@connection.connection_handler
def update_entry(cursor, table, entry_id, entry_updater):
    """

    :param cursor:
    :param table:
    :param entry_id:
    :param entry_updater:
    :return:
    """
    entry_updater.update({'id': entry_id})
    query = sql.SQL("UPDATE {} SET {} WHERE id = {}").format(
        sql.Identifier(table),
        sql.SQL(', ').join([
            sql.SQL(' = ').join([sql.Identifier(key), sql.Placeholder(key)])
            for key in entry_updater.keys()
        ]),
        sql.Placeholder('id')
    )
    cursor.execute(
        query,
        entry_updater
    )


@connection.connection_handler
def get_question_ids(cursor):
    cursor.execute(
        """
        SELECT id FROM question
        ORDER BY id;
        """
    )
    questions = cursor.fetchall()
    return [question['id'] for question in questions]


@connection.connection_handler
def increment_view_number(cursor, question_id):
    cursor.execute(
        """
        UPDATE question
        SET view_number = view_number + 1
        WHERE id = %(question_id)s;
        """,
        {'question_id': question_id}
    )


@connection.connection_handler
def write_new_answer_data_to_table(cursor, user_inputs, question_id):
    cursor.execute("""
                    INSERT INTO answer (submission_time, vote_number, question_id, message, image)
                    VALUES (%(submission_time)s, %(vote_number)s, %(question_id)s, %(new_answer)s, %(image)s)
                    """,
                   {
                    'submission_time': datetime.now(),
                    'vote_number': 0,
                    'question_id': question_id,
                    'new_answer': user_inputs['message'],
                    'image': user_inputs['image']
                    })


@connection.connection_handler
def delete_answer(cursor, answer_id):
    # delete comments to answer from comment table
    cursor.execute("""
                   DELETE FROM comment
                   WHERE answer_id=%(answer_id)s
                   """, {'answer_id': answer_id})
    # delete answer from answer table
    cursor.execute("""
                   DELETE FROM answer
                   WHERE id=%(answer_id)s
                   """, {'answer_id': answer_id})


@connection.connection_handler
def handle_votes(cursor, vote_option, message_id, message_type):
    """
    Check if the "message_type" is question or answer, and updates the votes for the given answer/question by writing
    and updates the SQL table.
    :param cursor:
    :param vote_option:  ("Upvote" or "Downvote"[str])
    :param message_id:   (id of question/answer[str])
    :param message_type: ("answer" or "question"[str])
    :return:
    """
    vote_calculation = 'vote_number + 1' if vote_option == 'Upvote' else 'vote_number - 1'
    table = 'answer' if message_type == 'answer' else 'question'
    cursor.execute(
        sql.SQL("""
                    UPDATE {table}
                    SET vote_number={vote_calculation}
                    WHERE id={message_id}
                    """)
        .format(table=sql.Identifier(table),
                vote_calculation=sql.SQL(vote_calculation),
                message_id=sql.SQL(message_id))
                )


@connection.connection_handler
def get_answer_count(cursor):
    """
    Counts the answers for every question.
    :return: answer_count (list of dict)
    """
    cursor.execute("""
                   SELECT question_id, COUNT(question_id)
                   FROM answer
                   GROUP BY question_id
                   ORDER BY question_id;
                   """)

    answer_count = cursor.fetchall()
    return answer_count


def add_answer_count_to_question(questions):
    """
    Adds an answer count key to the questions dictionary.
    :param questions: list of dicts of questions.
    """
    answer_count = get_answer_count()
    for question in questions:
        question['answer_count'] = 0
        for count in answer_count:
            if question['id'] == count['question_id']:
                question['answer_count'] = count['count']


@connection.connection_handler
def get_answer(cursor, answer_id):
    cursor.execute(
        """
        SELECT * FROM answer
        WHERE id = %(answer_id)s
        """,
        {'answer_id': answer_id}
    )
    answer = cursor.fetchone()
    return answer
