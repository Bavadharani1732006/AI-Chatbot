class Database:
    def save_chat(self, user_message, bot_response, session_id, model):
        return 1

    def save_query(self, query, category=None, user_ip=None):
        return True

    def get_chat_history(self, session_id, limit=50):
        return []

    def save_feedback(self, chat_id, rating, comment):
        return True

    def get_statistics(self):
        return {
            "total_chats": 0,
            "total_feedback": 0
        }

db = Database()
