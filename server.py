from flask import Flask, render_template, request, redirect, url_for
import connection
import data_manager

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
        return render_template('add-question.html', question_data={})

    # retrieve user inputs and change it to a mutable dictionary
    user_inputs_for_question = request.form.to_dict()
    new_question_data = data_manager.get_new_question_data(user_inputs_for_question)
    connection.append_data_to_file(new_question_data)

    # redirect to question url
    return redirect(url_for('display_question_and_answers', question_id=new_question_data["id"]))


@app.route('/question/<question_id>', methods=["GET", "POST"])
def display_question_and_answers(question_id):
    # get question and answer(s)
    question = connection.get_csv_data(data_id=question_id)
    answers = connection.get_csv_data(answer=True, data_id=question_id)

    # get id of last question
    latest_ids = connection.get_last_id_pair_from_file()
    last_question_id = latest_ids['question']

    if request.method == "POST":
        id_of_voted_answer = request.form["vote"]
        return redirect(url_for("update_vote_number", question_id=question_id, answer_id=id_of_voted_answer))
    return render_template('question.html', question=question, answers=answers, last_question_id=last_question_id)


@app.route("/question/<question_id>/<answer_id>/vote", methods=["GET", "POST"])
def update_vote_number(question_id, answer_id):
    """Print the question and the title with the specific answer that you want to vote.
    Buttons: Upvote, Downvote, Back
    With the Upvote, Downvote buttons, increase/decrease the "vote_number" of the anwser's dictionary and updates the
    csv file."""
    counter = 0
    question = connection.get_csv_data(data_id=question_id)
    answers = connection.get_csv_data(answer=True, data_id=answer_id)
    specified_answer = answers[int(answer_id)]
    specified_answer_copy = specified_answer.copy()
    if request.method == "POST":
        if request.form["vote"] == "Upvote":
            convert = int(specified_answer["vote_number"]) + 1
            specified_answer["vote_number"] = convert
            connection.update_data_in_file(specified_answer_copy, {"vote_number": convert}, answer=True)
        elif request.form["vote"] == "Downvote":
            convert = int(specified_answer["vote_number"]) - 1
            specified_answer["vote_number"] = convert
            connection.update_data_in_file(specified_answer_copy, specified_answer, answer=True)
        return redirect(url_for("display_question_and_answers", question_id=question_id))
    return render_template("vote.html", counter=counter, question=question, answer=specified_answer["message"])


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def route_edit(question_id):
    question_data = connection.get_csv_data(data_id=question_id)

    if request.method == 'GET':
        return render_template('add-question.html', question_data=question_data)

    user_inputs_for_question = request.form.to_dict()
    connection.update_data_in_file(question_data, user_inputs_for_question)

    return redirect(url_for('display_question_and_answers', question_id=question_id))


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def post_an_answer(question_id):
    if request.method == "POST":
        answer = request.form["get_answer"]
        answer_data = data_manager.get_new_answer_data(answer, question_id)
        connection.append_data_to_file(answer_data, True)
        return redirect(url_for('display_question_and_answers', question_id=question_id))

    else:
        question = connection.get_csv_data(data_id=question_id)
        return render_template("new_answer.html", question=question["title"], message_for_question=question["message"])


if __name__ == '__main__':
    app.run(debug=True)
