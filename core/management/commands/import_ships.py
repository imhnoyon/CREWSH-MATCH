import csv
from crewmatch.settings import BASE_DIR
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        csv_file = BASE_DIR / 'ships.csv'
        field_names = ['Adora', 'AIDA', 'Ambassador', 'Aroya', 'Carnival', 'Celebrity', 'Celestyal', 'Costa',
                       'Cunard', 'Disney', 'Holland America', 'Marella', 'Margaritaville', 'MSC', 'MSC Explora', 'Norwegian',
                       'Oceania', 'P&O Cruises', 'Princess', 'Regent Seven Seas', 'Royal Caribbean', 'TUI', 'Viking Cruises', 'Virgin Voyages']
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=field_names)
            next(reader)
            for data in reader:
                print(data)
                break


