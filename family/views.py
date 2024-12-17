from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, UserChallengeResult, Family, FamilyMember, FamilyMember, Task , Story, ChallengeAttempt, FamilyStory, FamilyGroup, AdminUser
from .serializers import UserSerializer, FamilySerializer, StorySerializer,FamilyMemberSerializer, FamilyMemberSerializer, UserProfileSerializer, FamilyStorySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import TaskSerializer
from rest_framework.authtoken.models import Token
from .serializers import AdminSignupSerializer, UserChallengeResultSerializer
from .models import Challenge, Question, AnswerSubmission
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
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user by email
        try:
            user = AdminUser.objects.get(email=email)
        except AdminUser.DoesNotExist:
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


class ChallengeCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        data['creator'] = request.user.id  # Add creator info
        serializer = ChallengeSerializer(data=data)
        if serializer.is_valid():
            challenge = serializer.save()
            return Response(ChallengeSerializer(challenge).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class QuestionCreateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, challenge_id):
#         try:
#             challenge = Challenge.objects.get(id=challenge_id, creator=request.user)
#         except Challenge.DoesNotExist:
#             return Response({'error': 'Challenge not found or you are not the creator.'}, status=status.HTTP_404_NOT_FOUND)

#         data = request.data
#         data['challenge'] = challenge.id  # Associate question with challenge
#         serializer = QuestionSerializer(data=data)
#         if serializer.is_valid():
#             question = serializer.save()
#             return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, challenge_id):
        try:
            # Retrieve the challenge instance
            challenge = Challenge.objects.get(id=challenge_id, creator=request.user)
        except Challenge.DoesNotExist:
            return Response({'error': 'Challenge not found or you are not the creator.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()  # Create a mutable copy of request data
        data['challenge'] = challenge.id  # Explicitly set the challenge ID
        serializer = QuestionSerializer(data=data)

        # Validate and save the question
        if serializer.is_valid():
            question = serializer.save()
            return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChallengeListView(APIView):
    def get(self, request):
        challenges = Challenge.objects.all()
        serializer = ChallengeSerializer(challenges, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class SubmitChallengeView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, challenge_id):
#         try:
#             challenge = Challenge.objects.get(id=challenge_id)
#         except Challenge.DoesNotExist:
#             return Response({'error': 'Challenge not found.'}, status=status.HTTP_404_NOT_FOUND)

#         answers = request.data.get('answers', {})  # Format: {question_id: selected_choice}
#         score = 0
#         for question in challenge.questions.all():
#             if question.id in answers and question.correct_answer == answers[question.id]:
#                 score += 1

#         # Record the result
#         result = UserChallengeResult.objects.create(
#             user=request.user,
#             challenge=challenge,
#             score=score
#         )
#         return Response(UserChallengeResultSerializer(result).data, status=status.HTTP_201_CREATED)


class CreatorStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        challenges = Challenge.objects.filter(creator=request.user)
        stats = []
        for challenge in challenges:
            stats.append({
                'title': challenge.title,
                'total_attempts': challenge.total_attempts(),
                'total_correct': challenge.total_correct()
            })
        return Response(stats, status=status.HTTP_200_OK)



class SubmitChallengeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, challenge_id):
        try:
            # Retrieve the challenge instance
            challenge = Challenge.objects.get(id=challenge_id)
        except Challenge.DoesNotExist:
            return Response({'error': 'Challenge not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get the answers from the request
        answers = request.data.get('answers', {})  # Expected format: {question_id: selected_choice}
        score = 0

        # Loop through the questions for the challenge
        for question in challenge.questions.all():
            selected_choice = answers.get(str(question.id))  # Ensure the question ID is in string format
            if selected_choice and question.correct_answer == selected_choice:
                score += 1  # Increment score if the answer is correct

        # Record the result
        result = UserChallengeResult.objects.create(
            user=request.user,
            challenge=challenge,
            score=score
        )

        return Response(UserChallengeResultSerializer(result).data, status=status.HTTP_201_CREATED)
class SubmitChallengeView(APIView):
    def post(self, request, challenge_id):
        # Fetch the challenge object
        challenge = Challenge.objects.get(id=challenge_id)
        
        # Fetch user's answers from the request
        answers = request.data.get('answers', {})

        # Initialize score
        score = 0

        # Loop through each question and check if the answer is correct
        for question_id, answer in answers.items():
            try:
                question = Question.objects.get(id=question_id, challenge=challenge)
                
                # Check if the user's answer is correct
                if question.correct_answer == answer:
                    score += 1
            except Question.DoesNotExist:
                continue

        # Save the answer submission with the calculated score
        answer_submission = AnswerSubmission.objects.create(
            user=request.user,
            challenge=challenge,
            score=score
        )

        return Response({
            "message": "Challenge submitted successfully.",
            "score": score
        }, status=status.HTTP_200_OK)