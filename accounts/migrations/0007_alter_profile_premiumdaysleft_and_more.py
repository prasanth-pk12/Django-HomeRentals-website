# Generated by Django 4.1.5 on 2023-03-10 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_profile_premium_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='PremiumDaysLeft',
            field=models.CharField(blank=True, default='0', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='premium_start_date',
            field=models.CharField(blank=True, default='2020-03-01', max_length=20, null=True),
        ),
    ]