# Generated by Django 5.0.7 on 2024-08-05 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0007_reaction_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='reaction',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
