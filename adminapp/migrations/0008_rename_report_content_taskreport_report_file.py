# Generated by Django 5.1.7 on 2025-04-03 04:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0007_taskreport'),
    ]

    operations = [
        migrations.RenameField(
            model_name='taskreport',
            old_name='report_content',
            new_name='report_File',
        ),
    ]
