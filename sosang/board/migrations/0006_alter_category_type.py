# Generated by Django 5.1.3 on 2024-12-22 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0005_alter_advertisement_main_poster_inquiry_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='type',
            field=models.CharField(choices=[('board', '글게시판'), ('story', '이야기게시판'), ('advertise', '광고게시판'), ('info', '정보게시판')], default='board', max_length=10),
        ),
    ]
