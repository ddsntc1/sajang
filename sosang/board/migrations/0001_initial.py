# Generated by Django 5.1.3 on 2024-12-18 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Advertisement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_link', models.URLField(verbose_name='광고 링크')),
                ('main_banner', models.ImageField(help_text='권장 크기: 1200x300px', upload_to='advertisements/main/', verbose_name='메인 배너')),
                ('side_banner', models.ImageField(help_text='권장 크기: 400x300px', upload_to='advertisements/side/', verbose_name='사이드 배너')),
                ('status', models.CharField(choices=[('pending', '승인대기'), ('approved', '승인완료'), ('rejected', '반려'), ('ended', '종료')], default='pending', max_length=10, verbose_name='상태')),
                ('admin_message', models.TextField(blank=True, verbose_name='관리자 메시지')),
                ('start_date', models.DateTimeField(blank=True, null=True, verbose_name='시작일')),
                ('end_date', models.DateTimeField(blank=True, null=True, verbose_name='종료일')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('modify_date', models.DateTimeField(blank=True, null=True)),
                ('create_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True)),
                ('order', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('is_business', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('board', '글게시판'), ('story', '이야기게시판'), ('advertise', '광고게시판')], default='board', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('modify_date', models.DateTimeField(blank=True, null=True)),
                ('create_date', models.DateTimeField()),
                ('is_notice', models.BooleanField(default=False)),
                ('view_count', models.PositiveIntegerField(default=0)),
            ],
        ),
    ]
