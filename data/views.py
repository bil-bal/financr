from django.shortcuts import render, redirect
from django.contrib import messages
from data.models import Expense, Category, Monthly
import datetime
import re
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import csv
from cryptography.fernet import Fernet
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from financr.settings import SECRET_KEY

# Create your views here.

@login_required
def add_monthly(request):
    if request.method == "POST":
        monthly_limit = Monthly()
        monthly_limit.monthly = encr(gen_encr(SECRET_KEY), request.POST['monthly'])
        monthly_limit.user = request.user
        if not Monthly.objects.filter(user_id = request.user.id):
            monthly_limit.save()
        else:
            Monthly.objects.filter(user_id = request.user.id).update(monthly = encr(gen_encr(SECRET_KEY), request.POST['monthly']))
        return redirect('add')
    else:
        return redirect('add')


@login_required
def add_data(request):
    if request.method == "POST":
        data = Expense()
        data.date = request.POST['date']
        data.category = request.POST['category']
        data.price_b = encr(gen_encr(SECRET_KEY), request.POST['price'])
        
        if request.POST["notes"].strip() == "":
            note = "-"
        else:
            note = request.POST["notes"]
        
        data.notes = note
        data.user = request.user
        data.save()
        return redirect('add')
    else:
        return redirect('add')

@login_required
def add_cat(request):
    if request.method == "POST":
        category = Category()
        category.cat = request.POST['cat'].strip()
        category.cat = re.sub('[^A-Za-z0-9 ]+', '', category.cat).lower().capitalize()
        category.user_id = request.user.id
        if not bool(category.cat) == False and not bool(Category.objects.filter(cat = category.cat, user_id = request.user.id)):
            category.save()
        return redirect('add')
    else:
        return redirect('add')

@login_required
def remove_cat(request):
    if request.method == "POST":
        category = request.POST['category'].strip()
        Category.objects.filter(cat = category, user_id = request.user.id).delete()
        return redirect('add')
    else:
        return redirect('add')

# @login_required
# def view_data(request):
#     total = 0
#     start = False
#     end = False

#     cat = Category.objects.filter(user_id = request.user.id).values('cat')
#     cat_set = set()
#     dat = Expense.objects.filter(user_id = request.user.id).order_by("-date")
#     for x in cat:
#         cat_set.add(x.get('cat'))
#     if bool(request.POST.get("date1")) and bool(request.POST.get("date2")):
#         start = request.POST['date1']
#         end = request.POST['date2']
#         if start > end:
#             start = request.POST['date2']
#             end = request.POST['date1']
#         dat = Expense.objects.filter(date__range=(start, end), user_id = request.user.id).order_by("-date")
#     elif bool(request.POST.get("range")):
#         end = datetime.date.today()
#         start = end - datetime.timedelta(int(request.POST.get("range")))
#         dat = Expense.objects.filter(date__range=(start, end), user_id = request.user.id).order_by("-date")
#     elif bool(request.POST.get("category")):
#         cat = request.POST.get("category")
#         dat = Expense.objects.filter(category = cat, user_id = request.user.id)

#     for x in dat:
#         x.price_b = float(decr(gen_encr(SECRET_KEY), bytes(x.price_b)))
#         total += x.price_b
        
#     return render(request, "view.html", {"name": request.user.first_name, "data": dat, "nbar": "view", "category": cat_set, "toggle_edit": False, "total": total, "start": start, "end": end})

@login_required
def remove_data(request):
    if request.method == "POST":
        cat = Category.objects.filter(user_id = request.user.id).values('cat')
        cat_set = set()
        for x in cat:
            cat_set.add(x.get('cat'))
        dat = Expense.objects.filter(user_id = request.user.id).order_by('-date')
        Expense.objects.filter(id = request.POST['dat_id'], user_id = request.user.id).delete()

        for x in dat:
            x.price_b = float(decr(gen_encr(SECRET_KEY), bytes(x.price_b)))
            
        return render(request, "view.html", {"name": request.user.first_name, "data": dat, "nbar": "view", "category": cat_set, "toggle_edit": True})
    else:
        return redirect("view")

@login_required
def edit_data(request):
    if request.method == "POST":
        if request.POST["notes"] == "":
            note = "-"
        else:
            note = request.POST["notes"]

        Expense.objects.filter(user_id = request.user.id, id = request.POST["dat_id"]).update(date = request.POST["date"], price_b = encr(gen_encr(SECRET_KEY), request.POST['price']), category = request.POST["category"], notes = note)
        cat = Category.objects.filter(user_id = request.user.id).values('cat')
        cat_set = set()
        for x in cat:
            cat_set.add(x.get('cat'))
        dat = Expense.objects.filter(user_id = request.user.id).order_by('-date')

        for x in dat:
            x.price_b = float(decr(gen_encr(SECRET_KEY), bytes(x.price_b)))

        return render(request, "view.html", {"name": request.user.first_name, "data": dat, "nbar": "view", "category": cat_set, "toggle_edit": True})
    else:
        return redirect("view")

@login_required
def toggle_edit(request):
    if request.method == "POST":
        tr = True
        if request.POST["toggle_edit_value"] == "True":
            tr = True
        else:
            return redirect("view")
        cat = Category.objects.filter(user_id = request.user.id).values('cat')
        cat_set = set()
        for x in cat:
            cat_set.add(x.get('cat'))
        dat = Expense.objects.filter(user_id = request.user.id).order_by('-date')

        for x in dat:
            x.price_b = float(decr(gen_encr(SECRET_KEY), bytes(x.price_b)))

        return render(request, "view.html", {"name": request.user.first_name, "data": dat, "nbar": "view", "category": cat_set, "toggle_edit": tr})
    else:
        return redirect("view")
        
# @login_required
# def download_csv(request, dat):
#     response = HttpResponse(content_type="text/csv")
#     response["Content-Disposition"] = 'attachment; filename="financr.csv"'

#     writer = csv.writer(response)
#     writer.writerow(["date","category","price","notes"])
    
#     #dat = Expense.objects.filter(user_id = request.user.id).order_by("-date")

#     print(dat)


#     for x in dat:
#         x.price_b = float(decr(gen_encr(SECRET_KEY), bytes(x.price_b)))
#         writer.writerow([x.date, x.category, x.price_b, x.notes])

#     return response

def import_csv(request):
    if request.method == "POST":
        csv_file = request.FILES['csv_file']
        
        f = csv_file.read().decode()
        lines = f.splitlines()
        reader = csv.reader(lines)
        first_row = next(reader)
        if "date" in first_row and "category" in first_row and "price" in first_row and "notes" in first_row:
            row_indexes = [first_row.index("date"), first_row.index("category"), first_row.index("price"), first_row.index("notes")]
            for row in reader:
                data = Expense()
                data.date = row[row_indexes[0]]
                cat = row[row_indexes[1]].strip()
                cat = re.sub('[^A-Za-z0-9 ]+', '', cat).lower().capitalize()
                if not bool(Category.objects.filter(cat = cat, user_id = request.user.id)):
                    category = Category()
                    category.cat = cat
                    category.user_id = request.user.id
                    category.save()

                data.category = cat
                data.price_b = encr(gen_encr(SECRET_KEY), row[row_indexes[2]])

                if row[row_indexes[3]] == "":
                    note = "-"
                else:
                    note = row[row_indexes[3]]

                data.notes = note
                data.user = request.user
                data.save()
        else:
            messages.info(request, "Invalid .csv file format. Use columns with \"date\", \"category\", \"price\", \"notes\" in header.")

            return redirect('add')
        
        messages.info(request, "Import from .csv successfull.")
        return redirect('add')
    else:
        return redirect('add')

@login_required
def delete_table(request):
    if request.method == "POST":
        Expense.objects.filter(user_id = request.user.id).delete()
    else: 
        return redirect('view')

    return redirect('view')

def gen_encr(pw_):
    password = bytes(pw_, 'utf-8')
    kdf = PBKDF2HMAC(
        algorithm = hashes.SHA256(),
        length=32,
        salt = b'O\x92"c=\x0b\x06\x91\xcb\x1d\x0c"\xf1OGY',
        iterations = 100,
        backend = default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def encr(key, price_to_enc):
    f = Fernet(key)
    token = f.encrypt(bytes(price_to_enc, 'utf-8'))
    return token

def decr(key, token_to_decr):
    f =  Fernet(key)
    return f.decrypt(token_to_decr)