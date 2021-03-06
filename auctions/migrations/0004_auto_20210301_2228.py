# Generated by Django 3.1.6 on 2021-03-02 03:28

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20210301_2152'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='category',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='auction',
            name='initial_bid',
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AddField(
            model_name='auction',
            name='watchlist_users',
            field=models.ManyToManyField(blank=True, related_name='watchlist', to=settings.AUTH_USER_MODEL),
        ),
    ]
