import csv

ANSWER_PATH = "sample_data/answer.csv"
QUESTION_PATH = "sample_data/question.csv"
LAST_ID_PAIR_PATH = "last_id_pair.txt"
ANSWER_KEYS = ("id", "submission_time", "vote_number", "question_id", "message", "image")
QUESTION_KEYS = ("id", "submission_time", "view_number", "vote_number", "title", "message", "image")


def get_data_type_info(for_answers=False):
    if for_answers:
        return {"path": ANSWER_PATH, "keys": ANSWER_KEYS}
    else:
        return {"path": QUESTION_PATH, "keys": QUESTION_KEYS}


def get_csv_data(answer=False, data_id=None):
    data_from_csv = []

    data_type_info = get_data_type_info(for_answers=answer)

    with open(data_type_info["path"], encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)

        if answer and data_id:
            for row in reader:
                data_row = dict(row)
                if data_id == data_row['question_id']:
                    data_from_csv.append(data_row)

        elif answer:
            for row in reader:
                data_row = dict(row)
                data_from_csv.append(data_row)

        else:
            for row in reader:
                data_row = dict(row)

                if data_id and data_id == data_row['id']:
                    return data_row

                data_from_csv.append(data_row)

            if data_id:
                return
    return data_from_csv


def append_data_to_file(data, answer=False):
    data_type_info = get_data_type_info(for_answers=answer)

    with open(data_type_info["path"], "a") as csv_file:
        data_writer = csv.DictWriter(csv_file, fieldnames=data_type_info["keys"])
        data_writer.writerow(data)


def get_last_id_pair_from_file():
    """
    Reads the file containing a comma-separated pair of IDs.
    This pair of IDs is the last question ID and the last answer ID, respectively.
    :return: pair of last IDs
    """

    with open(LAST_ID_PAIR_PATH, "r") as pair_txt:
        question_id, answer_id = [int(id_) for id_ in pair_txt.readline().split(",")]
        return {"question": question_id, "answer": answer_id}


def write_last_id_pair_to_file(new_id_pair):
    with open(LAST_ID_PAIR_PATH, "w") as pair_txt:
        pair_txt.write(f"{new_id_pair['question']},{new_id_pair['answer']}")


def update_data_in_file(old_data, user_inputs, answer=False):
    new_data = old_data
    for key, value in user_inputs.items():
        new_data[key] = value
    if answer:
        data_file_path = ANSWER_PATH
        data_keys = ANSWER_KEYS
    else:
        data_file_path = QUESTION_PATH
        data_keys = QUESTION_KEYS
    csv_data = get_csv_data(answer=answer)
    with open(data_file_path, "w") as csvfile:
        data_writer = csv.DictWriter(csvfile, fieldnames=data_keys)
        data_writer.writeheader()

        for data in csv_data:
            if data["id"] == new_data["id"]:
                data_writer.writerow(new_data)
            else:
                data_writer.writerow(data)


def overwrite_file(new_file_data, answer=False):

    data_type_info = get_data_type_info(for_answers=answer)

    with open(data_type_info["path"], "w") as csv_file:
        data_writer = csv.DictWriter(csv_file, fieldnames=data_type_info["keys"])
        data_writer.writeheader()
        for data in new_file_data:
            data_writer.writerow(data)


def get_latest_id_from_csv(answer=False):
    if answer:
        csv_data = get_csv_data(answer=True)
    else:
        csv_data = get_csv_data()

    if csv_data:
        return csv_data[-1]['id']
    else:
        return 0


def get_list_of_ids(answer=False):
    list_of_ids=[]
    if answer:
        csv_data = get_csv_data(answer=True)
    else:
        csv_data = get_csv_data()

    for row in csv_data:
        list_of_ids.append(row['id'])

    return list_of_ids