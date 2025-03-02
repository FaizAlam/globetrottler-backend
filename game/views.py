from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views import View
from game.utils.redis_utils import RedisClient
from django.utils.decorators import method_decorator
import random
import json
import uuid
from django.urls import reverse

@method_decorator(csrf_exempt, name='dispatch')
class RegisterUserView(View):
    def post(self, request):
        try:
            data = request.body.decode('utf-8')
            data = json.loads(data)
            user_name = data.get('user_name')
            assert user_name, 'user_name is required'

            redis_client = RedisClient()
            if redis_client.user_name_exists(user_name):
                return JsonResponse({'error': 'User already exists!'}, status=400)
            redis_client.create_user(user_name)
            redis_client.set_in_leaderboard(user_name, 0)
            return JsonResponse({'message': 'User created successfully!'})
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        

class RandomQuestionView(View):
    def get(self, request):
        redis_client = RedisClient()
        question_keys = redis_client.get_all_questions()
        if not question_keys:
            return JsonResponse({"error": "No questions available"}, status=404)
        
        try:
            random_question = random.choice(question_keys)
            question_data = redis_client.get_complete_question(random_question)

            clues = json.loads(question_data.get("clues"))
            correct_city = random_question.split(":")[-1]


            all_cities = [key.split(":")[1] for key in question_keys if key.split(":")[1] != correct_city]
            random_options = random.sample(all_cities, min(3, len(all_cities)))
            random_options.append(correct_city)
            random.shuffle(random_options)

            question_id = str(uuid.uuid4())
            redis_client.set(f"session_question:{question_id}", correct_city, expiry=600)

            if not clues or not correct_city or not random_options:
                return JsonResponse({"error": "Error fetching question data"}, status=500)

            clue = random.choice(clues)
            return JsonResponse({
                "question_id": question_id,
                "clue": clue,
                "options": random_options
            })
        
        except Exception as e:
            print("Error fetching random question", str)
            return JsonResponse({"error": str(e)}, status=500)
    

@method_decorator(csrf_exempt, name='dispatch')
class SubmitAnswerView(View):
    def post(self, request):
        try:
            data = request.body.decode('utf-8')
            data = json.loads(data)
            username = data.get("username")
            question_id = data.get("questionId")
            selected_answer = data.get("selectedAnswer")

            redis_client = RedisClient()
            correct_answer = redis_client.get(f"session_question:{question_id}")
            if not correct_answer:
                return JsonResponse({"error": "Session expired"}, status=400)
            
            correct = selected_answer == correct_answer
            fun_facts = redis_client.get_partial_question(f"question:{correct_answer}", "fun_fact")
            fun_facts = json.loads(fun_facts)

            if correct:
                redis_client.increase_user_correct_count(username, 1)
                redis_client.increase_leaderboard_score(username, 1)
            else:
                redis_client.increase_user_incorrect_count(username, 1)


            updated_correct_score = redis_client.get_user_correct_count(username) or 0
            updated_incorrect_score = redis_client.get_user_incorrect_count(username) or 0
            updated_score = (updated_correct_score, updated_incorrect_score)

            return JsonResponse({"correct": correct, "funFact": fun_facts if fun_facts else ["No fun fact available"],
                                 "score":{"correct": updated_score[0], "incorrect": updated_score[1]}})
        
        except Exception as e:
            print("Error submitting answer", str(e))
            return JsonResponse({"error": str(e)}, status=400)


class LeaderBoardDataView(View):
    def get(self, request):
        try:
            redis_client = RedisClient()
            top_users = redis_client.get_leaderboard_range(0, 9)
            leaderboard_data = [{"user": user, "score": score} for user, score in top_users]
            return JsonResponse(leaderboard_data)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        

class GenerateInviteView(View):
    def get(self, request):
        username = request.GET.get("username")
        score = RedisClient().get_user_correct_count(username)

        if not score:
            return JsonResponse({"error": "User not found"}, status=404)

        invite_link = f"http://localhost:3000/play/?challenge={username}"
        return JsonResponse({"inviteLink": invite_link, "score": score})

class ViewInviteView(View):
    def get(self, request, username):
        score = RedisClient().get_user_correct_count(username)
        if not score:
            return JsonResponse({"error": "User not found"}, status=404)

        return JsonResponse({"username": username, "score": score})

class UserDataView(View):
    def get(self,request):
        username = request.GET.get("username")
        redis_client = RedisClient()
        correct_score = redis_client.get_user_correct_count(username)
        incorrect_score = redis_client.get_user_incorrect_count(username)
        return JsonResponse({"correct": correct_score, "incorrect": incorrect_score})