# Generated by Django 4.1.7 on 2023-03-24 02:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_alter_basetransaction_points_transferred'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basetransaction',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='donor',
            name='phone_no',
            field=models.CharField(max_length=17),
        ),
        migrations.AlterField(
            model_name='ngo',
            name='phone_no',
            field=models.CharField(max_length=17),
        ),
    ]