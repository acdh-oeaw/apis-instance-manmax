# Generated by Django 4.1.13 on 2024-10-21 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0037_alter_factoid_review_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='genericstatement',
            name='certainty_values',
            field=models.JSONField(null=True),
        ),
    ]