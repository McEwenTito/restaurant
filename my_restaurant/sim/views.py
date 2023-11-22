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
        return redirect('restaurant_list')
    return render(request, 'restaurant_form.html', {'form': form})


def restaurant_update(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    form = RestaurantForm(request.POST or None, instance=restaurant)
    if form.is_valid():
        form.save()
        return redirect('restaurant_list')
    return render(request, 'restaurant_form.html', {'form': form})


def restaurant_delete(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    if request.method == 'POST':
        restaurant.delete()
        return redirect('sim:restaurant_list')
    return render(request, 'restaurant_confirm_delete.html', {'restaurant': restaurant})
