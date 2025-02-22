# Generated by Django 5.1.5 on 2025-01-22 13:46

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_feedback'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='is_template',
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['is_template'], name='core_projec_is_temp_b9e7eb_idx'),
        ),
    ]
