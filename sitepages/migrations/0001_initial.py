# Generated by Django 3.2.9 on 2025-04-02 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(max_length=255)),
                ('lastName', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=255)),
                ('street', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('county', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=255)),
                ('postcode', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'user_contact',
            },
        ),
    ]
