# Generated by Django 4.1.7 on 2023-05-10 15:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0021_rename_discoverycard_discoverycardsql'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Shape',
            new_name='ShapeSQL',
        ),
    ]
