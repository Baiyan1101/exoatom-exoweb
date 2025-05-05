from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

LANTHANIDES = tuple(range(57, 72))
ACTINIDES = tuple(range(89, 104))


class ElementQuerySet(models.QuerySet):
    def lanthanides(self):
        return self.filter(atomic_number__in=LANTHANIDES)

    def actinides(self):
        return self.filter(atomic_number__in=ACTINIDES)


class Element(models.Model):
    atomic_number = models.PositiveSmallIntegerField()
    symbol = models.CharField(max_length=2)
    name = models.CharField(max_length=25)
    group = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(18),
        ],
    )
    link = models.CharField(max_length=256, blank=True)

    category = ElementQuerySet.as_manager()

    objects = models.Manager()

    def __str__(self):
        return self.symbol
