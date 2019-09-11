from datetime import datetime
from copy import deepcopy


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


def unix_to_readable(data):
    readable_data = deepcopy(data)
    for entry in readable_data:
        entry['submission_time'] = datetime.utcfromtimestamp(int(entry['submission_time'])).strftime('%Y.%m.%d %H:%M')
    return readable_data
