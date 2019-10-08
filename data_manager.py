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


def get_tags_counted():
    tags_counted = select.tags_counted()
    return tags_counted


@connection.connection_handler
def get_hashed_password_for(cursor, username):
    cursor.execute("""
                    SELECT password
                    FROM user_data
                    WHERE username = %(username)s
                   """,
                   {'username': username})
    hashed_password = cursor.fetchone()
    if hashed_password:
        return hashed_password['password']


@connection.connection_handler
def get_user_id_for(cursor, username):
    cursor.execute("""
                    SELECT id
                    FROM user_data
                    WHERE username = %(username)s
                   """,
                   {'username': username})
    user_data = cursor.fetchone()
    user_id = user_data['id']
    return user_id

# ------------------------------------------------------------------
# ------------------------------INSERT------------------------------
# ------------------------------------------------------------------


def insert_question(question_data):
    question_data = util.amend_user_inputs_for_question(question_data)
    insert.question(question_data)


def insert_answer(user_inputs, question_id, user_id):
    new_answer_data = util.amend_user_inputs_for_answer(question_id, user_inputs, user_id)
    insert.answer(new_answer_data)


def insert_comment(message, question_id, answer_id=None):
    new_comment_data = {
        'message': message,
        'answer_id': answer_id,
        'question_id': question_id
    }
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


def insert_user(user_data):
    user_data['password'] = util.get_hashed_password(user_data['password'])
    user_data.update({'reg_date': util.get_datetime()})
    insert.new_user(user_data)


# ------------------------------------------------------------------
# ------------------------------UPDATE------------------------------
# ------------------------------------------------------------------


def update_entry(table, entry_id, entry_updater):
    entry_updater.update({'id': entry_id})
    update.entry(table, entry_updater)


def update_comment_message(comment_data, new_comment_message):
    updated_comment = util.handle_updated_comment(comment_data, new_comment_message)
    update.entry('comment', updated_comment)


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


def get_search_results(search_phrase):
    questions = select.questions_by_search_phrase(search_phrase)
    questions = util.split_text_values_in_search_results(questions, ['title', 'message'], search_phrase)

    answers = select.answers_by_search_phrase(search_phrase)
    answers = util.split_text_values_in_search_results(answers, ['message'], search_phrase)

    answers_by_question_id = util.get_answers_by_question_id(answers)
    search_results = util.merge_answers_by_question_id_into_questions(answers_by_question_id, questions)

    return search_results


# ------------------------------------------------------------------
# ------------------------------LOGIN-------------------------------
# ------------------------------------------------------------------

def validate_user_credentials(username, password):
    hashed_password = get_hashed_password_for(username)
    if hashed_password:
        password_valid = util.verify_password(password, hashed_password)
        if password_valid:
            return True

    return False
