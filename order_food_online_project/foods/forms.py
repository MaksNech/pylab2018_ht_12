from django.db import models
from django.forms import ModelForm

from .models import Dish, Ingredient, Order, Comment


class IngredientAddForm(ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'img', 'quantity', 'unit', 'cost']


class DishAddForm(ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'img', 'description', 'section']


class OrderAddForm(ModelForm):
    class Meta:
        model = Order
        fields = ['cost']


class CommentAddForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['dish', 'body']
