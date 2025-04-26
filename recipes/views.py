from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import Recipe, Category, Review, Collection, UserProfile
from .forms import RecipeForm, ReviewForm, CollectionForm, UserProfileForm
from django.db.models import Q


# Public Views
def home(request):
    recipes = Recipe.objects.filter(is_published=True).order_by('-created_at')[:6]
    categories = Category.objects.all()
    return render(request, 'recipes/home.html', {
        'recipes': recipes,
        'categories': categories
    })


class RecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 9

    def get_queryset(self):
        queryset = Recipe.objects.filter(is_published=True)

        # Get category from URL
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__name=category)  # Ensure this matches your model

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()  # Pass all categories to the template
        return context

class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipes/recipe_detail.html'
    context_object_name = 'recipe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_form'] = ReviewForm()
        return context


# Protected Views (require login)
class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/recipe_form.html'
    success_url = reverse_lazy('recipe-list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class RecipeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/recipe_form.html'

    def test_func(self):
        recipe = self.get_object()
        return self.request.user == recipe.author


class RecipeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Recipe
    success_url = reverse_lazy('recipe-list')
    template_name = 'recipes/recipe_confirm_delete.html'

    def test_func(self):
        recipe = self.get_object()
        return self.request.user == recipe.author


from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@login_required
def add_review(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                # Check if the user has already reviewed this recipe
                review = form.save(commit=False)
                review.recipe = recipe
                review.user = request.user
                review.save()
                messages.success(request, "Your review has been submitted successfully!")
            except IntegrityError:
                messages.error(request, "You have already reviewed this recipe.")
        else:
            messages.error(request, "There was an error with your review. Please try again.")
    return redirect('recipe-detail', pk=recipe_id)

def recipe_search(request):
    query = request.GET.get('q')
    recipes = Recipe.objects.filter(ingredients__icontains=query) if query else Recipe.objects.all()
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes, 'query': query})
# Profile Views
# class UserProfileView(LoginRequiredMixin, DetailView):
#     model = UserProfile
#     template_name = 'recipes/profile.html'
#     context_object_name = 'profile'
#
#     def get_object(self):
#         return get_object_or_404(UserProfile, user=self.request.user)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['user_recipes'] = Recipe.objects.filter(author=self.request.user).order_by('-created_at')
#         return context


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'recipes/edit_profile.html', {'form': form})


# Collection Views
class CollectionCreateView(LoginRequiredMixin, CreateView):
    model = Collection
    form_class = CollectionForm
    template_name = 'recipes/collection_form.html'
    success_url = reverse_lazy('collections')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


from django.views.generic.edit import UpdateView, DeleteView

class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'recipes/review_form.html'

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user

    def get_success_url(self):
        return reverse_lazy('recipe-detail', kwargs={'pk': self.object.recipe.id})
    
    
    
    
class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = 'recipes/review_confirm_delete.html'

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user

    def get_success_url(self):
        return reverse_lazy('recipe-detail', kwargs={'pk': self.object.recipe.id})