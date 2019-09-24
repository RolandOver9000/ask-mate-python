import data_manager


def add_new_tag_to_question(question_id, new_tag):
    if not_duplicate_tag(new_tag):
        data_manager.add_new_tag(new_tag)
    tag_id = data_manager.get_tag_id(new_tag)
    add_tag_to_question(question_id, tag_id['id'])


def add_tag_to_question(question_id, tag_id):
    data_manager.add_tag_to_question(question_id, tag_id)


def not_duplicate_tag(tag_text):
    existing_tags = data_manager.get_existing_tags()
    for tag in existing_tags:
        if tag_text == tag['name']:
            return False
    return True
