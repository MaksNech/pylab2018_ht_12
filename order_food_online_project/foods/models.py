import uuid
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from notes.models import NotedModel
from django.db.models.signals import post_delete, post_save
from django.contrib.auth.models import Group, Permission
from rest_framework.authtoken.models import Token
from django.contrib.contenttypes.fields import GenericRelation
from django.template.defaultfilters import slugify


def get_allowed_groups(codename):
    permission = Permission.objects.get(codename=codename)
    allowed_groups = Group.objects.all().filter(permissions__codename=codename)
    allowed_groups = [gr.name for gr in allowed_groups]
    return {'allowed_groups': allowed_groups, 'permission': permission}


class Section(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Name: {}".format(self.name)

    class Meta:
        ordering = ['name']


class Comment(models.Model):
    dish = models.ForeignKey('Dish', on_delete=models.CASCADE, related_name='dish', null=True)
    body = models.CharField(max_length=500)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='users_comment_authors', blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Dish: {} | Author: {}".format(self.dish, self.author)

    class Meta:
        ordering = ['created_on']


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    img = models.ImageField(upload_to='ingredients/', null=True)
    quantity = models.DecimalField(max_digits=6, default=10, decimal_places=1, null=True)
    unit = models.CharField(max_length=20)
    cost = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='users_ingredient_authors', blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Name: {} | Unit: {} | Quantity: {} | Cost: {}".format(self.name, self.unit, self.quantity, self.cost)

    class Meta:
        ordering = ['-created_on']


class Dish(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    img = models.ImageField(upload_to='dishes/', null=True)
    description = models.CharField(max_length=300, null=True)
    section = models.ForeignKey('Section', on_delete=models.CASCADE, related_name='dishes', null=True)
    ingredients = models.ManyToManyField('Ingredient', through='DishIngredients', through_fields=('dish', 'ingredient'),
                                         related_name='dishes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='users_dish_authors',
                               blank=True, null=True)
    notes = GenericRelation(NotedModel)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Name: {} | Section: {}".format(self.name, self.section)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Dish, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_on']


class DishIngredients(models.Model):
    dish = models.ForeignKey('Dish', on_delete=models.CASCADE, related_name='dish_ingredients', null=True)
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE, related_name='dish_ingredients', null=True)
    quantity = models.DecimalField(max_digits=6, decimal_places=1, null=True)

    def __str__(self):
        return "Dish: {} | Ingredient: {} | Quantity: {}".format(self.dish, self.ingredient, self.quantity)

    class Meta:
        ordering = ['dish__name']


class Order(models.Model):
    UNFULFILLED = 100
    FULFILLED = 200
    CANCELED = 300
    CLOSED = 400
    EXPIRED = 500
    STATUS = (
        (UNFULFILLED, 'unfulfilled'),
        (FULFILLED, 'fulfilled'),
        (CANCELED, 'canceled'),
        (CLOSED, 'closed'),
        (EXPIRED, 'expired'),
    )
    number = models.UUIDField(default=uuid.uuid1, editable=False)
    ingredients = models.ManyToManyField('Ingredient', through='OrderIngredients',
                                         through_fields=('order', 'ingredient'), related_name='orders')
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    status = models.IntegerField(
        choices=STATUS,
        default=UNFULFILLED,
    )
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='users_customers',
                                 blank=True, null=True)
    notes = GenericRelation(NotedModel)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Number: {} | Created: {} | Status: {} | Updated: {} | Cost: {}".format(self.number, self.created_on,
                                                                                       self.status,
                                                                                       self.updated_on, self.cost)

    class Meta:
        ordering = ['-created_on']


class OrderIngredients(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_ingredients', null=True)
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE, related_name='order_ingredients', null=True)
    quantity = models.DecimalField(max_digits=6, decimal_places=1)
    cost = models.DecimalField(max_digits=9, decimal_places=2, null=True)

    def __str__(self):
        return "Order: {} | Ingredient: {} | Quantity: {} | Cost: {}".format(self.order, self.ingredient, self.quantity,
                                                                             self.cost)


# SIGNALS:  ############################################################################################################
# Begin

# delete img with ingredient instance
@receiver(post_delete, sender=Ingredient)
def ingredient_img_delete(sender, instance, **kwargs):
    instance.img.delete(False)


# delete img with dish instance
@receiver(post_delete, sender=Dish)
def dish_img_delete(sender, instance, **kwargs):
    instance.img.delete(False)


# automatically generated Token to every rest api user
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

# End
########################################################################################################################
