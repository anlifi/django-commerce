# Generated by Django 4.2.1 on 2023-05-17 15:10

import auctions.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_alter_listing_category_alter_listing_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.ForeignKey(blank=True, default=auctions.models.CategoryManager.get_default_category, on_delete=django.db.models.deletion.CASCADE, related_name='category_listings', to='auctions.category'),
        ),
    ]
