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
                     SELECT
                        question.*, 
                        (SELECT COUNT(*) FROM answer WHERE answer.question_id = question.id) AS answer_number
                     FROM question
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
def get_specific_entries(cursor, table, entry_ids):
    id_placeholders = sql.SQL("({})").format(
        sql.SQL(', ').join([sql.Placeholder() for instance in range(len(entry_ids))])
    )
    query = sql.SQL("SELECT * FROM {} WHERE id IN {}").format(
        sql.Identifier(table),
        id_placeholders
    )
    cursor.execute(
        query,
        entry_ids
    )
    entries = cursor.fetchall()
    return entries


@connection.connection_handler
def get_most_recent_questions(cursor, number_of_entries=5):
    cursor.execute(
        """
        SELECT
            question.*,
            (SELECT COUNT(id) FROM answer WHERE answer.question_id = question.id) AS answer_number
            FROM question
            ORDER BY submission_time DESC LIMIT %s;
        """,
        (number_of_entries,)
    )
    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def get_answers_for_question(cursor, question_id):
    cursor.execute(
        """
        SELECT * FROM answer
        WHERE question_id = %(question_id)s
        ORDER BY submission_time desc;
        """,
        {'question_id': question_id}
    )
    answers_for_question = cursor.fetchall()
    return answers_for_question


@connection.connection_handler
def get_all_comments(cursor, comment_id):
    cursor.execute(
        sql.SQL("""
                    SELECT id, question_id, answer_id, message, submission_time,
                           COALESCE(edited_count, 0) AS edited_count 
                    FROM comment
                    WHERE question_id = {comment_id}
                    ORDER BY submission_time DESC
                    """).format(comment_id=sql.SQL(comment_id)))
    comment_data = cursor.fetchall()
    return comment_data


@connection.connection_handler
def delete_question(cursor, question_id):
    cursor.execute(
        """
        DELETE FROM question_tag WHERE question_id = %(question_id)s;
        DELETE FROM comment WHERE question_id = %(question_id)s;
        DELETE FROM answer WHERE question_id = %(question_id)s;
        DELETE FROM question WHERE id = %(question_id)s;
        """,
        {'question_id': question_id})


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
    composable_sets = [
            sql.SQL(' = ').join([sql.Identifier(key), sql.Placeholder(key)])
            for key in entry_updater.keys()
    ]

    query = sql.SQL("UPDATE {} SET {} WHERE id = {}").format(
        sql.Identifier(table),
        sql.SQL(', ').join(composable_sets),
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
                    'submission_time': datetime.now().replace(microsecond=0),
                    'vote_number': 0,
                    'question_id': question_id,
                    'new_answer': user_inputs['message'],
                    'image': user_inputs['image']
                    })


@connection.connection_handler
def write_new_comment_data_to_table(cursor, new_comment_data):
    """
    This function is filling the leftover data for the row that you want to insert and after that insert the row
    into the table of comments.
    :param cursor:
    :param new_comment_data: dictionary where the keys are the column names
    :return:
    """
    new_comment_data['submission_time'] = datetime.now().replace(microsecond=0)
    new_comment_data['edited_count'] = 0
    cursor.execute("""
                    INSERT INTO comment (answer_id, question_id, message, submission_time, edited_count)
                    VALUES (%(answer_id)s, %(question_id)s, %(message)s, %(submission_time)s, %(edited_count)s)
                    """,
                   new_comment_data
                   )


@connection.connection_handler
def delete_answer(cursor, answer_id):
    cursor.execute("""
                   DELETE FROM comment WHERE answer_id=%(answer_id)s;
                   DELETE FROM answer WHERE id=%(answer_id)s;
                   """,
                   {'answer_id': answer_id})


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
def get_single_entry(cursor, table, entry_id):
    cursor.execute(
        sql.SQL(
            """
            SELECT * FROM {table}
            WHERE id = %(entry_id)s
            """
        ).format(table=sql.Identifier(table)),
        {'entry_id': entry_id}
    )
    entry = cursor.fetchone()
    return entry


@connection.connection_handler
def get_tags_for_question(cursor, question_id):
    cursor.execute("""
                    SELECT id, name
                    FROM tag
                    JOIN question_tag as qt on tag.id = qt.tag_id
                    WHERE qt.question_id = %(question_id)s
                    """, {'question_id': question_id})
    tags = cursor.fetchall()
    return tags


@connection.connection_handler
def get_existing_tags(cursor):
    cursor.execute("""
                    SELECT id, name
                    FROM tag
                    ORDER BY id
                    """)
    existing_tags = cursor.fetchall()
    return existing_tags


@connection.connection_handler
def get_tag_id(cursor, tag_text):
    cursor.execute("""
                    SELECT id
                    FROM tag
                    WHERE name=%(tag_text)s
                    """, {'tag_text': tag_text})
    tag_id = cursor.fetchone()
    return tag_id


@connection.connection_handler
def add_tag_to_question(cursor, question_id, tag_id):
    cursor.execute("""
                    INSERT INTO question_tag
                    VALUES (%(question_id)s, %(tag_id)s)
                    """, {'question_id': question_id, 'tag_id': tag_id})


@connection.connection_handler
def add_new_tag(cursor, tag_text):
    cursor.execute("""
                    INSERT INTO tag (name)
                    VALUES ( %(name)s)
                    """, {'name': tag_text})


@connection.connection_handler
def remove_tag(cursor, question_id, tag_id):
    cursor.execute("""
                    DELETE FROM question_tag
                    WHERE question_id=%(question_id)s AND
                          tag_id=%(tag_id)s
                    """, {'question_id': question_id, 'tag_id': tag_id})


@connection.connection_handler
def get_questions_by_search_phrase(cursor, search_phrase):
    search_phrase = '%' + search_phrase.lower() + '%'
    cursor.execute(
        """
        SELECT DISTINCT  question.id AS q_id, question.title AS q_title, question.message AS q_message, question.submission_time AS q_time,
        question.vote_number AS q_vote,
            (SELECT COUNT(id) FROM answer WHERE answer.question_id=question.id) AS answer_number
        FROM question
        FULL JOIN answer ON question.id = answer.question_id
        WHERE LOWER(question.message) LIKE %(search_phrase)s OR
              LOWER(question.title) LIKE %(search_phrase)s
        ORDER BY question.submission_time DESC
        """,
        {'search_phrase': search_phrase})
    questions = cursor.fetchall()
    cursor.execute("""
        SELECT question.id AS q_id, question.title AS q_title, answer.message AS a_message, question.submission_time AS q_time,
        answer.vote_number AS a_vote
        FROM answer
        JOIN question ON answer.question_id = question.id
        WHERE LOWER(answer.message) LIKE %(search_phrase)s
        ORDER BY answer.submission_time DESC
        """, {'search_phrase': search_phrase})
    questions += cursor.fetchall()
    return questions


@connection.connection_handler
def delete_data_by_id(cursor, table_name, row_id):
    """
    :param cursor:
    :param table_name: string of table name
    :param row_id: id integer of the row that you want to delete
    :return:
    """
    if table_name == 'question':
        cursor.execute(
            """
            DELETE FROM question_tag, comment, answer WHERE question_id = %(question_id)s;
            DELETE FROM question WHERE id = %(question_id)s;
            """,
            {'question_id': row_id})
    elif table_name == 'answer':
        cursor.execute(
            """
            DELETE FROM comment WHERE answer_id=%(answer_id)s;
            DELETE FROM answer WHERE id=%(answer_id)s;
            """,
            {'answer_id': row_id})
    elif table_name == 'comment':
        cursor.execute(
            """
            DELETE FROM comment WHERE id=%(comment_id)s;    
            """,
            {'comment_id': row_id})
