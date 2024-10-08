from ..forms import SearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import render
from torrent.models import Torrent
from django.contrib import messages


def search_view(request):
    form = SearchForm(request.GET or None)
    query = form.cleaned_data['query'] if form.is_valid() and form.cleaned_data.get('query') else None
    torrents = Torrent.objects.filter(is_active=True).order_by('-creation')

    if query:
        torrents = torrents.filter(name__icontains=query)
    else:
        messages.info(request, "Please enter a valid search query.")

    # Handle pagination
    paginator = Paginator(torrents, 40)  # Number of torrents per page
    page = request.GET.get('page')

    try:
        torrents = paginator.page(page)
    except PageNotAnInteger:
        torrents = paginator.page(1)
    except EmptyPage:
        torrents = paginator.page(paginator.num_pages)

    # Pass the context to the template
    context = {
        'form': form,
        'torrent_list': torrents,
        'query': query,
        'total_results': paginator.count,  # This shows the total number of results
        'is_paginated': paginator.num_pages > 1,
    }

    return render(request, 'bt/search_results.html', context)
