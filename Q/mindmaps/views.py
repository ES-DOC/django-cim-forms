####################
#   ES-DOC CIM Questionnaire
#   Copyright (c) 2016 ES-DOC. All rights reserved.
#
#   University of Colorado, Boulder
#   http://cires.colorado.edu/
#
#   This project is distributed according to the terms of the MIT license [http://www.opensource.org/licenses/MIT].
####################

__author__ = "allyn.treshansky"

from django.template import RequestContext
from django.conf import settings
from django.shortcuts import render_to_response, loader
from django.http import *

from urlparse import urlparse
import os
import urllib2
import hashlib

from Q.questionnaire import get_version as get_questionnaire_version
from Q.mindmaps import get_version as get_mindmaps_version

from .models import MindMapSource
from .constants import *

hash_block_size = 65536

def mindmaps_index(request):

    # gather all the extra information required by the template
    _dict = {
        "questionnaire_version": get_questionnaire_version(),
        "mindmaps_version": get_mindmaps_version(),
    }

    return render_to_response('mindmaps/mindmaps_index.html', _dict, context_instance=RequestContext(request))


def mindmaps_error(request, **kwargs):

    error_msg = kwargs.pop("msg", "")
    status_code = kwargs.pop("status", 400)

    # (note that error_msg can have embedded HTML tags)

    # gather all the extra information required by the template
    _dict = {
        "questionnaire_version": get_questionnaire_version(),
        "mindmaps_version": get_mindmaps_version(),
        "error_msg": error_msg,
        "status_code": status_code,
    }
    template = loader.get_template('mindmaps/mindmaps_error.html')
    context = RequestContext(request, _dict)
    response = HttpResponse(template.render(context), status=status_code)

    return response


def mindmaps_project(request, project_name=None):

    project_name = project_name.lower()
    if project_name not in MINDMAP_PROJECTS:
        error_msg = "invalid project name: %s" % project_name
        return mindmaps_error(request, msg=error_msg)

    _dict = {
        "questionnaire_version": get_questionnaire_version(),
        "mindmaps_version": get_mindmaps_version(),
        "project_name": project_name,
        "project_mindmaps": MINDMAP_PROJECTS[project_name],
    }

    return render_to_response('mindmaps/mindmaps_project.html', _dict, context_instance=RequestContext(request))


def mindmaps_view(request, **kwargs):

    # get the url...
    if request.method == "GET":
        url = request.GET.get("url")
    else: # request.method == "POST"
        url = request.POST.get("url")

    # see if it is valid...
    valid_domains = []
    enabled_sources = MindMapSource.objects.filter(enabled=True).prefetch_related("domains")
    for enabled_source in enabled_sources:
        valid_domains += [domain.domain for domain in enabled_source.domains.all()]
    url_is_valid = url is not None and any([url.startswith(domain) for domain in valid_domains])
    if not url_is_valid:
        error_msg = "invalid url: %s" % url
        return mindmaps_error(request, msg=error_msg)

    # try to get the remote content...
    try:
        response = urllib2.urlopen(url)
        content = response.read()
    except urllib2.URLError:
        error_msg = "unable to reach url: %s" % url
        return mindmaps_error(request, msg=error_msg)

    # work out where to find/put the local content...
    parsed_url = urlparse(url)
    absolute_path = os.path.join(settings.MEDIA_ROOT, "mindmaps", parsed_url.path[1:])
    relative_path = u"%s%s%s" % (settings.MEDIA_URL, "mindmaps", parsed_url.path)

    # create the local path if it doesn't already exist...
    if not os.path.exists(os.path.dirname(absolute_path)):
        os.makedirs(os.path.dirname(absolute_path))

    # if the file (not just the path) exists...
    if os.path.exists(absolute_path):
        # then check if the content has changed...
        remote_hash = hashlib.sha1()
        remote_hash.update(content)
        local_hash = hashlib.sha1()
        with open(absolute_path, 'rb') as file:
            buff = file.read(hash_block_size)
            while len(buff) > 0:
                local_hash.update(buff)
                buff = file.read(hash_block_size)
        if remote_hash.hexdigest() != local_hash.hexdigest():
            # and overwrite the local file if it has...
            with open(absolute_path, 'w') as file:
                file.write(content)

    # if the file doesn't exist...
    else:
        # then create it...
        with open(absolute_path, 'w') as file:
            file.write(content)

    _dict = {
        "questionnaire_version": get_questionnaire_version(),
        "mindmaps_version": get_mindmaps_version(),
        "mindmap_url": url,
        "mindmap_relative_path": relative_path,
        "mindmap_absolute_path": absolute_path,
    }

    return render_to_response('mindmaps/mindmaps_view.html', _dict, context_instance=RequestContext(request))
