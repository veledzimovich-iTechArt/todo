from django.utils.deprecation import MiddlewareMixin
from cards.utils import NotifyUtil
from rest_framework.renderers import JSONRenderer


class NotificationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # For traditional Django templates
        if request.user.is_authenticated:
            notifications = NotifyUtil.get_user_notifications(request.user.id)
            # Store in request for process_response
            request._notifications = notifications
            for notification in request._notifications:
                from django.contrib import messages
                messages.add_message(
                    request,
                    notification['level'],
                    notification['message']
                )

    def process_response(self, request, response):
        # For API responses
        if hasattr(response, 'data'):
            if response.data is None:
                return response

            final_data = {
                "results": response.data,
            }
            if request.user.is_authenticated and hasattr(request, '_notifications'):
                final_data["notifications"] = request._notifications


            # Re-render the response with new data
            response.data = final_data
            response.content = JSONRenderer().render(final_data)
        return response
