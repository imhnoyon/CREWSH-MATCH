import csv
from crewmatch.settings import BASE_DIR

from django.db import transaction
from django.core.management import BaseCommand

from core.models import Company, Ship

class Command(BaseCommand):
    def handle(self, *args, **options):
        csv_file = BASE_DIR / 'ships.csv'
        field_names = ['Adora', 'AIDA', 'Ambassador', 'Aroya', 'Carnival', 'Celebrity', 'Celestyal', 'Costa',
                       'Cunard', 'Disney', 'Holland America', 'Marella', 'Margaritaville', 'MSC', 'MSC Explora', 'Norwegian',
                       'Oceania', 'P&O Cruises', 'Princess', 'Regent Seven Seas', 'Royal Caribbean', 'TUI', 'Viking Cruises', 'Virgin Voyages']
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=field_names)
            next(reader)
            company_count = len(field_names)
            ship_count = 0
            with transaction.atomic():
                try:
                    for data in reader:
                        for company_name, ship_name in data.items():
                            if company_name and ship_name:
                                company, _ = Company.objects.get_or_create(name=company_name)
                                ship, _ = Ship.objects.get_or_create(company=company, name=ship_name)
                                ship_count += 1

                    print("Data imported successfully.")

                except Exception as e:
                    print("Error %s" % str(e))
