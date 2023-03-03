from rest_framework import serializers
from .models import Quizzes, Question, Answer,User, UserStats, QuizStats,QuizTaker, UsersAnswer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['name','username','email','password']
        
    def save(self):
        reg=User(
            name=self.validated_data['name'],
            username=self.validated_data['username'],
            email=self.validated_data['email'],
        )
        password=self.validated_data['password']        
        reg.set_password(password)
        reg.save()
        return reg


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model=Quizzes
        fields=["id",'title']
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Question
        fields='__all__'

class ListAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Answer
        fields='__all__'


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Answer
        exclude=['is_right','question']

class UserSerializer(serializers.ModelSerializer):
     class Meta:
          model=User
          fields='__all__'


class UsersAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersAnswer
        fields = "__all__"

class QuizTakerSerializer(serializers.ModelSerializer):
    usersanswer_set = UsersAnswerSerializer(many=True)

    class Meta:
        model = QuizTaker
        exclude = ['id']

class QuestionSetSerializer(serializers.ModelSerializer):
    answer_set = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id','question','answer_set']

class QuizDetailSerializer(serializers.ModelSerializer):
    quiztakers_set = serializers.SerializerMethodField()
    question_set = QuestionSetSerializer(many=True)

    class Meta:
        model = Quizzes
        fields = ['title','question_set','quiztakers_set']

    def get_quiztakers_set(self, obj):
        try:
            quiz_taker = QuizTaker.objects.get(user=self.context['request'].user, quiz=obj)
            serializer = QuizTakerSerializer(quiz_taker)
            return serializer.data
        except QuizTaker.DoesNotExist:
            return None

class ScoreTakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizTaker
        fields = ['score']


class QuizResultSerializer(serializers.ModelSerializer):
    score_out_of_100 = serializers.SerializerMethodField()

    class Meta:
        model = Quizzes
        fields = ['score_out_of_100']

    def get_score_out_of_100(self, obj):
        try:
            quiztaker = QuizTaker.objects.get(user=self.context['request'].user, quiz=obj)
            serializer = ScoreTakerSerializer(quiztaker)
            return serializer.data

        except QuizTaker.DoesNotExist:
            return None 


class UserStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStats
        exclude = ['id','user']

class QuizStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizStats
        exclude = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    quiz_set = serializers.SerializerMethodField()
    class Meta:
        model=User
        fields=['email','username','quiz_set']

    def get_quiz_set(self,obj):
            try:
                quizset = Quizzes.objects.get(name=obj.id)
            except Quizzes.DoesNotExist:
                return None
            serializer = QuizSerializer(quizset)
            return serializer.data

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['name','email','password']
