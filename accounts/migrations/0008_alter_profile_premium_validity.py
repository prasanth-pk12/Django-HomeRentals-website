# Generated by Django 4.1.5 on 2023-03-10 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_profile_premiumdaysleft_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='premium_Validity',
            field=models.CharField(blank=True, default='0 months', max_length=100, null=True),
        ),
    ]
