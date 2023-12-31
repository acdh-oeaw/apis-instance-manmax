# Generated by Django 4.1.10 on 2023-08-30 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apis_entities', '0001_initial'),
        ('apis_ontology', '0011_armour_alter_repairofobject_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Factoid',
            fields=[
                ('tempentityclass_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_entities.tempentityclass')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=300)),
                ('created_when', models.DateTimeField(auto_now_add=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=300)),
                ('modified_when', models.DateTimeField(auto_now=True)),
                ('internal_notes', models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!')),
                ('schuh_index_id', models.CharField(blank=True, editable=False, max_length=500)),
            ],
            bases=('apis_entities.tempentityclass',),
        ),
    ]
