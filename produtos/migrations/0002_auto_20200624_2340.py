# Generated by Django 2.1.7 on 2020-06-25 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventos',
            name='user',
            field=models.CharField(max_length=30),
        ),
    ]
