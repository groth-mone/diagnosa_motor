from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('hasil/', views.proses_diagnosa, name='proses_diagnosa'),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('gejala/', views.gejala_list, name='gejala_list'),
    path('gejala/tambah/', views.gejala_add, name='gejala_add'),
    path('gejala/edit/<int:pk>/', views.gejala_edit, name='gejala_edit'),
    path('gejala/hapus/<int:pk>/', views.gejala_delete, name='gejala_delete'),

    path('rules/', views.rule_list, name='rule_list'),
    path('rules/create/', views.rule_create, name='rule_create'),
    path('rules/edit/<int:pk>/', views.rule_edit, name='rule_edit'),
    path('rules/delete/<int:pk>/', views.rule_delete, name='rule_delete'),

    path('diagnosa/', views.diagnosa_list, name='diagnosa_list'),
    path('diagnosa/create/', views.diagnosa_create, name='diagnosa_create'),
    path('diagnosa/<int:pk>/edit/', views.diagnosa_update, name='diagnosa_update'),
    path('diagnosa/<int:pk>/delete/', views.diagnosa_delete, name='diagnosa_delete'),
    
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_update, name='user_update'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
]
