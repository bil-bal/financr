from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.http import HttpResponse
import csv
from data.models import Expense, Category, Monthly
import datetime
from django.contrib.auth.decorators import login_required
from data.views import decr, gen_encr
from financr.settings import SECRET_KEY
from pygal.style import Style
import pygal
import os

# Create your views here.


def start(request):
    if request.user.is_authenticated:
        return render(request, "start.html", {"name": request.user.username, "nbar": "start"})
    else:
        messages.info(request, "Not logged in")
        return redirect("home")

def logout(request):
    auth.logout(request)
    return redirect("home")

# view for add page
@login_required
def add(request):
    cat = Category.objects.filter(user_id = request.user.id).values("cat")
    storage = messages.get_messages(request)
    cat_list = []

    for x in cat:
        cat_list.append(x.get("cat"))

    dat = Expense.objects.filter(user_id = request.user.id).order_by('-id')[:5]

    for x in dat:
        x.price_b = float(decr(gen_encr(SECRET_KEY), bytes(x.price_b)))

    monthly_limit = Monthly.objects.filter(user_id = request.user.id).values("monthly")

    if not monthly_limit:
        monthly_value = 0
    else:
        monthly_value = int(decr(gen_encr(SECRET_KEY), bytes(monthly_limit[0].get("monthly"))))

    return render(request, "add.html", {"name": request.user.username, "category": cat_list, "data": dat, "nbar": "add", "monthly": monthly_value, "messages": storage})

# view for view page
@login_required
def view(request):
    total = 0       # total sum
    cat = Category.objects.filter(user_id = request.user.id).values('cat')
    cat_list = []

    # booleans for view filter
    start = False
    end = False
    range_days = False
    category_select = False
    search_notes = False

    for x in cat:
        cat_list.append(x.get('cat'))
    
    monthly_limit = Monthly.objects.filter(user_id = request.user.id).values("monthly")

    # which way to filter entries
    if bool(request.POST.get("date1")) and bool(request.POST.get("date2")):
        start = f"{request.POST['date1']} 00:00:00"
        _start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        end = f"{request.POST['date2']} 23:59:59"
        _end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        if start > end:
            start = f"{request.POST['date2']} 00:00:00"
            _start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
            end = f"{request.POST['date1']} 23:59:59"
            _end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        dat = Expense.objects.filter(date__range=(_start, _end), user_id = request.user.id).order_by("-date")
        start = datetime.datetime.strftime(_start.date(), "%Y-%m-%d")
        end = datetime.datetime.strftime(_end.date(), "%Y-%m-%d")
    elif bool(request.POST.get("range")):
        range_days = request.POST.get("range")
        end = datetime.datetime.today()
        start = end - datetime.timedelta(int(range_days))
        dat = Expense.objects.filter(date__range=(start, end), user_id = request.user.id).order_by("-date")
    elif bool(request.POST.get("category")):
        category_select = request.POST.get("category")
        dat = Expense.objects.filter(category = category_select, user_id = request.user.id).order_by('-date')
    elif bool(request.POST.get("search_notes")):
        search_notes = request.POST.get("search_notes")
        dat = Expense.objects.filter(notes__icontains=search_notes, user_id = request.user.id).order_by('-date')
    else:
        dat = Expense.objects.filter(user_id = request.user.id).order_by('-date')

    # download filtered entries as .csv file
    if 'download' in request.POST and dat:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename=financr Backup {datetime.date.today()}.csv'

        writer = csv.writer(response)
        writer.writerow(["date","category","price","notes"])

        for x in dat:
            x.price_b = float(decr(gen_encr(SECRET_KEY), bytes(x.price_b)))
            writer.writerow([x.date, x.category, x.price_b, x.notes])

        return response

    # create dictionary of entries for dates to calculate monthly limit percantage
    date_dict = {}
    month_count = 0

    for x in dat:
        x.price_b = float(decr(gen_encr(SECRET_KEY), bytes(x.price_b)))
        date_dict[x.date.year] = {}
        total += x.price_b

    for x in dat:
        date_dict[x.date.year][x.date.month] = {}

    for x in dat:
        date_dict[x.date.year][x.date.month][x.date.day] = 0

    for x in dat:
        date_dict[x.date.year][x.date.month][x.date.day] += x.price_b

    for i in date_dict.values():
        month_count += len(i.keys())
    
    if monthly_limit:
        monthly_limit = int(decr(gen_encr(SECRET_KEY), bytes(monthly_limit[0].get("monthly"))))
        month_count_value = month_count * monthly_limit

    if monthly_limit and month_count_value != 0:
        percentage = round((total / month_count_value) * 100, 2)
    else:
        percentage = 0

    return render(request, "view.html", {"name": request.user.username, "data": dat, "nbar": "view", "category": cat_list, "toggle_edit": False, "total": total, "percentage": percentage, "start": start, "end": end, "range_days": range_days, "category_select": category_select, "search_notes": search_notes})
    
# view for graph page
@login_required
def graphs(request):
    custom_style = Style(
        font_family='googlefont:Noto Sans',
        label_font_size = 20,
    major_label_font_size = 20,
    value_font_size = 32,
    value_label_font_size = 20,
    tooltip_font_size = 28,
    title_font_size = 32,
    legend_font_size = 28
    )
    custom_style_ = Style(font_family='googlefont:Noto Sans')
    
    cat = Category.objects.filter(user_id = request.user.id).values('cat')
    dat = Expense.objects.filter(user_id = request.user.id).order_by('date')
    date_list = []
    expense_list = []

    date_dict_month = {}
    date_dict_day = {}

    start = False
    end = False

    if bool(request.POST.get("date1")) and bool(request.POST.get("date2")):
        start = f"{request.POST['date1']} 00:00:00"
        _start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        end = f"{request.POST['date2']} 23:59:59"
        _end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        if start > end:
            start = f"{request.POST['date2']} 00:00:00"
            _start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
            end = f"{request.POST['date1']} 23:59:59"
            _end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        dat = Expense.objects.filter(date__range=(_start, _end), user_id = request.user.id).order_by("date")
        start = datetime.datetime.strftime(_start.date(), "%Y-%m-%d")
        end = datetime.datetime.strftime(_end.date(), "%Y-%m-%d")

    for x in dat:
        date_dict_month[x.date.year] = {}
        print(x.date.strftime("%Y-%m-%d"))
        date_dict_day[x.date.strftime("%Y-%m-%d")] = {}

    for x in dat:
        x.price_b = float(decr(gen_encr(SECRET_KEY), bytes(x.price_b)))
        
        expense_list.append(x.price_b)
        date_dict_month[x.date.year][x.date.month] = 0
        date_dict_day[x.date.strftime("%Y-%m-%d")] = 0

    for x in dat:
        date_dict_month[x.date.year][x.date.month] += x.price_b
        date_dict_day[x.date.strftime("%Y-%m-%d")] += x.price_b

    monthly_list = []
    month_dates = []

    for i in date_dict_month.keys():
        monthly_list += date_dict_month[i].values()       #total of each month
        for k in date_dict_month[i].keys():
            month_dates.append(f"{i}-{k}")

    daily_list = []

    for i in date_dict_day.keys():
        daily_list.append(date_dict_day[i])
        date_list.append(i)

    bar_chart = pygal.Bar(style=custom_style)
    bar_chart.title ="Per month"
    bar_chart.x_labels = map(str, month_dates)
    bar_chart.add("Expense", monthly_list)

    monthly_limit = Monthly.objects.filter(user_id = request.user.id).values("monthly", "user_id")

    if monthly_limit:
        monthly_value = int(decr(gen_encr(SECRET_KEY), bytes(monthly_limit[0].get("monthly"))))
        if monthly_value > 0:
            bar_chart.add("Limit", [monthly_value for i in monthly_list])

    bar_chart_data = bar_chart.render_data_uri()

    line_chart = pygal.Line(x_label_rotation=20, stroke_style={'width': 3},height=300, width=800, style=custom_style_)
    line_chart.title = "Per day"
    #line_chart.x_labels = map(lambda d: d.strftime('%Y-%m-%d'), date_list)
    line_chart.x_labels = map(lambda d: d, date_list)

    line_chart.add("Expense", daily_list)
    line_chart_data = line_chart.render_data_uri()

    cat_chart = pygal.Pie(style=custom_style, inner_radius=.4)
    cat_chart.title = "Per category"

    for x in cat:
        total_cat = 0
        if start != False and end != False:
            dat_cat = Expense.objects.filter(date__range=(start, end), user_id = request.user.id, category = x["cat"])
        else:
            dat_cat = Expense.objects.filter(user_id = request.user.id, category = x["cat"])
        for i in dat_cat:
            total_cat += float(decr(gen_encr(SECRET_KEY), bytes(i.price_b)))
        cat_chart.add(x["cat"], total_cat)

    cat_chart_data = cat_chart.render_data_uri()

    return render(request, "graphs.html", {"name": request.user.username, "nbar": "graphs", "cat_chart_data": cat_chart_data, "line_chart_data": line_chart_data, "bar_chart_data": bar_chart_data, "start": start, "end": end})