from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.method == 'GET' or (request.user and request.user.is_staff))



class SendPrivateEmailToCustomerPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.has_perm('store.send_private_email')