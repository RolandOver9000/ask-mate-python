import connection


@connection.connection_handler
def question(cursor, question_data):
    cursor.execute(
        """
        INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
        VALUES (%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s);
        """,
        question_data
    )


@connection.connection_handler
def answer(cursor, new_answer_data):
    cursor.execute("""
                    INSERT INTO answer (submission_time, vote_number, question_id, message, image, user_id)
                    VALUES (%(submission_time)s, %(vote_number)s, %(question_id)s, %(new_answer)s, %(image)s, %(user_id)s)
                    """,
                   new_answer_data)


@connection.connection_handler
def comment(cursor, new_comment_data):
    cursor.execute("""
                    INSERT INTO comment (answer_id, question_id, message, submission_time, edited_count)
                    VALUES (%(answer_id)s, %(question_id)s, %(message)s, %(submission_time)s, %(edited_count)s)
                    """,
                   new_comment_data
                   )


@connection.connection_handler
def tag_into_tag_table(cursor, tag_text):
    cursor.execute("""
                    INSERT INTO tag (name)
                    VALUES ( %(name)s)
                    """, {'name': tag_text})


@connection.connection_handler
def tag_into_question_table(cursor, question_id, tag_id):
    cursor.execute("""
                    INSERT INTO question_tag
                    VALUES (%(question_id)s, %(tag_id)s)
                    """, {'question_id': question_id, 'tag_id': tag_id})


@connection.connection_handler
def new_user(cursor, user_data):
    cursor.execute(
        """
        INSERT INTO user_data (username, password, reg_date)
        VALUES (%(username)s, %(password)s, %(reg_date)s)
        """,
        user_data
    )
