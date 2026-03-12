import requests
from django.shortcuts import render


def external_products(request):
    url = "https://fakestoreapi.com/products"

    response = requests.get(url)
    products = response.json()

    return render(request, "products/external_products.html", {
        "products": products
    })
