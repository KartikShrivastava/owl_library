from django.urls import path
from . import views

urlpatterns = [
    path('', views.getAllBooks),
    path('bookdetail/<owl_id>', views.getBookDetails),
    path('borrow/', views.borrowBook),
    path('return/', views.returnBook),
]
