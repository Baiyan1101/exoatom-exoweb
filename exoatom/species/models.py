from django.db import models

class Species(models.Model):
    atom = models.CharField(max_length=2)
    charge = models.SmallIntegerField()
    isotope = models.CharField(max_length=5, blank=True)
    slug = models.CharField(max_length=16)
    html = models.CharField(max_length=32)

    def __str__(self):
        s = self.isotope if self.isotope else self.atom
        if self.charge == 1:
            return s + "+"
        elif self.charge == -1:
            return s + "-"
        elif self.charge:
            return s + f"{self.charge:+d}"
        else:
            return s
    
