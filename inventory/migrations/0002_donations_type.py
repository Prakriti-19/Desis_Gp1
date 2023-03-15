# Generated by Django 4.1.7 on 2023-03-15 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='donations',
            name='type',
            field=models.CharField(choices=[('homefood', 'Home Food'), ('party', 'Party'), ('restro', 'Restaurant'), ('other', 'Other')], default='other', max_length=10),
        ),
    ]
