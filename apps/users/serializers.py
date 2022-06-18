from django.db import IntegrityError
from rest_framework import serializers
from apps.users.models import User


class RegisterUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['mobile']


    def validate(self, data):
        mobile = data['mobile']

        if len(mobile) is not 10:
            raise serializers.ValidationError("Please enter valid number")
        return super().validate(data)

    def create(self, validated_data):
        mobile = validated_data['mobile']
        try:
            instance = super().create(validated_data)
        except IntegrityError as e:
            raise serializers.ValidationError("User with this number already exists.")
        except Exception as e:
            raise serializers.ValidationError("Something Went Wrong!")

        return instance


class VerifyOTPRequestSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    otp = serializers.CharField(required=False, max_length=6, min_length=6)


class PanSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    pan = serializers.CharField(required=True, max_length=10, min_length=10)