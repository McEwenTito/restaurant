from decimal import Decimal
from typing import Iterable
from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address_first_line = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)

    def __str__(self):
        return self.name
        
    @property
    def address(self) -> str:
        return f"{self.address_first_line}, {self.zip_code}"


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    

    def __str__(self):
        return self.name


class Dish(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    ingredients = models.ManyToManyField(Ingredient)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def unit_margin(self, prefetched_ingredients: Iterable[Ingredient] = None) -> Decimal:
        """
        The profit margin per dish.
        We add the option to prefetch ingredients to reduce the number of database queries where we have many ingredients.
        """
        ingredients = prefetched_ingredients or self.ingredients.all()
        return self.price - self.total_ingredient_cost(ingredients)

    def total_ingredient_cost(self, ingredients: Iterable[Ingredient]) -> Decimal:
        return sum(ingredient.unit_price for ingredient in ingredients)


