# Generated by Django 4.1.5 on 2023-02-27 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20210912_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='premium_star_date',
            field=models.CharField(blank=True, default='12/02/2022', max_length=20, null=True),
        ),
    ]
