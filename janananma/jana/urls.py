from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import custom_logout  # adjust if views are imported differently

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('owner/summary/', views.owner_dashboard, name='owner_dashboard'),
    path('purchase/', views.manager_purchase_entry, name='manager_purchase_entry'),
    #path('daily-finance/', views.manager_daily_finance_entry, name='manager_daily_finance_entry'),
    path('manager/finance-summary/', views.manager_finance_summary, name='manager-finance-summary'),
    path('manager/edit-daily-finance/<int:finance_id>/', views.edit_daily_finance, name='edit-daily-finance'),
    path('manager/purchase/', views.manager_purchase_entry, name='manager_purchase_entry'),
    path('owner/wholesalers/', views.owner_manage_wholesalers, name='owner_manage_wholesalers'),
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('manager/daily-finance/', views.manager_daily_finance_entry, name='manager-daily-finance'),
    path('owner/delete-finance/<str:date_str>/', views.delete_daily_finance, name='delete-daily-finance'),

    

]
