# Generated by Django 3.2.16 on 2024-06-10 00:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0030_taskcost'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subtask',
            old_name='task',
            new_name='parent_task',
        ),
        migrations.RenameField(
            model_name='subtask',
            old_name='subtask',
            new_name='subtask_name',
        ),
        migrations.RemoveField(
            model_name='subtask',
            name='updated_personnel',
        ),
        migrations.AddField(
            model_name='subtask',
            name='assigned_personnel',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='subtask',
            name='description',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subtask',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='subtask_files/'),
        ),
        migrations.AlterField(
            model_name='subtask',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('on_hold', 'On Hold'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='pending', max_length=20),
        ),
    ]
