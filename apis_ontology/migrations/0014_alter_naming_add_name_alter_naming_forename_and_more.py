# Generated by Django 4.1.10 on 2023-09-14 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0013_alter_conceptualobject_internal_notes_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='naming',
            name='add_name',
            field=models.CharField(blank=True, help_text='(additional name) contains an additional name component, such as a nickname, epithet, or alias, or any other descriptive phrase used within a personal name.', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='naming',
            name='forename',
            field=models.CharField(blank=True, help_text='contains a forename, given or baptismal name (for multiple, separate with a space)', max_length=200, null=True, verbose_name='Forename'),
        ),
        migrations.AlterField(
            model_name='naming',
            name='role_name',
            field=models.CharField(blank=True, help_text='contains a name component which indicates that the referent has a particular role or position in society, such as an official title or rank.', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='naming',
            name='surname',
            field=models.CharField(blank=True, help_text='contains a family (inherited) name, as opposed to a given, baptismal, or nick name (for multiple, separate with a space)', max_length=200, null=True),
        ),
    ]