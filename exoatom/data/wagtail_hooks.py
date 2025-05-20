from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

from data.models import Link, DataCollection


class LinkSnippetViewSet(SnippetViewSet):
    model = Link
    menu_icon = "pick"
    add_to_settings_menu = False
    add_to_admin_menu = True
    list_display = ("url", "description")
    list_filter = ("url", "description")
    search_fields = ("url", "description")

    panels = [
        FieldPanel("url"),
        FieldPanel("description"),
        FieldPanel("size"),
    ]


class DataCollectionSnippetViewSet(SnippetViewSet):
    model = DataCollection
    menu_icon = "pick"
    add_to_settings_menu = False
    add_to_admin_menu = True
    list_display = ("species", "species__isotope", "dataset")
    list_filter = ("species", "dataset")
    search_fields = ("species", "dataset")

    panels = [
        FieldPanel("dataset"),
        FieldPanel("species"),
        FieldPanel("links"),
        FieldPanel("metadata"),
    ]


register_snippet(LinkSnippetViewSet)
register_snippet(DataCollectionSnippetViewSet)
