from django.db import models

from project.core.models import BaseModel


class Gender(models.TextChoices):
    MALE = "MALE"
    FEMALE = "FEMALE"


class Division(BaseModel):
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=255, choices=Gender.choices)

    def __str__(self):
        return self.name
