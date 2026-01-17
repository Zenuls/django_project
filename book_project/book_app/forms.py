from django import forms
from .models import Book, Author, Publisher, Language, Rating

class BookForm(forms.ModelForm):
    
    average_rating = forms.DecimalField(
        max_digits=3,
        decimal_places=2,
        min_value=0,
        max_value=5,
        initial=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'max': '5'
        }),
        label="Средний рейтинг"
    )
    
    ratings_count = forms.IntegerField(
        min_value=0,
        initial=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0'
        }),
        label="Количество оценок"
    )
    
    text_reviews_count = forms.IntegerField(
        min_value=0,
        initial=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0'
        }),
        label="Количество отзывов"
    )

    class Meta:
        model = Book
        fields = ['title', 'num_pages', 'publication_date', 
                 'publisher', 'language', 'authors']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'num_pages': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'publication_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'publisher': forms.Select(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'authors': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
        if self.instance and self.instance.pk and hasattr(self.instance, 'rating'):
            rating = self.instance.rating
            self.fields['average_rating'].initial = rating.average_rating
            self.fields['ratings_count'].initial = rating.ratings_count
            self.fields['text_reviews_count'].initial = rating.text_reviews_count
        
        
        self.fields['authors'].queryset = Author.objects.order_by('author_name')
        self.fields['publisher'].queryset = Publisher.objects.order_by('publisher_name')
        self.fields['language'].queryset = Language.objects.order_by('language_name')
    
    def save(self, commit=True):
        
        average_rating = self.cleaned_data.get('average_rating')
        ratings_count = self.cleaned_data.get('ratings_count')
        text_reviews_count = self.cleaned_data.get('text_reviews_count')
        
        
        book = super().save(commit=False)
        
        
        if self.instance and self.instance.pk and hasattr(self.instance, 'rating'):
            
            rating = self.instance.rating
            rating.average_rating = average_rating
            rating.ratings_count = ratings_count
            rating.text_reviews_count = text_reviews_count
            if commit:
                rating.save()
        else:
            
            rating = Rating.objects.create(
                average_rating=average_rating,
                ratings_count=ratings_count,
                text_reviews_count=text_reviews_count
            )
            book.rating = rating
        
        if commit:
            book.save()
            self.save_m2m()  
        
        return book