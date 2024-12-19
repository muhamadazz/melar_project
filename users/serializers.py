from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import check_password

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=False)
    is_seller = serializers.BooleanField(required=False, default=False)  # Tambahkan is_seller

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'full_name', 'role', 'is_seller')
        extra_kwargs = {
            'password': {'write_only': True},
            'full_name': {'required': True},
        }

    def validate_password(self, value):
        """Validasi password untuk memastikan keamanan."""
        validate_password(value)
        return value

    def validate_role(self, value):
        """Validasi role agar hanya superuser yang dapat mengatur sebagai 'admin'."""
        if value == 'admin' and not self.context['request'].user.is_superuser:
            raise serializers.ValidationError("Hanya superuser yang dapat mengatur role sebagai 'admin'.")
        return value

    def create(self, validated_data):
        """Buat pengguna baru menggunakan metode `create_user`."""
        password = validated_data.pop('password')  # Ambil password dan hapus dari validated_data
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        """Perbarui data pengguna, termasuk penanganan perubahan password dengan aman."""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_new_password = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        """Validasi password lama."""
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise serializers.ValidationError("Password lama tidak sesuai.")
        return value

    def validate(self, attrs):
        """Validasi password baru dan konfirmasi password."""
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')
        old_password = attrs.get('old_password')

        if new_password != confirm_new_password:
            raise serializers.ValidationError("Password baru dan konfirmasi password tidak cocok.")
        
        if new_password == old_password:
            raise serializers.ValidationError("Password baru tidak boleh sama dengan password lama.")
        
        # Validasi standar Django untuk kekuatan password
        password_validation.validate_password(new_password, self.context['request'].user)

        return attrs

    def save(self, **kwargs):
        """Menyimpan password baru ke database."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

  
