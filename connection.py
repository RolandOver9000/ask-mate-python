import csv

ANSWER_PATH = "sample_data/answer.csv"
QUESTION_PATH = "sample_data/question.csv"


def get_csv_data(answer=False, data_id=None):
    data_from_csv = []

    if answer:
        data_file_path = ANSWER_PATH
    else:
        data_file_path = QUESTION_PATH

    with open(data_file_path, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            data_row = dict(row)

            if data_id and data_id == data_row['id']:
                return data_row

            data_from_csv.append(data_row)

    return data_from_csv
