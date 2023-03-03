from django.urls import path
from . import views



urlpatterns = [
    path('register/',views.RegisterAPI.as_view(),name='register'),
 
    path('create/quiz/', views.QuizCreateAPI.as_view(), name='create_quiz'),
    path('quiz/', views.QuizListAPI.as_view(), name='Quiz'),

    path('create/question/', views.QuestionCreateAPI.as_view(), name='create_question'),
    path('quiz/<int:title>/', views.QuestionListAPI.as_view(), name='question'),

    path('create/answer/', views.AnswerCreateAPI.as_view(), name='create_answer'),
    # path('quiz/<int:title>/<int:question>/', views.AnswerListAPI.as_view(), name='answer'),

    path("quiz/start/<int:id>/",views.QuizDetailAPI.as_view(),name='load_user'),
    path('quiz/answer/', views.SaveUsersAnswer.as_view(), name='save_answer'),
    path("quiz/submit/<int:id>/",views.SubmitQuizAPI.as_view(),name='submit'),
    
    path('quiz/stats/', views.QuizStatsAPI.as_view(), name='quiz_stats'),
    path('user/stats/', views.UserStatsAPI.as_view(), name='user_stats'),
    path('user/profile/', views.UserProfileAPI.as_view(), name='profile'),

    path('user/create/', views.UserCreateAPI.as_view(), name='create_user'),
    path('user/list/', views.ListUserAPI.as_view(), name='user'),
    path('user/update/<int:pk>/', views.UserUpdateAPI.as_view(), name='update_quiz'),
    path('user/delete/<int:pk>/', views.UserDeleteAPI.as_view(), name='delete_quiz'),
    
    path("logout/",views.LogoutAPI.as_view(),name='logout')
]
