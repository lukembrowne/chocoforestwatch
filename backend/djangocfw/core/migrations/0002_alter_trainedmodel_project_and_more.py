# Generated by Django 5.1.3 on 2024-11-18 20:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainedmodel',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.project', unique=True),
        ),
        migrations.AddConstraint(
            model_name='trainedmodel',
            constraint=models.UniqueConstraint(fields=('project',), name='unique_project_model'),
        ),
    ]
