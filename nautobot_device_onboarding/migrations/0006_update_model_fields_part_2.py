# Generated by Django 3.2.20 on 2023-09-25 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nautobot_device_onboarding', '0006_update_model_fields_part_1'),
    ]

    operations = [
        
        migrations.AlterField(
            model_name='onboardingtask',
            name='device_type',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
       

    ]


