from django.shortcuts import render, redirect
from accounts.forms import loginForm, GuestForm
from billing.models import BillingProfile
from accounts.models import GuestEmail
# Create your views here.
from .models import Cart
from products.models import Product
from orders.models import Order
from addresses.forms import AddressForm
from addresses.models import Address





def cart_home(request):
	cart_obj, new_obj = Cart.objects.new_or_get(request)
	return render(request, "carts/home.html", {"cart":cart_obj})


def cart_update(request):
	print(request.POST)
	product_id = request.POST.get('product')
	print(product_id)
	if product_id is not None:
		try:
			product_obj = Product.objects.get(id=product_id)
		except Product.DoesNotExist:
			print("Show message to user, Product is gone!")
			return redirect("cart:home")
	cart_obj, new_obj = Cart.objects.new_or_get(request)
	if product_obj in cart_obj.products.all():
		cart_obj.products.remove(product_obj)
	else:
		cart_obj.products.add(product_obj)
	request.session['cart_items'] = cart_obj.products.count()
	return redirect("cart:home")


def checkout_home(request):
	cart_obj, cart_created = Cart.objects.new_or_get(request)
	order_obj = None 
	if cart_created or cart_obj.products.count() == 0:
		return redirect("cart:home")

	user 					= request.user  
	billing_profile 		= None 
	login_form 				= loginForm() 
	guest_form 				= GuestForm()
	address_form 			= AddressForm()
	billing_address_id 		= request.session.get('billing_address_id', None)
	shipping_address_id 	= request.session.get('shipping_address_id', None)
	guest_email_id 			= request.session.get('guest_email_id')

	billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
	address_qs = None
	if billing_profile is not None:
		address_qs = Address.objects.filter(billing_profile=billing_profile)
		# shipping_address_qs = address_qs.filter(address_type = 'shipping')
		# billing_address_qs = address_qs.filter(address_type = 'billing')
		order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)
		if shipping_address_id:
			order_obj.shipping_address = Address.objects.get(id = shipping_address_id)
			del request.session["shipping_address_id"]
		if billing_address_id:
			order_obj.billing_address = Address.objects.get(id = billing_address_id)
			del request.session["billing_address_id"]
		if billing_address_id or shipping_address_id:
			order_obj.save()

	if request.method == 'POST':
		"some check that the order is done"
		is_done = order_obj.check_done()
		if is_done:
			order_obj.mark_paid()
			request.session['cart_items'] = 0
			del request.session['cart_id']
			return redirect("cart:success?")
		
	context = {
		"object":order_obj,
		"billing_profile":billing_profile,
		"login_form": login_form,
		"guest_form":guest_form,
		"address_form":address_form,
		"address_qs": address_qs,
	}
	return render(request, "carts/checkout.html", context)

def checkout_done_view(request):
	return render(request, "carts/checkout.html", context)

