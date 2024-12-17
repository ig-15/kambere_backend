from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import uuid
import random
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser

# class AdminUser(AbstractUser):
#     is_migepf_admin = models.BooleanField(default=True) 
#     pass

#     class Meta:
#         verbose_name = "Admin User"
#         verbose_name_plural = "Admin Users"

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
        
class AdminUser(AbstractBaseUser):
    email= models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
class AdminUser(AbstractBaseUser):
    email= models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    family_role = models.CharField(max_length=10, choices=[('parent', 'Parent'), ('child', 'Child')])
    region = models.CharField(max_length=100, default='Rwanda')
    likes = models.TextField(blank=True)
    dislikes = models.TextField(blank=True)
    family_code = models.CharField(max_length=6, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

def generate_family_code():
    return str(random.randint(100000, 999999))

class Family(models.Model):
    group_name = models.CharField(max_length=100)
    family_code = models.CharField(max_length=6, unique=True, default=generate_family_code)
    created_by = models.OneToOneField(User, related_name='created_family', on_delete=models.CASCADE)

class FamilyMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    family = models.ForeignKey(Family, related_name='members', on_delete=models.CASCADE)
    added_by = models.ForeignKey(User, related_name='added_members', on_delete=models.SET_NULL, null=True)

class FamilyGroup(models.Model):
    group_name = models.CharField(max_length=255)
    family_code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.group_name


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(max_length=100)  # Name of the child assigned the task
    description = models.TextField()
    date = models.DateTimeField(default=now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_by = models.CharField(max_length=10, choices=[('father', 'Father'), ('mother', 'Mother')])
    family = models.ForeignKey(Family, related_name='tasks', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, related_name='tasks', on_delete=models.CASCADE)  # Assigned user (child)

    def __str__(self):
        return f"Task for {self.name}: {self.description[:30]}"


class Story(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()  # The story or article content
    published_by = models.CharField(max_length=255)  # Admin's name or username
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ChallengeAttempt(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    challenge = models.ForeignKey('Challenge', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class FamilyStory(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    audio_recording = models.FileField(upload_to='family_stories/audio/', null=True, blank=True)
    created_by = models.ForeignKey('User', on_delete=models.CASCADE)
    # family_group = models.ForeignKey('FamilyGroup', on_delete=models.CASCADE)
    family_group = models.ForeignKey(FamilyGroup, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Challenge(models.Model):
    title = models.CharField(max_length=255)
    challenge_type = models.CharField(max_length=50, choices=[('multiple_choice', 'Multiple Choice')], default='multiple_choice')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_challenges', default=1)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.title
    def total_attempts(self):
        return self.userchallengeresults.count()

    def total_correct(self):
        return self.userchallengeresults.filter(score__gt=0).count()


class Question(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='questions')
    question_statement = models.TextField()
    choices = models.JSONField()  # Stores choices as a list
    correct_answer = models.CharField(max_length=255, default="no choices provided")

    def __str__(self):
        return f"Question for {self.challenge.title}"
    
class UserChallengeResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenge_results')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='userchallengeresults')
    score = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.challenge.title} - Score: {self.score}"
    

class AnswerSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)