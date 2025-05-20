from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

from species.models import Species


class SpeciesSnippetViewSet(SnippetViewSet):
    model = Species
    menu_icon = "pick"
    add_to_settings_menu = False
    add_to_admin_menu = True
    list_display = ("atom", "charge", "isotope")
    list_filter = ("atom", "isotope")
    search_fields = ("atom", "isotope", "slug")

    panels = [
        FieldPanel("atom"),
        FieldPanel("charge"),
        FieldPanel("isotope"),
        FieldPanel("slug"),
        FieldPanel("html"),
    ]


register_snippet(SpeciesSnippetViewSet)
