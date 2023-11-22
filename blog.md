# Start writing Django tests in 4 Minutes (with FactoryBoy and Faker)

Adding automated tests to your Django code benefits you by:

- reducing bugs
- making your code clearer
- allowing you to change your code without breaking the entire application.

This guide shows you how to write unit tests in Django, while using FactoryBoy and Faker to speed you.

## 0. Setting Up Your Django Project

- Install the packages and create your app `sim`

```bash
pip install django factory-boy faker
django-admin startproject my_restaurant
django-admin startapp sim
```

- Add your app to your project's settings, open the `settings.py` file in your project directory and add your app to the INSTALLED_APPS list.

## 1. Creating our Models

Our sim app will have 3 models: Dish, Ingredient, and Restaurant. 

- Add the below to `sim/models.py`

```python
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

```

- Create and run migrations for our models:

```
python manage.py makemigrations
python manage.py migrate
```

## 2. Write tests for our models


- Create a directory at `sim/tests`.
- Create an empty file called `init.py` file in `sim/tests` (we need this to detect that our folder contains tests)
- Create a file called `test_models.py` in `sim/tests` and add:

```python
from django.test import TestCase
from sim.models import Restaurant, Ingredient, Dish
from decimal import Decimal

class RestaurantTests(TestCase):

    def test_address(self):
        """
        Test the __str__ method of the restaurant model.
        """
        restaurant = Restaurant(name='Pizza Hut', address_first_line='123 Main Street', zip_code='203302', phone_number='123-456-7890')

        expected = "123 Main Street, 203302"

        self.assertEqual(expected, restaurant.address)


class DishTests(TestCase):
    def setUp(self):  # Runs before every test.
        self.restaurant = Restaurant.objects.create(name='Le Gavroche', address_first_line='123 Main Street', zip_code='203302', phone_number='123-456-7890')
        self.saffron = Ingredient.objects.create(name="saffron", unit_price=Decimal("20.30"))
        self.ginger = Ingredient.objects.create(name="ginger", unit_price=Decimal("0.90"))
        self.carrot = Ingredient.objects.create(name="carrot", unit_price=Decimal("0.20"))
        self.pilchard = Ingredient.objects.create(name="pilchard", unit_price=Decimal("1.20"))
        self.yeast = Ingredient.objects.create(name="yeast", unit_price=Decimal("0.12"))
        self.xantham_gum = Ingredient.objects.create(name="xantham_gum", unit_price=Decimal("0.06"))

    def test_total_ingredient_cost(self):
        dish = Dish.objects.create(name='Spiced Carrot Soup', price=Decimal("15.00"), restaurant=self.restaurant)
        dish.ingredients.add(self.carrot, self.ginger)

        expected_cost = self.carrot.unit_price + self.ginger.unit_price

        self.assertEqual(dish.total_ingredient_cost(dish.ingredients.all()), expected_cost)

    def test_unit_margin(self):
        dish = Dish.objects.create(name='Gourmet Pilchard Pizza', price=Decimal("25.00"), restaurant=self.restaurant)
        dish.ingredients.add(self.pilchard, self.yeast, self.xantham_gum)
        total_cost = self.pilchard.unit_price + self.yeast.unit_price + self.xantham_gum.unit_price

        expected_margin = dish.price - total_cost

        self.assertEqual(dish.unit_margin(), expected_margin)

    def test_unit_margin_with_prefetch(self):
        dish = Dish.objects.create(name='Exotic Saffron Dish', price=Decimal("50.00"), restaurant=self.restaurant)
        dish.ingredients.add(self.saffron, self.ginger)
        prefetched_dishes = Dish.objects.prefetch_related('ingredients').get(id=dish.id)

        expected_margin = dish.price - (self.saffron.unit_price + self.ginger.unit_price)

        self.assertEqual(prefetched_dishes.unit_margin(prefetched_ingredients=prefetched_dishes.ingredients.all()), expected_margin)

```

We can now run our first test scenarios for our new models with the command:

```
python manage.py test sim.tests
```

If they don’t pass, then debug your code. Else, congrats 🎉  

## 3. Add FactoryBoy and Faker to our Django tests

FactoryBoy allows you to define factories for your models, which avoids repeating code when creating python objects during your tests.
Faker helps generate realistic-looking fake data.

They are useful for a) making your tests easier to read and b) faster to write as your codebase grows. Let’s add them both.

- Create a file called `factories.py` at `sim/factories.py` and add

```python

import factory
from faker import Faker
from .models import Restaurant, Ingredient, Dish
from decimal import Decimal

fake = Faker()

class RestaurantFactory(factory.Factory):
    class Meta:
        model = Restaurant

    name = factory.Sequence(lambda n: f'Restaurant {n}')
    address_first_line = fake.address()
    phone_number = fake.phone_number()

class DishFactory(factory.Factory):
    class Meta:
        model = Dish

    name = factory.Sequence(lambda n: f'Dish {n}')
    price = Decimal(fake.random_number(2))
    restaurant = Restuarant

class IngredientFactory(factory.Factory):
    class Meta:
        model = Ingredient

    name = factory.Sequence(lambda n: f'Ingredient {n}')
		unit_price = Decimal(fake.random_number(2))

```

### Update our existing unit tests to use FactoryBoy and Faker

Now we can improve our current (and future) tests. Replace our existing model tests (`sim/test_models.py` ) with the below:

```python
from django.test import TestCase
from sim.factories import RestaurantFactory, DishFactory, IngredientFactory
from sim.models import Restaurant, Ingredient, Dish
from decimal import Decimal

class RestaurantTests(TestCase):

    def test_address(self):
        """
        Test the address method of the restaurant model.
        """
        restaurant = RestaurantFactory.create()
        expected = f"{restaurant.address_first_line}, {restaurant.zip_code}"
        self.assertEqual(expected, restaurant.address)

class DishTests(TestCase):
    def setUp(self):
        self.restaurant = RestaurantFactory.create()
        self.restaurant.save(using='default')
        self.saffron = IngredientFactory.create(name="saffron", unit_price=Decimal("20.30"))
        self.saffron.save(using='default')
        self.ginger = IngredientFactory.create(name="ginger", unit_price=Decimal("0.90"))
        self.ginger.save(using='default')

        self.carrot = IngredientFactory.create(name="carrot", unit_price=Decimal("0.20"))
        self.carrot.save(using='default')

        self.pilchard = IngredientFactory.create(name="pilchard", unit_price=Decimal("1.20"))
        self.pilchard.save(using='default')
        self.yeast = IngredientFactory.create(name="yeast", unit_price=Decimal("0.12"))
        self.yeast.save(using='default')

        self.xantham_gum = IngredientFactory.create(name="xantham gum", unit_price=Decimal("0.06"))
        self.xantham_gum.save(using='default')

    def test_total_ingredient_cost(self):
        dish = DishFactory.create(restaurant=self.restaurant)
        dish.save(using='default')
        dish.ingredients.add(self.carrot, self.ginger)
        expected_cost = self.carrot.unit_price + self.ginger.unit_price

        self.assertEqual(dish.total_ingredient_cost(dish.ingredients.all()), expected_cost)


    def test_unit_margin(self):
        dish = DishFactory.build(restaurant=self.restaurant)
        dish.save(using='default')

        dish.ingredients.add(self.pilchard, self.yeast, self.xantham_gum)
        total_cost = self.pilchard.unit_price + self.yeast.unit_price + self.xantham_gum.unit_price

        expected_margin = dish.price - total_cost

        self.assertEqual(dish.unit_margin(), expected_margin)

    def test_unit_margin_with_prefetch(self):
        dish = DishFactory.create(restaurant=self.restaurant)
        dish.save(using='default')

        dish.ingredients.add(self.saffron, self.ginger)
        prefetched_dishes = Dish.objects.prefetch_related('ingredients').get(id=dish.id)

        expected_margin = dish.price - (self.saffron.unit_price + self.ginger.unit_price)

        self.assertEqual(prefetched_dishes.unit_margin(prefetched_ingredients=prefetched_dishes.ingredients.all()), expected_margin)

```

- Run the tests again to check that they all pass. Debug your code if any failures.

## 4. Create our views (which we’ll then test)

Let's move on to views. We'll create basic views for listing, creating, updating, and deleting instances of the Restaurant, Ingredient, and Dish. 

- Create your `views.py` at `sim/views.py` and add:

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import Restaurant
from django import forms


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'address_first_line', 'zip_code', 'phone_number']


def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'restaurant_list.html', {'restaurants': restaurants})


def restaurant_create(request):
    form = RestaurantForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('sim:restaurant_list')
    return render(request, 'restaurant_form.html', {'form': form})


def restaurant_update(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    form = RestaurantForm(request.POST or None, instance=restaurant)
    if form.is_valid():
        form.save()
        return redirect('sim:restaurant_list')
    return render(request, 'restaurant_form.html', {'form': form})


def restaurant_delete(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    if request.method == 'POST':
        restaurant.delete()
        return redirect('sim:restaurant_list')
    return render(request, 'restaurant_confirm_delete.html', {'restaurant': restaurant})


```

### Add our urls

`restaurant/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('restaurants/new/', views.restaurant_create, name='restaurant_create'),
    path('restaurants/<int:pk>/edit/', views.restaurant_update, name='restaurant_edit'),
    path('restaurants/<int:pk>/delete/', views.restaurant_delete, name='restaurant_delete'),
]
```

### Add our html templates

- Create a folder called templates
- Add a file called `restaurant_list.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Restaurant List</title>
</head>
<body>
    <h1>Restaurant List</h1>
    <ul>
        {% for restaurant in restaurants %}
            <li>{{ restaurant.name }} - {{ restaurant.address }} - {{ restaurant.phone_number }}</li>
        {% endfor %}
    </ul>
</body>
</html>

```

- Add a file called `restaurant_form.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if form.instance.pk %}Edit{% else %}Create{% endif %} Restaurant</title>
</head>
<body>
    <h1>{% if form.instance.pk %}Edit{% else %}Create{% endif %} Restaurant</h1>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Save</button>
    </form>
</body>
</html>

```

- Add a file called `restaurant_confirm_delete.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Delete Restaurant</title>
</head>
<body>
    <h1>Delete Restaurant</h1>
    <p>Are you sure you want to delete the restaurant "{{ object }}"?</p>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        <button type="submit">Confirm Delete</button>
    </form>
</body>
</html>

```

## Add unit tests for our Django views

In our `sim/tests` folder, add a new file called `test_views.py` and insert the below:

```python
from django.test import TestCase
from django.urls import reverse
from sim.factories import RestaurantFactory, IngredientFactory, DishFactory
from sim.models import Restaurant


class RestaurantViewsTest(TestCase):

    def test_restaurant_list_view(self):
        response = self.client.get(reverse('sim:restaurant_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'restaurant_list.html')

    def test_restaurant_create_view(self):
        response = self.client.get(reverse('sim:restaurant_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'restaurant_form.html')

        data = {'name': 'New Restaurant', 'address': '123 New Street', 'phone_number': '987-654-3210'}
        response = self.client.post(reverse('sim:restaurant_create'), data)

        self.assertEqual(response.status_code, 200)  # Redirect after successful form submission


    def test_restaurant_update_view(self):
        restaurant = RestaurantFactory()
        restaurant.save()
        response = self.client.get(reverse('sim:restaurant_edit', args=[restaurant.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'restaurant_form.html')

        data = {'name': 'Updated Restaurant', 'address': '456 Updated Street', 'phone_number': '111-222-3333'}
        response = self.client.post(reverse('sim:restaurant_edit', args=[restaurant.pk]), data)

        self.assertEqual(response.status_code, 200)  # Redirect after successful form submission
        


    def test_restaurant_delete_view(self):
        restaurant = RestaurantFactory()
        restaurant.save()
        response = self.client.get(reverse('sim:restaurant_delete', args=[restaurant.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'restaurant_confirm_delete.html')
 
        response = self.client.post(reverse('sim:restaurant_delete', args=[restaurant.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion


```

### Run the tests:

```bash
python manage.py test sim.tests
```

Happy coding and bon appétit 🍽️👨‍🍳🎉