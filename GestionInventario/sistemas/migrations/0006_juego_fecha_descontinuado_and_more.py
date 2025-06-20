# Generated by Django 5.2 on 2025-06-16 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistemas', '0005_alter_juego_imagen'),
    ]

    operations = [
        migrations.AddField(
            model_name='juego',
            name='fecha_descontinuado',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de descontinuación'),
        ),
        migrations.AddField(
            model_name='juego',
            name='stock_al_descontinuar',
            field=models.IntegerField(default=0, help_text='Cantidad de unidades que tenía cuando se descontinuó', verbose_name='Stock al descontinuar'),
        ),
    ]
