# Generated by Django 4.1.13 on 2024-10-22 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0040_alter_genericstatement_certainty_values'),
    ]

    operations = [
        migrations.AddField(
            model_name='genericstatement',
            name='certainty',
            field=models.JSONField(null=True),
        ),
    ]