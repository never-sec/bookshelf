from django.db import models

# Create your models here.
class Quote(models.Model):
    author = models.CharField('author', max_length=50)
    book = models.CharField('book', max_length=50)
    text = models.TextField('text')
    likes = models.PositiveIntegerField('likes')
    weight = models.PositiveIntegerField('weight')
    views = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['text', 'author'], name='unique_text_author')
        ]

    def __str__(self):
        return f'"{self.text[:30]}..." — {self.author}, {self.book}'
