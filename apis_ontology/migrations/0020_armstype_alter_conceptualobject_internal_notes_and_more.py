# Generated by Django 4.1.10 on 2023-09-19 15:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0019_familymembership_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArmsType',
            fields=[
                ('typology_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.typology')),
            ],
            options={
                'verbose_name': 'Harnisches-/Waffentyp',
                'verbose_name_plural': 'Harnisches-/Waffentypen',
            },
            bases=('apis_ontology.typology',),
        ),
        migrations.AlterField(
            model_name='conceptualobject',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!', null=True, verbose_name='Interne Notizen'),
        ),
        migrations.AlterField(
            model_name='factoid',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!', null=True, verbose_name='Interne Notizen'),
        ),
        migrations.AlterField(
            model_name='family',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!', null=True, verbose_name='Interne Notizen'),
        ),
        migrations.AlterField(
            model_name='genericevent',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!', null=True, verbose_name='Interne Notizen'),
        ),
        migrations.AlterField(
            model_name='genericstatement',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!', null=True, verbose_name='Interne Notizen'),
        ),
        migrations.AlterField(
            model_name='groupofpersons',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!', null=True, verbose_name='Interne Notizen'),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!', null=True, verbose_name='Interne Notizen'),
        ),
        migrations.AlterField(
            model_name='person',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!', null=True, verbose_name='Interne Notizen'),
        ),
        migrations.AlterField(
            model_name='physicalobject',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!', null=True, verbose_name='Interne Notizen'),
        ),
        migrations.AlterField(
            model_name='place',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!', null=True, verbose_name='Interne Notizen'),
        ),
        migrations.AlterField(
            model_name='role',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!', null=True, verbose_name='Interne Notizen'),
        ),
        migrations.AlterField(
            model_name='task',
            name='internal_notes',
            field=models.TextField(blank=True, help_text='Internal searchable text, for disambiguation. Store information as statements!', null=True, verbose_name='Interne Notizen'),
        ),
    ]