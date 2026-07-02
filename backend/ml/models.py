from django.db import models
from students.models import Student


class PredictionResult(models.Model):
    PREDICTION_TYPES = (
        ('performance', 'Performance Prediction'),
        ('at_risk', 'At-Risk Detection'),
        ('dropout', 'Dropout Prediction'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='predictions')
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPES)
    predicted_value = models.FloatField()
    confidence = models.FloatField(help_text='Confidence score 0-1')
    risk_level = models.CharField(max_length=10, blank=True, null=True,
                                  choices=(('low', 'Low'), ('medium', 'Medium'), ('high', 'High')))
    details = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.name} - {self.get_prediction_type_display()}: {self.predicted_value}"
