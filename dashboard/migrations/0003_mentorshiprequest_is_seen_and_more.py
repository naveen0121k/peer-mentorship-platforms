# Generated by Django 5.1.7 on 2025-03-19 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_mentorshiprequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='mentorshiprequest',
            name='is_seen',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='mentorshiprequest',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='mentorshiprequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=10),
        ),
    ]
