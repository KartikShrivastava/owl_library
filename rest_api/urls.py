from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_all_books_api),
    path('books/available/', views.get_all_available_books_api),
    path('books/author/<name>', views.get_all_books_by_author_name_api),
    path('accounts/borrow/', views.borrow_book_api),
    path('accounts/return/', views.return_book_api),
    path('accounts/availability/<owl_id>', views.get_book_availability_api),
    path('accounts/mybooks/', views.get_my_books_api),
    path('accounts/register/', views.LibraryUserCreate.as_view()),
]
