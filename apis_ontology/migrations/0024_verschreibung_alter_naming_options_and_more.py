# Generated by Django 4.1.10 on 2023-11-14 08:11

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0023_alter_conceptualobject_alternative_schuh_ids_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Verschreibung',
            fields=[
                ('genericstatement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericstatement')),
            ],
            options={
                'verbose_name': 'Verschreibung',
                'verbose_name_plural': 'Verschreibungen',
            },
            bases=('apis_ontology.genericstatement',),
        ),
        migrations.AlterModelOptions(
            name='naming',
            options={'verbose_name': 'Benennung einer Person', 'verbose_name_plural': 'Benennungen von Personen'},
        ),
        migrations.AlterField(
            model_name='conceptualobject',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=list, editable=False, size=None),
        ),
        migrations.AlterField(
            model_name='factoid',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=list, editable=False, size=None),
        ),
        migrations.AlterField(
            model_name='family',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=list, editable=False, size=None),
        ),
        migrations.AlterField(
            model_name='genericevent',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=list, editable=False, size=None),
        ),
        migrations.AlterField(
            model_name='genericstatement',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=list, editable=False, size=None),
        ),
        migrations.AlterField(
            model_name='groupofpersons',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=list, editable=False, size=None),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=list, editable=False, size=None),
        ),
        migrations.AlterField(
            model_name='person',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=list, editable=False, size=None),
        ),
        migrations.AlterField(
            model_name='physicalobject',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=list, editable=False, size=None),
        ),
        migrations.AlterField(
            model_name='place',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=list, editable=False, size=None),
        ),
        migrations.AlterField(
            model_name='role',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=list, editable=False, size=None),
        ),
        migrations.AlterField(
            model_name='task',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=list, editable=False, size=None),
        ),
    ]