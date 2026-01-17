from django.db import models

class Language(models.Model):
    language_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)
    language_name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'languages'
    
    def __str__(self):
        return f"{self.language_name} ({self.code})"

class Publisher(models.Model):
    publisher_id = models.AutoField(primary_key=True)
    publisher_name = models.CharField(max_length=255, unique=True)
    
    class Meta:
        db_table = 'publishers'
    
    def __str__(self):
        return self.publisher_name

class Author(models.Model):
    author_id = models.AutoField(primary_key=True)
    author_name = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'authors'
    
    def __str__(self):
        return self.author_name

class Rating(models.Model):
    rating_id = models.AutoField(primary_key=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2)
    ratings_count = models.IntegerField()
    text_reviews_count = models.IntegerField()
    
    class Meta:
        db_table = 'ratings'
    
    def __str__(self):
        return f"{self.average_rating} ({self.ratings_count} оценок)"

class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=500)
    num_pages = models.IntegerField(null=True, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    
    
    publisher = models.ForeignKey(
        Publisher, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='books'
    )
    
    rating = models.OneToOneField(
        Rating,
        on_delete=models.CASCADE,
        related_name='book'
    )
    
    language = models.ForeignKey(
        Language,
        on_delete=models.SET_NULL,
        null=True,
        related_name='books'
    )
    
    
    authors = models.ManyToManyField(
        Author,
        through='BookAuthor',
        related_name='books'
    )
    
    class Meta:
        db_table = 'books'
    
    def __str__(self):
        return self.title
    
    @property
    def author_names(self):
        """Возвращает имена авторов через запятую"""
        return ", ".join([author.author_name for author in self.authors.all()])

class BookAuthor(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'books_authors'
        unique_together = [['book', 'author']]
    
    def __str__(self):
        return f"{self.book.title} - {self.author.author_name}"