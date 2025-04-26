from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('recipes/', views.RecipeListView.as_view(), name='recipe-list'),
    path('recipe/<int:pk>/', views.RecipeDetailView.as_view(), name='recipe-detail'),
    path('recipe/new/', views.RecipeCreateView.as_view(), name='recipe-create'),
    path('recipe/<int:pk>/edit/', views.RecipeUpdateView.as_view(), name='recipe-update'),
    path('recipe/<int:pk>/delete/', views.RecipeDeleteView.as_view(), name='recipe-delete'),
    path('recipe/<int:recipe_id>/review/', views.add_review, name='add-review'),
    path('collection/new/', views.CollectionCreateView.as_view(), name='collection-create'),
    path('review/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='edit-review'),
    path('review/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='delete-review'),
    path('search/', views.recipe_search, name='recipe-search'),
   
]