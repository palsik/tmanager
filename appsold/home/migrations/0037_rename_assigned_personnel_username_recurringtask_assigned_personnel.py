# Generated by Django 3.2.16 on 2024-06-24 09:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0036_recurringtask_client'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recurringtask',
            old_name='assigned_personnel_username',
            new_name='assigned_personnel',
        ),
    ]
