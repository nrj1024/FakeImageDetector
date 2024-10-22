# Generated by Django 3.1.7 on 2021-05-19 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0006_uservotedetails'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uservotedetails',
            name='downvoted_posts',
            field=models.ManyToManyField(related_name='downvoted_by', to='mainapp.Post'),
        ),
        migrations.AlterField(
            model_name='uservotedetails',
            name='upvoted_posts',
            field=models.ManyToManyField(related_name='upvoted_by', to='mainapp.Post'),
        ),
    ]
