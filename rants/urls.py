from django.urls import path
from . import views

app_name = 'rants'

urlpatterns = [
    # Homepage and feed
    path('', views.HomeView.as_view(), name='home'),
    path('hall-of-fame/', views.HallOfFameView.as_view(), name='hall_of_fame'),

    # Rant views
    path('rant/<uuid:pk>/', views.RantDetailView.as_view(), name='detail'),
    path('submit/', views.RantCreateView.as_view(), name='create'),

    # Side-by-side views
    path('sidebyside/<uuid:pk>/', views.SideBySideDetailView.as_view(), name='sidebyside_detail'),
    path('submit/sidebyside/', views.SideBySideCreateView.as_view(), name='sidebyside_create'),

    # Category view
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),

    # Reactions (HTMX)
    path('react/<str:content_type>/<uuid:pk>/<str:reaction_type>/',
         views.ReactView.as_view(), name='react'),

    # Reporting
    path('report/<str:content_type>/<uuid:pk>/',
         views.ReportView.as_view(), name='report'),
]
