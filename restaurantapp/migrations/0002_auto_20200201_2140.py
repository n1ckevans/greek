# Generated by Django 2.2 on 2020-02-02 05:40

from django.db import migrations, models
import django_s3_storage.storage


class Migration(migrations.Migration):

    dependencies = [
        ('restaurantapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_image',
            field=models.ImageField(blank=True, null=True, storage=django_s3_storage.storage.S3Storage(aws_s3_bucket_name='greek-restaurant'), upload_to=''),
        ),
    ]