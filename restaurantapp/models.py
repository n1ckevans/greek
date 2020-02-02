import re
from collections import Counter
from datetime import datetime, date, timedelta, timezone
from django.conf import settings
from django.db import models
from django.contrib import messages
import timeago
from django.contrib.sites.models import Site
from PIL import Image
from django_s3_storage.storage import S3Storage


import bcrypt

storage = S3Storage(aws_s3_bucket_name='greek-restaurant')


class UserManager(models.Manager):
    # def is_reg_valid(self, request):
    def registration_validator(self, postData):
        errors = {}
        if len(postData['first_name']) < 2:
            errors['first_name'] = "first name: at least 2 characters required"
        if len(postData['last_name']) < 2:
            errors['last_name'] = "last name: at least 2 characters required"
        if not postData['first_name'].isalpha() or not postData['last_name'].isalpha():
            errors['name'] = "invalid name"
        EMAIL_REGEX = re.compile(
            r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(postData['email']):
            errors['email'] = 'invalid email address!'
        for user in User.objects.all():
            if user.email == postData['email']:
                errors['email'] = "something went wrong!"
        if len(postData['password']) < 6:
            errors['password'] = "password must be longer than 5 characters"
        if postData['password'] != postData['password_ver']:
            errors['password'] = "password does not match!"
        return errors

    def register(self, postData):
        user = User(
            first_name=postData['first_name'],
            last_name=postData['last_name'],
            email=postData['email'],
            user_level=1,

            password_hash=bcrypt.hashpw(
                postData['password'].encode(), bcrypt.gensalt())
        )
        user.save()
        return user


class SearchManager(models.Manager):
    def filter_search(self, postData):
        # select all products
        products = Product.objects.all()

        # category filter
        if postData['category'] == 'sale':
            products = Product.objects.filter(
                discount_price__isnull=False)

        elif postData['category'] == 'new':
            today = date.today()
            products = Product.objects.filter(
                updated_at__gte=today)

        elif postData['category'] and postData['category'] != 'all':
            products = Category.objects.filter(
                name=postData['category'])[0].products.all()

        # filter price
        if not postData['min']:
            min = 0
        else:
            min = postData['min']

        if not postData['max']:
            max = 100000
        else:
            max = postData['max']

        products = products.filter(price__gte=min).filter(
            price__lte=max)

        # filter search
        products = products.filter(name__icontains=postData['search'])
        return products


class OrderManager(models.Manager):
    def popular_items(self, limit=5):
        pop_dict = {}
        all_orders = Order.objects.all()
        for order in all_orders:
            for item in order.items.all():
                if item.item.id not in pop_dict:
                    pop_dict[item.item.id] = 1
                else:
                    pop_dict[item.item.id] += 1
        k = Counter(pop_dict)
        high = k.most_common(limit)
        return high


class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    user_level = models.IntegerField(default=0)
    phone = models.CharField(max_length=10, blank=True, default='')
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    # .orders

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # .products lists all the products with that category

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=8)
    discount_price = models.DecimalField(
        decimal_places=2, max_digits=8, blank=True, null=True)
    # size 0: onesize 1:sm 2:md 3:lg 4:xl
    size = models.CharField(max_length=100)
    description = models.TextField()
    categories = models.ManyToManyField(Category, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    product_image = models.ImageField(storage=storage, null=True, blank=True)
    objects = SearchManager()

    def __str__(self):
        return self.name

    def is_new(self):
        now = datetime.now(timezone.utc)
        product_date = self.updated_at
        if now - product_date < timedelta(days=1):
            return True
        return False


class OrderItem(models.Model):
    item = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    # .orders show all orders with that orderitme

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_item_total(self):
        if self.item.discount_price:
            return round(self.quantity * self.item.discount_price, 2)
        else:
            return round(self.quantity * self.item.price, 2)


class Order(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE, related_name="orders", null=True, blank=True)
    items = models.ManyToManyField(
        OrderItem, related_name="orders")
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    promo_valid = models.BooleanField(default=False)
    promo_rate = models.FloatField(null=True, blank=True, default=0)
    objects = OrderManager()
    # .shipping_address

    def order_subtotal(self):
        subtotal = 0
        for item in self.items.all():
            subtotal += round(item.quantity * item.item.price, 2)
        return subtotal

    def total_saving(self):
        saving = 0
        for item in self.items.all():
            if item.item.discount_price:
                saving += (item.item.price -
                           item.item.discount_price)*item.quantity
        return round(saving, 2)

    def get_tax(self):
        return round(float(self.order_subtotal()-self.total_saving()) * 0.08)

    def final_total(self):
        return self.order_subtotal() - self.total_saving() + self.get_tax()

    def applypromo(self, discount_percent):
        return float(self.final_total()) * (1-discount_percent)

    def is_delivered(self):
        now = datetime.now(timezone.utc)
        ordered_date = self.updated_at
        if now - ordered_date > timedelta(days=5):
            return True
        return False


class ShippingAddress(models.Model):
    street = models.CharField(max_length=100)
    street2 = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zipcode = models.IntegerField()
    ordered_by = models.ForeignKey(
        User, related_name='address', null=True, blank=True, on_delete=models.PROTECT)
    order = models.ForeignKey(
        Order, related_name='shipping_address', null=True, blank=True, on_delete=models.PROTECT)


class PromoCode(models.Model):
    code = models.CharField(max_length=100)
    discount = models.FloatField()
    description = models.TextField()
    expiration_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
