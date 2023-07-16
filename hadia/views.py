from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime
# from django.views.decorators.csrf import csrf_exempt
# from .models import User
# from django.shortcuts import redirect

# Create your views here.


# def index(request):
#   if request.method == 'GET':
#      return render(request, 'index.html')


# @csrf_exempt
# def login(request):
#   if request.method == 'GET':
#      return render(request, 'login.html')
# if request.method == 'POST':
#    username1 = request.POST.get('username')
#   email1 = request.POST.get('email')
#  password1 = request.POST.get('password')

#        user = User.objects.filter(username=username1)
#       if user.email == email1 and user.password == password1:
#          return render(request, 'good.html')

#     else:
#        return render(request, 'login.html')


# def signup(request):
#   if request.method == 'GET':
#      return render(request, 'signup.html')
# if request.method == 'POST':
#    username1 = request.POST.get('username')
#   email1 = request.POST.get('email')
#  password1 = request.POST.get('password')

# user = User(username=username1, email=email1, password=password1)
# user.save()
# return redirect('signup')


def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'hadia/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'hadia/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()

        cartItems = order.get_cart_items

    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'hadia/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action: ', action)
    print('productId: ', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        total = data(['form']['total'])
        order.transaction_id = transaction_id

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )

    else:
        print('User is not logged in...')
    return JsonResponse('Payment complete', safe=False)
