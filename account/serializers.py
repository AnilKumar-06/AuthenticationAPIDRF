from rest_framework import serializers
from account.models import User
from xml.dom import ValidationErr
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from account.utils import Util

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'password2', 'tc']
        extra_kwargs={
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password !=  password2:
            raise serializers.ValidationError("Password does not match!")
        return attrs
    
    
    def create(self, validiate_data):
        return User.objects.create_user(**validiate_data)
    
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields = ['email', 'password']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']


class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=100, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("Password does not match.")
        user.set_password(password)
        user.save()

        return attrs


class SendPassworResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print("Encoded UID: " ,uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print('Password reset token', token)
            link = 'http://localhost:3000/api/user/reset/'+uid+'/'+token
            body = 'Click on the following link to reset your password'+link
            data = {
                "subject": "Reset your password",
                'body': body,
                'to_email': user.email
            }
            Util.send_email(data)

            print('password reset link: ', link)
            return attrs

        else:
            raise ValidationErr("You are not registered user")
        
class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, style={
'input_style': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=100, style={
        'input_type': 'password'}, write_only=True)
    
    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        try: 
            password = attrs.get('password')
            password2 = attrs.get('password')
            uid = self.context.get('uid')
            token = self.context.get('token')

            if password != password2:
                raise serializers.ValidationError("Password does not match")
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise ValidationErr("token is not valid or Expired")
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise ValidationErr('Token is not valid or expired')



        