import data_manager
from datetime import datetime


def add_new_tag_to_question(question_id, new_tag):
    if not_duplicate_tag(new_tag):
        data_manager.add_new_tag(new_tag)
    tag_id = data_manager.get_tag_id(new_tag)
    add_tag_to_question(question_id, tag_id['id'])


def add_tag_to_question(question_id, tag_id):
    data_manager.add_tag_to_question(question_id, tag_id)


def not_duplicate_tag(tag_text):
    existing_tags = data_manager.get_existing_tags(-1)
    for tag in existing_tags:
        if tag_text == tag['name']:
            return False
    return True


def handle_updated_comment(comment_data, updated_comment_message):
    updated_comment = {'message': updated_comment_message,
                       'submission_time': datetime.now().replace(microsecond=0),
                       'edited_count': comment_data['edited_count'] + 1}
    return updated_comment


def sort_search_results(results):
    sorted_results = sorted(results, key=lambda k: k['q_time'], reverse=True)
    return sorted_results


def highlight_search_result(search_results, highlight):
    for result in search_results:
        for key in result:
            try:
                if highlight.lower() in result[key]:
                    result[key] = result[key].replace(highlight.lower(), f'<em>{highlight.lower()}</em>')
                elif highlight.upper() in result[key]:
                    result[key] = result[key].replace(highlight.upper(), f'<em>{highlight.upper()}</em>')
                elif highlight.title() in result[key]:
                    result[key] = result[key].replace(highlight.title(), f'<em>{highlight.title()}</em>')
            except (TypeError, AttributeError):
                continue
    return search_results


def handle_search(search_phrase):
    search_results = data_manager.get_questions_by_search_phrase(search_phrase)
    sorted_search_results = sort_search_results(search_results)
    hl_sorted_search_results = highlight_search_result(sorted_search_results, search_phrase)
    return hl_sorted_search_results


def emphasize(substr, text):
    current = 0
    while True:
        try:
            left = text[current:].lower().index(substr.lower()) + current
        except (ValueError, IndexError):
            break
        right = left + len(substr)
        text = text[:left] + '<em>' + text[left:right] + '</em>' + text[right:]
        current = right + len('<em></em>')
    return text


def highlight_search_phrase_in_search_results(questions, search_phrase):
    for question in questions:
        for text in ('title', 'message', 'a_message'):
            if question[text]:
                question[text] = emphasize(search_phrase, question[text])
    return questions


def get_answers_by_question_id(questions):
    answers_by_question_id = {}

    for question in questions:
        question_id = question['id']

        if question_id not in answers_by_question_id:
            answers_by_question_id[question_id] = []

        if question['a_id']:
            answers_by_question_id[question_id].append(
                {'id': question['a_id'], 'message': question['a_message']})

    return answers_by_question_id


def remove_duplicate_questions_from_search_results(questions):
    questions_orig = [dict(question) for question in questions]
    question_ids = set()
    for question in questions_orig:
        if question['id'] in question_ids:
            questions.remove(question)
        else:
            question_ids.add(question['id'])
    return questions
