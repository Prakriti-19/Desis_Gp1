# Generated by Django 4.1.7 on 2023-03-01 01:20

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('sent', models.DateField(auto_now_add=True)),
                ('seen', models.DateField()),
                ('sent_time', models.TimeField(auto_now_add=True)),
                ('seen_time', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='donations',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('exp_date', models.DateField()),
                ('quantity', models.IntegerField(default=10)),
                ('desc', models.TextField(default='xyz')),
                ('donation_date', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField(default=248001)),
                ('city', models.CharField(default='es', max_length=250)),
                ('state', models.CharField(default='qw', max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='ngo',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ngo_name', models.CharField(default='a', max_length=255)),
                ('email', models.CharField(default='b', max_length=55)),
                ('phone_no', models.IntegerField(default=123456789)),
                ('is_ngo', models.BooleanField(default=True)),
                ('longitude', models.DecimalField(decimal_places=10, default=2.313, max_digits=15)),
                ('latitude', models.DecimalField(decimal_places=10, default=13.131, max_digits=15)),
                ('groups', models.ManyToManyField(related_name='ngo_groups', to='auth.group')),
                ('pincode', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.location')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='ngo_user_permissions', to='auth.permission')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='donor',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('donor_name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=55)),
                ('phone_no', models.IntegerField(default=123456789)),
                ('points', models.PositiveBigIntegerField(default=0)),
                ('longitude', models.DecimalField(decimal_places=10, default=2.313, max_digits=15)),
                ('latitude', models.DecimalField(decimal_places=10, default=13.13, max_digits=15)),
                ('is_donor', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(related_name='donor_groups', to='auth.group')),
                ('pincode', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.location')),
                ('user_permissions', models.ManyToManyField(related_name='donor_user_permissions', to='auth.permission')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
