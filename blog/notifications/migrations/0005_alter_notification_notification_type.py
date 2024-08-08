# Generated by Django 5.0.7 on 2024-08-08 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0004_alter_notification_notification_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('follow', 'New Follower'), ('comment', 'Commented on'), ('comment_reaction', 'Reacted to your comment on'), ('reply', 'Replied to your comment on'), ('clap', ' Clapped on your post'), ('sad', 'Reacted Sad on your post'), ('laugh', 'Reacted Laugh on your post'), ('mention', 'Mentioned you on')], max_length=20),
        ),
    ]
