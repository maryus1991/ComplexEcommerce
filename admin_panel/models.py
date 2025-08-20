from django.db import models


class DailyViewCount(models.Model):
    date = models.DateField(verbose_name='تاریخ')
    count = models.PositiveIntegerField(default=0, verbose_name='تعداد')

    class Meta:
        unique_together = ('date',)  # جلوگیری از رکورد تکراری در هر روز
        ordering = ['-date']
        verbose_name = 'بازدید روزانه'
        verbose_name_plural = 'بازدید های روزانه'

    def __str__(self):
        return f"{self.date}: {self.count} views"


