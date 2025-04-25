from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel

from data.models import DataCollection

from pyvalem.formula import Formula, FormulaParseError
def parse_query(query):
    try:
        formula = Formula(query)
    except FormulaParseError:
        return None, None
    if formula.natoms != 1:
        return None, None
    atom = formula.atoms.pop().symbol
    return atom, formula.charge

class HomePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        query = request.GET.get('q', '')
        if query:
            atom, charge = parse_query(query)
            if atom is None:
                context['results'] = []
            else:
                context['results'] = DataCollection.objects.filter(
                            species__atom=atom, species__charge=charge)
        return context
