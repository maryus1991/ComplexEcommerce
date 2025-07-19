from django.db import models


class DailyViewCount(models.Model):
    date = models.DateField()
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('date',)  # جلوگیری از رکورد تکراری در هر روز
        ordering = ['-date']

    def __str__(self):
        return f"{self.date}: {self.count} views"


