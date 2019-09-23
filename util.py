from datetime import datetime
from copy import deepcopy


def sort_data_by(data_rows, order_by, order_direction):
    """
    Sorts a list of dictionaries by chosen key.
    :param data_rows: list of dictionaries (e.g. questions/answers)
    :param order_by: key to sort by
    :param order_direction: "desc" (descending) or "asc" (ascending) order
    :return: sorted list of dictionaries
    """

    if order_by in ['id', 'submission_time', 'view_number', 'vote_number']:
        convert = int
    else:
        convert = str

    reverse_values = {"desc": True, "asc": False}

    return sorted(
        data_rows,
        key=lambda data_row: convert(data_row[order_by]),
        reverse=reverse_values[order_direction]
    )


def unix_to_readable(data):
    readable_data = deepcopy(data)
    for entry in readable_data:
        entry['submission_time'] = datetime.utcfromtimestamp(int(entry['submission_time'])).strftime('%Y.%m.%d. %H:%M')
    return readable_data


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