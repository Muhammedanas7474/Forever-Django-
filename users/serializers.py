from rest_framework import serializers
from django.contrib.auth import get_user_model


User=get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(required=True)
    password=serializers.CharField(write_only=True,required=True)
    password2=serializers.CharField(write_only=True,required=True)


    class Meta:
        model=User
        fields=['username','email','password','password2']
        extra_kwargs={
            'username':{'required':True}
        }

    def validate(self, attrs):
        if attrs['password']!= attrs['password2']:
                raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
         validated_data.pop('password2')
         user=User.objects.create_user(
              username=validated_data['username'],
              email=validated_data['email'],
              password=validated_data['password']
         )

         return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
