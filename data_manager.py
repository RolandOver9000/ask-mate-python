from time import time
import connection
import util


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


def increment_view_number(question_data):
    new_view_number = int(question_data["view_number"]) + 1
    update_question_data_in_file(question_data['id'], {"view_number": str(new_view_number)})


def get_reduced_data_rows(data_id, data_rows, deleting_answers_for_question=False):
    if deleting_answers_for_question:
        for data in [dict(data_orig) for data_orig in data_rows]:
            if data['question_id'] == data_id:
                data_rows.remove(data)
        return data_rows
    else:
        for data in [dict(data_orig) for data_orig in data_rows]:
            if data['id'] == data_id:
                data_rows.remove(data)
                return data_rows


def delete_question_from_file(question_id):

    question_csv_data = connection.get_csv_data()
    question_csv_data = get_reduced_data_rows(question_id, question_csv_data)
    connection.overwrite_file(question_csv_data)

    answer_csv_data = connection.get_csv_data(answer=True)
    answer_csv_data = get_reduced_data_rows(question_id, answer_csv_data, deleting_answers_for_question=True)
    connection.overwrite_file(answer_csv_data, answer=True)


def delete_answer_from_file(answer_id):

    answer_csv_data = connection.get_csv_data(answer=True)
    answer_csv_data = get_reduced_data_rows(answer_id, answer_csv_data)
    connection.overwrite_file(answer_csv_data, answer=True)


def update_question_data_in_file(question_id, data_updater):

    question_csv_data = connection.get_csv_data()

    for data_index, question_data in enumerate(question_csv_data):
        if question_data['id'] == question_id:
            updated_question_data = question_data
            updated_question_data.update(data_updater)
            question_csv_data[data_index] = updated_question_data
            break

    connection.overwrite_file(question_csv_data)


def count_answers():
    """
    Counts the answers for every question.
    :return:
    """
    answer_count = {}
    answers = connection.get_csv_data(answer=True)
    for answer in answers:
        if answer['question_id'] in answer_count:
            answer_count[answer['question_id']] += 1
        else:
            answer_count[answer['question_id']] = 1

    return answer_count


def merge_answer_count_into_questions(questions):
    answer_count = count_answers()
    for question in questions:
        if question['id'] in answer_count:
            question['answer_number'] = answer_count[question['id']]
        else:
            question['answer_number'] = 0
    return questions


def get_sorted_questions(order_by, order_direction):
    questions = connection.get_csv_data()
    amended_questions = merge_answer_count_into_questions(questions)
    sorted_questions = util.sort_data_by(amended_questions, order_by, order_direction)
    sorted_questions = util.unix_to_readable(sorted_questions)
    return sorted_questions


def handle_votes(vote_option, message_id, message_type):
    """
    Check if the "message_type" is question or answer, and updates the votes for the given answer/question by writing
    the updated data into the file.
    :param vote_option:  (Upvote or Downvote[str])
    :param message_id:   (id of question/answer[str])
    :param message_type: (answer or question[str])
    :return:
    """
    if message_type == "answer":
        answers = connection.get_csv_data(answer=True)
        specified_answer = answers[int(message_id)]
        specified_answer_copy = specified_answer.copy()

        if vote_option == "Upvote":
            specified_answer["vote_number"] = int(specified_answer["vote_number"]) + 1
            connection.update_data_in_file(specified_answer_copy, specified_answer, answer=True)

        elif vote_option == "Downvote":
            specified_answer["vote_number"] = int(specified_answer["vote_number"]) - 1
            connection.update_data_in_file(specified_answer_copy, specified_answer, answer=True)

    elif message_type == "question":
        question_data = connection.get_csv_data(data_id=message_id)
        question_data_copy = question_data.copy()
        if vote_option == "Upvote":
            question_data["vote_number"] = int(question_data["vote_number"]) + 1
            connection.update_data_in_file(question_data_copy, question_data)
        elif vote_option == "Downvote":
            question_data["vote_number"] = int(question_data["vote_number"]) - 1
            connection.update_data_in_file(question_data_copy, question_data)