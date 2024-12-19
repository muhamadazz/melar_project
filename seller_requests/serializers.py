# seller_requests/serializers.py

from rest_framework import serializers
from .models import SellerRequest

class SellerRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerRequest
        fields = '__all__'
