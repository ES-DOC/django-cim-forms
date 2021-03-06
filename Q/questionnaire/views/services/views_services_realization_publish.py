####################
#   ES-DOC CIM Questionnaire
#   Copyright (c) 2017 ES-DOC. All rights reserved.
#
#   University of Colorado, Boulder
#   http://cires.colorado.edu/
#
#   This project is distributed according to the terms of the MIT license [http://www.opensource.org/licenses/MIT].
####################


from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse

from Q.questionnaire.models.models_realizations import QModelRealization
from Q.questionnaire.views.services.views_services_base import validate_request
from Q.questionnaire.q_utils import QError


def q_realization_publish(request):

    valid_request, msg = validate_request(request)
    if not valid_request:
        return HttpResponseForbidden(msg)

    realization_model_id = request.POST.get("document_id")
    try:
        realization = QModelRealization.objects.get(pk=realization_model_id)
    except QModelRealization.DoesNotExist:
        msg = "unable to locate document with id={0}".format(realization_model_id)
        return HttpResponseBadRequest(msg)

    if not realization.is_active:
        msg = u"This document has been disabled."
        return HttpResponseBadRequest(msg)
    if not realization.is_document and realization.is_root:
        msg = u"This is not a root document."
        return HttpResponseBadRequest(msg)
    if not realization.is_complete:
        msg = u"This model is incomplete."
        return HttpResponseBadRequest(msg)

    try:
        publication = realization.publish(force_save=True)
        msg = "You have successfully published this document.  It should appear in the ES-DOC Archive within 4 hours."
        messages.add_message(request, messages.INFO, msg)
    except Exception as e:
        msg = "Error publishing document."
        messages.add_message(request, messages.ERROR, msg)
        raise QError(e.message)

    return JsonResponse({"msg": msg})
