from rest_framework import serializers
from .models import User, Family, FamilyMember, FamilyStory,Story, ChallengeQuestion, FamilyChallenge, ChallengeAnswer
from .models import Task , Challenge, Question
from django.contrib.auth import get_user_model

AdminUser = get_user_model()

class AdminSignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = AdminUser
        fields = ['email', 'username', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = AdminUser.objects.create_user(**validated_data)
        user.is_migepf_admin = True
        user.save()
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone_number', 'avatar', 'family_role', 'region', 'likes', 'dislikes', 'family_code']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone_number', 'avatar', 'family_role', 'region', 'likes', 'dislikes', 'family_code', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ['group_name', 'family_code', 'created_by']

class FamilyMemberSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()

    class Meta:
        model = FamilyMember
        fields = ['id', 'user', 'family', 'added_by']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserProfileSerializer(instance.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
        return super().update(instance, validated_data)

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'date', 'status', 'assigned_by', 'family', 'assigned_to']

    def validate(self, data):
        if self.context['request'].user.family_role != 'parent':
            raise serializers.ValidationError("Only parents can create or modify tasks.")
        return data


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_statement', 'answer', 'choices', 'correct_choice']

class ChallengeSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Challenge
        fields = ['id', 'title', 'question_type', 'number_of_questions', 'questions']


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['id', 'title', 'content', 'published_by', 'created_at', 'updated_at']


class ChallengeQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallengeQuestion
        fields = ['id', 'question_type', 'statement', 'choices', 'correct_answer']

class FamilyChallengeSerializer(serializers.ModelSerializer):
    questions = ChallengeQuestionSerializer(many=True, write_only=True)

    class Meta:
        model = FamilyChallenge
        fields = ['id', 'family_group', 'name', 'created_by', 'questions', 'created_at', 'updated_at']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        challenge = FamilyChallenge.objects.create(**validated_data)
        for question_data in questions_data:
            ChallengeQuestion.objects.create(challenge=challenge, **question_data)
        return challenge


class ChallengeAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallengeAnswer
        fields = ['id', 'challenge', 'question', 'answered_by', 'answer', 'is_correct', 'answered_at']


class FamilyStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyStory
        fields = ['id', 'title', 'content', 'audio_recording', 'created_by', 'family_group', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'family_group']

    def validate(self, data):
        if not data.get('content') and not data.get('audio_recording'):
            raise serializers.ValidationError("You must provide either a story text or an audio recording.")
        return data
