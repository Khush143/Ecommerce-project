from django.shortcuts import render,redirect
from .models import User,Product,Wishlist,Cart
from django.conf import settings
from django.core.mail import send_mail
import random
import stripe
from django.conf import settings
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone

stripe.api_key = settings.STRIPE_PRIVATE_KEY
YOUR_DOMAIN = 'http://localhost:8000'

# Create your views here.
def index(request):
	try:
		user=User.objects.get(email=request.session['email'])
		if user.usertype=="buyer":
			products=Product.objects.all()
			carts=Cart.objects.filter(user=user,payment_status=False)
			return render(request,'index.html',{'products':products,'carts':carts})
		else:
			return render(request,'seller-index.html')
	except:
		products=Product.objects.all()
		return render(request,'index.html',{'products':products})

def seller_index(request):
	return render(request,'seller-index.html')

def signup(request):
	if request.method=="POST":
		try:
			User.objects.get(email=request.POST['email'])
			msg="Email Already Registered"
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
					    fname=request.POST['fname'],
						lname=request.POST['lname'],
						email=request.POST['email'],
						mobile=request.POST['mobile'],
						address=request.POST['address'],
						city=request.POST['city'],
						zipcode=request.POST['zipcode'],
						password=request.POST['password'],
						profile_pic=request.FILES['profile_pic'],
						usertype=request.POST['usertype']
					)
				msg="User Sign Up Successfully"
				return render(request,'signin.html',{'msg':msg})
			else:
				msg="Password & Confirm Password Does Not Matched"
				return render(request,'signup.html',{'msg':msg})
	else:
	    return render(request,'signup.html')
	
	# Function to Validate Email using AJAX

def validate_signup(request):
	email=request.GET.get('email')
	data={
		'is_taken':User.objects.filter(email__iexact=email).exists()
	}
	return JsonResponse(data)

def validate_mobile(request):
	mobile=request.GET.get('mobile')
	data={
		'is_taken':User.objects.filter(mobile__iexact=mobile).exists()
	}
	return JsonResponse(data)
	
def signin(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			if user.password==request.POST['password']:
				if user.usertype=="buyer":	
					request.session['email']=user.email
					request.session['fname']=user.fname
					request.session['profile_pic']=user.profile_pic.url
					wishlists=Wishlist.objects.filter(user=user)
					request.session['wishlist_count']=len(wishlists)
					carts=Cart.objects.filter(user=user,payment_status=False)
					request.session['carts_count']=len(carts)
					return redirect('index')
				else:
					request.session['email']=user.email
					request.session['fname']=user.fname
					request.session['profile_pic']=user.profile_pic.url
					return redirect('seller-index')
			else:
				msg="Incorrect Password"
				return render(request,'signin.html',{'msg':msg})
		except:
			msg="Email Not Registered"
			return render(request,'signup.html',{'msg':msg})
	else:
		return render(request,'signin.html')

def signout(request):
	try:
		del request.session['email']
		del request.session['fname']
		del request.session['wishlist_count']
		return render(request,'signin.html')
	except:
		return render(request,'signin.html')


def profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.mobile=request.POST['mobile']
		user.address=request.POST['address']
		user.city=request.POST['city']
		user.zipcode=request.POST['zipcode']
		try:
			user.profile_pic=request.FILES['profile_pic']
		except:
			pass
		user.save()
		request.session['profile_pic']=user.profile_pic.url
		msg="Profile Update Successfully"
		if user.usertype=='buyer':
			carts=Cart.objects.filter(user=user,payment_status=False)
			return render(request,'profile.html',{'user':user,'msg':msg,'carts':carts})
		else:
			return render(request,'seller-profile.html',{'user':user,'msg':msg,})

	else:
		if user.usertype=="buyer":
			carts=Cart.objects.filter(user=user,payment_status=False)
			return render(request,'profile.html',{'user':user,'carts':carts})
		else:
			return render(request,'seller-profile.html',{'user':user})


def change_password(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password=request.POST['new_password']
				user.save()
				return redirect('signout')
			else:
				if user.usertype=='buyer':
					carts=Cart.objects.filter(user=user,payment_status=False)
					msg="New Password & Confirm New Password Does Not Matched"
					return render(request,'change-password.html',{'msg':msg,'carts':carts})
				else:
					msg="New Password & Confirm New Password Does Not Matched"
					return render(request,'seller-change-password.html',{'msg':msg})

		else:
			if user.usertype=='buyer':
				carts=Cart.objects.filter(user=user)
				msg="Old Password Does Not Matched"
				return render(request,'change-password.html',{'msg':msg,'carts':carts})
			else:
				msg="Old Password Does Not Matched"
				return render(request,'seller-change-password.html',{'msg':msg})
	else:
		if user.usertype=='buyer':
			return render(request,'change-password.html')
		else:
			return render(request,'seller-change-password.html')
		
def validate_change_password(request):
	old_password=request.GET.get('old_password')
	data={
		'is_taken':User.objects.filter(password__iexact='old_password').exists()
	}
	return JsonResponse(data)

def forgot_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			otp=random.randint(1000,9999)
			subject = 'OTP For Forgot Password'
			message = 'Hello '+user.fname+", Your OTP For Forgot Password Is "+str(otp)
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [user.email, ]
			send_mail( subject, message, email_from, recipient_list )
			return render(request,'otp.html',{'email':user.email,'otp':otp})
		except:
			msg="Email Not Registered"
			return render(request,'forgot-password.html',{'msg':msg})
	else:
		return render(request,'forgot-password.html')
	
def verify_otp(request):
	email=request.POST['email']  
	otp=request.POST['otp']
	uotp=request.POST['uotp']

	if otp==uotp:
		return render(request,'new-password.html',{'email':email})
	else:
		msg="Invalid OTP"
		return render(request,'otp.html',{'email':email,'otp':otp,'msg':msg})
	
def new_password(request):
	email=request.POST['email']
	np=request.POST['new_password']
	cnp=request.POST['cnew_password']

	if np==cnp:
		user=User.objects.get(email=email)
		user.password=np
		user.save()
		return redirect('signin')
	else:
		msg="New Password & Confirm New Password Does Not Matched"
		return render(request,'new-password.html',{'email':email,'msg':msg})

def seller_add_product(request):
	seller=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		Product.objects.create(
				seller=seller,
				product_category=request.POST['product_category'],
				product_name=request.POST['product_name'],
				product_price=request.POST['product_price'],
				product_desc=request.POST['product_desc'],
				product_image=request.FILES['product_image'],
			)
		msg="Product Added Successfully"
		return render(request,'seller-add-product.html',{'msg':msg})
	else:
		return render(request,'seller-add-product.html')
	
def validate_product_name(request):
	product_name=request.GET.get('product_name')
	data={
		'is_taken':Product.objects.filter(product_name__iexact=product_name).exists()
	}
	return JsonResponse(data)

def seller_view_product(request):
	user=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=user)
	return render(request,'seller-view-product.html',{'products':products})

def seller_product_details(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'seller-product-details.html',{'product':product})

def seller_edit_product(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=="POST":
		product.product_category=request.POST['product_category']
		product.product_name=request.POST['product_name']
		product.product_price=request.POST['product_price']
		product.product_desc=request.POST['product_desc']
		product.product_stock=request.POST['product_stock']
		try:
			product.product_image=request.FILES['product_image']
		except:
			pass
		product.save()
		return redirect('seller-view-product')
	else:
		return render(request,'seller-edit-product.html',{'product':product})

def seller_delete_product(request,pk):
	product=Product.objects.get(pk=pk)
	product.delete()
	return redirect('seller-view-product')

def laptops(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	products=Product.objects.filter(product_category="Laptop")
	return render(request,'index.html',{'products':products,'carts':carts})

def Accessories(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	products=Product.objects.filter(product_category="Accessories")
	return render(request,'index.html',{'products':products,'carts':carts})

def camera(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	products=Product.objects.filter(product_category="Camera")
	return render(request,'index.html',{'products':products,'carts':carts})

def product_details(request,pk):
	wishlist_flag=False
	cart_flag=False
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)

	try:
		Wishlist.object.get(user=user,product=product)
		wishlist_flag=True
	except:
		pass
	try:
		Cart.object.get(user=user,product=product)
		cart_flag=True
	except:
		pass
	return render(request,'product-details.html',{'product':product,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag,'carts':carts})

def add_to_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	product.wishlist_status=True
	product.save()
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(product=product,user=user)
	return redirect('wishlist')

def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'wishlist.html',{'wishlists':wishlists,'carts':carts})

def remove_from_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	product.wishlist_status=False
	product.save()
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.get(user=user,product=product)
	wishlist.delete()
	return redirect('wishlist')

def cart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	request.session['cart_count']=len(carts)
	for i in carts:
		net_price=net_price+i.total_price
	return render(request,'cart.html',{'carts':carts,'net_price':net_price})

def add_to_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(
		product=product,
		user=user,
		product_price=product.product_price,
		product_qty=1,
		total_price=product.product_price,
		payment_status=False
		)
	product.cart_status=True
	product.save()
	return redirect('cart')

def remove_from_cart(request,pk):
	product=Product.objects.get(pk=pk)
	product.cart_status=False
	product.save()
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,product=product)
	cart.delete()
	return redirect('cart')

def change_qty(request):
	cid=int(request.POST['cid'])
	product_qty=int(request.POST['product_qty'])
	cart=Cart.objects.get(pk=cid)
	cart.product_qty=product_qty
	cart.total_price=cart.product_price*product_qty
	cart.save()
	return redirect('cart')

def checkout(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	net_price=0
	for i in carts:
		net_price=net_price+i.total_price
	return render(request,'checkout.html',{'user':user,'carts':carts,'net_price':net_price})

@csrf_exempt
def create_checkout_session(request):
	amount = int(json.load(request)['post_data'])
	final_amount=amount*100
	
	session = stripe.checkout.Session.create(
		payment_method_types=['card'],
		line_items=[{
			'price_data': {
				'currency': 'inr',
				'product_data': {
					'name': 'Checkout Session Data',
					},
				'unit_amount': final_amount,
				},
			'quantity': 1,
			}],
		mode='payment',
		success_url=YOUR_DOMAIN + '/success.html',
		cancel_url=YOUR_DOMAIN + '/cancel.html',)
	return JsonResponse({'id': session.id})

def success(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	for i in carts:
		i.payment_status=True
		i.save()
		product=Product.objects.get(id=i.product.id)
		product.cart_status=False
		product.save()
		
	carts=Cart.objects.filter(user=user,payment_status=False)
	request.session['cart_count']=len(carts)
	return render(request,'success.html')

def cancel(request):
	return render(request,'cancel.html')

def myorder(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=True)
	return render(request,'myorder.html',{'carts':carts})

def seller_order(request):
	seller=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(payment_status=True)
	orders=[]
	for i in carts:
		if i.product.seller==seller:
			orders.append(i)
	print(orders)
	return render(request,'seller-order.html',{'orders':orders})