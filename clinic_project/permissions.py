from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication

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



# Superadmin + panel switching
class RoleBasedPanelAccess(BasePermission):
    """
    Superadmin can access all panels.
    Others only their own.
    If Superadmin switches panel, 'acting_as_role' in token decides access.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Extract "acting_as_role" from JWT (if available)
        jwt_auth = JWTAuthentication()
        header = jwt_auth.get_header(request)
        if header:
            raw_token = jwt_auth.get_raw_token(header)
            validated_token = jwt_auth.get_validated_token(raw_token)
            acting_as_role = validated_token.get("acting_as_role", None)
        else:
            acting_as_role = None

        # Determine current role
        current_role = acting_as_role or user.role.lower()

        # Superadmin can access everything
        if current_role == "superadmin":
            return True

        # For other roles, match view.panel_role
        panel_role = getattr(view, "panel_role", None)
        if not panel_role:
            return True  # if no specific panel role set

        return current_role == panel_role.lower()