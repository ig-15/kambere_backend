from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, Family, FamilyMember, FamilyMember, ChallengeAnswer,  FamilyChallenge,Task , Story, ChallengeAttempt, FamilyStory, FamilyGroup
from .serializers import UserSerializer, FamilySerializer, StorySerializer, ChallengeAnswerSerializer,FamilyMemberSerializer, FamilyMemberSerializer, UserProfileSerializer, FamilyStorySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import TaskSerializer, FamilyChallengeSerializer
from rest_framework.authtoken.models import Token
from .serializers import AdminSignupSerializer
from .models import Challenge, Question
from .serializers import ChallengeSerializer, QuestionSerializer
from django.db.models import Count
from rest_framework import serializers



from rest_framework_simplejwt.tokens import RefreshToken

class AdminSignupView(APIView):
    def post(self, request):
        serializer = AdminSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'status': 201,
                'message': "Admin created successfully, login to continue.",
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminLoginView(APIView):
    def post(self, request):
        username_or_email = request.data.get('username_or_email')
        password = request.data.get('password')
        user = authenticate(username=username_or_email, password=password)
        print(password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class SignupView(APIView):
    def post(self, request):
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            if data.get('family_role') == 'parent':
                print("hello")
                family = Family.objects.create(group_name=data.get('group_name'), created_by=user)
                family.save()
                family_member = FamilyMember.objects.create(user=user, family=family)
                print(family_member)
                family_member.save()
                fam_grp = FamilyGroup.objects.create(group_name=data.get('group_name'), family_code=family.family_code)
                fam_grp.save()
                user.family_code = family.family_code
                user.save()
            elif data.get("family_role") == 'child':
                print("hello")
                family = Family.objects.all().filter(family_code=data.get('family_code'))
                family_member = FamilyMember.objects.create(user=user, family=family[0])
                print(family_member)
                family_member.save()
                user.family_code = data.get("family_code")
                user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class LoginView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         password = request.data.get('password')
#         user = authenticate(email=email, password=password)
#         if user:
#             return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
#         return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

# class LoginView(APIView):
#     def post(self, request):
#         # Retrieve login credentials
#         email_or_username = request.data.get('email_or_username')
#         password = request.data.get('password')

#         if not email_or_username or not password:
#             return Response({'error': 'Email/Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Authenticate user using either email or username
#         try:
#             user = User.objects.get(email=email_or_username)
#         except User.DoesNotExist:
#             try:
#                 user = User.objects.get(username=email_or_username)
#             except User.DoesNotExist:
#                 return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

#         # Validate the password
#         if user.check_password(password):
#             return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
#         else:
#             return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
class LoginView(APIView):
    def post(self, request):
        email_or_username = request.data.get('email_or_username')
        password = request.data.get('password')

        if not email_or_username or not password:
            return Response({'error': 'Email/Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user by email or username
        try:
            user = User.objects.get(email=email_or_username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=email_or_username)
            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if user.check_password(password):
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful',
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    # def get_object(self):
    #     print(self.request.user)
    #     return self.request.user
    def get_object(self):
        user = self.request.user
        if user.is_authenticated:
            return user
        else:
            return Response({"detail": "User not found", "code": "user_not_found"}, status=status.HTTP_401_UNAUTHORIZED)


class FamilyMembersView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FamilyMemberSerializer

    def get_queryset(self):
        user = self.request.user
        print(user)
        print(FamilyMember.objects.all())
        u = User.objects.all().filter(email=user)
        print(u[0].family_code)
        fam = Family.objects.all().filter(family_code=u[0].family_code)
        fam_members = FamilyMember.objects.all().values()
        print(fam_members)
        return FamilyMember.objects.all().filter(family=fam[0])

    def perform_create(self, serializer):
        parent = self.request.user
        family = parent.created_family
        serializer.save(family=family, added_by=parent)

class UpdateFamilyMemberView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FamilyMemberSerializer
    queryset = FamilyMember.objects.all()



class TaskListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        # Parents see tasks they created, children see all family tasks
        parent = self.request.user
        print(parent)
        user = User.objects.all().filter(email=parent)
        print(user)
        family = Family.objects.all().filter(family_code=user[0].family_code)
        if user[0].family_role == 'parent':
            return Task.objects.filter(family=family[0])
        return Task.objects.filter(family__members__user=user)

    def perform_create(self, serializer):
        parent = self.request.user
        print(parent)
        user = User.objects.all().filter(email=parent)
        print(user)
        family = Family.objects.all().filter(family_code=user[0].family_code)
        print(family)
        serializer.save(family=family[0], assigned_by=parent.family_role)

class TaskUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(family__members__user=self.request.user)

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        user = self.request.user

        # Children can only update status
        if user.family_role == 'child':
            if request.data.get('status') in ['completed', 'in_progress']:
                task.status = request.data['status']
                task.save()

                # Delete task if both parent and child complete it
                if task.status == 'completed' and request.data['status'] == 'completed':
                    task.delete()
                    return Response({'message': 'Task completed and deleted.'}, status=status.HTTP_204_NO_CONTENT)

            return Response({'message': 'Status updated.'}, status=status.HTTP_200_OK)
        return super().update(request, *args, **kwargs)

class ChallengeListCreateView(ListCreateAPIView):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    permission_classes = [IsAuthenticated]

class ChallengeDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    permission_classes = [IsAuthenticated]


class SubmitChallengeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, challenge_id):
        try:
            challenge = Challenge.objects.get(id=challenge_id)
        except Challenge.DoesNotExist:
            return Response({"error": "Challenge not found"}, status=status.HTTP_404_NOT_FOUND)

        user_answers = request.data.get('answers', {})
        questions = challenge.questions.all()
        correct_answers = 0

        for question in questions:
            if question.question_type == 'multiple-choice':
                if question.correct_choice == user_answers.get(str(question.id)):
                    correct_answers += 1
            else:
                if question.answer.lower() == user_answers.get(str(question.id), "").lower():
                    correct_answers += 1

        score = {
            "correct_answers": correct_answers,
            "total_questions": questions.count(),
            "percentage": (correct_answers / questions.count()) * 100,
        }

        return Response(score, status=status.HTTP_200_OK)

class AddQuestionToChallengeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, challenge_id):
        try:
            challenge = Challenge.objects.get(id=challenge_id)
        except Challenge.DoesNotExist:
            return Response({"error": "Challenge not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        serializer = QuestionSerializer(data=data)
        if serializer.is_valid():
            serializer.save(challenge=challenge)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoryListCreateView(ListCreateAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]  # Ensure only logged-in admins can access

class StoryDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]

class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Total number of users
        total_users = User.objects.count()

        # Challenge analytics
        total_challenges = ChallengeAttempt.objects.count()
        completed_challenges = ChallengeAttempt.objects.filter(completed=True).count()
        incomplete_challenges = total_challenges - completed_challenges

        return Response({
            "total_users": total_users,
            "total_challenges": total_challenges,
            "completed_challenges": completed_challenges,
            "incomplete_challenges": incomplete_challenges,
        })


class FamilyChallengeListCreateView(ListCreateAPIView):
    queryset = FamilyChallenge.objects.all()
    serializer_class = FamilyChallengeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter challenges for the family group of the logged-in user
        return FamilyChallenge.objects.filter(family_group=self.request.user.family_group)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class FamilyChallengeDetailView(RetrieveUpdateDestroyAPIView):
    queryset = FamilyChallenge.objects.all()
    serializer_class = FamilyChallengeSerializer
    permission_classes = [IsAuthenticated]



class ChallengeAnswerListCreateView(ListCreateAPIView):
    queryset = ChallengeAnswer.objects.all()
    serializer_class = ChallengeAnswerSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Check if answer is correct
        question = serializer.validated_data['question']
        answer = serializer.validated_data['answer']
        is_correct = question.correct_answer == answer
        serializer.save(answered_by=self.request.user, is_correct=is_correct)

    def get_queryset(self):
        # Show answers for the family group
        return ChallengeAnswer.objects.filter(challenge__family_group=self.request.user.family_group)



class FamilyStoryListCreateView(ListCreateAPIView):
    queryset = FamilyStory.objects.all()
    serializer_class = FamilyStorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):

        family_member = FamilyMember.objects.filter(user=self.request.user).first()
        if family_member:
            family_group = FamilyGroup.objects.filter(family_code=family_member.family.family_code)
            return FamilyStory.objects.filter(family_group=family_group[0])
        return FamilyStory.objects.none()
    
    def perform_create(self, serializer):
        print(self.request.user)
        print("Hello")
        family_member = FamilyMember.objects.filter(user=self.request.user).first()
        print(family_member)
        if not family_member:
            raise serializers.ValidationError("User is not part of any family group.")
        
        print(family_member.family)

        family_group = FamilyGroup.objects.filter(family_code=family_member.family.family_code)
        if(len(family_group) == 0):
            print("No family group")
        print(family_group[0])
        
        serializer.save(
        created_by=self.request.user,
        family_group=family_group[0])
    

    # def get_queryset(self):
    #     # Filter stories to those within the user's family group
    #     return FamilyStory.objects.filter(family_group=self.request.user.family_group)

    # def perform_create(self, serializer):
    #     serializer.save(created_by=self.request.user, family_group=self.request.user.family_group)

    

class FamilyStoryDetailView(RetrieveUpdateDestroyAPIView):
    queryset = FamilyStory.objects.all()
    serializer_class = FamilyStorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FamilyStory.objects.filter(family_group=self.request.user.family_group)
