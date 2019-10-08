from datetime import datetime
from queries import select
from password import hash_password, verify_password


def handle_updated_comment(comment_data, updated_comment_message):
    comment_data.update({
        'message': updated_comment_message,
        'submission_time': datetime.now().replace(microsecond=0),
        'edited_count': comment_data['edited_count'] + 1})
    return comment_data


def not_duplicate_tag(tag_text):
    existing_tags = select.existing_tags_for_question(-1)
    for tag in existing_tags:
        if tag_text == tag['name']:
            return False
    return True


def amend_user_inputs_for_question(question_data):
    question_data['submission_time'] = datetime.now().replace(microsecond=0)
    question_data['view_number'] = 0
    question_data['vote_number'] = 0
    return question_data


def amend_user_inputs_for_answer(question_id, user_inputs):
    new_answer_data = {
        'submission_time': datetime.now().replace(microsecond=0),
        'vote_number': 0,
        'question_id': question_id,
        'new_answer': user_inputs['message'],
        'image': user_inputs['image']
    }
    return new_answer_data


def amend_user_inputs_for_comment(new_comment_data):
    new_comment_data['submission_time'] = datetime.now().replace(microsecond=0)
    new_comment_data['edited_count'] = 0
    return new_comment_data


def split_text_at_substring_occurrences(substr, text):
    char_seq = []
    current_split_point = 0
    text_split = []

    for i, char in enumerate(text):
        char_seq.append(char)

        if len(char_seq) < len(substr):
            continue

        if len(char_seq) > len(substr):
            del char_seq[0]

        current_substr = ''.join(char_seq)
        if current_substr.lower() == substr.lower():
            left_split_point = i - (len(substr) - 1)
            text_split.append(text[current_split_point:left_split_point])
            current_split_point = i + 1
            text_split.append(text[left_split_point:current_split_point])
        elif i == len(text) - 1:
            text_split.append(text[current_split_point:])

    return text_split


def split_text_values_in_search_results(search_results, text_keys, search_phrase):
    for search_result in search_results:
        for text_key in text_keys:
            text = search_result[text_key]
            if search_phrase.lower() in text.lower():
                search_result[text_key] = split_text_at_substring_occurrences(search_phrase, text)
            elif text_key == 'title':
                search_result[text_key] = [text]
            else:
                search_result[text_key] = []
    return search_results


def get_answers_by_question_id(answers):
    answers_by_question_id = {}
    for answer in answers:
        q_id = answer['question_id']
        if q_id in answers_by_question_id:
            answers_by_question_id[q_id].append(answer)
        else:
            answers_by_question_id[q_id] = [answer]
    return answers_by_question_id


def merge_answers_by_question_id_into_questions(answers_by_question_id, questions):
    for question in questions:
        q_id = question['id']
        if q_id in answers_by_question_id:
            question['answers'] = answers_by_question_id[q_id]
        else:
            question['answers'] = []
    return questions


def get_hashed_password(plain_text_password):
    return hash_password(plain_text_password)


def get_datetime():
    return datetime.now().replace(microsecond=0)


def is_password_valid(plain_text_password, hashed_password):
    return verify_password(plain_text_password, hashed_password)
