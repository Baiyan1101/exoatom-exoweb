import re
from django.db import models


def roman_numeral(x):
    if x == 0:
        return "I"
    return "II"


class Species(models.Model):
    atom = models.CharField(max_length=2)
    charge = models.SmallIntegerField()
    isotope = models.CharField(max_length=5, blank=True)
    slug = models.CharField(max_length=16)
    html = models.CharField(max_length=32)

    class Meta:
        verbose_name_plural = "Species"

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

    def querystr(self):
        # The query parameter is just the formula, but escape the + sign.
        return str(self).replace("+", "%2B")

    def spectroscopic_notation(self):
        s = self.isotope if self.isotope else self.atom
        return f"{s} {roman_numeral(self.charge)}"

    def spectroscopic_notation_html(self):
        # TODO handle this better
        if self.isotope:
            m = re.match("(\d+)", self.isotope)
            A = m.group(1)
            s = f"<sup>{A}</sup>{self.atom}"
        else:
            s = self.atom
        return f"{s} {roman_numeral(self.charge)}"
