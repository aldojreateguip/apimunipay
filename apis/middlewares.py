from django.http import JsonResponse

class JsonRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST':
            if not self._is_json_request(request):
                return JsonResponse({'error': 'Se ha rechazado la peticion debido a un error en la solicitud'}, status=400)
        return self.get_response(request)

    def _is_json_request(self, request):
        content_type = request.headers.get('Content-Type', '')
        return 'application/json' in content_type

