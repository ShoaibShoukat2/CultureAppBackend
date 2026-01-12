from django.core.management.base import BaseCommand
from api.models import Artwork
from PIL import Image
import imagehash

class Command(BaseCommand):
    help = 'Generate perceptual hashes for existing artworks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate hashes for artworks that already have them',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        # Get artworks that need hash generation
        if force:
            artworks = Artwork.objects.filter(image__isnull=False)
            self.stdout.write(f'Processing all {artworks.count()} artworks (force mode)')
        else:
            artworks = Artwork.objects.filter(image__isnull=False, perceptual_hash__isnull=True)
            self.stdout.write(f'Processing {artworks.count()} artworks without hashes')

        success_count = 0
        error_count = 0

        for artwork in artworks:
            try:
                # Generate hash
                hash_value = artwork.generate_perceptual_hash()
                if hash_value:
                    artwork.perceptual_hash = hash_value
                    artwork.save(update_fields=['perceptual_hash'])
                    success_count += 1
                    self.stdout.write(f'✓ Generated hash for artwork {artwork.id}: {artwork.title}')
                else:
                    error_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Could not generate hash for artwork {artwork.id}: {artwork.title}')
                    )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Error processing artwork {artwork.id}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Successfully processed {success_count} artworks, {error_count} errors'
            )
        )