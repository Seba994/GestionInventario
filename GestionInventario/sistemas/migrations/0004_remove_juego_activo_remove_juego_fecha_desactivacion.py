# Generated by Django 5.2 on 2025-06-15 05:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sistemas', '0003_juego_activo_juego_fecha_desactivacion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='juego',
            name='activo',
        ),
        migrations.RemoveField(
            model_name='juego',
            name='fecha_desactivacion',
        ),
    ]
