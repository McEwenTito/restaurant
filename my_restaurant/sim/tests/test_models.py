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
