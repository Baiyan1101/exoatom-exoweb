from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from django.views.generic.base import RedirectView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views
import data.views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
    path("coverage/", data.views.coverage_matrix, name="coverage_matrix"),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    re_path('^ExoAtom.all.json$', RedirectView.as_view(url='/exoatom/db/exoatom.all.json')),
    re_path('^exoatom.all.json$', RedirectView.as_view(url='/exoatom/db/exoatom.all.json')),
    path("data/preview/<path:file_path>", data.views.file_preview, name="data_file_preview"),
    path("data/download/<path:file_path>", data.views.file_download, name="data_file_download"),
    path("data/<int:pk>", data.views.datacollection, name="datacollection"),
]

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
