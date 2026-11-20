from django.conf import settings
from django.db import models


class MemberProfile(models.Model):
    GENDER_CHOICES = [
        ("female", "Female"),
        ("male", "Male"),
        ("non_binary", "Non-binary"),
        ("prefer_not_to_say", "Prefer not to say"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_profile",
    )
    phone_number = models.CharField(max_length=30)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    gender = models.CharField(max_length=24, choices=GENDER_CHOICES)

    def __str__(self):
        full_name = self.user.get_full_name() or self.user.username
        return f"{full_name} — {self.city}, {self.country}"
