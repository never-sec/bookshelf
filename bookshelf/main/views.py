from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Sum
from .models import Quote
import random
import json

def index(request):
    quotes = Quote.objects.all()
    quote = random.choice(quotes) if quotes else None
    return render(request, 'main/index.html', {'quote': quote})

def create(request):
    return render(request,'main/create.html')

def tier(request):
    quotes = Quote.objects.order_by('-likes')[:10]
    books = (
        Quote.objects.values('book')
        .annotate(total_likes=Sum('likes'))
        .order_by('-total_likes')[:10]
    )
    authors = (
        Quote.objects.values('author')
        .annotate(total_likes=Sum('likes'))
        .order_by('-total_likes')[:10]
    )
    return render(request, 'main/tier.html', {
        'quotes': quotes,
        'books': books,
        'authors': authors
    })
def random_quote(request):
    # 1. Получаем ID текущей цитаты из GET-параметра
    current_id = request.GET.get('current_id')

    # 2. Получаем все цитаты, ИСКЛЮЧАЯ текущую
    quotes_to_choose_from = Quote.objects.all()
    if current_id:
        quotes_to_choose_from = quotes_to_choose_from.exclude(id=current_id)

    # Крайний случай: если в базе всего одна цитата (или после исключения ничего не осталось),
    # то мы не можем выдать "другую". Вернем пустой ответ или первую попавшуюся.
    if not quotes_to_choose_from.exists():
        # Если есть хоть какие-то цитаты в базе, вернем любую
        first_quote = Quote.objects.first()
        if not first_quote:
             return JsonResponse({'id': None, 'text': 'Нет цитат для выбора', 'author': '', 'book': ''})
        # Если ничего не осталось после фильтрации, вернем ту же самую
        quotes_to_choose_from = Quote.objects.filter(id=current_id)


    # 3. Готовим данные для взвешенного выбора
    # Создаем список всех цитат, которые могут быть выбраны
    selection = list(quotes_to_choose_from)
    # Создаем список весов. Вес = likes + weight. Убедимся, что вес не меньше 1, чтобы избежать ошибок.
    weights = [q.likes + q.weight if (q.likes + q.weight > 0) else 1 for q in selection]

    # 4. Выполняем взвешенный случайный выбор
    # random.choices возвращает список, поэтому берем первый элемент [0]
    try:
        quote = random.choices(selection, weights=weights, k=1)[0]
    except IndexError:
        # Это может случиться, если population пуст
        return JsonResponse({'id': None, 'text': 'Нет цитат для выбора', 'author': '', 'book': ''})


    return JsonResponse({
        'id': quote.id,
        'text': quote.text,
        'author': getattr(quote, "author", ""),
        'book': getattr(quote, "book", ""),
        'likes': quote.likes
    })

@csrf_exempt
def like_quote(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    liked_quotes = request.session.get("liked_quotes", [])

    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')

        if action == 'like':
            if quote_id not in liked_quotes:
                quote.likes += 1
                quote.save()
                liked_quotes.append(quote_id)
                request.session["liked_quotes"] = liked_quotes
        elif action == 'unlike':
            if quote_id in liked_quotes and quote.likes > 0:
                quote.likes -= 1
                quote.save()
                liked_quotes.remove(quote_id)
                request.session["liked_quotes"] = liked_quotes

        return JsonResponse({'likes': quote.likes})

def create(request):
    if request.method == "POST":
        text = request.POST.get("quote")
        author = request.POST.get("author")
        book = request.POST.get("book")

        if Quote.objects.filter(book=book).count() >= 3:
            return render(request, 'main/create.html', {
                "error": f"Нельзя добавить больше 3 цитат из книги «{book}»"
            })
        # создаём запись в базе
        Quote.objects.create(text=text, author=author, book=book, likes=0, weight=10)

        # редиректим обратно на главную страницу
        return redirect('home')

    # если GET — просто показываем форму
    return render(request, 'main/create.html')