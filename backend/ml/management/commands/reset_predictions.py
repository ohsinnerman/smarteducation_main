"""
`python manage.py reset_predictions [--clear-only] [--train]`

Consolidates the old root-level clear_predictions.py / run_predictions.py:
clears existing PredictionResult rows and regenerates predictions for all
students. Pass --clear-only to just delete, or --train to retrain models first.
"""

from django.core.management.base import BaseCommand

from ml.models import PredictionResult


class Command(BaseCommand):
    help = "Clear and regenerate ML predictions for all students."

    def add_arguments(self, parser):
        parser.add_argument('--clear-only', action='store_true',
                            help="Only delete existing predictions; do not regenerate.")
        parser.add_argument('--train', action='store_true',
                            help="Retrain models before generating predictions.")

    def handle(self, *args, **options):
        count, _ = PredictionResult.objects.all().delete()
        self.stdout.write(f"Deleted {count} existing predictions.")
        if options['clear_only']:
            return

        from ml.predictor import train_models, run_predictions_for_all

        if options['train']:
            self.stdout.write("Training models…")
            self.stdout.write(str(train_models()))

        generated = run_predictions_for_all()
        self.stdout.write(self.style.SUCCESS(f"Generated {generated} predictions."))
