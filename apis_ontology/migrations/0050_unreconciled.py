# Generated by Django 4.1.13 on 2025-06-11 11:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apis_entities', '0001_initial'),
        ('apis_ontology', '0049_degreetype_educationsubject_educationtype_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Unreconciled',
            fields=[
                ('tempentityclass_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_entities.tempentityclass')),
                ('unreconciled_type', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_entities.tempentityclass',),
        ),
    ]
