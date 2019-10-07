import data_manager
import bcrypt
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


def verify_password(plain_text_password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)
