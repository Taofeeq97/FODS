# Generated by Django 4.2 on 2023-05-16 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Orders', '0007_rename_ip_address_orderedfood_session_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foodcart',
            name='session_id',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='orderedfood',
            name='session_id',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]