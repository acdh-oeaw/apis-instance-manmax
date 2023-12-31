# Generated by Django 4.1.10 on 2023-09-19 19:53

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0021_remove_arms_arms_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='conceptualobject',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=[], size=None),
        ),
        migrations.AddField(
            model_name='factoid',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=[], size=None),
        ),
        migrations.AddField(
            model_name='family',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=[], size=None),
        ),
        migrations.AddField(
            model_name='genericevent',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=[], size=None),
        ),
        migrations.AddField(
            model_name='genericstatement',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=[], size=None),
        ),
        migrations.AddField(
            model_name='groupofpersons',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=[], size=None),
        ),
        migrations.AddField(
            model_name='organisation',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=[], size=None),
        ),
        migrations.AddField(
            model_name='person',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=[], size=None),
        ),
        migrations.AddField(
            model_name='physicalobject',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=[], size=None),
        ),
        migrations.AddField(
            model_name='place',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=[], size=None),
        ),
        migrations.AddField(
            model_name='role',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=[], size=None),
        ),
        migrations.AddField(
            model_name='task',
            name='alternative_schuh_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, editable=False, max_length=500), default=[], size=None),
        ),
        migrations.AlterField(
            model_name='naming',
            name='add_name',
            field=models.CharField(blank=True, help_text="enthält ergänzende Namensbestandteile wie Spitznamen, Beinamen, Alias oder beschreibende Bestandteile von einem Namen ('Katharina <addName>die Große</addName>')", max_length=200, null=True, verbose_name='Beiname(n)'),
        ),
        migrations.AlterField(
            model_name='naming',
            name='forename',
            field=models.CharField(blank=True, help_text='der Vorname, Taufname, Rufname o.ä.', max_length=200, null=True, verbose_name='Vorname'),
        ),
        migrations.AlterField(
            model_name='naming',
            name='role_name',
            field=models.CharField(blank=True, help_text='bezeichnet eine spezifische Rolle, ein Rang in der Gesellschaft, mit der eine Person identifiziert werden kann', max_length=200, null=True, verbose_name='Titel'),
        ),
        migrations.AlterField(
            model_name='naming',
            name='surname',
            field=models.CharField(blank=True, help_text='der Name, der Familienzugehörigkeit beschreibt, im Gegensatz zum individuellen Vornamen. Zur Verwendung von Herkunfts- oder Berufsbezeichnungen als Famliennamen vgl. die Kodierungsrichtlinien', max_length=200, null=True, verbose_name='Familienname'),
        ),
    ]
