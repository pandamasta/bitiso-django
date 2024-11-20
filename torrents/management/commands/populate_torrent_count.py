from django.core.management.base import BaseCommand
from django.db.models import Count
from torrents.models import Project  # Update to match your app and model

class Command(BaseCommand):
    help = "Populate torrent_count field for all projects in bulk"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting bulk update for torrent_count...")

        # Annotate projects with the count of related torrents
        projects_with_counts = Project.objects.annotate(torrent_count_agg=Count('torrents'))

        # Prepare a list of Project instances with updated torrent_count
        projects_to_update = []
        for project in projects_with_counts:
            project.torrent_count = project.torrent_count_agg
            projects_to_update.append(project)

        # Bulk update the torrent_count field for all projects
        Project.objects.bulk_update(projects_to_update, ['torrent_count'])

        self.stdout.write(f"Successfully updated {len(projects_to_update)} projects with torrent counts!")
