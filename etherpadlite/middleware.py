from django.template import loader, RequestContext


class Http403Middleware(object):
    def process_response(self, request, response):
        if response.status_code == 403 and response.tell() == 0:
            t = loader.get_template('403.html')
            c = RequestContext(request, {'request_path': request.path})
            response.write(t.render(c))
        return response
