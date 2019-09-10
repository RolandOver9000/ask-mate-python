from flask import Flask, render_template, request, redirect, url_for
import connection
import data_manager

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
@app.route("/list", methods=['GET', 'POST'])
def route_list():
    if request.method == "POST":
        return goto_sorted_url()

    questions = connection.get_csv_data()
    sorted_questions = data_manager.sort_data_by(questions)
    return render_template('list.html', sorted_questions=sorted_questions,
                           selected_sorting='submission_time', selected_order='desc')


def goto_sorted_url():
    sorting = {'sorting_method': request.form['sorting_method'].split('.')[0],
               'sorting_order': request.form['sorting_method'].split('.')[1]}
    return redirect(url_for('route_sort', sorting=sorting['sorting_method'], order=sorting['sorting_order']))


@app.route('/list?order_by=<sorting>&order_direction=<order>', methods=['GET', 'POST'])
def route_sort(sorting, order):
    if request.method == 'POST':
        return goto_sorted_url()

    if order == 'desc':
        order_by = True
    else:
        order_by = False

    questions = connection.get_csv_data()
    sorted_questions = data_manager.sort_data_by(questions, sorting=sorting, descending=order_by)
    return render_template('list.html', sorted_questions=sorted_questions,
                           selected_sorting=sorting, selected_order=order)


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


@app.route('/question/<question_id>')
def display_question_and_answers(question_id):
    # get question and answer(s)
    question = connection.get_csv_data(data_id=question_id)
    answers = connection.get_csv_data(answer=True, data_id=question_id)

    # get id of last question
    latest_ids = connection.get_last_id_pair_from_file()
    last_question_id = latest_ids['question']

    data_manager.increment_view_number(question)

    return render_template('question.html', question=question, answers=answers, last_question_id=last_question_id)


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
        user_inputs_for_answer = request.form.to_dict()
        answer_data = data_manager.get_new_answer_data(user_inputs_for_answer, question_id)
        connection.append_data_to_file(answer_data, True)
        return redirect(url_for('display_question_and_answers', question_id=question_id))
    else:
        question = connection.get_csv_data(data_id=question_id)
        return render_template("new_answer.html", question=question)


if __name__ == '__main__':
    app.run(debug=True)
