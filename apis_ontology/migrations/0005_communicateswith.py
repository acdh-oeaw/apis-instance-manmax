# Generated by Django 4.1.10 on 2023-07-19 12:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0004_remove_election_position_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunicatesWith',
            fields=[
                ('genericstatement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericstatement')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.genericstatement',),
        ),
    ]
