from django.urls import path
from . import views

urlpatterns = [
    path("add/add_data", views.add_data, name="add_data"),
    path("add/add_cat", views.add_cat, name="add_cat"),
    path("add/remove_cat", views.remove_cat, name="remove_cat"),
    path("view/remove_data", views.remove_data, name="remove_data"),
    path("view/toggle_edit", views.toggle_edit, name="toggle_edit"),
    path("view/edit_data", views.edit_data, name="edit_data"),
    path("add/add_monthly", views.add_monthly, name="add_monthly"),
    path("add/import_csv", views.import_csv, name="import_csv"),
    path("view/delete_table", views.delete_table, name="delete_table")
]