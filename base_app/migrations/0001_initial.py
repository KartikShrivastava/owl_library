# Generated by Django 4.1.5 on 2023-01-13 14:08

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('name', models.CharField(help_text='Full name of author', max_length=200, primary_key=True, serialize=False)),
                ('is_popular', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('owl_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base_app.author')),
            ],
            options={
                'unique_together': {('title', 'author')},
            },
        ),
        migrations.CreateModel(
            name='BookCopy',
            fields=[
                ('book_copy_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('book_copy_type', models.CharField(blank=True, choices=[('pb', 'PAPERBACK'), ('hc', 'HARDCOVER'), ('hm', 'HANDMADE'), ('nd', 'NOTDEFINED')], default='nd', help_text='Book copy type', max_length=2)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base_app.book')),
            ],
        ),
        migrations.CreateModel(
            name='LibraryUser',
            fields=[
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=200, verbose_name='user name')),
            ],
        ),
        migrations.CreateModel(
            name='BorrowRecord',
            fields=[
                ('borrow_record_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('borrow_date', models.DateTimeField()),
                ('return_date', models.DateTimeField()),
                ('is_returned', models.BooleanField(default=False)),
                ('book_copy', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base_app.bookcopy')),
                ('library_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base_app.libraryuser')),
            ],
            options={
                'unique_together': {('book_copy', 'library_user')},
            },
        ),
    ]
