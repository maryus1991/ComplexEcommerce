from django.views.generic import ListView, UpdateView, CreateView, RedirectView, View
from django.shortcuts import get_object_or_404, redirect, reverse, render
from stores.forms import AddProductForm
from product.models import Product, ProductCategory, ProductBrand

