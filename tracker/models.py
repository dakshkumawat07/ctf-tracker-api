from django.contrib.auth.models import User
from django.db import models


class Event(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="events",
    )
    name = models.CharField(max_length=200)
    platform = models.CharField(max_length=100, blank=True)
    event_date = models.DateField(null=True, blank=True)
    url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Challenge(models.Model):
    class Category(models.TextChoices):
        WEB = "web", "Web"
        CRYPTO = "crypto", "Crypto"
        PWN = "pwn", "Pwn"
        REVERSE = "reverse", "Reverse"
        FORENSICS = "forensics", "Forensics"
        MISC = "misc", "Misc"

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="challenges",
    )
    title = models.CharField(max_length=200)
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.MISC,
    )
    points = models.PositiveIntegerField(default=0)
    solved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Writeup(models.Model):
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name="writeups",
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    tools_used = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
