# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-22 21:18
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='\u7528\u6237\u540d')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='\u6ce8\u518c\u90ae\u7bb1')),
                ('moblie', models.CharField(max_length=12, unique=True, verbose_name='\u624b\u673a\u53f7')),
                ('serial', models.CharField(db_index=True, default='01001', max_length=32, null=True, verbose_name='\u5e8f\u5217\u53f7')),
                ('serial_changed', models.IntegerField(default=0, verbose_name='\u5e8f\u5217\u53f7\u6539\u53d8\u6b21\u6570')),
                ('uid', models.CharField(max_length=32, unique=True, verbose_name='\u4f18\u5b9c\u5de7\u8d2d\u7528\u6237ID')),
                ('reg_time', models.DateTimeField(verbose_name='\u4f18\u5b9c\u5de7\u8d2d\u6ce8\u518c\u65f6\u95f4')),
            ],
            options={
                'verbose_name': '\u7528\u6237',
                'verbose_name_plural': '\u7528\u6237',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('order_number', models.IntegerField(unique=True, verbose_name='\u4f18\u5b9c\u5de7\u8d2d\u8ba2\u5355\u53f7')),
                ('buyer_id', models.CharField(max_length=32, verbose_name='\u4e70\u5bb6ID')),
                ('buyer_name', models.CharField(max_length=32, verbose_name='\u4e70\u5bb6\u540d')),
                ('total', models.FloatField(verbose_name='\u8ba2\u5355\u91d1\u989d')),
                ('order_time', models.DateTimeField(verbose_name='\u4e0b\u5355\u65f6\u95f4')),
                ('finished_time', models.DateTimeField(verbose_name='\u5b8c\u6210\u65f6\u95f4')),
            ],
            options={
                'verbose_name': '\u8ba2\u5355',
                'verbose_name_plural': '\u8ba2\u5355',
            },
        ),
        migrations.CreateModel(
            name='Serial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('serial', models.CharField(db_index=True, max_length=32, unique=True, verbose_name='\u5e8f\u5217\u4f1a\u5458\u53f7')),
                ('is_supper', models.BooleanField(default=False, verbose_name='\u8d85\u7ea7\u4f1a\u5458')),
                ('level', models.PositiveSmallIntegerField(verbose_name='\u4f1a\u5458\u5c42\u7ea7')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='\u4f1a\u5458\u59d3\u540d')),
                ('moblie', models.CharField(max_length=12, unique=True, verbose_name='\u624b\u673a\u53f7')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u5e8f\u5217\u4f1a\u5458',
                'verbose_name_plural': '\u5e8f\u5217\u4f1a\u5458',
            },
        ),
    ]
