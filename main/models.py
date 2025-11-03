from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username}: {self.content[:30]}"


class WorkoutLog(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    workout_type = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.username} - {self.workout_type} ({self.date})"


class Player(models.Model):
    YEAR_CHOICES = [
        ('Freshman', 'Freshman'),
        ('Sophomore', 'Sophomore'),
        ('Junior', 'Junior'),
        ('Senior', 'Senior'),
    ]

    # Roster info
    number = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=100)
    height = models.CharField(max_length=10)
    position = models.CharField(max_length=20)
    year = models.CharField(max_length=20, choices=YEAR_CHOICES)

    # Statistics
    sets_played = models.PositiveIntegerField(default=0)
    serves = models.PositiveIntegerField(default=0)
    serve_aces = models.PositiveIntegerField(default=0)
    serve_errors = models.PositiveIntegerField(default=0)
    digs = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    blocks = models.PositiveIntegerField(default=0)
    attacks = models.PositiveIntegerField(default=0)
    kills = models.PositiveIntegerField(default=0)
    attack_errors = models.PositiveIntegerField(default=0)
    receive_errors = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Profile(models.Model):
    ROLE_CHOICES = [
        ("alumni", "Alumni"),
        ("supporter", "Supporter"),
        ("player", "Player"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="supporter")

    def __str__(self):
        return f"{self.user.username} ({self.role})"


