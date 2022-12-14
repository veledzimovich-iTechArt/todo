# Generated by Django 4.1.2 on 2022-11-16 11:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cards', '0002_tag_alter_todo_options_todo_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='todo',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='todos', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
