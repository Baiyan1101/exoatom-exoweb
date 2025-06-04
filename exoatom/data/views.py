from django.shortcuts import render, get_object_or_404
from data.models import DataCollection

def datacollection(request, pk):
    datacollection = get_object_or_404(DataCollection, pk=pk)
    c = {"datacollection": datacollection}
    return render(request, "data/datacollection.html", c)
