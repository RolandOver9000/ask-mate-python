import connection
from psycopg2 import sql


@connection.connection_handler
def question(cursor, question_id):
    cursor.execute(
        """
        DELETE FROM question_tag WHERE question_id = %(question_id)s;
        DELETE FROM comment WHERE question_id = %(question_id)s;
        DELETE FROM answer WHERE question_id = %(question_id)s;
        DELETE FROM question WHERE id = %(question_id)s;
        """,
        {'question_id': question_id})


@connection.connection_handler
def answer(cursor, answer_id):
    cursor.execute("""
                   DELETE FROM comment WHERE answer_id=%(answer_id)s;
                   DELETE FROM answer WHERE id=%(answer_id)s;
                   """,
                   {'answer_id': answer_id})


@connection.connection_handler
def tag(cursor, question_id, tag_id):
    cursor.execute("""
                    DELETE FROM question_tag
                    WHERE question_id=%(question_id)s AND
                          tag_id=%(tag_id)s
                    """, {'question_id': question_id, 'tag_id': tag_id})


@connection.connection_handler
def comment(cursor, comment_id):
    cursor.execute(
        """
        DELETE FROM comment WHERE id=%(comment_id)s;    
        """,
        {'comment_id': comment_id})
