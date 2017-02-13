# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import Q.questionnaire.q_utils


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0004_auto_20170201_0836'),
    ]

    operations = [
        migrations.CreateModel(
            name='QReference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.UUIDField()),
                ('model', models.CharField(max_length=128, null=True, blank=True)),
                ('experiment', models.CharField(max_length=128, null=True, blank=True)),
                ('institute', models.CharField(max_length=128, null=True, blank=True)),
                ('name', models.CharField(max_length=128, null=True, blank=True)),
                ('canonical_nama', models.CharField(max_length=128, null=True, blank=True)),
                ('alternative_name', models.CharField(max_length=128, null=True, blank=True)),
                ('long_name', models.TextField(null=True, blank=True)),
                ('version', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Questionnaire Reference',
                'verbose_name_plural': 'Questionnaire References',
            },
        ),
        migrations.AlterField(
            model_name='qcategorycustomization',
            name='category_title',
            field=models.CharField(max_length=64, verbose_name=b'Title', validators=[Q.questionnaire.q_utils.ValidateNoProfanities()]),
        ),
        migrations.AlterField(
            model_name='qcategorycustomization',
            name='name',
            field=models.CharField(help_text=b'A unique name for this customization.  Only alphanumeric characters are allowed.', max_length=128, verbose_name=b'Customization Name', validators=[Q.questionnaire.q_utils.ValidateNoBadChars(), Q.questionnaire.q_utils.ValidateNoSpaces(), Q.questionnaire.q_utils.ValidateNoReservedWords(), Q.questionnaire.q_utils.ValidateNoProfanities()]),
        ),
        migrations.AlterField(
            model_name='qcategoryproxy',
            name='cim_id',
            field=models.CharField(blank=True, max_length=256, null=True, help_text='A unique, CIM-specific, identifier.  This is distinct from the automatically-generated key.  It is required for distinguishing specialized objects of the same class.', validators=[Q.questionnaire.q_utils.ValidateNoSpaces()]),
        ),
        migrations.AlterField(
            model_name='qmodelcustomization',
            name='name',
            field=models.CharField(help_text=b'A unique name for this customization.  Only alphanumeric characters are allowed.', max_length=128, verbose_name=b'Customization Name', validators=[Q.questionnaire.q_utils.ValidateNoBadChars(), Q.questionnaire.q_utils.ValidateNoSpaces(), Q.questionnaire.q_utils.ValidateNoReservedWords(), Q.questionnaire.q_utils.ValidateNoProfanities()]),
        ),
        migrations.AlterField(
            model_name='qmodelproxy',
            name='cim_id',
            field=models.CharField(blank=True, max_length=256, null=True, help_text='A unique, CIM-specific, identifier.  This is distinct from the automatically-generated key.  It is required for distinguishing specialized objects of the same class.', validators=[Q.questionnaire.q_utils.ValidateNoSpaces()]),
        ),
        migrations.AlterField(
            model_name='qontology',
            name='name',
            field=models.CharField(max_length=512, validators=[Q.questionnaire.q_utils.ValidateNoSpaces(), Q.questionnaire.q_utils.ValidateNoBadChars()]),
        ),
        migrations.AlterField(
            model_name='qproject',
            name='name',
            field=models.CharField(help_text="This is a unique name that identifies the project.  Choose wisely as, unlike the 'title', it will be used in various URLs.  Note that this must match up w/ the project name used by other ES-DOC tools.", unique=True, max_length=128, validators=[Q.questionnaire.q_utils.ValidateNoSpaces(), Q.questionnaire.q_utils.ValidateNoBadChars(), Q.questionnaire.q_utils.ValidateNoReservedWords(), Q.questionnaire.q_utils.ValidateNoProfanities()]),
        ),
        migrations.AlterField(
            model_name='qpropertycustomization',
            name='name',
            field=models.CharField(help_text=b'A unique name for this customization.  Only alphanumeric characters are allowed.', max_length=128, verbose_name=b'Customization Name', validators=[Q.questionnaire.q_utils.ValidateNoBadChars(), Q.questionnaire.q_utils.ValidateNoSpaces(), Q.questionnaire.q_utils.ValidateNoReservedWords(), Q.questionnaire.q_utils.ValidateNoProfanities()]),
        ),
        migrations.AlterField(
            model_name='qpropertycustomization',
            name='property_title',
            field=models.CharField(max_length=128, validators=[Q.questionnaire.q_utils.ValidateNoProfanities()]),
        ),
        migrations.AlterField(
            model_name='qpropertyproxy',
            name='cim_id',
            field=models.CharField(blank=True, max_length=256, null=True, help_text='A unique, CIM-specific, identifier.  This is distinct from the automatically-generated key.  It is required for distinguishing specialized objects of the same class.', validators=[Q.questionnaire.q_utils.ValidateNoSpaces()]),
        ),
    ]
