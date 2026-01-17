from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Avg, Count, Q, Sum
from .models import Book, Author, Publisher, Language, Rating
from .forms import BookForm
from django.views.generic import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def home(request):
    books = Book.objects.select_related('rating').all()[:5]
    total_books = Book.objects.count()
    avg_rating = Book.objects.aggregate(avg=Avg('rating__average_rating'))['avg'] or 0
    total_pages = Book.objects.aggregate(total=Sum('num_pages'))['total']
    total_reviews = Book.objects.aggregate(total=Sum('rating__text_reviews_count'))['total']
    
    return render(request, 'home.html', {
        'books': books,
        'total_books': total_books,
        'avg_rating': avg_rating,
        'total_pages': total_pages,
        'total_reviews': total_reviews,
    })

class BookListView(ListView):
    model = Book
    template_name = 'book_app/book_list.html'
    context_object_name = 'books'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Book.objects.select_related(
            'rating', 'publisher', 'language'
        ).prefetch_related('authors').order_by('book_id')
        
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(authors__author_name__icontains=search_query)
            ).distinct()
        
        return queryset

class BookCreateView(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'book_app/book_form.html'
    success_url = reverse_lazy('book_list')

class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'book_app/book_form.html'
    
    def get_success_url(self):
        return reverse_lazy('book_list')

class BookDeleteView(DeleteView):
    model = Book
    template_name = 'book_app/book_confirm_delete.html'
    success_url = reverse_lazy('book_list')

class StatisticsView(TemplateView):
    template_name = 'book_app/statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        
        total_stats = {
            'total_books': Book.objects.count(),
            'total_authors': Author.objects.count(),
            'total_publishers': Publisher.objects.count(),
            'total_languages': Language.objects.count(),
        }
        
        
        books_page = self.request.GET.get('books_page', 1)
        authors_page = self.request.GET.get('authors_page', 1)
        publishers_page = self.request.GET.get('publishers_page', 1)
        languages_page = self.request.GET.get('languages_page', 1)
        
        
        books_queryset = Book.objects.select_related(
            'publisher', 'rating', 'language'
        ).prefetch_related('authors').all()
        books_paginator = Paginator(books_queryset, 10)  
        try:
            books = books_paginator.page(books_page)
        except (PageNotAnInteger, EmptyPage):
            books = books_paginator.page(1)
        
        
        authors_queryset = Author.objects.annotate(
            book_count=Count('books'),
            avg_rating=Avg('books__rating__average_rating')
        ).order_by('-book_count', 'author_name')
        authors_paginator = Paginator(authors_queryset, 15)  
        try:
            authors = authors_paginator.page(authors_page)
        except (PageNotAnInteger, EmptyPage):
            authors = authors_paginator.page(1)
        
        
        publishers_queryset = Publisher.objects.annotate(
            book_count=Count('books'),
            avg_rating=Avg('books__rating__average_rating')
        ).order_by('-book_count', 'publisher_name')
        publishers_paginator = Paginator(publishers_queryset, 10)  
        try:
            publishers = publishers_paginator.page(publishers_page)
        except (PageNotAnInteger, EmptyPage):
            publishers = publishers_paginator.page(1)
        
        
        languages_queryset = Language.objects.annotate(
            book_count=Count('books'),
            avg_rating=Avg('books__rating__average_rating')
        ).order_by('-book_count', 'language_name')
        languages_paginator = Paginator(languages_queryset, 10)  
        try:
            languages = languages_paginator.page(languages_page)
        except (PageNotAnInteger, EmptyPage):
            languages = languages_paginator.page(1)
        
        
        overall_stats = Book.objects.aggregate(
            avg_rating=Avg('rating__average_rating'),
            total_pages=Sum('num_pages'),
            avg_pages=Avg('num_pages')
        )
        
        
        overall_stats['avg_rating'] = overall_stats['avg_rating'] or 0
        overall_stats['total_pages'] = overall_stats['total_pages'] or 0
        overall_stats['avg_pages'] = overall_stats['avg_pages'] or 0
        
        context.update({
            'total_stats': total_stats,
            'books': books,
            'authors': authors,
            'publishers': publishers,
            'languages': languages,
            'overall_stats': overall_stats,
            'books_page': books_page,
            'authors_page': authors_page,
            'publishers_page': publishers_page,
            'languages_page': languages_page,
        })
        
        return context