# Generated by Django 4.1.5 on 2023-04-02 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0002_remove_temp_reg_mess_restaurent_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='Advance',
            field=models.IntegerField(default=5000),
        ),
    ]