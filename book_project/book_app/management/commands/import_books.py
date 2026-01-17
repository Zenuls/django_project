import csv
from django.core.management.base import BaseCommand
from datetime import datetime
from django.db import transaction
from book_app.models import Book, Author, Publisher, Language, Rating, BookAuthor
import os

class Command(BaseCommand):
    help = 'Импорт книг из CSV файла'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Путь к CSV файлу')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f"Файл {csv_file_path} не найден!"))
            return

        languages_cache = {}
        publishers_cache = {}
        authors_cache = {}
        
        books_count = 0
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader, 1):
                try:
                    with transaction.atomic():
                        
                        try:
                            month, day, year = map(int, row['publication_date'].split('/'))
                            pub_date = f"{year:04d}-{month:02d}-{day:02d}"
                        except:
                            pub_date = None
                        
                        
                        lang_code = row['language_code']
                        if lang_code not in languages_cache:
                            lang_obj, created = Language.objects.get_or_create(
                                code=lang_code,
                                defaults={'language_name': f"Language {lang_code}"}
                            )
                            languages_cache[lang_code] = lang_obj
                        
                        
                        publisher_name = row['publisher'].strip()
                        if publisher_name not in publishers_cache:
                            pub_obj, created = Publisher.objects.get_or_create(
                                publisher_name=publisher_name
                            )
                            publishers_cache[publisher_name] = pub_obj
                        
                        
                        rating = Rating.objects.create(
                            average_rating=float(row['average_rating']),
                            ratings_count=int(row['ratings_count']),
                            text_reviews_count=int(row['text_reviews_count'])
                        )
                        
                        
                        book = Book.objects.create(
                            title=row['title'],
                            num_pages=int(row['num_pages']) if row['num_pages'].isdigit() else None,
                            publication_date=pub_date,
                            publisher=publishers_cache[publisher_name],
                            rating=rating,
                            language=languages_cache[lang_code]
                        )
                        
                        
                        authors_str = row['authors']
                        for author_name in authors_str.split('/'):
                            author_name = author_name.strip()
                            if not author_name:
                                continue
                            
                            if author_name not in authors_cache:
                                author_obj, created = Author.objects.get_or_create(
                                    author_name=author_name
                                )
                                authors_cache[author_name] = author_obj
                            
                            
                            BookAuthor.objects.create(
                                book=book,
                                author=authors_cache[author_name]
                            )
                        
                        books_count += 1
                        
                        if i % 100 == 0:
                            self.stdout.write(f"Обработано книг: {books_count}")
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Ошибка в строке {i}: {str(e)}")
                    )
                    continue
        
        self.stdout.write(self.style.SUCCESS(f"Импорт завершен! Добавлено книг: {books_count}"))