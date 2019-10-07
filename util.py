from datetime import datetime


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
