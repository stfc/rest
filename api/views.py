# from django.shortcuts import render
# from django.http import HttpResponse
# from django.views.decorators.http import require_http_methods
from dirq.queue import Queue
from rest_framework.views import APIView
from rest_framework.response import Response
import logging
import os


class IndexView(APIView):
    """An example URL."""

    def get(self, request, format=None):
        """An example get method."""
        logger = logging.getLogger(__name__)

        response = "Hello, world. You're at the index."
        logger.info(response)
        return Response(response, status=200)

    def post(self, request, format=None):
        """An example post method."""
        logger = logging.getLogger(__name__)

        try:
            empaid = request.META['HTTP_EMPA_ID']
        except KeyError:
            empaid = 'noid'

        logger.info("Received message. ID = %s", empaid)

        # this will fail is the request isn't coming through apache
        signer = request.META['SSL_CLIENT_S_DN']

        if "_content" in request.POST.dict():
            # then POST likely to come via the rest api framework
            # hence use the content of request.POST as message
            body = request.POST.get('_content')
        else:
            # POST likely to comes through a browser client or curl
            # hence use request.body as message
            body = request.body

        logger.debug("Message body received: %s", body)

        for header in request.META:
            logger.debug("%s: %s", header, request.META[header])

        qpath = '/tmp/flask/'
        # taken from ssm2
        QSCHEMA = {'body': 'string',
                   'signer': 'string',
                   'empaid': 'string?'}

        inqpath = os.path.join(qpath, 'incoming')
        # rejectqpath = os.path.join(qpath, 'reject')
        inq = Queue(inqpath, schema=QSCHEMA)
        # rejectq = Queue(rejectqpath, schema=REJECT_SCHEMA)

        name = inq.add({'body': body,
                        'signer': signer,
                        'empaid': empaid})

        new_body_path = "%s/%s/body" % (inqpath, name)
        new_body_file = open(new_body_path)
        new_body_contents = new_body_file.read()
        new_body_file.close()

        logger.info("Message saved to in queue as %s/%s", inqpath, name)

        response = "Data received is well-formed and stored for processing."

        custom_headers = {}
        # can't have new line characters in header
        custom_headers["FILE_CONTENTS"] = new_body_contents.replace("\n", " ")

        return Response(response, status=202, headers=custom_headers)
