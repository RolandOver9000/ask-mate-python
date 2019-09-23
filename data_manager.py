from time import time
import connection
import util
from psycopg2 import sql
from datetime import datetime


@connection.connection_handler
def get_all_questions(cursor, order_by='submission_time', order='DESC'):
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
        WHERE question_id = %(question_id)s;
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
    question_data['submission_time'] = datetime.now()
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


def update_id_pair_in_file():
    new_id_pair = {
        'question': connection.get_latest_id_from_csv(),
        'answer': connection.get_latest_id_from_csv(answer=True)
    }
    connection.write_last_id_pair_to_file(new_id_pair)


def write_new_question_data_to_file(user_inputs, new_id):

    new_question_data = {
        'id': new_id,
        'submission_time': int(time()),
        'view_number': -1,
        'vote_number': 0
    }
    new_question_data.update(user_inputs)
    connection.append_data_to_file(new_question_data)


@connection.connection_handler
def write_new_answer_data_to_table(cursor, user_inputs, question_id):
    cursor.execute("""
                    INSERT INTO answer (submission_time, vote_number, question_id, message, image)
                    VALUE (%(submission_time)s, %(vote_number)s, %(question_id)s, %(new_answer)s, %(image)s)
                    """,
                   {
                    'submission_time': datetime.now(),
                    'vote_number': 0,
                    'question_id': question_id,
                    'new_answer': user_inputs['message'],
                    'image': user_inputs['image']
                    })


def get_question_data_with_incremented_view_number(question_id):
    question_data = connection.get_single_data_entry(question_id)
    new_view_number = int(question_data['view_number']) + 1
    question_data['view_number'] = str(new_view_number)
    update_data_entry_in_file(question_id, {'view_number': str(new_view_number)})
    return question_data


def delete_question_from_file(question_id):

    question_csv_data = connection.get_csv_data()
    question_csv_data = util.get_reduced_data_rows(question_id, question_csv_data)
    connection.overwrite_file(question_csv_data)

    answer_csv_data = connection.get_csv_data(answer=True)
    answer_csv_data = util.get_reduced_data_rows(question_id, answer_csv_data, deleting_answers_for_question=True)
    connection.overwrite_file(answer_csv_data, answer=True)


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


def update_data_entry_in_file(data_id, data_updater, answer=False):

    csv_data = connection.get_csv_data(answer=answer)

    for data_index, data_entry in enumerate(csv_data):
        if data_entry['id'] == data_id:
            updated_data_entry = data_entry
            updated_data_entry.update(data_updater)
            csv_data[data_index] = updated_data_entry
            break

    connection.overwrite_file(csv_data, answer=answer)


def get_sorted_questions(order_by, order_direction):
    questions = connection.get_csv_data()
    answers = connection.get_csv_data(answer=True)
    amended_questions = util.merge_answer_count_into_questions(questions, answers)
    sorted_questions = util.sort_data_by(amended_questions, order_by, order_direction)
    sorted_questions = util.unix_to_readable(sorted_questions)
    return sorted_questions


def get_answers_readable(question_id):
    answers = connection.get_answers_for_question(question_id)
    readable_timestamp_answers = util.unix_to_readable(answers)
    return readable_timestamp_answers


@connection.connection_handler
def handle_votes(cursor, vote_option, message_id, message_type):
    """
    :param cursor:
    :param vote_option:
    :param message_id:
    :param message_type:
    :return:
    """
    print("bejön")
    vote_calculation = 'vote_number + 1' if vote_option == 'Upvote' else 'vote_number - 1'
    table = 'answer' if message_type == 'answer' else 'question'
    print(vote_calculation, table)
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
    :return:
    """
    cursor.execute("""
                   SELECT question_id, COUNT(question_id)
                   FROM answer
                   GROUP BY question_id
                   ORDER BY question_id;
                   """)

    answer_count = cursor.fetchall()
    return answer_count
