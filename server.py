from flask import \
    Flask, \
    render_template, \
    request, \
    redirect, \
    url_for, \
    session, \
    flash
import data_manager
import util

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/login', methods=['GET', 'POST'])
def route_login():
    error = None
    if request.method == 'POST':
        user_credentials = request.form.to_dict()
        if log_in_user(user_credentials):
            flash("Login successful")
            return redirect(session['url'])

        error = 'Invalid password and/or username!'
    return render_template('home/login.html', error=error)


def log_in_user(user_credentials):
    user_credentials_valid = data_manager.validate_user_credentials(user_credentials['username'],
                                                                    user_credentials['password'])
    if user_credentials_valid:
        session['username'] = user_credentials['username']
        session['user_id'] = data_manager.get_user_id_for(user_credentials['username'])
        return True
    else:
        return False


@app.route('/logout')
def route_logout():
    session.pop('username', None)
    session.pop('user_id', None)
    flash("You've logged out successfully")
    return redirect(session['url'])


@app.route('/login_or_register', methods=["GET", "POST"])
def login_or_register():
    if request.method == "POST":
        user_credentials = request.form.to_dict()
        if request.form.get('login'):
            log_in_user(user_credentials)
        elif request.form.get('register'):
            record_user(user_credentials)
            log_in_user(user_credentials)
        return redirect(session['url'])

    return render_template('home/login_or_register.html')


@app.route("/")
def route_index():
    session['url'] = url_for('route_index')
    sorted_questions = data_manager.get_most_recent_questions()

    return render_template('home/index.html', sorted_questions=sorted_questions)


@app.route("/list")
def route_list():
    """
    Retrieves sorted questions and renders template for the page that lists them.
    Sorting parameters are either retrieved from the query string generated by pressing the 'Sort' button,
        or are set to default values.
    :return: rendered template
    """

    if request.args:
        order_by = request.args.get('order_by')
        order = request.args.get('order_direction')
    else:
        order_by, order = 'submission_time', 'desc'

    sorted_questions = data_manager.get_all_questions(order_by, order)
    return render_template('home/list.html', sorted_questions=sorted_questions,
                           selected_sorting=order_by, selected_order=order)


@app.route("/add-question", methods=['GET', 'POST'])
def route_add_question():

    if request.method == 'GET':
        if 'user_id' in session:
            return render_template('database_ops/add-question.html', question_data={})
        else:
            return redirect('/')

    user_inputs_for_question = request.form.to_dict()
    data_manager.insert_question(user_inputs_for_question, session['user_id'])
    new_id = data_manager.get_latest_id('question')
    return redirect(url_for('display_question_and_answers', question_id=new_id), code=307)


@app.route('/question/<question_id>', methods=["GET", "POST"])
def display_question_and_answers(question_id):
    session['url'] = url_for('display_question_and_answers', question_id=question_id)

    if request.method == 'GET':
        # update view number for question
        data_manager.increment_view_number(question_id)

    question_ids = data_manager.get_question_ids()
    question = data_manager.get_single_question(question_id)
    answers = data_manager.get_answers_for_question(question_id)
    tags = data_manager.get_tags_for_question(question_id)
    comments = data_manager.get_all_comments(question_id)
    user_id = session.get('user_id', False)

    return render_template('display_question/question_display.html', question=question, tags=tags,
                           answers=answers, question_ids=question_ids, comments=comments, user_id=user_id)


@app.route('/question/<question_id>/vote', methods=['POST'])
def route_vote(question_id):
    vote_option, message_id, message_type = request.form['vote'].split(',')
    data_manager.handle_votes(vote_option, message_id, message_type)
    data_manager.handle_user_reputation(vote_option, message_id, message_type)

    # the code=307 argument ensures that the request type (POST) is preserved after redirection
    # so that the view number of the question doesn't increase after voting
    return redirect(url_for('display_question_and_answers', question_id=question_id), code=307)


@app.route('/question/<question_id>/<answer_id>/accepted_answer', methods=['GET'])
def route_accepted_answer(question_id, answer_id):
    data_manager.handle_accepted_answer(question_id, answer_id)
    data_manager.handle_user_reputation('accepted_answer', answer_id)

    # the code=307 argument ensures that the request type (POST) is preserved after redirection
    # so that the view number of the question doesn't increase after voting
    return redirect(url_for('display_question_and_answers', question_id=question_id))


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def route_edit_question(question_id):
    if data_manager.question_belongs_to_user(session.get('username'), question_id):
        if request.method == 'GET':
            question_data = data_manager.get_single_question(question_id)
            return render_template('database_ops/add-question.html', question_data=question_data)

        user_inputs_for_question = request.form.to_dict()
        data_manager.update_entry('question', question_id, user_inputs_for_question)

    return redirect(url_for('display_question_and_answers', question_id=question_id), code=307)


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def route_new_answer(question_id):
    """
    If the method is POST: When the user wants to submit a new answer to the specific question, this function saves the inputs into the table
    and redirect it to the page of the specific question.
    If the method is GET: It redirects you to page where you can add your inputs for answer.
    :param question_id: id integer of the specific question
    :return:
    """
    if request.method == "POST":
        user_inputs_for_answer = request.form.to_dict()
        data_manager.insert_answer(user_inputs_for_answer, question_id, session['user_id'])
        return redirect(url_for('display_question_and_answers', question_id=question_id), code=307)

    question = data_manager.get_single_question(question_id)
    return render_template("database_ops/new_answer.html", question=question)


@app.route('/question/<question_id>/delete')
def route_delete_question(question_id):
    if data_manager.question_belongs_to_user(session.get('username'), question_id):
        data_manager.delete_question(question_id)
        return redirect(url_for('route_index'))
    return redirect(url_for('display_question_and_answers', question_id=question_id))


@app.route('/question/<question_id>/<answer_id>/delete')
def route_delete_answer(question_id, answer_id):
    if data_manager.answer_belongs_to_user(session.get('username'), answer_id):
        data_manager.delete_answer(answer_id)
    return redirect(url_for('display_question_and_answers', question_id=question_id))


@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
def route_edit_answer(answer_id):
    answer_data = data_manager.get_single_entry('answer', answer_id)
    question_id = answer_data.get('question_id')
    question_data = data_manager.get_single_entry('question', question_id)

    if data_manager.answer_belongs_to_user(session.get('username'), answer_id):

        if request.method == 'GET':
            return render_template('database_ops/new_answer.html', answer=answer_data, question=question_data)

        user_inputs_for_answer = request.form.to_dict()
        data_manager.update_entry('answer', answer_id, user_inputs_for_answer)

    return redirect(url_for('display_question_and_answers', question_id=question_id), code=307)


@app.route('/question/<question_id>/new-tag', methods=["GET", "POST"])
def route_new_tag(question_id):
    existing_tags = data_manager.get_existing_tags_for_question(question_id, )

    if request.method == "POST":
        new_tag = request.form.get('new_tag')
        existing_tag_id = request.form.get('existing_tag')
        data_manager.handle_tag(question_id, new_tag, existing_tag_id)
        return redirect(url_for('display_question_and_answers', question_id=question_id), code=307)

    if data_manager.question_belongs_to_user(session.get('username'), question_id):
        return render_template('database_ops/new_tag.html', existing_tags=existing_tags)


@app.route('/question/<question_id>/tag/<tag_id>/delete')
def route_delete_tag(question_id, tag_id):
    if data_manager.question_belongs_to_user(session.get('username'), question_id):
        data_manager.delete_tag(question_id, tag_id)

    return redirect(url_for('display_question_and_answers', question_id=question_id))


@app.route('/answer/<question_id>/<answer_id>/new_comment', methods=["GET", "POST"])
def route_add_comment_to_answer(question_id, answer_id):
    """
    It redirects you to the page where you can add your inputs for comment, it also shows you the answer that you want to
    comment.
    :param question_id: id integer of the specific question
    :param answer_id: id integer of the specific answer
    :return:
    """
    if request.method == "GET":
        answer_by_id = data_manager.get_single_entry('answer', answer_id)
        return render_template('database_ops/new_comment.html', answer_by_id=answer_by_id)

    # After you submit your comment for the specific answer
    # this program part will make a dictionary with the inputs and
    # insert it as a row in the table of comments.
    # After this process it redirects you to the specific page of the question.

    comment_message = request.form['message']
    user_id = session['user_id']
    data_manager.insert_comment(comment_message, question_id, answer_id=answer_id, user_id=user_id)
    return redirect(url_for('display_question_and_answers', question_id=question_id), code=307)


@app.route('/question/<question_id>/new-comment', methods=["GET", "POST"])
def route_add_comment_to_question(question_id):
    if request.method == 'GET':
        question = data_manager.get_single_entry('question', question_id)
        return render_template('database_ops/new_comment.html', answer_by_id=question)

    user_id = session['user_id']
    comment_message = request.form['message']
    data_manager.insert_comment(comment_message, question_id, user_id)

    return redirect(url_for('display_question_and_answers', question_id=question_id), code=307)


@app.route('/search')
def route_search():
    search_phrase = request.args.get('search_phrase')
    search_results = data_manager.get_search_results(search_phrase)
    return render_template('search/search_results.html', questions=search_results, search_phrase=search_phrase)


@app.route('/tags')
def route_tags():
    tags_counted = data_manager.get_tags_counted()
    return render_template('home/tags.html', tags_counted=tags_counted)


@app.route('/comment/<comment_id>/delete', methods=["GET", "POST"])
def route_delete_comment(comment_id):
    comment = data_manager.get_single_entry('comment', comment_id)
    if data_manager.comment_belongs_to_user(session.get('username'), comment_id):
        answer_id_of_comment = comment['answer_id']
        question_id_of_comment = comment['question_id']

        if request.method == "GET":
            if answer_id_of_comment:
                answer_data = data_manager.get_single_entry('answer', answer_id_of_comment)
                return render_template('database_ops/delete_comment.html', answer=answer_data['message'], comment=comment)
            question_data = data_manager.get_single_entry('question', question_id_of_comment)
            return render_template('database_ops/delete_comment.html', question=question_data, comment=comment)

        if request.form['delete-button'] == 'Yes':
            data_manager.delete_comment(comment_id)

    return redirect(url_for('display_question_and_answers', question_id=comment['question_id']), code=307)


@app.route('/comments/<comment_id>/edit', methods=["GET", "POST"])
def route_edit_comment(comment_id):
    comment_data = data_manager.get_single_entry('comment', comment_id)
    question_id = comment_data.get('question_id')

    if data_manager.comment_belongs_to_user(session.get('username'), comment_id):
        question_data = data_manager.get_single_entry('question', question_id)
        answer_data = None
        if comment_data['answer_id']:
            answer_id = comment_data['answer_id']
            answer_data = data_manager.get_single_entry('answer', answer_id)

        if request.method == 'GET':
            return render_template('database_ops/new_comment.html', comment=comment_data, answer=answer_data, question=question_data)

        new_comment_message = request.form['message']
        data_manager.update_comment_message(comment_data, new_comment_message)

    return redirect(url_for('display_question_and_answers', question_id=question_id), code=307)


@app.route('/register', methods=['GET', 'POST'])
def route_register():
    if request.method == 'POST':
        user_data = request.form.to_dict()
        if record_user(user_data):
            log_in_user(user_data)
            flash("Login successful")
        return redirect('/')

    return render_template('home/register.html')


def record_user(user_data):
    username_is_unique = data_manager.is_username_unique(user_data['username'])
    if username_is_unique:
        data_manager.insert_user(user_data)
        return True


@app.route('/user/<user_id>')
def route_user_page(user_id):
    user_id = int(user_id)
    if not ('user_id' in session and session['user_id'] == user_id):
        return redirect('/')

    user_data = data_manager.get_user_data_for_user_page(session['user_id'], session['username'])
    return render_template('user_page/main.html', user_data=user_data)


@app.route('/users')
def route_users():
    user_stats = data_manager.get_user_stats()
    return render_template('users_summary_page/main.html', user_stats=user_stats)


if __name__ == '__main__':
    app.run(debug=True)
