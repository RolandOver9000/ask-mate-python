from flask import Flask, render_template, request, redirect, url_for
import connection
from time import time

app = Flask(__name__)


@app.route("/")
@app.route("/list")
def route_list():
    questions_data = connection.get_csv_data()
    pass


@app.route("/add-question", methods=['GET', 'POST'])
def route_add():
    if request.method == 'GET':
        return render_template('add-question.html')

    last_id = connection.get_last_id_from_file()
    new_id = last_id + 1
    connection.write_last_id_to_file(new_id)
    new_question = {
        "id": new_id,
        "submission_time": time(),
        "view_number": 0,
        "vote_number": 0,
        "title": request.form.get("title"),
        "message": request.form.get("message")
        "image": ""
    }
    connection.append_data_to_file(new_question)
    return redirect(url_for(f"/question/{new_id}"))


@app.route('/question/<question_id>')
def display_question_and_answers(question_id):
    question_to_display = connection.get_csv_data(data_id=question_id)
    answers_to_display = connection.get_csv_data(answer=True, data_id=question_id)
    return render_template(
        'question.html',
        question_to_display=question_to_display,
        answers_to_display=answers_to_display
    )


if __name__ == '__main__':
    app.run(debug=True)
