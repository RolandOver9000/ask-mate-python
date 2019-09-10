from flask import Flask, render_template, request, redirect
import csv
import time

app = Flask(__name__)

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


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def post_an_answer(question_id):

    question_data = get_csv_data(False, question_id)
    if request.method == "POST":
        answer = {}
        answer["answer_id"] = get_next_anwser_id()
        answer["submission_time"] = int(time.time())
        answer["vote_number"] = 0
        answer["question_id"] = question_data["question_id"]
        answer["message"] = request.form["get_answer"]
        return redirect("/")
    else:
        answer_for_question = get_answer_data(question_id)
        return render_template("new_answer.html", question=question_data, answer_for_question=answer_for_question)


if __name__ == "__main__":
    app.run(
        debug=True, # Allow verbose error reports
        port=5000 # Set custom port
    )