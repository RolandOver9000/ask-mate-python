import connection
from psycopg2 import sql


@connection.connection_handler
def all_questions(cursor, order_by, order):
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
def single_question(cursor, question_id):
    cursor.execute(
        """
        SELECT question.*, user_data.username as username, user_data.reputation as reputation
        FROM question
        LEFT JOIN user_data ON question.user_id = user_data.id
        WHERE question.id = %(question_id)s
        """,
        {'question_id': question_id}
    )
    question = cursor.fetchone()
    return question


@connection.connection_handler
def most_recent_questions(cursor, number_of_entries):
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
def answers_for_question(cursor, question_id):
    cursor.execute(
        """
        SELECT answer.*, user_data.username as username, user_data.reputation as reputation
        FROM answer
        LEFT JOIN question ON answer.id = question.accepted_answer_id
        LEFT JOIN user_data ON answer.user_id = user_data.id
        WHERE question_id = %(question_id)s
        ORDER BY question.accepted_answer_id, submission_time desc;
        """,
        {'question_id': question_id}
    )
    answers = cursor.fetchall()
    return answers


@connection.connection_handler
def all_comments(cursor, comment_id):
    cursor.execute(
        sql.SQL("""
                    SELECT comment.id as id, question_id, answer_id, message, submission_time,
                           COALESCE(edited_count, 0) AS edited_count, user_id, ud.username as username, ud.reputation as
                           reputation
                    FROM comment
                    LEFT JOIN user_data ud on comment.user_id = ud.id
                    WHERE question_id = {comment_id}
                    ORDER BY submission_time DESC
                    """).format(comment_id=sql.SQL(comment_id)))
    comment_data = cursor.fetchall()
    return comment_data


@connection.connection_handler
def latest_id(cursor, table):
    cursor.execute(sql.SQL("SELECT id FROM {} ORDER BY id DESC LIMIT 1;").format(
        sql.Identifier(table)
    ))
    entry_data = cursor.fetchone()
    return entry_data['id']


@connection.connection_handler
def all_question_ids(cursor):
    cursor.execute(
        """
        SELECT id FROM question
        ORDER BY id;
        """
    )
    questions = cursor.fetchall()
    return [question['id'] for question in questions]


@connection.connection_handler
def single_entry(cursor, table, entry_id):
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
def tags_for_question(cursor, question_id):
    cursor.execute("""
                    SELECT id, name
                    FROM tag
                    JOIN question_tag as qt on tag.id = qt.tag_id
                    WHERE qt.question_id = %(question_id)s
                    """, {'question_id': question_id})
    tags = cursor.fetchall()
    return tags


@connection.connection_handler
def existing_tags_for_question(cursor, question_id):
    cursor.execute("""
                    SELECT id, name
                    FROM tag
                    WHERE tag.id not in (SELECT tag_id
                    FROM question_tag
                    WHERE question_id=%(question_id)s)
                    ORDER BY id
                    """, {'question_id': question_id})
    existing_tags = cursor.fetchall()
    return existing_tags


@connection.connection_handler
def tag_id(cursor, tag_text):
    cursor.execute("""
                    SELECT id
                    FROM tag
                    WHERE name=%(tag_text)s
                    """, {'tag_text': tag_text})
    tag = cursor.fetchone()
    return tag['id']


@connection.connection_handler
def questions_by_search_phrase(cursor, search_phrase):
    search_phrase = '%' + search_phrase.lower() + '%'
    cursor.execute(
        """
        SELECT DISTINCT q.id, q.submission_time, q.title, q.message
        FROM question q
        LEFT JOIN answer a on q.id = a.question_id
        WHERE
            LOWER(q.title) LIKE %(search_phrase)s OR
            LOWER(q.message) LIKE %(search_phrase)s OR
            LOWER(a.message) LIKE %(search_phrase)s
        ORDER BY q.submission_time DESC
        """,
        {'search_phrase': search_phrase}
    )
    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def answers_by_search_phrase(cursor, search_phrase):
    search_phrase = '%' + search_phrase.lower() + '%'
    cursor.execute(
        """
        SELECT a.question_id, a.id, a.message, a.submission_time
        FROM answer a
        WHERE LOWER(a.message) LIKE %(search_phrase)s
        ORDER BY a.question_id
        """,
        {'search_phrase': search_phrase}
    )
    answers = cursor.fetchall()
    return answers


@connection.connection_handler
def tags_counted(cursor):
    cursor.execute("""
                    SELECT tag.name, COUNT(question_id) as count
                    FROM tag
                    RIGHT JOIN question_tag qt on tag.id = qt.tag_id
                    GROUP BY tag.name
                    """)
    tags_counted_ = cursor.fetchall()
    return tags_counted_


@connection.connection_handler
def hashed_password_for(cursor, username):
    cursor.execute("""
                    SELECT password
                    FROM user_data
                    WHERE username = %(username)s
                   """,
                   {'username': username})
    user_data = cursor.fetchone()
    if user_data:
        return user_data['password']


@connection.connection_handler
def get_user_id_by_username(cursor, username):
    cursor.execute("""
                    SELECT id
                    FROM user_data
                    WHERE username = %(username)s
                   """,
                   {'username': username})
    user_data = cursor.fetchone()
    if user_data:
        return user_data['id']


@connection.connection_handler
def user_id_for_question(cursor, question_id):
    cursor.execute(
        """
        SELECT user_id
        FROM question
        WHERE id = %(question_id)s
        """,
        {'question_id': question_id}
    )
    question_data = cursor.fetchone()
    return question_data['user_id']


@connection.connection_handler
def user_id_for_answer(cursor, answer_id):
    cursor.execute("""
                    SELECT user_id
                    FROM answer
                    WHERE id = %(answer_id)s
                    """, {'answer_id': answer_id})
    answer_data = cursor.fetchone()
    return answer_data['user_id']


@connection.connection_handler
def user_id_for_comment(cursor, comment_id):
    cursor.execute("""
                    SELECT user_id
                    FROM comment
                    WHERE id = %(comment_id)s
                    """, {'comment_id': comment_id})
    comment_data = cursor.fetchone()
    return comment_data['user_id']


@connection.connection_handler
def questions_by_user_id(cursor, user_id):
    cursor.execute(
        """
        SELECT id, title, submission_time
        FROM question
        WHERE user_id = %(user_id)s
        ORDER BY submission_time DESC
        """,
        {'user_id': user_id}
    )
    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def answers_by_user_id(cursor, user_id):
    cursor.execute(
        """
        SELECT
            a.id, a.message, a.submission_time, a.question_id,
            q.title AS q_title, q.submission_time AS q_submission_time
        FROM answer a
        JOIN question q on a.question_id = q.id
        WHERE a.user_id = %(user_id)s
        ORDER BY a.submission_time DESC
        """,
        {'user_id': user_id}
    )
    answers = cursor.fetchall()
    return answers


@connection.connection_handler
def comments_by_user_id(cursor, user_id):
    cursor.execute(
        """
        SELECT
            c.id, c.message, c.submission_time, c.question_id, c.answer_id,
            q.title AS q_title, q.submission_time AS q_submission_time,
            a.message AS a_message, a.submission_time AS a_submission_time
        FROM comment c
        JOIN question q on c.question_id = q.id
        LEFT JOIN answer a on c.answer_id = a.id
        WHERE c.user_id = %(user_id)s
        ORDER BY c.submission_time DESC
        """,
        {'user_id': user_id}
    )
    comments = cursor.fetchall()
    return comments


@connection.connection_handler
def user_stats(cursor):
    cursor.execute(
        """
         SELECT username,
                reputation,
                COUNT (DISTINCT answer.id) AS answer_count,
                COUNT (DISTINCT question.id) AS question_count,
                COUNT (DISTINCT comment.id) AS comment_count,
                COUNT (DISTINCT question.accepted_answer_id) AS accepted_answer_count,
                reg_date
         FROM user_data
         LEFT JOIN question
            ON user_data.id = question.user_id
         LEFT JOIN answer
            ON answer.user_id = question.user_id
         LEFT JOIN comment
            ON user_data.id = comment.user_id
         GROUP BY username, reputation, reg_date
        """)
    stats = cursor.fetchall()

    return stats

