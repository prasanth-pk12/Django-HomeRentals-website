# Generated by Django 4.1.5 on 2023-04-07 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0006_room_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='Tenant_id',
            field=models.IntegerField(default=0),
        ),
    ]