
####################
#   CIM_Questionnaire
#   Copyright (c) 2013 CoG. All rights reserved.
#
#   Developed by: Earth System CoG
#   University of Colorado, Boulder
#   http://cires.colorado.edu/
#
#   This project is distributed according to the terms of the MIT license [http://www.opensource.org/licenses/MIT].
####################

__author__="allyn.treshansky"
__date__ ="Sep 30, 2013 3:04:42 PM"

"""
.. module:: views

Summary of module goes here

"""


from django import forms
from django.forms import *

from questionnaire.views  import *
from questionnaire.models import *
from questionnaire.utils  import get_version

def questionnaire_index(request):

    active_projects = MetadataProject.objects.filter(active=True)

    class _IndexForm(forms.Form):
        class Meta:
            fields  = ("projects",)

        projects        = ModelChoiceField(queryset=active_projects,label="Active Metadata Projects",required=True)
        projects.help_text = "This is a list of all projects that have registered as 'active' with the CIM Questionnaire."

        def __init__(self,*args,**kwargs):
            super(_IndexForm,self).__init__(*args,**kwargs)

    if request.method == "POST":
        form = _IndexForm(request.POST)
        if form.is_valid():
            project             = form.cleaned_data["projects"]
            project_index_url   = reverse("project_index",kwargs={
                "project_name"      : project.name,
            })
            return HttpResponseRedirect(project_index_url)

    else: # request.method == "GET":
        form = _IndexForm()
      
    # gather all the extra information required by the template
    dict = {
        "site"                  : get_current_site(request),
        "form"                  : form,
        "questionnaire_version" : get_version(),
    }

    return render_to_response('questionnaire/questionnaire_index.html', dict, context_instance=RequestContext(request))

#
#    allVersions         = MetadataVersion.objects.all()
#    allCategorizations  = MetadataCategorization.objects.all()
#    allVocabularies     = MetadataVocabulary.objects.all()
#    allProjects         = MetadataProject.objects.all()
#    allCustomizations   = MetadataModelCustomizer.objects.all()
#
#    allModels   = set([model.getName() for model in get_subclasses(MetadataModel) if model._is_metadata_document])
#
#    class _IndexForm(forms.Form):
#        class Meta:
#            fields  = ("versions","categorizations","vocabularies","projects","customizations","models","action")
#
#        versions        = ModelChoiceField(queryset=allVersions,label="Metadata Version",required=False)
#        categorizations = ModelChoiceField(queryset=allCategorizations,label="Associated Categorization",required=False)
#        vocabularies    = ModelMultipleChoiceField(queryset=allVocabularies,label="Associated Vocabularies",required=False)
#        projects        = ModelChoiceField(queryset=allProjects,label="Metadata Project",required=True)
#        customizations  = ModelChoiceField(queryset=allCustomizations,label="Form Customization",required=False)
#
#        models          = ChoiceField(label="Metadata Model",required=False)
#        models.choices  = [(model_name.lower(),model_name) for model_name in allModels]
#        action          = CharField(max_length=LIL_STRING)
#
#        def __init__(self,*args,**kwargs):
#            super(_IndexForm,self).__init__(*args,**kwargs)
#
#            update_field_widget_attributes(self.fields["versions"],{"onchange":"reset_options(this);"})
#            update_field_widget_attributes(self.fields["categorizations"],{"onchange":"reset_options(this);"})
#            update_field_widget_attributes(self.fields["projects"],{"onchange":"reset_options(this);"})
#            update_field_widget_attributes(self.fields["vocabularies"],{"onchange":"reset_options(this);"})
#            update_field_widget_attributes(self.fields["customizations"],{"onchange":"reset_options(this);"})
#            update_field_widget_attributes(self.fields["models"],{"onchange":"reset_options(this);"})
#
#    data = "{ \"versions\" : %s, \"categorizations\" : %s, \"vocabularies\" : %s, \"projects\" : %s, \"customizations\" : %s }" % ( \
#        JSON_SERIALIZER.serialize(allVersions),
#        JSON_SERIALIZER.serialize(allCategorizations),
#        JSON_SERIALIZER.serialize(allVocabularies),
#        JSON_SERIALIZER.serialize(allProjects),
#        JSON_SERIALIZER.serialize(allCustomizations)
#    )
#
#    if request.method == "POST":
#        form = _IndexForm(request.POST)
#        if form.is_valid():
#            action          = form.cleaned_data["action"]
#            version         = form.cleaned_data["versions"]
#            categorization  = form.cleaned_data["categorizations"]
#            vocabulary      = form.cleaned_data["vocabularies"]
#            project         = form.cleaned_data["projects"]
#            customization   = form.cleaned_data["customizations"]
#            model           = form.cleaned_data["models"]
#            parameters      = ""
#
#            if not action in ["customize","edit","test"]:
#                msg = "unknown action: %s" % action
#                return error(request,msg)
#
#            if version:
#                version_number = version.version
#            if customization and action == "customize":
#                parameters = "?name=%s" % customization.name
#
#            url = "%s/%s/%s/%s/%s" % (action,project.name,model,version_number,parameters)
#            return HttpResponseRedirect(url)
#
#    else:
#        form = _IndexForm()
#
#    return render_to_response('dcf/dcf_index.html', {"form":form,"data":data}, context_instance=RequestContext(request))

def questionnaire_project_index(request,project_name=""):

    if not project_name:
        return HttpResponseRedirect(reverse("index"))

    try:
        project = MetadataProject.objects.get(name__iexact=project_name,active=True)
    except MetadataProject.DoesNotExist:
        msg = "Could not find an active project named '%s'." % (project_name)
        return error(request,msg)

    customizers = MetadataModelCustomizer.objects.filter(project=project)

   # I AM HERE
    
    class _AdminIndexForm(forms.Form):
        class Meta:
            pass

        versions        = ModelChoiceField(queryset=MetadataVersion.objects.filter(registered=True),label="Metadata Version",required=True)
        models          = ModelChoiceField(queryset=MetadataModelProxy.objects.all(),label="Metadata Model",required=True)
        customizations  = ModelChoiceField(queryset=MetadataModelCustomizer.objects.filter(project=project),label="Form Customization",required=False)
        customizations.help_text = "If this field is left blank, a <i>new</i> customization will be created."

    class _UserIndexForm(forms.Form):
        class Meta:
            pass

        versions        = ModelChoiceField(queryset=MetadataVersion.objects.filter(registered=True),label="Metadata Version",required=True)
        models          = ModelChoiceField(queryset=MetadataModelProxy.objects.all(),label="Metadata Model",required=True)

    class _DefaultIndexForm(forms.Form):
        class Meta:
            pass

        versions        = ModelChoiceField(queryset=MetadataVersion.objects.filter(registered=True),label="Metadata Version",required=True)
        models          = ModelChoiceField(queryset=MetadataModelProxy.objects.all(),label="Metadata Model",required=True)

    if request.method == "POST":
        admin_form   = _AdminIndexForm(request.POST,prefix="admin")
        user_form    = _UserIndexForm(request.POST,prefix="user")
        default_form = _DefaultIndexForm(request.POST,prefix="default")
        if "admin_customize" in request.POST:
            remove_form_errors(user_form)
            remove_form_errors(default_form)
            if admin_form.is_valid():
                version = admin_form.cleaned_data["versions"]
                model = admin_form.cleaned_data["models"]
                customization = admin_form.cleaned_data["customizations"]
                if customization:
                    url = "/%s/customize/%s/%s?name=%s" % (project_name,version.name,model.name,customization.name)
                else:
                    url = "/%s/customize/%s/%s" % (project_name,version.name,model.name)
                return redirect(url)
            
        elif "user_edit" in request.POST:
            remove_form_errors(admin_form)
            remove_form_errors(default_form)
            if user_form.is_valid():
                print "user_edit"
        elif "user_create" in request.POST:
            remove_form_errors(admin_form)
            remove_form_errors(default_form)
            if user_form.is_valid():
                print "user_create"
        elif "default_view" in request.POST:
            remove_form_errors(admin_form)
            remove_form_errors(user_form)
            if default_form.is_valid():
                print "default_view"
        else:
            msg = "unknown action recieved."
            messages.add_message(request, messages.ERROR, msg)
        

    else: # request.method == "GET":
        admin_form   = _AdminIndexForm(prefix="admin")
        user_form    = _UserIndexForm(prefix="user")
        default_form = _DefaultIndexForm(prefix="default")

        pass

    # gather all the extra information required by the template
    dict = {
        "site"          : get_current_site(request),
        "project"       : project,
        "admin_form"    : admin_form,
        "user_form"     : user_form,
        "default_form"  : default_form,
        "questionnaire_version" : get_version(),
    }


    return render_to_response('questionnaire/questionnaire_project_index.html', dict, context_instance=RequestContext(request))