from rest_framework import serializers
from goods.models import SKU

class CartSerializer(serializers.Serializer):
    """购物车序列化"""
    sku_id = serializers.IntegerField(label='sku_id', min_value=1)
    count = serializers.IntegerField(label='数量', min_value=1)
    selected = serializers.BooleanField(label='勾选', default=True)

    def validate_sku_id(self, value):
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('sku_id不存在')
        return value