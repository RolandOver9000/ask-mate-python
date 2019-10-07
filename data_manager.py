import connection
import util
from queries import select, insert, update, delete

# ------------------------------------------------------------------
# ------------------------------SELECT------------------------------
# ------------------------------------------------------------------


def get_all_questions(order_by, order):
    questions = select.all_questions(order_by, order, )
    return questions


def get_single_question(question_id):
    question = select.single_question(question_id, )
    return question


def get_most_recent_questions(number_of_entries=5):
    questions = select.most_recent_questions(number_of_entries)
    return questions


def get_answers_for_question(question_id):
    answers = select.answers_for_question(question_id)
    return answers


def get_all_comments(comment_id):
    comment_data = select.all_comments(comment_id)
    return comment_data


def get_latest_id(table):
    latest_id = select.latest_id(table)
    return latest_id


def get_question_ids():
    question_ids = select.all_question_ids()
    return question_ids


def get_single_entry(table, entry_id):
    entry = select.single_entry(table, entry_id)
    return entry


def get_tags_for_question(question_id):
    tags = select.tags_for_question(question_id)
    return tags


def get_existing_tags_for_question(question_id):
    existing_tags = select.existing_tags_for_question(question_id)
    return existing_tags


# ------------------------------------------------------------------
# ------------------------------INSERT------------------------------
# ------------------------------------------------------------------


def insert_question(question_data):
    question_data = util.amend_user_inputs_for_question(question_data)
    insert.question(question_data)


def insert_answer(user_inputs, question_id):
    new_answer_data = util.amend_user_inputs_for_answer(question_id, user_inputs)
    insert.answer(new_answer_data)


def insert_comment(new_comment_data):
    new_comment_data = util.amend_user_inputs_for_comment(new_comment_data)
    insert.comment(new_comment_data)


def handle_tag(question_id, new_tag, existing_tag_id):
    if new_tag == '':
        insert.tag_into_question_table(question_id, existing_tag_id)
        return

    if util.not_duplicate_tag(new_tag):
        insert.tag_into_tag_table(new_tag)

    tag_id = select.tag_id(new_tag)
    insert.tag_into_question_table(question_id, tag_id)


# ------------------------------------------------------------------
# ------------------------------UPDATE------------------------------
# ------------------------------------------------------------------


def update_entry(table, entry_id, entry_updater):
    entry_updater.update({'id': entry_id})
    update.entry(table, entry_updater)


def increment_view_number(question_id):
    update.increment_view_number(question_id)


def handle_votes(vote_option, message_id, message_type):
    vote_calculation = 'vote_number + 1' if vote_option == 'Upvote' else 'vote_number - 1'
    table = 'answer' if message_type == 'answer' else 'question'
    update.votes(vote_calculation, message_id, table)

# ------------------------------------------------------------------
# ------------------------------DELETE------------------------------
# ------------------------------------------------------------------


def delete_question(question_id):
    delete.question(question_id)


def delete_answer(answer_id):
    delete.answer(answer_id)


def delete_tag(question_id, tag_id):
    delete.tag(question_id, tag_id)


def delete_comment(comment_id):
    delete.comment(comment_id)


# ------------------------------------------------------------------
# ------------------------------SEARCH------------------------------
# ------------------------------------------------------------------


@connection.connection_handler
def select_questions_by_search_phrase(cursor, search_phrase):
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
def select_answers_by_search_phrase(cursor, search_phrase):
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


def split_text_values_in_search_results(search_results, text_keys, search_phrase):
    for search_result in search_results:
        for text_key in text_keys:
            text = search_result[text_key]
            if search_phrase.lower() in text.lower():
                search_result[text_key] = util.split_text_at_substring_occurrences(search_phrase, text)
            elif text_key == 'title':
                search_result[text_key] = [text]
            else:
                search_result[text_key] = []
    return search_results


def handle_questions_by_search_phrase(search_phrase):
    questions = select_questions_by_search_phrase(search_phrase)
    questions = split_text_values_in_search_results(questions, ['title', 'message'], search_phrase)
    return questions


def handle_answers_by_search_phrase(search_phrase):
    answers = select_answers_by_search_phrase(search_phrase)
    answers = split_text_values_in_search_results(answers, ['message'], search_phrase)
    return answers


def get_search_results(search_phrase):
    questions = handle_questions_by_search_phrase(search_phrase)
    answers = handle_answers_by_search_phrase(search_phrase)
    answers_by_question_id = util.get_answers_by_question_id(answers)
    search_results = util.merge_answers_by_question_id_into_questions(answers_by_question_id, questions)
    return search_results
