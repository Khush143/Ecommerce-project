from django.db import models
from django.utils import timezone

# Create your models here.

class User(models.Model):
	fname=models.CharField(max_length=100)
	lname=models.CharField(max_length=100)
	email=models.EmailField()
	mobile=models.PositiveIntegerField()
	address=models.TextField()
	city=models.CharField(max_length=100)
	zipcode=models.PositiveIntegerField()
	password=models.CharField(max_length=100)
	profile_pic=models.ImageField(upload_to="profile_pic",default="")
	usertype=models.CharField(max_length=100,default="buyer")

	def __str__(self):
		return self.fname+" "+self.lname

class Product(models.Model):
	category=(
		('Laptop','Laptop'),
		('Camera','Camera'),
		('Accessories','Accessories'),
		)
	seller=models.ForeignKey(User,on_delete=models.CASCADE)
	product_category=models.CharField(max_length=100,choices=category)
	product_name=models.CharField(max_length=100)
	product_price=models.PositiveIntegerField()
	product_desc=models.TextField()
	product_image=models.ImageField(upload_to="product_image/")
	wishlist_status=models.BooleanField(default=False)
	cart_status=models.BooleanField(default=False)

	def __str__(self):
		return self.seller.fname+" - "+self.product_name
	
class Wishlist(models.Model):
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.user.fname+" - "+self.product.product_name

class Cart(models.Model):
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)
	product_price=models.PositiveIntegerField()
	product_qty=models.PositiveIntegerField()
	total_price=models.PositiveIntegerField()
	payment_status=models.BooleanField(default=False)

	def __str__(self):
		return self.user.fname+" - "+self.product.product_name