import datetime as date


def toDate(dateString):
    return date.datetime.strptime(dateString, "%Y-%m-%d").date()

def pagination(page, list, per_page):

    per_page = per_page
    start = (page - 1) * per_page
    end = start + per_page

    total_pages = (len(list) + per_page - 1) // per_page
    item_on_page = list[start:end]

    return total_pages, item_on_page