# Generated by Django 4.0.6 on 2022-07-31 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0007_alter_vehicle_company'),
        ('users', '0003_alter_user_vehicles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='vehicles',
            field=models.ManyToManyField(blank=True, related_name='drivers', to='companies.vehicle'),
        ),
    ]
