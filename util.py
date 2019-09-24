import data_manager


def add_new_tag_to_question(question_id, new_tag):
    data_manager.add_new_tag(new_tag)
    tag_id = data_manager.get_tag_id(new_tag)
    data_manager.add_tag_to_question(question_id, tag_id['id'])


def add_tag_to_question(question_id, tag_id):
    data_manager.add_tag_to_question(question_id, tag_id)