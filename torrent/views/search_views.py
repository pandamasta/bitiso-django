from ..models import Torrent
from django.http import HttpResponse
from django.shortcuts import render
from ..forms import SearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..ratelimit import RateLimit, RateLimitExceeded

from django.conf import settings
from django.shortcuts import render
from torrent.models import Torrent

def search_view(request):
    try:
        RateLimit(
            key=f"{request.user.id}:torrent_list",
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

    if form.is_valid() and form.cleaned_data['query']:
        query = form.cleaned_data['query']
        torrents = torrents.filter(name__icontains=query)

    # Pagination for search results
    paginator = Paginator(torrents, 40)  # Adjust number of torrents per page as needed
    page = request.GET.get('page')
    try:
        torrents = paginator.page(page)
    except PageNotAnInteger:
        torrents = paginator.page(1)
    except EmptyPage:
        torrents = paginator.page(paginator.num_pages)

    context = {
        'form': form,
        'torrent_list': torrents,
    }
    return render(request, 'torrent/search_results.html', context)