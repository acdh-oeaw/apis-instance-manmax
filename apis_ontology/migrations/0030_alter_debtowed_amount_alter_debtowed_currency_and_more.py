# Generated by Django 4.1.13 on 2023-12-04 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0029_debtowed_taxesandincome'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debtowed',
            name='amount',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Betrag'),
        ),
        migrations.AlterField(
            model_name='debtowed',
            name='currency',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Währung'),
        ),
        migrations.AlterField(
            model_name='debtowed',
            name='reason_for_debt',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='Grund für die Verschuldung'),
        ),
    ]