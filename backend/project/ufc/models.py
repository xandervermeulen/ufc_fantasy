from django.db import models

from project.core.models import BaseModel


class Gender(models.TextChoices):
    MALE = "MALE"
    FEMALE = "FEMALE"


class Stance(models.TextChoices):
    SOUTHPAW = "SOUTHPAW"
    ORTHODOX = "ORTHODOX"
    BOTH = "BOTH"


class FightStatsMixin(models.Model):

    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    no_contests = models.IntegerField(default=0)

    class Meta:
        abstract = True


class WeightClass(models.TextChoices):
    STRAWWEIGHT = "STRAWWEIGHT", "Strawweight (115 lbs)"
    FLYWEIGHT = "FLYWEIGHT", "Flyweight (125 lbs)"
    BANTAMWEIGHT = "BANTAMWEIGHT", "Bantamweight (135 lbs)"
    FEATHERWEIGHT = "FEATHERWEIGHT", "Featherweight (145 lbs)"
    LIGHTWEIGHT = "LIGHTWEIGHT", "Lightweight (155 lbs)"
    WELTERWEIGHT = "WELTERWEIGHT", "Welterweight (170 lbs)"
    MIDDLEWEIGHT = "MIDDLEWEIGHT", "Middleweight (185 lbs)"
    LIGHT_HEAVYWEIGHT = "LIGHT_HEAVYWEIGHT", "Light Heavyweight (205 lbs)"
    HEAVYWEIGHT = "HEAVYWEIGHT", "Heavyweight (265 lbs)"

    @property
    def limit(self):
        limits = {
            self.STRAWWEIGHT: 115,
            self.FLYWEIGHT: 125,
            self.BANTAMWEIGHT: 135,
            self.FEATHERWEIGHT: 145,
            self.LIGHTWEIGHT: 155,
            self.WELTERWEIGHT: 170,
            self.MIDDLEWEIGHT: 185,
            self.LIGHT_HEAVYWEIGHT: 205,
            self.HEAVYWEIGHT: 265,
        }
        return limits[self]


class Division(BaseModel):
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=255, choices=Gender.choices)
    weight_class = models.CharField(max_length=255, choices=WeightClass.choices)

    def __str__(self):
        return self.name, self.gender, self.weight_class


class Fighter(BaseModel):
    name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255)
    gender = models.CharField(max_length=255, choices=Gender.choices)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, many_to_many=True)
    nationality_code = models.CharField(max_length=3)
    birth_date = models.DateField()
    height_cm = models.IntegerField()
    is_active = models.BooleanField(default=True)
    fighting_style = models.CharField(max_length=255, choices=Stance.choices)
    reach_cm = models.IntegerField()
    leg_reach_cm = models.IntegerField()

    current_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name, self.gender, self.weight_class, self.division
