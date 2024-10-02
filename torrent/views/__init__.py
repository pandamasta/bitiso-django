# views/__init__.py

from .torrent_views import (
    TorrentListView,
    TorrentDetailView,
    TorrentCreateView,
    TorrentUpdateView,
    TorrentDeleteView
)
from .category_views import (
    CategoryListView,
    CategoryDetailView
)
from .project_views import (
    ProjectListView,
    ProjectDetailView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView
)
from .user_views import (
    login_view,
    logout_view,
    register_view,
)
from .dashboard_views import dashboard, delete_torrents
from .upload_views import file_upload
from .download_views import download_torrent
from .search_views import search_view


__all__ = [
    "TorrentListView",
    "TorrentDetailView",
    "TorrentCreateView",
    "TorrentUpdateView",
    "TorrentDeleteView",
    "CategoryListView",
    "CategoryDetailView",
    "ProjectListView",
    "ProjectDetailView",
    "ProjectCreateView",
    "ProjectUpdateView",
    "ProjectDeleteView",
    "file_upload",
    "download_torrent",
    "login_view",
    "logout_view",
    "register_view",
    "dashboard",
]
