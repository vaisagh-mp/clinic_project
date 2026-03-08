from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

def get_acting_user_context(request):
    """
    Returns the user object that a Superadmin is currently acting as.
    """
    from rest_framework_simplejwt.tokens import AccessToken
    
    user = request.user
    if not user.is_authenticated or user.role.upper() != "SUPERADMIN":
        return None

    auth_header = request.headers.get("Authorization", "")
    token = auth_header.split(" ")[1] if " " in auth_header else None
    if token:
        try:
            token_obj = AccessToken(token)
            target_user_id = token_obj.get("target_id") or token_obj.get("acting_as_user_id")
            if target_user_id:
                return User.objects.get(id=target_user_id)
        except Exception:
            pass
    return None

def get_clinic_context(request):
    """
    Centralized helper to determine the clinic context for a request.
    Works for:
    1. Superadmin 'acting as' a clinic (via token payload or query param)
    2. Clinic users (via their profile)
    3. Doctor users (via their clinic profile)
    """
    from admin_panel.models import Clinic
    
    user = request.user
    if not user.is_authenticated:
        return None

    # --- 1. Explicit clinic_id in request ---
    clinic_id = request.query_params.get("clinic_id") or request.data.get("clinic_id") or request.data.get("clinic")
    if clinic_id:
        try:
            return Clinic.objects.get(id=clinic_id)
        except (Clinic.DoesNotExist, ValueError):
            pass

    # --- 2. Token-based 'acting as' logic (for Superadmin) ---
    if user.role.upper() == "SUPERADMIN":
        target_user = get_acting_user_context(request)
        if target_user and hasattr(target_user, "clinic_profile"):
            return target_user.clinic_profile

    # --- 3. Role-based fallback ---
    if user.role.upper() == "CLINIC":
        return getattr(user, "clinic_profile", None)
    
    if user.role.upper() == "DOCTOR":
        return getattr(user.doctor_profile, "clinic", None)

    return None
