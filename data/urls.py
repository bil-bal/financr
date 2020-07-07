from django.urls import path
from . import views

urlpatterns = [
    path("add_data", views.add_data, name="add_data"),
    path("add_cat", views.add_cat, name="add_cat"),
    path("remove_cat", views.remove_cat, name="remove_cat"),
    path("remove_data", views.remove_data, name="remove_data"),
    path("toggle_edit", views.toggle_edit, name="toggle_edit"),
    path("edit_data", views.edit_data, name="edit_data"),
    path("add_monthly", views.add_monthly, name="add_monthly"),
    path("import_csv", views.import_csv, name="import_csv"),
    path("delete_table", views.delete_table, name="delete_table")
]