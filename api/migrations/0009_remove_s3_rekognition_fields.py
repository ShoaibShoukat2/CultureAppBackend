# Generated migration to remove S3 and Rekognition fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_artwork_rekognition_checked_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artwork',
            name='s3_image_key',
        ),
        migrations.RemoveField(
            model_name='artwork',
            name='s3_image_url',
        ),
        migrations.RemoveField(
            model_name='artwork',
            name='s3_watermarked_key',
        ),
        migrations.RemoveField(
            model_name='artwork',
            name='s3_watermarked_url',
        ),
        migrations.RemoveField(
            model_name='artwork',
            name='rekognition_checked',
        ),
        migrations.RemoveField(
            model_name='artwork',
            name='rekognition_labels',
        ),
        migrations.RemoveField(
            model_name='artwork',
            name='similarity_score',
        ),
    ]