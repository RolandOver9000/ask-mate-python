from time import time
from datetime import datetime
from psycopg2 import sql
import connection
import util
from psycopg2 import sql


@connection.connection_handler
def get_all_questions(cursor, order_by='submission_time', order='DESC'):
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


def get_new_id_for(data_type):
    """
    Gets a new id for given datatype.
    Function first retrieves the last ID pair,
    then increments the specified ID
    and finally returns it.
    :param data_type: "question" or "answer"
    :return: new id
    """

    last_id_pair = connection.get_last_id_pair_from_file()
    last_id_pair[data_type] += 1
    connection.write_last_id_pair_to_file(last_id_pair)
    return last_id_pair[data_type]


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


def write_new_answer_data_to_file(user_inputs, question_id):

    new_id = get_new_id_for('answer')

    new_answer_data = {
        'id': new_id,
        'submission_time': int(time()),
        'vote_number': 0,
        'question_id': question_id,
    }

    new_answer_data.update(user_inputs)
    connection.append_data_to_file(new_answer_data, answer=True)


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


def delete_answer_from_file(answer_id):

    answer_csv_data = connection.get_csv_data(answer=True)
    answer_csv_data = util.get_reduced_data_rows(answer_id, answer_csv_data)
    connection.overwrite_file(answer_csv_data, answer=True)


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


def handle_votes(vote_option, message_id, message_type):
    """
    Check if the "message_type" is question or answer, and updates the votes for the given answer/question by writing
    the updated data into the file.
    :param vote_option:  ("Upvote" or "Downvote"[str])
    :param message_id:   (id of question/answer[str])
    :param message_type: ("answer" or "question"[str])
    :return:
    """

    vote_calculators = {"Upvote": lambda v: v + 1, "Downvote": lambda v: v - 1}
    answer = True if message_type == "answer" else False

    data_entry = connection.get_single_data_entry(message_id, answer=answer)

    vote_number = int(data_entry["vote_number"])
    new_vote_number = vote_calculators[vote_option](vote_number)

    update_data_entry_in_file(message_id, {'vote_number': new_vote_number}, answer=answer)
