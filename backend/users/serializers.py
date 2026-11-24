"""Users serializers"""
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Organisation, OrganisationMember
from .phone import normalize_phone

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    # Declared explicitly so the uniqueness check runs on the normalised number
    # (the auto-generated UniqueValidator would compare the raw input).
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'phone_number', 'password', 'password_confirm',
            'full_name', 'user_type', 'preferred_language',
            'consented_to_processing',
        ]

    def validate_phone_number(self, value):
        phone = normalize_phone(value)
        if User.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError('An account with this phone number already exists.')
        return phone

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        if not data.get('consented_to_processing'):
            raise serializers.ValidationError(
                {'consented_to_processing': 'You must consent to data processing to use LegalBridge.'}
            )
        return data

    def create(self, validated_data):
        from django.utils import timezone
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        validated_data['consent_date'] = timezone.now()
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'email', 'full_name',
            'user_type', 'preferred_language',
            'is_verified', 'created_at',
        ]
        read_only_fields = ['id', 'phone_number', 'created_at', 'is_verified']


class OrganisationSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Organisation
        fields = [
            'id', 'name', 'org_type', 'registration_number',
            'contact_email', 'contact_phone', 'location', 'district',
            'description', 'is_active', 'is_verified', 'member_count', 'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'is_verified']

    def get_member_count(self, obj):
        return obj.members.filter(is_active=True).count()
