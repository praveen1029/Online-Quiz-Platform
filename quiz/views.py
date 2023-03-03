from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import QuizSerializer,QuestionSerializer,UserRegisterSerializer,UserSerializer,UsersAnswerSerializer,UserUpdateSerializer
from .serializers import QuizDetailSerializer,QuizResultSerializer,UserStatsSerializer,QuizStatsSerializer, UserProfileSerializer,ListAnswerSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from .models import Quizzes, Question, Answer, QuizTaker, UsersAnswer, User, QuizStats, UserStats
from rest_framework import generics, status
from django.shortcuts import get_object_or_404,get_list_or_404
from rest_framework.filters import SearchFilter
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

# user register
class RegisterAPI(APIView):
    permission_classes = [AllowAny, ]
    def post(self,request,format=None):
        serializer=UserRegisterSerializer(data=request.data)
        data={}
        if serializer.is_valid():
            account=serializer.save()
            data['name']=account.name
            data['username']=account.username
            data['email']=account.email
            return Response("Registeration Successfull")
        else:
            data=serializer.errors
            return Response(data)

# Quiz Create, list Operations
class QuizCreateAPI(generics.CreateAPIView):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated,]
    def post(self, request, *args, **kwargs):
        category = request.data['category']
        title = request.data['title']
        difficulty = request.data['difficulty']
        Quizzes.objects.create(name=self.request.user, category=category, title=title,difficulty=difficulty)
        return Response("Succesfully created")
    
class QuizListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = Quizzes.objects.all()
    serializer_class = QuizSerializer
    filter_backends = [SearchFilter]
    search_fields = ['category','difficulty','date_created']


# Question Create, list Operations
class QuestionCreateAPI(generics.CreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class QuestionListAPI(APIView):
    permission_classes = [IsAuthenticated,]
    def get(self, request, format=None, **kwargs):
        quiz = Question.objects.filter(title=kwargs['title'])
        serializer = QuestionSerializer(quiz, many=True)
        return Response(serializer.data)


# Answer Create, list Operations
class AnswerCreateAPI(generics.CreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = ListAnswerSerializer

# class AnswerListAPI(APIView):
#     permission_classes = [IsAuthenticated,]
#     def get(self, request, format=None, **kwargs):
#         quiz = Answer.objects.filter(question=kwargs['question'])
#         serializer = AnswerSerializer(quiz, many=True)
#         return Response(serializer.data)


# Start Quiz operations 
class QuizDetailAPI(generics.RetrieveAPIView):
    serializer_class = QuizDetailSerializer
    permission_classes = [IsAuthenticated,]
    def get(self, *args, **kwargs):
        id = self.kwargs["id"]
        
        quiz = get_object_or_404(Quizzes, id=id)
        last_question = None
        obj, created = QuizTaker.objects.get_or_create(user=self.request.user,quiz=quiz)
        if created:
            for question in Question.objects.filter(title=quiz):
                UsersAnswer.objects.create(quiz_taker=obj, question=question)
        else:
            last_question = UsersAnswer.objects.filter(quiz_taker=obj,answer__isnull=False)
            if last_question.count() > 0:
                last_question = last_question.last().question.id
            else:
                last_question = None

        return Response({'quiz': self.get_serializer(quiz, context={'request': self.request}).data})

# save quiz answer operations
class SaveUsersAnswer(generics.UpdateAPIView):
    serializer_class = UsersAnswerSerializer

    permission_classes = [IsAuthenticated,]
    def put(self, request, *args, **kwargs):
        quiztaker_id = request.data['quiz_taker']
        question_id = request.data['question']
        answer_id = request.data['answer']

        quiztaker = get_object_or_404(QuizTaker, id=quiztaker_id)
        question = get_object_or_404(Question, id=question_id)
        answer = get_object_or_404(Answer, id=answer_id)
        if quiztaker.completed:
            return Response({
                "message": "This quiz is already complete. you can't answer any more questions"},
                status=status.HTTP_412_PRECONDITION_FAILED
            )

        obj = get_object_or_404(UsersAnswer, quiz_taker=quiztaker, question=question)
        obj.answer = answer
        obj.save()
        return Response(self.get_serializer(obj).data)


# submit quiz, create user analytics, create quiz analytics operations
class SubmitQuizAPI(generics.GenericAPIView):
    serializer_class = QuizResultSerializer
    permission_classes = [IsAuthenticated,]
    def post(self, request, *args, **kwargs):
        quiztaker_id = request.data['quiz_taker']
        quiztaker = get_object_or_404(QuizTaker, id=quiztaker_id)
        quiz = Quizzes.objects.get(id=self.kwargs['id'])
        

        if quiztaker.completed:
            return Response({
                "message": "This quiz is already complete. You can't submit again"},
                status=status.HTTP_412_PRECONDITION_FAILED
            )

        quiztaker.completed = True
        correct_answers = 0

        for users_answer in UsersAnswer.objects.filter(quiz_taker=quiztaker):
            answer = Answer.objects.get(question=users_answer.question, is_right=True)
            if users_answer.answer == answer:
                correct_answers += 1

        quiztaker.score = int(correct_answers / quiztaker.quiz.question_set.count() * 100)
        quiztaker.save()

        # create user analytics
        user_obj = get_list_or_404(QuizTaker, user=self.request.user)
        for obj in user_obj:
            if obj.completed:
                temp_obj = UserStats.objects.filter(quiz=obj.quiz.title)
                if len(temp_obj) == 0:
                    UserStats.objects.create(user=self.request.user.name, quiz=obj.quiz.title,score=obj.score)


        # create quiz analytics
        quiz_obj = get_list_or_404(Quizzes)
        for item in quiz_obj:
            stat_obj = QuizTaker.objects.filter(quiz=item )
            total_score = 0
            user_count = 0
            completed_count = 0
            passed_count = 0
            for obj in stat_obj:
                if obj.completed:
                    total_score += obj.score
                    completed_count += 1


                    if obj.score>=50:
                        passed_count +=1
                user_count += 1
                    
            if completed_count == 0:
                avg_score=0
            else:
                avg_score = total_score/completed_count

            if user_count==0:
                pass_percentage=0
            else:
                pass_percentage = (passed_count/user_count)*100
            
            try:
                temp_obj = QuizStats.objects.get(quiz=obj.quiz.title)
                if user_count != temp_obj.quiz_attempts:
                    temp_obj.quiz=obj.quiz.title
                    temp_obj.avg_score= temp_obj.avg_score
                    temp_obj.quiz_attempts = user_count
                    temp_obj.pass_percentage = temp_obj.pass_percentage
                    temp_obj.save()

            except QuizStats.DoesNotExist:
                QuizStats.objects.create(quiz=obj.quiz.title,avg_score=avg_score,quiz_attempts=user_count,pass_percentage=round(pass_percentage,2))


        return Response(self.get_serializer(quiz).data)
    

# user analytics
class UserStatsAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated,]
    def get(self, *args, **kwargs):
        quiz = UserStats.objects.filter(user=self.request.user.name)
        serializer = UserStatsSerializer(quiz, many=True)
        return Response(serializer.data)
        
                

# quiz analytics
class QuizStatsAPI(generics.ListAPIView):
    queryset = QuizStats.objects.all()
    serializer_class = QuizStatsSerializer
    permission_classes = [IsAuthenticated,]

# user profile creation
class UserProfileAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated,]
    def get(self, *args, **kwargs):
        userdata = User.objects.filter(username=self.request.user)
        serializer = UserProfileSerializer(userdata,many=True)
        return Response(serializer.data)
    
# user CRUD operatins for admin users 
class UserCreateAPI(generics.CreateAPIView): 
    permission_classes = [IsAdminUser,]
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

class ListUserAPI(generics.ListAPIView):
    permission_classes = [IsAdminUser,]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserUpdateAPI(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser,]
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer

class UserDeleteAPI(generics.DestroyAPIView):
    permission_classes = [IsAdminUser,]
    queryset = User.objects.all()
    serializer_class = UserSerializer


# logout
class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated,]

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)