# Generated by Django 2.0.13 on 2020-11-14 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LoginApp', '0003_logindb_profilesetting'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logindb',
            name='profilesetting',
            field=models.CharField(default='0', max_length=8),
        ),
    ]