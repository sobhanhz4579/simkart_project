# simkart/serializers.py

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import SimCard, Comment, ContactModel, Account

User = get_user_model()


class SimCardSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    class Meta:
        model = SimCard
        fields = ['id', 'title', 'body', 'account', 'number', 'price', 'discount', 'publish', 'sim_type',
                  'status', 'quantity', 'tags', 'created', 'updated', 'active']

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and not request.user.is_staff:
            validated_data.pop('status', None)
            validated_data.pop('active', None)
        return super().update(instance, validated_data)

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("قیمت نمی‌تواند منفی باشد.")
        return value


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['phone_number', 'date_of_birth', 'gender', 'address', 'age', 'last_login']


class UserSerializer(serializers.ModelSerializer):
    account = AccountSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'is_active', 'last_login', 'account']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ['old_password', 'new_password']

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        user = self.instance
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError("پسورد قدیمی صحیح نیست.")
        return attrs


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate(self, data):
        if not data.get('username'):
            raise serializers.ValidationError("نام کاربری الزامی است.")
        if not data.get('password'):
            raise serializers.ValidationError("کلمه عبور الزامی است.")
        if not data.get('email'):
            raise serializers.ValidationError("ایمیل الزامی است.")
        return data


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactModel
        fields = ['username', 'email', 'phone', 'message']

    def validate(self, data):
        if not data.get('username'):
            raise serializers.ValidationError("نام کاربری الزامی است.")
        if not data.get('phone'):
            raise serializers.ValidationError("شماره تلفن الزامی است.")
        if not data.get('email'):
            raise serializers.ValidationError("ایمیل الزامی است.")
        if not data.get('message'):
            raise serializers.ValidationError("وارد کردن پیام الزامی است.")
        return data
