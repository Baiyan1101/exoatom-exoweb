from collections import defaultdict
from pathlib import Path

from django.conf import settings
from django.db.models import Max
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache

from data.models import DataCollection
from periodic_table.models import Element
from species.models import Species
from species.utils import int_to_roman_numerals


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


def coverage_matrix(request):
    coverage = defaultdict(set)
    collections = DataCollection.objects.select_related("species").filter(
        dataset__in=["Kurucz", "NIST"]
    )
    for collection in collections:
        species = collection.species
        coverage[(species.atom, species.charge)].add(collection.dataset)

    max_charge = Species.objects.aggregate(max_charge=Max("charge"))["max_charge"] or 0
    stages = [
        {"charge": charge, "stage": charge + 1, "label": int_to_roman_numerals[charge + 1]}
        for charge in range(max_charge + 1)
    ]

    rows = []
    counts = {"both": 0, "kurucz": 0, "nist": 0}
    for element in Element.objects.order_by("atomic_number"):
        cells = []
        row_total = 0
        for stage in stages:
            datasets = coverage.get((element.symbol, stage["charge"]), set())
            status = coverage_status(datasets)
            if status:
                counts[status] += 1
                row_total += 1
            cells.append({
                "status": status,
                "label": coverage_label(status),
                "datasets": sorted(datasets),
                "query": f"{element.symbol} {stage['label']}",
                "url": f"/?qf={element.symbol}%20{stage['label']}",
            })
        rows.append({"element": element, "cells": cells, "total": row_total})

    context = {
        "stages": stages,
        "rows": rows,
        "counts": counts,
        "total_cells": sum(counts.values()),
        "nist_species": DataCollection.objects.filter(dataset="NIST").count(),
        "kurucz_species": DataCollection.objects.filter(dataset="Kurucz").count(),
    }
    return render(request, "data/coverage_matrix.html", context)


def coverage_status(datasets):
    has_kurucz = "Kurucz" in datasets
    has_nist = "NIST" in datasets
    if has_kurucz and has_nist:
        return "both"
    if has_kurucz:
        return "kurucz"
    if has_nist:
        return "nist"
    return ""


def coverage_label(status):
    return {"both": "B", "kurucz": "K", "nist": "N"}.get(status, "")
