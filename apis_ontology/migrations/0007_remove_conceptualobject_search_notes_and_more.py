# Generated by Django 4.1.10 on 2023-07-19 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0006_communicateswith_method'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conceptualobject',
            name='search_notes',
        ),
        migrations.RemoveField(
            model_name='family',
            name='search_notes',
        ),
        migrations.RemoveField(
            model_name='genericevent',
            name='search_notes',
        ),
        migrations.RemoveField(
            model_name='genericstatement',
            name='search_notes',
        ),
        migrations.RemoveField(
            model_name='groupofpersons',
            name='search_notes',
        ),
        migrations.RemoveField(
            model_name='organisation',
            name='search_notes',
        ),
        migrations.RemoveField(
            model_name='person',
            name='search_notes',
        ),
        migrations.RemoveField(
            model_name='physicalobject',
            name='search_notes',
        ),
        migrations.RemoveField(
            model_name='place',
            name='search_notes',
        ),
        migrations.RemoveField(
            model_name='role',
            name='search_notes',
        ),
        migrations.RemoveField(
            model_name='task',
            name='search_notes',
        ),
        migrations.AddField(
            model_name='conceptualobject',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!'),
        ),
        migrations.AddField(
            model_name='family',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!'),
        ),
        migrations.AddField(
            model_name='genericevent',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!'),
        ),
        migrations.AddField(
            model_name='genericstatement',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!'),
        ),
        migrations.AddField(
            model_name='groupofpersons',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!'),
        ),
        migrations.AddField(
            model_name='organisation',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!'),
        ),
        migrations.AddField(
            model_name='person',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!'),
        ),
        migrations.AddField(
            model_name='physicalobject',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!'),
        ),
        migrations.AddField(
            model_name='place',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!'),
        ),
        migrations.AddField(
            model_name='role',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!'),
        ),
        migrations.AddField(
            model_name='task',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!'),
        ),
    ]
