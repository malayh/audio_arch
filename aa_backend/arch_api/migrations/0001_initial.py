# Generated by Django 3.1.7 on 2021-03-04 05:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AudioTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audio_type', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Songs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(max_length=100)),
                ('creator', models.TextField()),
                ('duration_s', models.IntegerField()),
                ('upload_time', models.DateTimeField()),
                ('rel_path', models.TextField()),
                ('file_format', models.TextField()),
                ('audio_type_fk', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='arch_api.audiotypes')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Podcasts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(max_length=100)),
                ('creator', models.TextField()),
                ('duration_s', models.IntegerField()),
                ('upload_time', models.DateTimeField()),
                ('rel_path', models.TextField()),
                ('file_format', models.TextField()),
                ('audio_type_fk', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='arch_api.audiotypes')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PodcastGuests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guest_name', models.TextField(max_length=100)),
                ('podcast_fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='arch_api.podcasts')),
            ],
        ),
        migrations.CreateModel(
            name='Audiobooks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(max_length=100)),
                ('creator', models.TextField()),
                ('duration_s', models.IntegerField()),
                ('upload_time', models.DateTimeField()),
                ('rel_path', models.TextField()),
                ('file_format', models.TextField()),
                ('narrator', models.TextField()),
                ('audio_type_fk', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='arch_api.audiotypes')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]