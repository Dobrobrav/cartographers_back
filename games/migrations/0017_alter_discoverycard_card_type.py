# Generated by Django 4.1.7 on 2023-05-04 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0016_alter_discoverycard_card_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discoverycard',
            name='card_type',
            field=models.CharField(choices=[('mountain', 'Mountain'), ('ruins', 'Ruins')], max_length=20),
        ),
    ]
