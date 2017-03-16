# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import Q.questionnaire.models.models_ontologies
import Q.questionnaire.q_utils
import Q.questionnaire.q_fields
import Q.questionnaire.models.models_projects
import django.db.models.deletion
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='QCategoryCustomization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text=b'A unique name for this customization.  Only alphanumeric characters are allowed.', max_length=128, verbose_name=b'Customization Name', validators=[Q.questionnaire.q_utils.ValidateNoBadChars(), Q.questionnaire.q_utils.ValidateNoSpaces(), Q.questionnaire.q_utils.ValidateNoReservedWords(), Q.questionnaire.q_utils.ValidateNoProfanities()])),
                ('category_title', models.CharField(max_length=64, verbose_name=b'Title', validators=[Q.questionnaire.q_utils.ValidateNoProfanities()])),
                ('category_description', models.TextField(null=True, verbose_name=b'Description', blank=True)),
                ('is_hidden', models.BooleanField(default=False, help_text='Note that hiding a category will not hide all of its member properties; It will simply not render them in a parent tab.', verbose_name=b'Should this category <u>not</u> be displayed?')),
                ('order', models.PositiveIntegerField(help_text='Do not modify this value directly <em>here</em>.  Instead, drag and drop individual category widgets on the main form.', null=True, verbose_name=b'Order', blank=True)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
                'verbose_name': '_Questionnaire Customization: Category',
                'verbose_name_plural': '_Questionnaire Customizations: Categories',
            },
        ),
        migrations.CreateModel(
            name='QCategoryProxy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.PositiveIntegerField(null=True, blank=True)),
                ('is_meta', models.NullBooleanField()),
                ('name', models.CharField(max_length=256)),
                ('documentation', models.TextField(null=True, blank=True)),
                ('cim_id', models.CharField(blank=True, max_length=256, null=True, help_text='A unique, CIM-specific, identifier.  This is distinct from the automatically-generated key.  It is required for distinguishing specialized objects of the same class.', validators=[Q.questionnaire.q_utils.ValidateNoSpaces()])),
                ('is_uncategorized', models.BooleanField(default=False, help_text="An 'uncategorized' category is one which was not specified by the CIM; it acts as a placeholder within which to nest properties in the Questionnaire.")),
            ],
            options={
                'ordering': ['order'],
                'abstract': False,
                'verbose_name': '_Questionnaire Proxy: Category',
                'verbose_name_plural': '_Questionnaire Proxy: Categories',
            },
        ),
        migrations.CreateModel(
            name='QCategoryRealization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_complete', models.BooleanField(default=False)),
                ('order', models.PositiveIntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=256)),
                ('category_value', models.CharField(max_length=1024)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
                'verbose_name': '_Questionnaire Realization: Category',
                'verbose_name_plural': '_Questionnaire Realizations: Categories',
            },
        ),
        migrations.CreateModel(
            name='QInstitute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=512)),
                ('description', models.TextField(null=True, blank=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
                'verbose_name': 'Questionnaire Institute',
                'verbose_name_plural': 'Questionnaire Institutes',
            },
        ),
        migrations.CreateModel(
            name='QModelCustomization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text=b'A unique name for this customization.  Only alphanumeric characters are allowed.', max_length=128, verbose_name=b'Customization Name', validators=[Q.questionnaire.q_utils.ValidateNoBadChars(), Q.questionnaire.q_utils.ValidateNoSpaces(), Q.questionnaire.q_utils.ValidateNoReservedWords(), Q.questionnaire.q_utils.ValidateNoProfanities()])),
                ('order', models.PositiveIntegerField()),
                ('documentation', models.TextField(help_text=b'An explanation of how this customization is intended to be used. This information is for informational purposes only.', null=True, verbose_name=b'Customization Description', blank=True)),
                ('is_default', models.BooleanField(default=False, help_text=b'Every CIM Document Type must have one default customization. If this is the first customization you are creating, please ensure this checkbox is selected.', verbose_name=b'Is Default Customization?')),
                ('model_title', models.CharField(max_length=512, null=True, verbose_name=b'Name that should appear on the Document Form')),
                ('model_description', models.TextField(help_text=b'This text will appear as documentation in the editing form.  Inline HTML formatting is permitted.  The initial documentation comes from the ontology.', null=True, verbose_name=b'A description of the document', blank=True)),
                ('model_hierarchy_title', models.CharField(help_text=b'This text will appear as a label for the tree view widget used to navigate the hierarchy of components', max_length=256, null=True, verbose_name=b'Title to use for the component hierarchy tree', blank=True)),
                ('model_show_empty_categories', models.BooleanField(default=False, help_text=b'Include categories in the editing form for which there are no (visible) properties associated with.', verbose_name=b'Display empty categories?')),
                ('owner', models.ForeignKey(related_name='owned_customizations', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
                'verbose_name': '_Questionnaire Customization: Model',
                'verbose_name_plural': '_Questionnaire Customizations: Models',
            },
        ),
        migrations.CreateModel(
            name='QModelProxy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.PositiveIntegerField(null=True, blank=True)),
                ('is_meta', models.NullBooleanField()),
                ('name', models.CharField(max_length=256)),
                ('documentation', models.TextField(null=True, blank=True)),
                ('cim_id', models.CharField(blank=True, max_length=256, null=True, help_text='A unique, CIM-specific, identifier.  This is distinct from the automatically-generated key.  It is required for distinguishing specialized objects of the same class.', validators=[Q.questionnaire.q_utils.ValidateNoSpaces()])),
                ('package', models.CharField(max_length=256)),
                ('is_document', models.NullBooleanField()),
                ('label', Q.questionnaire.q_fields.QJSONField(null=True, blank=True)),
            ],
            options={
                'ordering': ['order'],
                'abstract': False,
                'verbose_name': '_Questionnaire Proxy: Model',
                'verbose_name_plural': '_Questionnaire Proxy: Models',
            },
        ),
        migrations.CreateModel(
            name='QModelRealization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_complete', models.BooleanField(default=False)),
                ('order', models.PositiveIntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=256)),
                ('version', Q.questionnaire.q_fields.QVersionField(null=True, blank=True)),
                ('is_root', models.BooleanField(default=False)),
                ('is_published', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('owner', models.ForeignKey(related_name='owned_models', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
                'verbose_name': '_Questionnaire Realization: Model',
                'verbose_name_plural': '_Questionnaire Realizations: Models',
            },
        ),
        migrations.CreateModel(
            name='QOntology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=512, validators=[Q.questionnaire.q_utils.ValidateNoSpaces(), Q.questionnaire.q_utils.ValidateNoBadChars()])),
                ('version', Q.questionnaire.q_fields.QVersionField()),
                ('documentation', models.TextField(help_text=b'This may be overwritten by any descriptive text found in the QConfig file.', null=True, blank=True)),
                ('url', models.URLField(null=True, blank=True)),
                ('file', Q.questionnaire.q_fields.QFileField(help_text=b'Note that files with the same names will be overwritten', storage=Q.questionnaire.q_fields.OverwriteStorage(), upload_to=b'questionnaire/ontologies', validators=[Q.questionnaire.models.models_ontologies.validate_ontology_file_extension, Q.questionnaire.models.models_ontologies.validate_ontology_file_schema])),
                ('last_registered_version', Q.questionnaire.q_fields.QVersionField(null=True, blank=True)),
                ('ontology_type', models.CharField(max_length=256, choices=[(b'SPECIALIZATION', b'Specialization (ie: CMIP6)'), (b'SCHEMA', b'Schema (ie: CIM2)')])),
                ('is_registered', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='questionnaire.QOntology', help_text='Which existing ontology (if any) is this ontology based upon?', null=True, verbose_name=b'Base Ontology')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Questionnaire Ontology',
                'verbose_name_plural': 'Questionnaire Ontologies',
            },
        ),
        migrations.CreateModel(
            name='QProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128, validators=[Q.questionnaire.q_utils.ValidateNoSpaces(), Q.questionnaire.q_utils.ValidateNoBadChars(), Q.questionnaire.q_utils.ValidateNoReservedWords(), Q.questionnaire.q_utils.ValidateNoProfanities()])),
                ('title', models.CharField(max_length=128, validators=[Q.questionnaire.q_utils.ValidateNoProfanities()])),
                ('description', models.TextField(blank=True)),
                ('email', models.EmailField(help_text='Point of contact for this project.', max_length=254, verbose_name=b'Contact Email')),
                ('url', models.URLField(help_text='External URL for this project.', blank=True)),
                ('logo', models.ImageField(help_text=b'All images will be resized to 96 x 96.', storage=Q.questionnaire.q_fields.OverwriteStorage(), null=True, upload_to=Q.questionnaire.models.models_projects.generate_upload_to, blank=True)),
                ('display_logo', models.BooleanField(default=False)),
                ('authenticated', models.BooleanField(default=True)),
                ('is_legacy', models.BooleanField(default=False, help_text=b"A legacy project is one that still uses CIM1 and requests must therefore be routed through the legacy site.  Do not check this unless you really know what you're doing.")),
                ('is_active', models.BooleanField(default=True, help_text=b'A project that is not active cannot be used')),
                ('is_displayed', models.BooleanField(default=True, help_text=b'A project that is not displayed is not included in the Index Page, although users can still navigate to it if they know its URL')),
                ('groups', models.ManyToManyField(to='auth.Group', blank=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Questionnaire Project',
                'verbose_name_plural': 'Questionnaire Projects',
            },
        ),
        migrations.CreateModel(
            name='QProjectOntology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ontology', models.ForeignKey(related_name='+', to='questionnaire.QOntology')),
                ('project', models.ForeignKey(related_name='+', to='questionnaire.QProject')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Questionnaire Project Ontology',
                'verbose_name_plural': 'Questionnaire Project Ontologies',
            },
        ),
        migrations.CreateModel(
            name='QPropertyCustomization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text=b'A unique name for this customization.  Only alphanumeric characters are allowed.', max_length=128, verbose_name=b'Customization Name', validators=[Q.questionnaire.q_utils.ValidateNoBadChars(), Q.questionnaire.q_utils.ValidateNoSpaces(), Q.questionnaire.q_utils.ValidateNoReservedWords(), Q.questionnaire.q_utils.ValidateNoProfanities()])),
                ('property_title', models.CharField(max_length=128, validators=[Q.questionnaire.q_utils.ValidateNoProfanities()])),
                ('is_required', models.BooleanField(default=True, help_text='All required properties must be completed prior to publication.  A property that is defined as required <em>in the CIM or a CV</em> cannot be made optional.', verbose_name=b'Is this property required?')),
                ('is_hidden', models.BooleanField(default=True, help_text='A property that is defined as required in an ontology should not be hidden.', verbose_name=b'Should this property <u>not</u> be displayed?')),
                ('is_editable', models.BooleanField(default=True, help_text='If this field is disabled, this is because a default value was set by the ontology itselfand should not therefore be overridden by the ES-DOC Questionnaire.', verbose_name=b'Can this property be edited?')),
                ('is_nillable', models.BooleanField(default=True, help_text=b'A nillable property can be intentionally left blank for several reasons: Unknown, Missing, Inapplicable, Template, Withheld.', verbose_name=b'Should <i>nillable</i> options be allowed?')),
                ('property_description', models.TextField(null=True, verbose_name="What is the help text to associate with this property?<p class='documentation'>Any initial help text comes from the CIM.</p><p class='documentation'>Note that basic HTML tags are supported.</p>", blank=True)),
                ('inline_help', models.BooleanField(default=False, verbose_name=b'Should the help text be displayed inline?')),
                ('order', models.PositiveIntegerField(null=True, blank=True)),
                ('field_type', models.CharField(max_length=512, choices=[(b'ATOMIC', b'Atomic'), (b'RELATIONSHIP', b'Relationship'), (b'ENUMERATION', b'Enumeration')])),
                ('can_inherit', models.BooleanField(default=False, help_text="Enabling inheritance will allow the corresponding properties of child components to 'inherit' the value of this property.  The editing form will allow users the ability to 'opt-out' of this inheritance.", verbose_name=b'Can this property be inherited by children?')),
                ('default_values', Q.questionnaire.q_fields.QJSONField(help_text='If this field is disabled, this is because a default value was set by the ontology itselfand should not therefore be overridden by the ES-DOC Questionnaire.  <em>In this case, the property should also not be editable.</em>', null=True, verbose_name="What are the default values for this property?<p class='documentation'>Please enter a comma-separated list of strings.</p>", blank=True)),
                ('atomic_type', models.CharField(default=b'DEFAULT', help_text='By default, all fields are rendered as strings.  However, a field can be customized to accept longer snippets of text, dates, email addresses, etc.', max_length=512, verbose_name=b'How should this field be rendered?', choices=[(b'DEFAULT', b'Character Field (default)'), (b'TEXT', b'Text Field (large block of text as opposed to a small string)'), (b'BOOLEAN', b'Boolean Field'), (b'INTEGER', b'Integer Field'), (b'DECIMAL', b'Decimal Field'), (b'URL', b'URL Field'), (b'EMAIL', b'Email Field'), (b'DATE', b'Date Field'), (b'DATETIME', b'Date Time Field'), (b'TIME', b'Time Field')])),
                ('atomic_suggestions', models.TextField(help_text=b"Please enter a '|' separated list of words or phrases.", null=True, verbose_name=b'Are there any suggestions you would like to offer as auto-completion options?', blank=True)),
                ('enumeration_is_open', models.BooleanField(default=False, verbose_name=b'Can a user can specify a custom "OTHER" value?')),
                ('relationship_show_subforms', models.BooleanField(default=False, help_text='Checking this will cause the property to be rendered as a nested subform within the parent form;  All properties of the target model will be available to view and edit in that subform.  Unchecking it will cause the attribute to be rendered as a <em>reference</em> widget.', verbose_name="Should this property be rendered in its own subform?<p class='documentation'>Note that a relationship to another CIM Document <u>cannot</u> use subforms, while a relationship to anything else <u>must</u> use subforms.</p>")),
                ('relationship_is_hierarchical', models.BooleanField(default=False, help_text="Checking this will cause the property to be rendered in a treeview; All properties of the target model will be avaialble as a pane next to that treeview.  This value is set by the ontology itself.  Unless you know what you're doing, <em>don't mess with it</em>.", verbose_name='Should this property be rendered as part of a hierarchy?')),
                ('category_customization', models.ForeignKey(related_name='property_customizations', blank=True, to='questionnaire.QCategoryCustomization', null=True)),
                ('model_customization', models.ForeignKey(related_name='property_customizations', to='questionnaire.QModelCustomization')),
                ('project', models.ForeignKey(related_name='property_customizations', to='questionnaire.QProject')),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
                'verbose_name': '_Questionnaire Customization: Property',
                'verbose_name_plural': '_Questionnaire Customizations: Properties',
            },
        ),
        migrations.CreateModel(
            name='QPropertyProxy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.PositiveIntegerField(null=True, blank=True)),
                ('is_meta', models.NullBooleanField()),
                ('name', models.CharField(max_length=256)),
                ('documentation', models.TextField(null=True, blank=True)),
                ('cim_id', models.CharField(blank=True, max_length=256, null=True, help_text='A unique, CIM-specific, identifier.  This is distinct from the automatically-generated key.  It is required for distinguishing specialized objects of the same class.', validators=[Q.questionnaire.q_utils.ValidateNoSpaces()])),
                ('category_id', models.CharField(max_length=256, null=True, blank=True)),
                ('field_type', models.CharField(max_length=256, choices=[(b'ATOMIC', b'Atomic'), (b'RELATIONSHIP', b'Relationship'), (b'ENUMERATION', b'Enumeration')])),
                ('cardinality_min', models.CharField(max_length=2, choices=[(b'0', b'0'), (b'1', b'1'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'10')])),
                ('cardinality_max', models.CharField(max_length=2, choices=[(b'N', b'N'), (b'0', b'0'), (b'1', b'1'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'10')])),
                ('is_nillable', models.BooleanField(default=True)),
                ('is_hierarchical', models.BooleanField(default=False)),
                ('values', Q.questionnaire.q_fields.QJSONField(null=True, blank=True)),
                ('atomic_type', models.CharField(blank=True, max_length=256, null=True, choices=[(b'DEFAULT', b'Character Field (default)'), (b'TEXT', b'Text Field (large block of text as opposed to a small string)'), (b'BOOLEAN', b'Boolean Field'), (b'INTEGER', b'Integer Field'), (b'DECIMAL', b'Decimal Field'), (b'URL', b'URL Field'), (b'EMAIL', b'Email Field'), (b'DATE', b'Date Field'), (b'DATETIME', b'Date Time Field'), (b'TIME', b'Time Field')])),
                ('enumeration_is_open', models.BooleanField(default=False)),
                ('enumeration_choices', Q.questionnaire.q_fields.QJSONField(null=True, blank=True)),
                ('relationship_target_names', Q.questionnaire.q_fields.QJSONField(null=True, blank=True)),
                ('category_proxy', models.ForeignKey(related_name='property_proxies', blank=True, to='questionnaire.QCategoryProxy', null=True)),
                ('model_proxy', models.ForeignKey(related_name='property_proxies', to='questionnaire.QModelProxy')),
                ('ontology', models.ForeignKey(related_name='property_proxies', blank=True, to='questionnaire.QOntology', null=True)),
                ('relationship_target_models', models.ManyToManyField(to='questionnaire.QModelProxy', blank=True)),
            ],
            options={
                'ordering': ['order'],
                'abstract': False,
                'verbose_name': '_Questionnaire Proxy: Property',
                'verbose_name_plural': '_Questionnaire Proxy: Properties',
            },
        ),
        migrations.CreateModel(
            name='QPropertyRealization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_complete', models.BooleanField(default=False)),
                ('order', models.PositiveIntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=256)),
                ('is_nil', models.BooleanField(default=False)),
                ('nil_reason', models.CharField(default=b'UNKNOWN', max_length=512, choices=[(b'UNKNOWN', b'The correct value is not known, and not computable by, the sender of this data.  However, a correct value probably exists.'), (b'MISSING', b'The correct value is not readily available to the sender of this data. Furthermore, a correct value may not exist.'), (b'INAPPLICABLE', b'There is no value.'), (b'TEMPLATE', b'The value will be available later.'), (b'WITHHELD', b'The value is not divulged.')])),
                ('field_type', models.CharField(max_length=512, choices=[(b'ATOMIC', b'Atomic'), (b'RELATIONSHIP', b'Relationship'), (b'ENUMERATION', b'Enumeration')])),
                ('atomic_value', models.TextField(null=True, blank=True)),
                ('enumeration_value', Q.questionnaire.q_fields.QEnumerationField(null=True, blank=True)),
                ('enumeration_other_value', models.CharField(max_length=1024, null=True, blank=True)),
                ('category', models.ForeignKey(related_name='properties', blank=True, to='questionnaire.QCategoryRealization', null=True)),
                ('model', models.ForeignKey(related_name='properties', to='questionnaire.QModelRealization')),
                ('proxy', models.ForeignKey(related_name='properties', to='questionnaire.QPropertyProxy')),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
                'verbose_name': '_Questionnaire Realization: Property',
                'verbose_name_plural': '_Questionnaire Realizations: Properties',
            },
        ),
        migrations.CreateModel(
            name='QPublication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.UUIDField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('version', Q.questionnaire.q_fields.QVersionField()),
                ('format', models.CharField(max_length=128, choices=[(b'CIM2_XML', b'CIM2 XML')])),
                ('content', models.TextField()),
                ('model', models.ForeignKey(related_name='publications', to='questionnaire.QModelRealization')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Questionnaire Publication',
                'verbose_name_plural': 'Questionnaire Publications',
            },
        ),
        migrations.CreateModel(
            name='QReference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.UUIDField(null=True, verbose_name=b'UUID', blank=True)),
                ('model', models.CharField(max_length=128, null=True, blank=True)),
                ('experiment', models.CharField(max_length=128, null=True, blank=True)),
                ('institute', models.CharField(max_length=128, null=True, blank=True)),
                ('name', models.CharField(max_length=128, null=True, blank=True)),
                ('canonical_name', models.CharField(max_length=128, null=True, blank=True)),
                ('alternative_name', models.CharField(max_length=128, null=True, blank=True)),
                ('long_name', models.TextField(null=True, blank=True)),
                ('version', models.IntegerField(null=True, blank=True)),
                ('document_type', models.CharField(max_length=512, null=True, blank=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Questionnaire Reference',
                'verbose_name_plural': 'Questionnaire References',
            },
        ),
        migrations.CreateModel(
            name='QSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(blank=True, max_length=128, choices=[(b'LOCAL', b'Local'), (b'TEST', b'Test'), (b'DEV', b'Development'), (b'PROD', b'Production')])),
                ('site', models.OneToOneField(related_name='q_site', to='sites.Site')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Questionnaire Site',
                'verbose_name_plural': 'Questionnaire Sites',
            },
        ),
        migrations.CreateModel(
            name='QSynchronization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(unique=True, max_length=128, choices=[(b'ONTOLOGY_ADDED', b'Added Ontology'), (b'ONTOLOGY_REMOVED', b'Removed Ontology'), (b'ONTOLOGY_CHANGED', b'Changed Ontology'), (b'CUSTOMIZATION_ADDED', b'Added Customization'), (b'CUSTOMIZATION_REMOVED', b'Removed Customization'), (b'CUSTOMIZATION_CHANGED', b'Changed Customization')])),
                ('description', models.TextField(null=True, blank=True)),
                ('priority', models.PositiveIntegerField(unique=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Questionnaire (Un)Synchronization Type',
                'verbose_name_plural': 'Questionnaire (Un)Synchronization Types',
            },
        ),
        migrations.CreateModel(
            name='QUserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('change_password', models.BooleanField(default=False, verbose_name=b'Change password at next logon')),
                ('description', models.TextField(null=True, verbose_name=b'Description', blank=True)),
                ('institute', models.ForeignKey(verbose_name=b'Institution', blank=True, to='questionnaire.QInstitute', null=True)),
                ('projects', models.ManyToManyField(to='questionnaire.QProject', verbose_name=b'Project Membership', blank=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Questionnaire User Profile',
                'verbose_name_plural': 'Questionnaire User Profiles',
            },
        ),
        migrations.AddField(
            model_name='qpropertyrealization',
            name='relationship_references',
            field=models.ManyToManyField(related_name='properties', to='questionnaire.QReference', blank=True),
        ),
        migrations.AddField(
            model_name='qpropertycustomization',
            name='proxy',
            field=models.ForeignKey(to='questionnaire.QPropertyProxy'),
        ),
        migrations.AddField(
            model_name='qproject',
            name='ontologies',
            field=models.ManyToManyField(help_text=b'Only registered ontologies (schemas or specializations) can be added to projects.', to='questionnaire.QOntology', verbose_name=b'Supported Ontologies', through='questionnaire.QProjectOntology', blank=True),
        ),
        migrations.AddField(
            model_name='qmodelrealization',
            name='project',
            field=models.ForeignKey(related_name='models', to='questionnaire.QProject'),
        ),
        migrations.AddField(
            model_name='qmodelrealization',
            name='proxy',
            field=models.ForeignKey(related_name='models', to='questionnaire.QModelProxy'),
        ),
        migrations.AddField(
            model_name='qmodelrealization',
            name='relationship_property',
            field=models.ForeignKey(related_name='relationship_values', blank=True, to='questionnaire.QPropertyRealization', null=True),
        ),
        migrations.AddField(
            model_name='qmodelrealization',
            name='shared_owners',
            field=models.ManyToManyField(related_name='shared_models', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='qmodelrealization',
            name='synchronization',
            field=models.ManyToManyField(to='questionnaire.QSynchronization', blank=True),
        ),
        migrations.AddField(
            model_name='qmodelproxy',
            name='ontology',
            field=models.ForeignKey(related_name='model_proxies', blank=True, to='questionnaire.QOntology', null=True),
        ),
        migrations.AddField(
            model_name='qmodelcustomization',
            name='project',
            field=models.ForeignKey(related_name='model_customizations', to='questionnaire.QProject'),
        ),
        migrations.AddField(
            model_name='qmodelcustomization',
            name='proxy',
            field=models.ForeignKey(related_name='model_customizations', to='questionnaire.QModelProxy'),
        ),
        migrations.AddField(
            model_name='qmodelcustomization',
            name='relationship_source_property_customization',
            field=models.ForeignKey(related_name='relationship_target_model_customizations', blank=True, to='questionnaire.QPropertyCustomization', null=True),
        ),
        migrations.AddField(
            model_name='qmodelcustomization',
            name='shared_owners',
            field=models.ManyToManyField(related_name='shared_customizations', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='qmodelcustomization',
            name='synchronization',
            field=models.ManyToManyField(to='questionnaire.QSynchronization', blank=True),
        ),
        migrations.AddField(
            model_name='qcategoryrealization',
            name='model',
            field=models.ForeignKey(related_name='categories', to='questionnaire.QModelRealization'),
        ),
        migrations.AddField(
            model_name='qcategoryrealization',
            name='proxy',
            field=models.ForeignKey(related_name='categories', to='questionnaire.QCategoryProxy'),
        ),
        migrations.AddField(
            model_name='qcategoryproxy',
            name='model_proxy',
            field=models.ForeignKey(related_name='category_proxies', to='questionnaire.QModelProxy'),
        ),
        migrations.AddField(
            model_name='qcategoryproxy',
            name='ontology',
            field=models.ForeignKey(related_name='category_proxies', blank=True, to='questionnaire.QOntology', null=True),
        ),
        migrations.AddField(
            model_name='qcategorycustomization',
            name='model_customization',
            field=models.ForeignKey(related_name='category_customizations', to='questionnaire.QModelCustomization'),
        ),
        migrations.AddField(
            model_name='qcategorycustomization',
            name='project',
            field=models.ForeignKey(related_name='category_customizations', to='questionnaire.QProject'),
        ),
        migrations.AddField(
            model_name='qcategorycustomization',
            name='proxy',
            field=models.ForeignKey(to='questionnaire.QCategoryProxy'),
        ),
        migrations.AlterUniqueTogether(
            name='qpublication',
            unique_together=set([('name', 'version')]),
        ),
        migrations.AlterUniqueTogether(
            name='qprojectontology',
            unique_together=set([('project', 'ontology')]),
        ),
        migrations.AlterUniqueTogether(
            name='qontology',
            unique_together=set([('name', 'version')]),
        ),
        migrations.AlterUniqueTogether(
            name='qmodelproxy',
            unique_together=set([('ontology', 'name', 'package', 'cim_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='qcategoryproxy',
            unique_together=set([('model_proxy', 'name', 'cim_id')]),
        ),
    ]
