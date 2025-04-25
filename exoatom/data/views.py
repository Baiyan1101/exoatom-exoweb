from django.shortcuts import render
from data.models import DataCollection

def exoatom_search(request):
    query = request.GET.get('q', '')
    results = DataCollection.objects.filter(species__atom=query)  # Example search
    return render(request, 'data/search_results.html', {'results': results, 'query': query})
