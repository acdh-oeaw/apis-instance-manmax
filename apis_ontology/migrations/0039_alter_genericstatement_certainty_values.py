# Generated by Django 4.1.13 on 2024-10-21 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0038_genericstatement_certainty_values'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genericstatement',
            name='certainty_values',
            field=models.JSONField(editable=False, null=True),
        ),
    ]