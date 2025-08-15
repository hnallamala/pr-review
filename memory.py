import json

def get_user_memory(redis_client, user_id):
    key = f"user:{user_id}:history"
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return []

def update_user_memory(redis_client, user_id, user_input, bot_response):
    key = f"user:{user_id}:history"
    history = get_user_memory(redis_client, user_id)
    history.append({"user": user_input, "bot": bot_response})
    redis_client.set(key, json.dumps(history)) 