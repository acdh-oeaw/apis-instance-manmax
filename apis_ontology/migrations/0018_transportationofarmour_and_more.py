# Generated by Django 4.1.10 on 2023-09-18 11:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0017_rename_repairofobject_repairofarmour_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransportationOfArmour',
            fields=[
                ('transportationofobject_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.transportationofobject')),
            ],
            options={
                'verbose_name': 'Transport von Harnisch/Waffe',
                'verbose_name_plural': 'Transporte von Harnischen/Waffen',
            },
            bases=('apis_ontology.transportationofobject',),
        ),
        migrations.AlterModelOptions(
            name='decorationofarmour',
            options={'verbose_name': 'Verzierung von Harnisch/Waffe', 'verbose_name_plural': 'Verzierung von Harnischen/Waffen'},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'Befehl', 'verbose_name_plural': 'Befehle'},
        ),
        migrations.AlterModelOptions(
            name='repairofarmour',
            options={'verbose_name': 'Reparatur von Harnisch/Waffe', 'verbose_name_plural': 'Reparaturen von Harnischen/Waffen'},
        ),
        migrations.AlterModelOptions(
            name='transportationofobject',
            options={'verbose_name': 'Transport eines Objekts', 'verbose_name_plural': 'Transporte von Objekten'},
        ),
    ]
