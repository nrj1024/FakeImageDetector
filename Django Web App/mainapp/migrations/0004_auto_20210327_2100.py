# Generated by Django 3.1.7 on 2021-03-27 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_post_binary_mask'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='p_fake',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='p_real',
            field=models.FloatField(null=True),
        ),
    ]
