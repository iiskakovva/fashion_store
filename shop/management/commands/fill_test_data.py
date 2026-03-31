from django.core.management.base import BaseCommand
from shop.models import Category, Product, Size, User, Cart, CartItem, Order, OrderItem, Review
from django.utils.text import slugify
from django.core.files import File
from django.conf import settings
import random
import os

class Command(BaseCommand):
    help = 'Fill database with test categories and products'

    def create_placeholder_image(self, product_name, slug):
        """Создает изображение-заглушку для товара"""
        # Создаем папку если не существует
        img_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        os.makedirs(img_dir, exist_ok=True)
        
        # Путь к файлу
        img_path = os.path.join(img_dir, f'{slug}.jpg')
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Создаем изображение
            img = Image.new('RGB', (400, 400), color=(73, 109, 137))
            draw = ImageDraw.Draw(img)
            
            # Текст на изображении
            text = product_name[:15]
            
            # Пытаемся использовать шрифт, если нет - стандартный
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Получаем размер текста
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Позиция по центру
            position = ((400 - text_width) // 2, (400 - text_height) // 2)
            
            # Рисуем белый прямоугольник под текстом
            draw.rectangle(
                [position[0] - 10, position[1] - 5, 
                 position[0] + text_width + 10, position[1] + text_height + 5],
                fill=(255, 255, 255)
            )
            
            # Рисуем текст черным
            draw.text(position, text, fill=(0, 0, 0), font=font)
            
            # Добавляем рамку
            draw.rectangle([0, 0, 399, 399], outline=(255, 255, 255), width=3)
            
            # Сохраняем
            img.save(img_path)
            
        except ImportError:
            # Если PIL не установлен, создаем пустой файл
            with open(img_path, 'wb') as f:
                f.write(b'')
        
        return img_path

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Начинаем заполнение базы данных...'))
        
        # Очищаем существующие данные в правильном порядке
        self.stdout.write('Очищаем существующие данные...')
        Size.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Review.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        # Не удаляем пользователей, чтобы сохранить админа если он есть
        
        self.stdout.write(self.style.SUCCESS('✅ База данных очищена'))

        # Создание категорий
        categories_data = [
            {'name': 'Футболки', 'description': 'Стильные футболки на любой вкус'},
            {'name': 'Джинсы', 'description': 'Качественные джинсы от лучших брендов'},
            {'name': 'Платья', 'description': 'Элегантные платья для особых случаев'},
            {'name': 'Куртки', 'description': 'Модные куртки на все сезоны'},
            {'name': 'Обувь', 'description': 'Удобная и стильная обувь'},
            {'name': 'Свитера', 'description': 'Теплые и уютные свитера'},
            {'name': 'Рубашки', 'description': 'Классические и повседневные рубашки'},
            {'name': 'Юбки', 'description': 'Разнообразные юбки для любого образа'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            # Создаем уникальный slug
            base_slug = slugify(cat_data['name'])
            slug = base_slug
            counter = 1
            # Проверяем уникальность (хотя таблица пустая, но для надежности)
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            category = Category.objects.create(
                name=cat_data['name'],
                slug=slug,
                description=cat_data['description']
            )
            categories[cat_data['name']] = category
            self.stdout.write(f'  ✓ Создана категория: {category.name}')
        
        self.stdout.write(self.style.SUCCESS(f'✅ Создано {len(categories)} категорий'))

        # Создание товаров
        products_data = [
            # Футболки
            {'name': 'Классическая белая футболка', 'category': 'Футболки', 'price': 1990, 'style': 'casual', 'description': 'Базовая белая футболка из 100% хлопка. Подходит для повседневной носки.'},
            {'name': 'Черная футболка с принтом', 'category': 'Футболки', 'price': 2490, 'style': 'casual', 'description': 'Черная футболка с оригинальным принтом. Состав: хлопок 95%, эластан 5%.'},
            {'name': 'Футболка оверсайз серая', 'category': 'Футболки', 'price': 2790, 'style': 'casual', 'description': 'Модная футболка свободного кроя. Подходит для создания стильных образов.'},
            
            # Джинсы
            {'name': 'Черные джинсы скинни', 'category': 'Джинсы', 'price': 3990, 'style': 'casual', 'description': 'Узкие черные джинсы с эффектом потертости. Материал: хлопок, эластан.'},
            {'name': 'Синие джинсы прямого кроя', 'category': 'Джинсы', 'price': 4590, 'style': 'casual', 'description': 'Классические синие джинсы прямого кроя. Универсальная модель.'},
            {'name': 'Рваные джинсы с потертостями', 'category': 'Джинсы', 'price': 5290, 'style': 'casual', 'description': 'Модные рваные джинсы с эффектом потертости. Для смелых образов.'},
            
            # Платья
            {'name': 'Вечернее платье в пол', 'category': 'Платья', 'price': 8990, 'style': 'formal', 'description': 'Элегантное вечернее платье длиной в пол. Идеально для торжественных мероприятий.'},
            {'name': 'Маленькое черное платье', 'category': 'Платья', 'price': 5490, 'style': 'formal', 'description': 'Классическое маленькое черное платье. Подходит для любых случаев.'},
            {'name': 'Платье-рубашка в клетку', 'category': 'Платья', 'price': 4290, 'style': 'casual', 'description': 'Стильное платье-рубашка в клетку. Универсальный вариант для повседневной носки.'},
            
            # Куртки
            {'name': 'Кожаная куртка', 'category': 'Куртки', 'price': 12990, 'style': 'vintage', 'description': 'Стильная кожаная куртка прямого кроя. Подкладка из полиэстера.'},
            {'name': 'Джинсовая куртка', 'category': 'Куртки', 'price': 5990, 'style': 'casual', 'description': 'Классическая джинсовая куртка. Подходит для создания повседневных образов.'},
            {'name': 'Пуховик зимний', 'category': 'Куртки', 'price': 8990, 'style': 'sport', 'description': 'Теплый зимний пуховик. Защищает от холода и ветра.'},
            
            # Обувь
            {'name': 'Кроссовки для бега', 'category': 'Обувь', 'price': 5990, 'style': 'sport', 'description': 'Легкие кроссовки с амортизацией. Подходят для бега и фитнеса.'},
            {'name': 'Кожаные ботинки', 'category': 'Обувь', 'price': 7990, 'style': 'formal', 'description': 'Классические кожаные ботинки. Подходят для офиса и повседневной носки.'},
            {'name': 'Кеды белые', 'category': 'Обувь', 'price': 3490, 'style': 'casual', 'description': 'Универсальные белые кеды. Подходят к любой одежде.'},
            
            # Свитера
            {'name': 'Вязаный свитер оверсайз', 'category': 'Свитера', 'price': 3990, 'style': 'casual', 'description': 'Теплый вязаный свитер свободного кроя. Состав: шерсть, акрил.'},
            {'name': 'Свитер с высоким воротом', 'category': 'Свитера', 'price': 4290, 'style': 'casual', 'description': 'Уютный свитер с высоким воротником. Защищает от холода.'},
            {'name': 'Кардиган длинный', 'category': 'Свитера', 'price': 4890, 'style': 'bohemian', 'description': 'Длинный кардиган в богемном стиле. Создает расслабленный образ.'},
            
            # Рубашки
            {'name': 'Белая классическая рубашка', 'category': 'Рубашки', 'price': 3290, 'style': 'formal', 'description': 'Классическая белая рубашка. Подходит для офиса и особых случаев.'},
            {'name': 'Рубашка в клетку', 'category': 'Рубашки', 'price': 2890, 'style': 'casual', 'description': 'Рубашка в клетку. Универсальный вариант для повседневной носки.'},
            {'name': 'Рубашка джинсовая', 'category': 'Рубашки', 'price': 3590, 'style': 'casual', 'description': 'Джинсовая рубашка. Подходит для создания кэжуал образов.'},
            
            # Юбки
            {'name': 'Юбка-карандаш черная', 'category': 'Юбки', 'price': 2990, 'style': 'formal', 'description': 'Элегантная юбка-карандаш. Подходит для офиса.'},
            {'name': 'Юбка-солнце в цветочек', 'category': 'Юбки', 'price': 3490, 'style': 'bohemian', 'description': 'Романтичная юбка-солнце с цветочным принтом.'},
            {'name': 'Джинсовая юбка мини', 'category': 'Юбки', 'price': 2590, 'style': 'casual', 'description': 'Стильная джинсовая юбка мини. Для молодых и активных.'},
        ]
        
        products_created = 0
        
        for prod_data in products_data:
            category = categories.get(prod_data['category'])
            if not category:
                self.stdout.write(self.style.ERROR(f'  ✗ Категория не найдена: {prod_data["category"]}'))
                continue
            
            # Создаем уникальный slug для товара
            base_slug = slugify(prod_data['name'])
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            # Создаем товар
            product = Product.objects.create(
                name=prod_data['name'],
                slug=slug,
                category=category,
                description=prod_data['description'],
                price=prod_data['price'],
                style=prod_data['style'],
                stock=random.randint(10, 50),
                available=True,
            )
            
            # Создаем изображение-заглушку
            try:
                img_path = self.create_placeholder_image(prod_data['name'], slug)
                if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
                    with open(img_path, 'rb') as f:
                        product.image.save(f'{slug}.jpg', File(f), save=True)
                    self.stdout.write(f'  ✓ Создано изображение для: {product.name}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠ Не удалось создать изображение для {product.name}: {e}'))
            
            # Создание размеров для товара
            sizes_data = [
                {'size': 'xs', 'quantity': random.randint(3, 10)},
                {'size': 's', 'quantity': random.randint(5, 15)},
                {'size': 'm', 'quantity': random.randint(8, 20)},
                {'size': 'l', 'quantity': random.randint(5, 15)},
                {'size': 'xl', 'quantity': random.randint(3, 10)},
            ]
            
            for size_data in sizes_data:
                Size.objects.create(
                    product=product,
                    size=size_data['size'],
                    quantity=size_data['quantity']
                )
            
            products_created += 1
            if products_created % 10 == 0:
                self.stdout.write(f'  ... создано {products_created} товаров')
        
        self.stdout.write(self.style.SUCCESS(f'✅ Создано товаров: {products_created}'))
        
        # Создание тестового пользователя (только если нет)
        if not User.objects.filter(username='testuser').exists():
            User.objects.create_user(
                username='testuser',
                email='test@test.com',
                password='testpass123',
                first_name='Тестовый',
                last_name='Пользователь'
            )
            self.stdout.write('  ✓ Создан тестовый пользователь: testuser / testpass123')
        
        # Создание админа (только если нет)
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Администратор',
                last_name='Системы'
            )
            self.stdout.write('  ✓ Создан администратор: admin / admin123')
        
        # Подсчет итогов
        total_categories = Category.objects.count()
        total_products = Product.objects.count()
        total_sizes = Size.objects.count()
        
        self.stdout.write(self.style.SUCCESS('\n📊 Итоговая статистика:'))
        self.stdout.write(f'   Категорий: {total_categories}')
        self.stdout.write(f'   Товаров: {total_products}')
        self.stdout.write(f'   Размеров: {total_sizes}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Заполнение базы данных завершено!'))