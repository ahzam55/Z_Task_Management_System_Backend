# Generated by Django 5.1.7 on 2025-03-27 12:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0006_project_assigned_to'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskReport',
            fields=[
                ('taskreport_id', models.AutoField(primary_key=True, serialize=False)),
                ('report_date', models.DateTimeField(auto_now_add=True)),
                ('report_content', models.FileField(blank=True, null=True, upload_to='task_reports/')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminapp.task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table_comment': 'Task Report File',
            },
        ),
    ]
