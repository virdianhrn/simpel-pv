import json
from django.contrib import messages

def messages_json(request):
    """
    Converts Django's messages framework into a JSON string
    that can be easily read by JavaScript in the template.
    """
    message_list = []
    # Use get_messages to retrieve all messages
    for message in messages.get_messages(request):
        message_list.append({
            'body': str(message),
            'tags': message.tags,
        })
    return {'messages_json': json.dumps(message_list)}