from django.core.management.base import BaseCommand
from api.models import Artwork
import imagehash

class Command(BaseCommand):
    help = 'Find and report duplicate artworks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--threshold',
            type=int,
            default=5,
            help='Similarity threshold (0-64, lower = more strict)',
        )
        parser.add_argument(
            '--delete-duplicates',
            action='store_true',
            help='Delete duplicate artworks (keeps the oldest one)',
        )

    def handle(self, *args, **options):
        threshold = options['threshold']
        delete_duplicates = options['delete_duplicates']
        
        self.stdout.write(f'Finding duplicates with threshold: {threshold}')
        
        artworks = Artwork.objects.filter(perceptual_hash__isnull=False, is_available=True)
        duplicate_groups = []
        processed_ids = set()

        for artwork in artworks:
            if artwork.id in processed_ids:
                continue

            duplicates = artwork.check_for_duplicates(threshold)
            if duplicates:
                group = [artwork] + [dup['artwork'] for dup in duplicates]
                duplicate_groups.append(group)
                processed_ids.update([art.id for art in group])

        if not duplicate_groups:
            self.stdout.write(self.style.SUCCESS('No duplicates found!'))
            return

        self.stdout.write(f'\nFound {len(duplicate_groups)} duplicate groups:')
        
        deleted_count = 0
        for i, group in enumerate(duplicate_groups, 1):
            self.stdout.write(f'\n--- Duplicate Group {i} ---')
            
            # Sort by creation date (oldest first)
            group.sort(key=lambda x: x.created_at)
            
            for j, artwork in enumerate(group):
                status = "KEEPING (oldest)" if j == 0 else "DUPLICATE"
                self.stdout.write(
                    f'  {status}: ID={artwork.id}, Title="{artwork.title}", '
                    f'Artist={artwork.artist.username}, Date={artwork.created_at.strftime("%Y-%m-%d")}'
                )
                
                if delete_duplicates and j > 0:  # Delete all except the first (oldest)
                    artwork.delete()
                    deleted_count += 1
                    self.stdout.write(self.style.WARNING(f'    DELETED: {artwork.title}'))

        if delete_duplicates:
            self.stdout.write(
                self.style.SUCCESS(f'\nDeleted {deleted_count} duplicate artworks')
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'\nFound duplicates but did not delete them. '
                    f'Use --delete-duplicates to remove them.'
                )
            )