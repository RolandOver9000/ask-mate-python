import connection
from psycopg2 import sql


@connection.connection_handler
def entry(cursor, table, entry_updater):
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
def votes(cursor, vote_calculation, message_id, table):
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
def accepted_answer(cursor, question_id, answer_id):
    cursor.execute(
        sql.SQL("""
                    UPDATE question
                    SET accepted_answer_id={answer_id}
                    WHERE id={question_id}
                    """)
        .format(answer_id=sql.SQL(answer_id),
                question_id=sql.SQL(question_id))
                )
