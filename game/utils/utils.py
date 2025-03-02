
import json
from .redis_utils import RedisClient

# from ..questions import globetrotter_expanded_dataset
def load_questions_from_file():
    try:
        dataset_path = "D:\proj\gaming_backend\globetrotter_backend\game\questions\globetrotter_expanded_dataset.json"
        with open(dataset_path, "r") as f:
            destinations = json.load(f)

        redis_client = RedisClient()
        for destination in destinations:
            city_key = f"question:{destination['city']}"
            mapping = {
                "clues": json.dumps(destination["clues"]),
                "fun_fact": json.dumps(destination["fun_fact"]),
                "trivia": json.dumps(destination["trivia"]),
                "country": destination["country"]
            }


            redis_client.push_to_hset(city_key, mapping)

    except Exception as e:
        print("Error loading questions from file", str(e))