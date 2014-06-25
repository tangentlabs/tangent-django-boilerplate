from django.views import generic
from django import http
from django.conf import settings


class PrivateMediaView(generic.View):
    """
    A proxying view that uses the X-Accel-Redirect header to instruct Nginx to
    server the specified file.

    See:
        http://wiki.nginx.org/XSendfile
        http://zacharyvoase.com/2009/09/08/sendfile/
    """

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return http.HttpResponseForbidden()
        response = http.HttpResponse()
        del response['content-type']  # Let Nginx determine the content type
        # Path should be relative to the internal alias defined in the nginx
        # config.
        response['X-Accel-Redirect'] = (
            settings.PRIVATE_MEDIA_URL + kwargs['path'])
        return response
