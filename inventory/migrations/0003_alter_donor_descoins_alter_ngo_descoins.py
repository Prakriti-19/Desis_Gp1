# Generated by Django 4.1.7 on 2023-03-24 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_alter_donor_latitude_alter_donor_longitude'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donor',
            name='descoins',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='ngo',
            name='descoins',
            field=models.PositiveBigIntegerField(default=500),
        ),
    ]