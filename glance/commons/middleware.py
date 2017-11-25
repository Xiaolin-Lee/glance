# -*- coding: utf-8 -*-
import logging
from django.http import JsonResponse

from .exceptions import APIError

logger = logging.getLogger(__name__)


class ExceptionHandlerMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):

        if isinstance(exception, APIError):
            logger.exception(exception.detail)
            return JsonResponse({'code': exception.code,
                                 'msg': exception.message,
                                 'detail': exception.detail})
        else:
            logger.exception(exception.message)
            error = APIError(APIError.UNKNOWN_ERROR)
            return JsonResponse({'code': error.code,
                                 'msg': error.message,
                                 'detail': exception.message})
