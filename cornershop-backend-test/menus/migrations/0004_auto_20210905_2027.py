# Generated by Django 3.0.8 on 2021-09-05 20:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menus', '0003_menurequest'),
    ]

    operations = [
        migrations.RenameField(
            model_name='menurequest',
            old_name='menu_id',
            new_name='menu',
        ),
    ]