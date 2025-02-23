# Generated by Django 3.2.16 on 2024-07-19 09:58

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0048_auto_20240719_0756'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rtaskdirectory',
            name='parent',
        ),
        migrations.AddField(
            model_name='rtaskdirectory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2024, 7, 19, 9, 43, 0, 504029, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rtaskdirectory',
            name='created_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rtaskdirectory',
            name='parent_directory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subdirectories', to='home.rtaskdirectory'),
        ),
        migrations.AddField(
            model_name='rtaskfile',
            name='directory',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='files', to='home.rtaskdirectory'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rtaskfile',
            name='remarks',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='rtaskfile',
            name='status',
            field=models.CharField(default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='rtaskdirectory',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='rtaskdirectory',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='directories', to='home.recurringtask'),
        ),
        migrations.AlterField(
            model_name='rtaskfile',
            name='uploaded_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='rtaskupdate',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='updates', to='home.recurringtask'),
        ),
        migrations.AlterField(
            model_name='rtaskupdate',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='rtaskupdate',
            name='updated_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='TaskUpdate',
        ),
    ]
