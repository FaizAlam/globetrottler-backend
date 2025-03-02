from django.urls import path
from .views import (
    RegisterUserView, RandomQuestionView, SubmitAnswerView, GenerateInviteView, LeaderBoardDataView, ViewInviteView, UserDataView
)
urlpatterns = [
    path("user/register/", RegisterUserView.as_view(), name="register"),
    path("random_question/", RandomQuestionView.as_view(), name="random_question"),
    path("submit_answer/", SubmitAnswerView.as_view(), name="submit_answer"),
    path("leaderboard/", LeaderBoardDataView.as_view(), name="leaderboard"),
    path("invite/", GenerateInviteView.as_view(), name="invite"),
    path("invite/<str:username>/", ViewInviteView.as_view() , name="view_invite"),
    path('user/', UserDataView.as_view(), name="user_data")
]
