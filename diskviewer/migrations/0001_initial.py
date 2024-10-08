# Generated by Django 5.1 on 2024-08-31 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('part_path', models.CharField(max_length=255)),
                ('url', models.URLField(blank=True, null=True)),
                ('mime_type', models.CharField(blank=True, max_length=255, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('api_key', models.CharField(max_length=255)),
            ],
            options={
                'unique_together': {('name', 'part_path', 'api_key')},
            },
        ),
    ]
