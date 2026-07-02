
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarteducation.settings')
django.setup()

from ml.models import PredictionResult

count, _ = PredictionResult.objects.all().delete()
print(f"Deleted {count} existing predictions!")
