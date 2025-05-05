from django.db import models
from django.conf import settings

from species.models import Species


class Link(models.Model):
    url = models.CharField(max_length=200)
    size = models.BigIntegerField(blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        return self.url

    def filename(self):
        return self.url.split("/")[-1]

    def download_url(self):
        return f"{settings.DB_URL}/{self.url}"


class DataCollection(models.Model):
    dataset = models.CharField(max_length=10)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    links = models.ManyToManyField(Link)
    metadata = models.JSONField(blank=True)

    def __str__(self):
        return f"{self.species} {self.dataset} dataset"
