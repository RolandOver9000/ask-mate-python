from flask import Flask, render_template, request, redirect, url_for
import connection

app = Flask(__name__)


@app.route("/")
@app.route("/list")
def route_list():
    questions_data = connection.get_csv_data()
    pass


@app.route("/add-question")
def route_add():
    pass


@app.route('/question/<question_id>')
def display_question(question_id):
    question_to_display = connection.get_csv_data(data_id=str(question_id))
    return render_template('question.html', question_to_display=question_to_display)


if __name__ == '__main__':
    app.run(debug=True)
