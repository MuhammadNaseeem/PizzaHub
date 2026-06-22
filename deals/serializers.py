from rest_framework import serializers
from .models import Deal, DealItem


class DealItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = DealItem
        fields = [
            'id',
            'product',
            'product_name',
            'quantity',
            'item_discount'
        ]


class DealSerializer(serializers.ModelSerializer):

    items = DealItemSerializer(many=True, read_only=True)
    status = serializers.CharField(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    remaining_uses = serializers.CharField(read_only=True)

    class Meta:
        model = Deal
        fields = '__all__'

        