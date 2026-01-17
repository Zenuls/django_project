from django.urls import path
from . import views
from .views import BookListView, BookCreateView, BookUpdateView, BookDeleteView, StatisticsView 

urlpatterns = [
    
    path('', views.home, name='home'),
    
    
    path('books/', BookListView.as_view(), name='book_list'),
    path('books/create/', BookCreateView.as_view(), name='book_create'),
    path('books/<int:pk>/update/', BookUpdateView.as_view(), name='book_update'),
    path('books/<int:pk>/delete/', BookDeleteView.as_view(), name='book_delete'),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
]