from ..models import Torrent
from django.http import HttpResponse
from django.shortcuts import render
from ..forms import SearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..ratelimit import RateLimit, RateLimitExceeded

from django.conf import settings
from django.shortcuts import render
from torrent.models import Torrent
from django.contrib import messages


def search_view(request):
    # Handle rate-limiting for logged-in users
    try:
        rate_limit_key = f"{request.user.id}:torrent_list" if request.user.is_authenticated else request.META['REMOTE_ADDR']
        RateLimit(
            key=rate_limit_key,
            limit=20,  # Limit to 20 requests per minute
            period=60,  # Period in seconds
            request=request,
        ).check()
    except RateLimitExceeded as e:
        return HttpResponse(
            f"Rate limit exceeded. You have used {e.usage} requests, limit is {e.limit}.",
            status=429,
        )

    form = SearchForm(request.GET or None)
    torrents = Torrent.objects.filter(is_active=True).order_by('-creation')

    # Handle search query
    query = None
    if form.is_valid() and form.cleaned_data['query']:
        query = form.cleaned_data['query']
        torrents = torrents.filter(name__icontains=query)
    else:
        messages.info(request, "Please enter a valid search query.")

    # Pagination
    paginator = Paginator(torrents, 40)  # Adjust number of torrents per page as needed
    page = request.GET.get('page')
    try:
        torrents = paginator.page(page)
    except PageNotAnInteger:
        torrents = paginator.page(1)
    except EmptyPage:
        torrents = paginator.page(paginator.num_pages)

    # Context setup
    context = {
        'form': form,
        'torrent_list': torrents,
        'query': query,
        'total_results': paginator.count,
        'is_paginated': paginator.num_pages > 1,
    }

    return render(request, 'bt/search_results.html', context)