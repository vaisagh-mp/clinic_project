from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=[], required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
            "role",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically set role choices
        ROLE_CHOICES = [
            ("SUPERADMIN", "Superadmin"),
            ("ADMIN", "Admin"),
            ("CLINIC", "Clinic"),
            # ("DOCTOR", "Doctor"),  # Removed doctor
        ]

        # Check if a superadmin already exists
        if User.objects.filter(role="SUPERADMIN").exists():
            # remove SUPERADMIN and ADMIN from choices
            ROLE_CHOICES = [r for r in ROLE_CHOICES if r[0] not in ["SUPERADMIN", "ADMIN"]]

        self.fields["role"].choices = ROLE_CHOICES

    def validate_email(self, value):
        """Ensure the email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")
    
        user = User(**validated_data)
        user.set_password(password)
    
        # Automatically promote Superadmin/Admin
        if user.role in ["SUPERADMIN", "ADMIN"]:
            user.is_superuser = True
            user.is_staff = True
        else:
            user.is_superuser = False
            user.is_staff = False
    
        user.save()
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role"]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        data["user"] = user
        return data
