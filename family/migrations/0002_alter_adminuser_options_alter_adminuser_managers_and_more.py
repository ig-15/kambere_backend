# Generated by Django 5.1.3 on 2024-12-17 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('family', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adminuser',
            options={},
        ),
        migrations.AlterModelManagers(
            name='adminuser',
            managers=[
            ],
        ),
        migrations.RemoveField(
            model_name='adminuser',
            name='date_joined',
        ),
        migrations.RemoveField(
            model_name='adminuser',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='adminuser',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='adminuser',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='adminuser',
            name='is_migepf_admin',
        ),
        migrations.RemoveField(
            model_name='adminuser',
            name='is_staff',
        ),
        migrations.RemoveField(
            model_name='adminuser',
            name='is_superuser',
        ),
        migrations.RemoveField(
            model_name='adminuser',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='adminuser',
            name='user_permissions',
        ),
        migrations.RemoveField(
            model_name='adminuser',
            name='username',
        ),
        migrations.AlterField(
            model_name='adminuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
