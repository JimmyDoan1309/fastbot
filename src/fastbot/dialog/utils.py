JOINER = '||'


def create_user_conversation_id(user_id: str, conversation_id: str):
    if conversation_id is None:
        return user_id
    return user_id+'||'+conversation_id
