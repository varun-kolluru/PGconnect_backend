# Generated by Django 5.0.1 on 2024-01-17 06:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pgid', models.IntegerField(default=0)),
                ('roomno', models.IntegerField(default=0)),
                ('payer', models.CharField(max_length=40)),
                ('name_in_upi', models.CharField(max_length=40)),
                ('method', models.CharField(max_length=30)),
                ('Amount_paid', models.IntegerField(default=0)),
                ('actual_amount', models.IntegerField(default=0)),
                ('payment_date', models.CharField(max_length=20)),
                ('status', models.SmallIntegerField()),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Room_Info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roomno', models.IntegerField(default=0)),
                ('pgid', models.IntegerField(default=0)),
                ('capacity', models.IntegerField(default=0)),
            ],
            options={
                'unique_together': {('pgid', 'roomno')},
            },
        ),
        migrations.CreateModel(
            name='AppUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=50, unique=True)),
                ('username', models.CharField(max_length=40, unique=True)),
                ('register_date', models.DateField(auto_now_add=True)),
                ('fname', models.CharField(max_length=40)),
                ('lname', models.CharField(max_length=40)),
                ('is_active', models.BooleanField(default=True)),
                ('phone', models.CharField(max_length=12)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Pgs_Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pgname', models.CharField(max_length=40)),
                ('floors', models.IntegerField()),
                ('flats', models.IntegerField()),
                ('location', models.CharField(blank=True, default='Unknown', max_length=50, null=True)),
                ('address', models.CharField(blank=True, default='Unknown', max_length=100, null=True)),
                ('city', models.CharField(blank=True, default='Unknown', max_length=40, null=True)),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
            options={
                'unique_together': {('pgname', 'username')},
            },
        ),
        migrations.CreateModel(
            name='Guest_Info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roomno', models.IntegerField(default=0)),
                ('pgid', models.IntegerField(default=0)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('days_stay', models.IntegerField(default=30)),
                ('fee', models.IntegerField(default=0)),
                ('penality', models.IntegerField(default=0)),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
            options={
                'unique_together': {('username', 'pgid', 'roomno')},
            },
        ),
    ]
