# Generated by Django 4.1.5 on 2023-03-25 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_profile_premium_validity'),
    ]

    operations = [
        migrations.AddField(
            model_name='premiumplan',
            name='Name',
            field=models.CharField(default='standard', max_length=100),
            preserve_default=False,
        ),
    ]
