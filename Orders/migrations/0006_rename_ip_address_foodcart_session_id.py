# Generated by Django 4.2 on 2023-05-16 17:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Orders', '0005_alter_deliveryentity_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='foodcart',
            old_name='ip_address',
            new_name='session_id',
        ),
    ]
