from datetime import date


def year(request):
    """Добавляет переменную с текущим годом."""
    year_now = date.today()
    year_format = year_now.strftime('%Y')
    return {
        'year': int(year_format)
    }
