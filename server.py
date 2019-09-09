from flask import Flask, render_template, request, redirect, url_for
import connection
import data_manager
from time import time

app = Flask(__name__)


@app.route("/")
@app.route("/list")
def route_list():
    questions = connection.get_csv_data()
    sorted_questions = data_manager.sort_data_by(questions)
    return render_template('list.html', sorted_questions=sorted_questions)


@app.route("/add-question", methods=['GET', 'POST'])
def route_add():
    # handle GET request
    if request.method == 'GET':
        return render_template('add-question.html')

    # retrieve last id pair from storage file
    # last id pair is a dictionary:
    # {"question": <last_question_id>, "answer": <last_answer_id>}
    last_id_pair = connection.get_last_id_pair_from_file()
    # increment question id by 1
    last_id_pair["question"] += 1
    # write new id pair to storage file
    connection.write_last_id_pair_to_file(last_id_pair)

    # assign incremented value to new variable name
    new_id = last_id_pair["question"]

    # initialize dictionary for new question
    new_question = {
        "id": new_id,
        "submission_time": int(time()),
        "view_number": 0,
        "vote_number": 0,
        "title": request.form.get("title"),
        "message": request.form.get("message"),
        "image": ""
    }
    # append new dictionary data to question file
    connection.append_data_to_file(new_question)

    # redirect to question url
    return redirect(f"/question/{new_id}")


@app.route('/question/<question_id>')
def display_question_and_answers(question_id):
    # get question and answer(s)
    question = connection.get_csv_data(data_id=question_id)
    answers = connection.get_csv_data(answer=True, data_id=question_id)

    return render_template('question.html', question=question, answers=answers)


if __name__ == '__main__':
    app.run(debug=True)
