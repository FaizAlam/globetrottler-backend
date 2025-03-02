#create a singleton class to connect to redis client and also create some wrapper functions to push data into redis

import redis
from threading import Lock
from globetrotter_backend.settings import REDIS_URL

class RedisClient:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(RedisClient, cls).__new__(cls, *args, **kwargs)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.client = redis.StrictRedis(host=REDIS_URL, port=13462, username="default",password="rNaR7ttDwpj8o4yaq5IqJNr9e1zxpEX0", decode_responses=True)

    def set(self, key, value, expiry=None):
        return self.client.set(key, value, ex=expiry)

    def get(self, key):
        return self.client.get(key)

    def delete(self, key):
        return self.client.delete(key)

    # ------ Users utility functions ------
    def user_name_exists(self, user_name):
        return self.client.hexists(f"users:{user_name}", "score")
    
    def get_all_users(self):
        return self.client.hgetall("users:*")
    
    def create_user(self, user_name):
        return self.client.hset(f"users:{user_name}", mapping={"correct_answers": 0, "incorrect_answers": 0})
    
    def increase_user_correct_count(self, user_name, score):
        return self.client.hincrby(f"users:{user_name}", "correct_answers", score)
    
    def increase_user_incorrect_count(self, user_name, score):
        return self.client.hincrby(f"users:{user_name}", "incorrect_answers", score)
    
    def get_user_correct_count(self, user_name):
        return self.client.hget(f"users:{user_name}", "correct_answers")
    
    def get_user_incorrect_count(self, user_name):
        return self.client.hget(f"users:{user_name}", "incorrect_answers")

    # ------ Questions utility functions ------
    def push_to_hset(self, key, mapping):
        return self.client.hset(key, mapping=mapping)

    def get_all_questions(self):
        return self.client.keys("question:*")
    
    def get_complete_question(self, question_id):
        return self.client.hgetall(question_id)
    
    def get_partial_question(self, question_id, fields):
        return self.client.hget(question_id, fields)


    # ------ leaderboard utility functions ------

    def get_leaderboard(self):
        return self.client.zrevrange("leaderboard", 0, -1, withscores=True)
    
    
    def get_user_rank(self, user_name):
        return self.client.zrevrank("leaderboard", user_name)
    
    def get_user_rank_and_score(self, user_name):
        return self.client.zscore("leaderboard", user_name)
    
    def get_leaderboard_range(self, start, end):
        return self.client.zrevrange("leaderboard", start, end, withscores=True)
    
    def set_in_leaderboard(self, user_name, score):
        return self.client.zadd("leaderboard", {user_name: score})
    
    def increase_leaderboard_score(self, user_name, score):
        return self.client.zincrby("leaderboard", score, user_name)
    