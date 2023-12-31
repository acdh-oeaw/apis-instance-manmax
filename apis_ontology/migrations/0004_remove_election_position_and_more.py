# Generated by Django 4.1.10 on 2023-07-19 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0003_conceptualobject_search_notes_family_search_notes_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='election',
            name='position',
        ),
        migrations.AddField(
            model_name='conceptualobject',
            name='schuch_index_id',
            field=models.CharField(blank=True, editable=False, max_length=500),
        ),
        migrations.AddField(
            model_name='family',
            name='schuch_index_id',
            field=models.CharField(blank=True, editable=False, max_length=500),
        ),
        migrations.AddField(
            model_name='genericevent',
            name='schuch_index_id',
            field=models.CharField(blank=True, editable=False, max_length=500),
        ),
        migrations.AddField(
            model_name='genericstatement',
            name='schuch_index_id',
            field=models.CharField(blank=True, editable=False, max_length=500),
        ),
        migrations.AddField(
            model_name='groupofpersons',
            name='schuch_index_id',
            field=models.CharField(blank=True, editable=False, max_length=500),
        ),
        migrations.AddField(
            model_name='organisation',
            name='schuch_index_id',
            field=models.CharField(blank=True, editable=False, max_length=500),
        ),
        migrations.AddField(
            model_name='person',
            name='schuch_index_id',
            field=models.CharField(blank=True, editable=False, max_length=500),
        ),
        migrations.AddField(
            model_name='physicalobject',
            name='schuch_index_id',
            field=models.CharField(blank=True, editable=False, max_length=500),
        ),
        migrations.AddField(
            model_name='place',
            name='schuch_index_id',
            field=models.CharField(blank=True, editable=False, max_length=500),
        ),
        migrations.AddField(
            model_name='role',
            name='schuch_index_id',
            field=models.CharField(blank=True, editable=False, max_length=500),
        ),
        migrations.AddField(
            model_name='task',
            name='schuch_index_id',
            field=models.CharField(blank=True, editable=False, max_length=500),
        ),
        migrations.DeleteModel(
            name='Acquisition',
        ),
    ]
