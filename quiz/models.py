from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, name, username, email, password, **extra_fields):
        user = self.model(name=name, username=username, email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.full_clean()
        user.save()
        return user

    def create_superuser(self, name, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have staff priviledges')
        return self.create_user(name, username, email, password, **extra_fields)



class User(AbstractBaseUser):
    first_name =None
    last_name =None
    name = models.CharField( max_length=100)
    email = models.EmailField( unique=True)
    username = models.CharField( unique=True, max_length=100)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'email']

    objects = CustomUserManager()
        
    def __str__(self):
        return self.username

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, perm, obj=None):
        return True
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
    

class Quizzes(models.Model):
    SCALE = (
        (1, 'Beginner'),
        (2, 'Intermediate'),
        (3, 'Advanced')
    )
    name = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    category = models.CharField(max_length=255)
    title = models.CharField(max_length=255,unique=True)
    difficulty = models.IntegerField(choices=SCALE, default=1)
    date_created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class Question(models.Model):

    title = models.ForeignKey(Quizzes, on_delete=models.DO_NOTHING)
    question = models.CharField(max_length=255)
    def __str__(self):
        return self.question


class Answer(models.Model):

    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    option = models.CharField(max_length=255)
    is_right = models.BooleanField(default=False)

    def __str__(self):
        return self.option
    
class QuizTaker(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    quiz = models.ForeignKey(Quizzes, on_delete=models.DO_NOTHING)
    score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email


class UsersAnswer(models.Model):
    quiz_taker = models.ForeignKey(QuizTaker, on_delete=models.DO_NOTHING)
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    answer = models.ForeignKey(Answer, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return str(self.question)
    

class UserStats(models.Model):
    user = models.CharField(max_length=255)
    quiz = models.CharField(max_length=255)
    score = models.IntegerField(default=0)
    def __str__(self):
        return self.user


class QuizStats(models.Model):
    quiz = models.CharField(max_length=255,default="")
    avg_score = models.IntegerField(default=0)
    quiz_attempts = models.IntegerField(default=0)
    pass_percentage = models.IntegerField(default=0)
    def __str__(self):
        return self.quiz


