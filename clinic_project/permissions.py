from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "ADMIN")

class IsClinic(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "CLINIC")

class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "DOCTOR")

# Example object-level: ensure resource belongs to user's clinic
class IsClinicOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # works for objects with `clinic` field
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == "ADMIN":
            return True
        if request.user.role == "CLINIC":
            # assume clinic_profile exists (OneToOne)
            return getattr(request.user, "clinic_profile", None) == getattr(obj, "clinic", None)
        return False
