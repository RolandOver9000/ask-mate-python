from time import time
import connection


def sort_data_by(data, sorting='submission_time', descending=True):
    """
    Sorts a list of dictionaries by chosen key.
    :param data: list of dictionaries (e.g. questions/answers)
    :param sorting: key to sort by (default: submission_time)
    :param descending: descending or ascending order (default: descending)
    :return: sorted list of dictionaries
    """

    if sorting in ['id', 'submission_time', 'view_number', 'vote_number']:
        convert = int
    else:
        convert = str

    sorted_data = sorted(data, key=lambda k: convert(k[sorting]), reverse=descending)
    return sorted_data


def get_new_id_for(data_type):
    # retrieve last id pair from storage file
    # last id pair is a dictionary:
    # {"question": <last_question_id>, "answer": <last_answer_id>}
    last_id_pair = connection.get_last_id_pair_from_file()
    # increment datatype id by 1
    last_id_pair[data_type] += 1
    # write new id pair to storage file
    connection.write_last_id_pair_to_file(last_id_pair)
    # return new id
    return last_id_pair[data_type]


def get_new_question_data(user_inputs):
    # get new id for new question
    new_id = get_new_id_for("question")
    user_inputs["id"] = new_id

    # set default values
    user_inputs["image"] = ""
    user_inputs["submission_time"] = int(time())
    user_inputs["view_number"] = 0
    user_inputs["vote_number"] = 0

    return user_inputs
