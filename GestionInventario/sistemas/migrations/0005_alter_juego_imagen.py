# Generated by Django 5.2 on 2025-06-16 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistemas', '0004_remove_juego_activo_remove_juego_fecha_desactivacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='juego',
            name='imagen',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
