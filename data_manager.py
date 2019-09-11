from time import time
import connection


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


def write_new_question_data_to_file(user_inputs, new_id):
    """
    Updates the dictionary containing the user inputs for the newly submitted question.
    :param new_id: new id for question
    :param user_inputs: contains the key-value pairs for the new question specified by the user
    :return: the updated dictionary containing all the necessary data for the new question
    """

    new_question_data = {
        'id': new_id,
        'submission_time': int(time()),
        'view_number': -1,
        'vote_number': 0
    }

    new_question_data.update(user_inputs)

    connection.append_data_to_file(new_question_data)


def get_new_answer_data(user_inputs, question_id):
    """
    Initialize a new dictionary with the new answer data for the specific question.
    :param user_inputs: user inputs as a dictionary from the form at /new-answer
    :param question_id: id of the question to which the answer is to be posted
    :return: Filled out dictionary with the data of the new answer
    """

    answer = {}
    last_question_and_answer_id = connection.get_last_id_pair_from_file()
    last_question_and_answer_id["answer"] = last_question_and_answer_id["answer"] + 1
    connection.write_last_id_pair_to_file(last_question_and_answer_id)

    answer["id"] = last_question_and_answer_id["answer"]
    answer["submission_time"] = int(time())
    answer["vote_number"] = 0
    answer["question_id"] = question_id
    answer["message"] = user_inputs["message"]
    answer["image"] = user_inputs["image"]
    return answer


def increment_view_number(question_data):
    new_view_number = int(question_data["view_number"]) + 1
    connection.update_data_in_file(question_data, {"view_number": str(new_view_number)})


def delete_question_from_file(question_id):

    question_csv_data = connection.get_csv_data()

    for question_data in question_csv_data:
        if question_data['id'] == question_id:
            question_csv_data.remove(question_data)

    connection.overwrite_file(question_csv_data)

    answer_csv_data = connection.get_csv_data(answer=True)
    for answer_data in answer_csv_data:
        if answer_data['question_id'] == question_id:
            answer_csv_data.remove(answer_data)

    connection.overwrite_file(answer_csv_data, answer=True)


def delete_answer_from_file(answer_id):

    answer_csv_data = connection.get_csv_data(answer=True)

    for answer_data in answer_csv_data:
        if answer_data['id'] == answer_id:
            answer_csv_data.remove(answer_data)
            break

    connection.overwrite_file(answer_csv_data, answer=True)


def update_question_data_in_file(question_id, data_updater):

    question_csv_data = connection.get_csv_data()

    for data_index, question_data in enumerate(question_csv_data):
        if question_data['id'] == question_id:
            updated_question_data = question_data
            for key, value in data_updater.items():
                updated_question_data[key] = value
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
