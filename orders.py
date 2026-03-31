from shop.models import Order

order = Order.objects.last()  
print(f"Заказ №{order.id}")
print(f"Покупатель: {order.first_name} {order.last_name}")
print(f"Email: {order.email}")
print(f"Телефон: {order.phone}")
print(f"Адрес: {order.address}")
print(f"Сумма: {order.total_price} ₽")
print(f"Статус: {order.status}")
print("\nТовары в заказе:")
for item in order.items.all():
    print(f"  - {item.product.name} x{item.quantity} = {item.price * item.quantity} ₽")