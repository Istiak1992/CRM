from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import Group
from django.forms import inlineformset_factory
from .models import *
from .form import OrderForm
from .filters import OrderFilter
from django.contrib.auth.forms import UserCreationForm
from .form import CreateUserForm, CustomerForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, admin_only



def registerPage(request):
	
	form = CreateUserForm()

	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			
			

			messages.success(request,'Account has been successfully created for '+ username)
			return redirect('login')

	context = {'form': form}
	return render(request, 'accounts/register.html',context)
@unauthenticated_user
def loginPage(request):

	username = request.POST.get('username')
	password = request.POST.get('password')

	user = authenticate(request, username = username, password = password)
	if user is not None:
		login(request, user)
		return redirect('crm-home')
	
	else:
		messages.info(request,'')
	
		
	return render(request, 'accounts/login.html')

def logoutPage(request):
	logout(request)
	return redirect('login')

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):

	orders = request.user.customer.order_set.all()
	total_order = orders.count()
	delivered_order = orders.filter(status = 'Delivered').count()
	pending_order = orders.filter(status = 'Pending').count()

	context = {'orders':orders, 'total_order':total_order, 
	'delivered_order':delivered_order, 'pending_order':pending_order}

	return render(request,'accounts/user_page.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
	customer = request.user.customer
	form = CustomerForm(instance=customer)
	if request.method=='POST':
		form = CustomerForm(request.POST, request.FILES,instance=customer)
		if form.is_valid():
			form.save()
	context = {'form':form}
	return render(request, 'accounts/account_settings.html',context)

@login_required(login_url='login')
@admin_only
def home(request):
	customers = Customer.objects.all()
	products = Product.objects.all()
	orders = Order.objects.all()
	total_order = orders.count()
	delivered_order = orders.filter(status = 'Delivered').count()
	pending_order = orders.filter(status = 'Pending').count()
	

	context = {'customers':customers, 'products': products, 
	'orders': orders, 'total_order': total_order,
	'delivered_order': delivered_order,
	'pending_order': pending_order}
	return render(request,'accounts/dashbord.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def product(request):
	products = Product.objects.all()
	context = {'products':products}
	return render(request,'accounts/product.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk_test):
	customer = Customer.objects.get(id=pk_test)
	order = customer.order_set.all()
	total_order = order.count()
	myFilter = OrderFilter(request.GET, queryset=order)
	order = myFilter.qs
	context = {'order': order, 'customer': customer, 
	'total_order': total_order,'myFilter':myFilter}
	return render(request,'accounts/customer.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def create_order(request, pk):
	OrderFormSet = inlineformset_factory(Customer, Order, fields=('product','status'),extra=8)
	customer = Customer.objects.get(id=pk)
	formset = OrderFormSet(queryset=Order.objects.none(),instance=customer)
	#form = OrderForm(initial={'customer':customer})
	if request.method == 'POST':
		#form = OrderForm(request.POST)
		formset = OrderFormSet(request.POST,instance=customer)
		if formset.is_valid():
			formset.save()
			return redirect('/')
	
	context = {'formset':formset}

	return render(request,'accounts/create_order.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
	order = Order.objects.get(id=pk)
	form = OrderForm(instance=order)
	if request.method == 'POST':
		form = OrderForm(request.POST, instance=order)
		if form.is_valid():
			form.save()
			return redirect('/')
	
	context = {'form':form}

	return render(request,'accounts/create_order.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
	order = Order.objects.get(id=pk)
	if request.method == "POST":
		order.delete()
		return redirect('/')
	context = {'item': order}
	return render(request,'accounts/delete.html', context)
