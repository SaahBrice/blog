# Generated by Django 5.0.7 on 2024-08-05 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('follow', 'New Follower'), ('comment', 'New Comment'), ('clap', 'New Clap'), ('sad', 'New Sad Reaction'), ('laugh', 'New Laugh Reaction')], max_length=20),
        ),
    ]
