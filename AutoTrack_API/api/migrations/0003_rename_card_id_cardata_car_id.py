# Generated by Django 4.1.2 on 2023-04-05 21:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_alter_cardata_created"),
    ]

    operations = [
        migrations.RenameField(
            model_name="cardata",
            old_name="card_id",
            new_name="car_id",
        ),
    ]
