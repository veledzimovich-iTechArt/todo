# Generated by Django 4.1.2 on 2022-11-09 13:11

import django.contrib.postgres.fields.citext
from django.contrib.postgres.operations import CITextExtension
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0001_initial'),
    ]

    operations = [
        CITextExtension(),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('title', django.contrib.postgres.fields.citext.CICharField(max_length=120, unique=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.AlterModelOptions(
            name='todo',
            options={'ordering': ['title']},
        ),
        migrations.AddField(
            model_name='todo',
            name='tags',
            field=models.ManyToManyField(blank=True, to='cards.tag'),
        ),
    ]
