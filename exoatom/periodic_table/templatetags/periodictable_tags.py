from django import template
from periodic_table.models import Element

register = template.Library()


@register.inclusion_tag("periodic_table/includes/periodic_table.html")
def periodic_table():
    lanthanides = Element.category.lanthanides()
    actinides = Element.category.actinides()
    main_elements = Element.objects.exclude(group__isnull=True)
    main_table = [[None] * 18 for i in range(7)]
    iperiod = 0
    for element in main_elements:
        main_table[iperiod][element.group - 1] = element
        if element.group == 18:
            iperiod += 1
    return {
        "main_table": main_table,
        "lanthanides": lanthanides,
        "actinides": actinides,
    }
