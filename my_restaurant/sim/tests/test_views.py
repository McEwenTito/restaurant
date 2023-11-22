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

