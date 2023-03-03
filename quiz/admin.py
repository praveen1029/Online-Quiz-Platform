from django.contrib import admin
from .models import Quizzes, Question, Answer, UsersAnswer, QuizTaker, User, UserStats, QuizStats
# Register your models here.

admin.site.register(User)

class AnswerAdmin(admin.StackedInline):
    model = Answer

class QuestionAdmin(admin.ModelAdmin):
    inlines=[AnswerAdmin]

admin.site.register(Quizzes)
admin.site.register(Question,QuestionAdmin)
admin.site.register(Answer)
admin.site.register(QuizTaker)
admin.site.register(UsersAnswer)
admin.site.register(UserStats)
admin.site.register(QuizStats)