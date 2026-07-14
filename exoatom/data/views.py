from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache

from data.models import DataCollection


def safe_data_file(file_path):
    data_root = Path(settings.EXOATOM_DATA_DIR).resolve()
    requested = (data_root / file_path).resolve()

    if data_root not in requested.parents and requested != data_root:
        raise Http404("Invalid data file path")
    if not requested.is_file():
        raise Http404("Data file not found")
    return requested


def datacollection(request, pk):
    datacollection = get_object_or_404(DataCollection, pk=pk)
    c = {"datacollection": datacollection}
    return render(request, "data/datacollection.html", c)


@never_cache
def file_preview(request, file_path):
    requested = safe_data_file(file_path)

    limit = settings.EXOATOM_FILE_PREVIEW_LIMIT
    size = requested.stat().st_size
    with requested.open("rb") as handle:
        payload = handle.read(limit + 1)

    truncated = len(payload) > limit
    payload = payload[:limit]
    preview_text = payload.decode("utf-8", errors="replace")

    return render(
        request,
        "data/file_preview.html",
        {
            "file_path": file_path,
            "preview_text": preview_text,
            "truncated": truncated,
            "limit": limit,
            "size": size,
        },
    )


@never_cache
def file_download(request, file_path):
    requested = safe_data_file(file_path)
    return FileResponse(
        requested.open("rb"),
        as_attachment=True,
        filename=requested.name,
    )
