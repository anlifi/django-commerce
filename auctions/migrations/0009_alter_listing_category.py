# Generated by Django 4.2.1 on 2023-05-25 12:32

import auctions.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_alter_listing_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.ForeignKey(blank=True, default=auctions.models.CategoryManager.get_default_category, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='category_listings', to='auctions.category'),
        ),
    ]
