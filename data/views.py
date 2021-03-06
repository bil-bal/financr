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

# add monthly limit
@login_required
def add_monthly(request):
    if request.method == "POST":
        monthly_limit = Monthly()
        monthly_limit.monthly = encr(gen_encr(SECRET_KEY), request.POST['monthly'])
        monthly_limit.user = request.user

        # save if entry in database doesnt exist yet or update existing entry
        if not Monthly.objects.filter(user_id = request.user.id):
            monthly_limit.save()
        else:
            Monthly.objects.filter(user_id = request.user.id).update(monthly = encr(gen_encr(SECRET_KEY), request.POST['monthly']))
        return redirect('add')
    else:
        return redirect('add')

# add data entry
@login_required
def add_data(request):
    if request.method == "POST":
        data = Expense()
        print(request.POST['date'])
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print(current_time)
        data.date = f"{request.POST['date']} {current_time}"
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

# add category
@login_required
def add_cat(request):
    if request.method == "POST":
        category = Category()
        category.cat = request.POST['cat'].strip()
        category.cat = re.sub('[^A-Za-z0-9 ]+', '', category.cat).lower().capitalize()
        category.user_id = request.user.id
        # category is not empty and doesnt exist
        if not bool(category.cat) == False and not bool(Category.objects.filter(cat = category.cat, user_id = request.user.id)):
            category.save()
        return redirect('add')
    else:
        return redirect('add')

# remove category
@login_required
def remove_cat(request):
    if request.method == "POST":
        category = request.POST['category'].strip()
        Category.objects.filter(cat = category, user_id = request.user.id).delete()
        return redirect('add')
    else:
        return redirect('add')

# delete entry
@login_required
def remove_data(request):
    if request.method == "POST":
        cat = Category.objects.filter(user_id = request.user.id).values('cat')
        cat_list = []
        for x in cat:
            cat_list.append(x.get('cat'))
        dat = Expense.objects.filter(user_id = request.user.id).order_by('-date')
        Expense.objects.filter(id = request.POST['dat_id'], user_id = request.user.id).delete()

        for x in dat:
            x.price_b = float(decr(gen_encr(SECRET_KEY), bytes(x.price_b)))
            
        return render(request, "view.html", {"name": request.user.username, "data": dat, "nbar": "view", "category": cat_list, "toggle_edit": True})
    else:
        return redirect("view")

# edit entry
@login_required
def edit_data(request):
    if request.method == "POST":
        if request.POST["notes"] == "":
            note = "-"
        else:
            note = request.POST["notes"]

        Expense.objects.filter(user_id = request.user.id, id = request.POST["dat_id"]).update(date = request.POST["date"], price_b = encr(gen_encr(SECRET_KEY), request.POST['price']), category = request.POST["category"], notes = note)
        cat = Category.objects.filter(user_id = request.user.id).values('cat')
        cat_list = []

        for x in cat:
            cat_list.append(x.get('cat'))
        dat = Expense.objects.filter(user_id = request.user.id).order_by('-date')

        for x in dat:
            x.price_b = str(float(decr(gen_encr(SECRET_KEY), bytes(x.price_b))))

        return render(request, "view.html", {"name": request.user.username, "data": dat, "nbar": "view", "category": cat_list, "toggle_edit": True})
    else:
        return redirect("view")

# toggle edit view
@login_required
def toggle_edit(request):
    if request.method == "POST":
        tr = True
        if request.POST["toggle_edit_value"] == "True":
            tr = True
        else:
            return redirect("view")
        cat = Category.objects.filter(user_id = request.user.id).values('cat')
        cat_list = []

        for x in cat:
            cat_list.append(x.get('cat'))

        dat = Expense.objects.filter(user_id = request.user.id).order_by('-date')

        for x in dat:
            x.price_b = str(float(decr(gen_encr(SECRET_KEY), bytes(x.price_b))))

        return render(request, "view.html", {"name": request.user.username, "data": dat, "nbar": "view", "category": cat_list, "toggle_edit": tr})
    else:
        return redirect("view")

# import from .csv file
@login_required
def import_csv(request):
    if request.method == "POST":
        csv_file = request.FILES['csv_file']
        
        f = csv_file.read().decode()
        lines = f.splitlines()
        reader = csv.reader(lines)
        first_row = next(reader)
        # check if .csv file header is in correct format and save indices of columns
        if "date" in first_row and "category" in first_row and "price" in first_row and "notes" in first_row:
            row_indexes = [first_row.index("date"), first_row.index("category"), first_row.index("price"), first_row.index("notes")]
            for row in reader:
                data = Expense()
                data.date = row[row_indexes[0]]
                cat = row[row_indexes[1]].strip()
                cat = re.sub('[^A-Za-z0-9 ]+', '', cat).lower().capitalize()

                # create categories from .csv file
                if not bool(Category.objects.filter(cat = cat, user_id = request.user.id)):
                    category = Category()
                    category.cat = cat
                    category.user_id = request.user.id
                    category.save()

                data.category = cat
                data.price_b = encr(gen_encr(SECRET_KEY), row[row_indexes[2]])

                # placeholder for notes column
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

# delete all entries at once
@login_required
def delete_table(request):
    if request.method == "POST":
        Expense.objects.filter(user_id = request.user.id).delete()
    else: 
        return redirect('view')

    return redirect('view')

# generate encryption key
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

# encrypt data
def encr(key, price_to_enc):
    f = Fernet(key)
    token = f.encrypt(bytes(price_to_enc, 'utf-8'))
    return token

# decrypt data
def decr(key, token_to_decr):
    f =  Fernet(key)
    return f.decrypt(token_to_decr)