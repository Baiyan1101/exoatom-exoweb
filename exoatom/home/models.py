from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel

from species.models import Species
from data.models import DataCollection

from pyvalem.formula import Formula, FormulaParseError
from species.utils import roman_numerals_to_int

def parse_formula(formula, all_charges):
    formula = formula.strip()
    
    if formula[0].isdigit():
        # Put brackets around isotope if not already present.
        formula = "(" + formula
        idx = len(formula)
        if "+" in formula:
            idx = formula.index("+")
        elif "-" in formula:
            idx = formula.index("-")
        elif " " in formula:
            idx = formula.index(" ")
        formula = formula[:idx] + ")" + formula[idx:]

    try:
        species, ionization_stage = formula.split()
        charge = int(roman_numerals_to_int[ionization_stage.upper()]) - 1
        formula = f"{species}+{charge}"
    except ValueError:
        pass
    except KeyError:
        return None

    try:
        pyvalem_formula = Formula(formula)
    except FormulaParseError:
        return None

    atom = list(pyvalem_formula.atoms)[0]
    if pyvalem_formula.charge > atom.Z:
        return None

    return pyvalem_formula

def parse_query(formula, all_charges=True):
    formula = formula.strip()
    
    pyvalem_formula = parse_formula(formula, all_charges)
    if not pyvalem_formula:
        return {"results": []}

    if pyvalem_formula.natoms != 1:
        # No molecules, photons, etc.
        return {"results": []}

    is_isotope = str(pyvalem_formula)[0] == "("
    if is_isotope:
        isotope = pyvalem_formula.atoms.pop().symbol
        charge = pyvalem_formula.charge
        if charge or not all_charges:
            try:
                species = Species.objects.get(isotope=isotope, charge=charge)
            except Species.DoesNotExist:
                return {"results": []}
            return {"results": DataCollection.objects.filter(species=species)}
        species = Species.objects.filter(isotope=isotope)
        return {"species": species}

    atom = pyvalem_formula.atoms.pop().symbol
    charge = pyvalem_formula.charge
    if charge or not all_charges:
        species = Species.objects.filter(atom=atom, charge=charge)
        if species.count() == 1:
            return {"results": DataCollection.objects.filter(species__in=species)}
        return {"species": species}
    species = Species.objects.filter(atom=atom)
    return {"species": species}


class HomePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    def get_context(self, request):
        context = super().get_context(request)

        # Do we have submission through the input field?
        query = request.GET.get("qf")
        if query:
            all_charges = request.GET.get("input_box_all_charges", False)
        else:
            # Do we have a click on a periodic_table element?
            query = request.GET.get("q")
            all_charges = request.GET.get("all_charges", True)

        if query:
            context |= parse_query(query, all_charges)
        return context
