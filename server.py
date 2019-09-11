from flask import Flask, render_template, request, redirect, url_for
import connection
import data_manager
import util

app = Flask(__name__)


@app.route("/")
@app.route("/list")
def route_list():
    questions = connection.get_csv_data()

    if request.args:
        sorting_method, sorting_order = request.args.get('sorting').split('.')
    else:
        sorting_method, sorting_order = 'submission_time', 'desc'

    if sorting_order == 'desc':
        descending = True
    else:
        descending = False

    sorted_questions = util.sort_data_by(questions, sorting=sorting_method, descending=descending)
    sorted_questions = util.unix_to_readable(sorted_questions)
    return render_template('list.html', sorted_questions=sorted_questions,
                           selected_sorting=sorting_method, selected_order=sorting_order)


@app.route("/add-question", methods=['GET', 'POST'])
def route_add():

    if request.method == 'GET':
        return render_template('add-question.html', question_data={})

    user_inputs_for_question = request.form.to_dict()
    new_id = data_manager.get_new_id_for("question")
    data_manager.write_new_question_data_to_file(user_inputs_for_question, new_id)

    return redirect(url_for('display_question_and_answers', question_id=new_id))


@app.route('/question/<question_id>', methods=["GET", "POST"])
def display_question_and_answers(question_id):
    # get question and answer(s)
    question_data = connection.get_csv_data(data_id=question_id)
    answers_data = connection.get_csv_data(answer=True, data_id=question_id)

    # get ids of all questions as a list for 'next/previous question' links
    question_ids = connection.get_list_of_ids()

    if request.method == "POST":
        id_of_voted_answer = request.form["vote"]
        return redirect(url_for("update_vote_number", question_id=question_id, answer_id=id_of_voted_answer))

    data_manager.increment_view_number(question_data)

    return render_template('question.html', question=question_data, answers=answers_data, question_ids=question_ids)


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
    data_manager.update_question_data_in_file(question_id, user_inputs_for_question)

    return redirect(url_for('display_question_and_answers', question_id=question_id))


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def post_an_answer(question_id):
    if request.method == "POST":
        user_inputs_for_answer = request.form.to_dict()
        answer_data = data_manager.get_new_answer_data(user_inputs_for_answer, question_id)
        connection.append_data_to_file(answer_data, True)
        return redirect(url_for('display_question_and_answers', question_id=question_id))
    else:
        question = connection.get_csv_data(data_id=question_id)
        return render_template("new_answer.html", question=question)


@app.route('/question/<question_id>/delete')
def route_delete(question_id):

    # delete question and answer(s) from file
    data_manager.delete_question_from_file(question_id)

    # update 'last id pair' file
    new_id_pair = {'question': connection.get_latest_id_from_csv(),
                   'answer': connection.get_latest_id_from_csv(answer=True)}
    connection.write_last_id_pair_to_file(new_id_pair)

    return redirect(url_for('route_list'))


if __name__ == '__main__':
    app.run(debug=True)
