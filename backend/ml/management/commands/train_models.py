from django.core.management.base import BaseCommand
from ml.predictor import train_models, run_predictions_for_all


class Command(BaseCommand):
    help = 'Train ML models and run predictions for all students'

    def add_arguments(self, parser):
        parser.add_argument(
            '--train-only',
            action='store_true',
            help='Only train models without running predictions',
        )
        parser.add_argument(
            '--predict-only',
            action='store_true',
            help='Only run predictions without training',
        )

    def handle(self, *args, **options):
        if not options['predict_only']:
            self.stdout.write('Training ML models...')
            metrics = train_models()
            if 'error' in metrics:
                self.stdout.write(self.style.ERROR(f"Training failed: {metrics['error']}"))
                return
            self.stdout.write(self.style.SUCCESS(f"Training complete. Metrics: {metrics}"))

        if not options['train_only']:
            self.stdout.write('Running predictions for all students...')
            count = run_predictions_for_all()
            self.stdout.write(self.style.SUCCESS(f"Predictions complete. {count} predictions generated."))
