# Generated by Django 4.1.13 on 2023-12-04 15:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0031_depicitionofpersoninart_textualcitationallusion'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArtworkHasAdditionalName',
            fields=[
                ('genericstatement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericstatement')),
                ('additional_name', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Kunstwerk hat zusätzlichen Namen',
                'verbose_name_plural': 'Kunstwerke hat zusätzliche Namen',
            },
            bases=('apis_ontology.genericstatement',),
        ),
        migrations.AlterModelOptions(
            name='utilisationinevent',
            options={'verbose_name': 'Verwendung von Harnisch/Waffe', 'verbose_name_plural': 'Verwendungen von Harnischen/Waffen'},
        ),
    ]