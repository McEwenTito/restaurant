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
