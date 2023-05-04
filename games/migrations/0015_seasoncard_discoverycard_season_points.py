# Generated by Django 4.1.7 on 2023-05-03 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0014_alter_discoverycard_shape_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SeasonCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('points_to_end', models.IntegerField()),
                ('image', models.ImageField(upload_to='season_cards/')),
            ],
        ),
        migrations.AddField(
            model_name='discoverycard',
            name='season_points',
            field=models.IntegerField(default=3),
        ),
    ]
