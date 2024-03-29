from django.shortcuts import render, redirect
from .forms import ProfileForm, LoginForm
from django.core.mail import send_mail
from core.utils.pass_generator import generator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Order, Profile, Diler, Provider, Quantity, Region, Shape, Implement, Review
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from .tasks import *

logger = logging.getLogger('django')


#LOGIN REGISTER LOGOUT
#============================================================================



def login_view(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            cd = login_form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user.is_active:
                if 'remember' not in request.POST:
                    request.session.set_expiry(0)
                    request.session.modified = True
                login(request, user)
                return redirect(index)
            else:
                return render(request, 'auth/disable.html')
    else:
        if request.user.is_authenticated:
            return redirect(index)
        login_form = LoginForm()
    return render(request, 'auth/login.html', {'form': login_form})



def signup(request):
    if request.method == 'POST':
        password = generator(8)
        profile_form = ProfileForm(request.POST)
        if profile_form.is_valid():
            cd = profile_form.cleaned_data
            new_user = User()
            new_user.username = cd['email']
            new_user.email = cd['email']
            new_user.set_password(password)
            new_user.save()
            spec = 'Дилер' if request.POST['spec']=='D' else 'Поставщик окон'
            p = Profile.objects.create(user=new_user,fio=cd['fio'],spec=request.POST['spec'],email=cd['email'],phone_number=cd['phone'])
            if request.POST['spec']=='D':
                Diler.objects.create(user=p)
            else:
                Provider.objects.create(user=p)

            msg = 'Вы зарегистрировались как ' + spec + '\n' + 'Ваш login: ' + request.POST['email'] + '\n' + 'Ваш password: ' + password
            try:
                send_mail('Регистрация в todotodo', msg, settings.EMAIL_HOST_USER, [request.POST['email']], fail_silently=False)
                newuser.delay(f'В сервис зарегистрировался новый {spec.lower()}: {cd["fio"]}, подробнее в дилеры-окон.рф')
            except:
                new_user.delete()
                return render(request, 'auth/lose_register.html')
            return render(request, 'auth/register_success.html')
    else:
        profile_form = ProfileForm()

    return render(request, 'auth/register.html', {'form': profile_form})

def logout_view(request):
    logout(request)
    return redirect(login_view)


#INDEX
#============================================================================

@login_required(login_url='/login/')
def index(request):
    logger.info('test')
    if request.user.is_superuser:
        logout(request)
        return redirect(login_view)
    if request.user.profile.spec == 'D':
        return redirect(diler_orders)
    else:
        return redirect(provider_orders)



#DILER
#============================================================================

@login_required(login_url='/login/')
def diler_orders(request):
    if request.user.profile.spec == 'D':
        orders = request.user.profile.diler.order_set.all().order_by('-id')
        return render(request, 'diler/orders-diler.html', {'orders': orders})
    else:
        return HttpResponseForbidden()



@login_required(login_url='/login/')
def diler_order(request, id):
    if request.user.profile.spec == 'D':
        order = request.user.profile.diler.order_set.get(id=id)
        return render(request, 'diler/order-diler.html', {'order': order})
    else:
        return HttpResponseForbidden()

    


@login_required(login_url='/login/')
def diler_profile_save(request):
    if request.method == 'POST':
        user = request.user
        user.profile.fio = request.POST['fio']
        user.profile.phone_number = request.POST['phone']
        user.profile.email = request.POST['email']
        user.profile.save()
        user.profile.diler.organization = request.POST['company']
        user.profile.diler.warehouse_address = request.POST['warehouse_address']
        try:
            user.profile.diler.logo = request.FILES['logo']
        except KeyError:
            pass
        user.profile.diler.region_id = request.POST['region']
        user.profile.diler.save()
        return redirect(diler_orders)
    regions = Region.objects.all()
    return render(request, 'diler/diler-profile.html', {'regions': regions})




@login_required(login_url='/login/')
def order_save(request):
    if request.method == 'GET':
        shapes = Shape.objects.all()
        implements = Implement.objects.all()
        return render(request, 'diler/new-order.html', {'shapes': shapes, 'implements': implements})
    else:
        user = request.user
        order = user.profile.diler.order_set.create(shape_id=request.POST['shape'],implement_id=request.POST['implement'],address=request.POST['address'], type_pay=request.POST['type_pay'], type_delivery=request.POST['type_delivery'], amount_window=int(request.POST['amount']), price=request.POST['price'], comment=request.POST['comment'])
        order.file = request.FILES['upload']
        order.save()
        sendmass.delay(order.id, True)
        return redirect(diler_orders)




#PROVIDER
#============================================================================


@login_required(login_url='/login/')
def provider_profile(request):
    if request.user.profile.spec == 'P':
        if request.method == 'POST':
            p = request.user.profile.provider
            p.user = request.user.profile
            p.company = request.POST['company']
            p.legal_entity = request.POST['legal_entity']
            p.product_address = request.POST['product_address']
            p.contact_entity = request.POST['contact_entity']
            p.contact_phone = request.POST['contact_phone']
            p.service_entity = request.POST['service_entity']
            p.service_phone = request.POST['service_phone']
            p.service_email = request.POST['service_email']
            
            try: 
                p.logo = request.FILES['logo']
            except KeyError:
                pass
            p.description = request.POST['description']
            p.save()
            try:
                p.shapes.clear()
                for i in request.POST.getlist('shapes'):
                    p.shapes.add(Shape.objects.get(id=i))
            except KeyError:
                p.shapes.clear()
            try:
                p.implements.clear()   
                for i in request.POST.getlist('implements'):
                    p.implements.add(Implement.objects.get(id=i))  
            except KeyError:
                p.implements.clear() 
            try:
                p.regions.clear()
                for i in request.POST.getlist('regions'):
                    p.regions.add(Region.objects.get(id=i))
            except KeyError:
                p.regions.clear()

            return redirect(index)
        
        shapes = Shape.objects.all()
        implements = Implement.objects.all()
        regions = Region.objects.all()
        return render(request, 'provider/profile-company.html', {'shapes': shapes, 'implements': implements, 'regions': regions})
    

    else:
        return HttpResponseForbidden()
        
            


    

@login_required(login_url='/login/')
def provider_balance(request):
    return render(request, 'provider/balance-company.html', {'prices': Price.objects.all().order_by('price')})


@login_required(login_url='/login/')
def provider_response(request, id):
    if request.user.profile.spec == 'P':
        if request.method == 'GET':
            return render(request, 'provider/call-out.html', {'order': Order.objects.get(id=id)})
        else:
            q = Quantity()
            q.order_id = id
            q.author  = request.user.profile.provider
            q.date = request.POST['date']
            q.shape_id = request.POST['shape']
            q.implement_id = request.POST['implement']
            q.price = request.POST['price']
            q.file = request.FILES['upload']
            q.comment = request.POST['comment']
            q.save()
            return redirect(provider_quantity)
    else:
        return HttpResponseForbidden()

@login_required(login_url='/login/')
def provider_work(request):
    return render(request, 'provider/processed-company.html', {'quantitys': request.user.profile.provider.quantity_set.all()})

@login_required(login_url='/login/')
def provider_archive(request):
    return render(request, 'provider/archive-company.html', {'quantitys': request.user.profile.provider.quantity_set.all()})


@login_required(login_url='/login/')
def provider_orders(request):
    if request.user.profile.spec == 'P':
        orders = []
        for region in request.user.profile.provider.regions.all():
            for diler in region.diler_set.all():
                orders += diler.order_set.all()
        orders = sorted(orders, key=lambda item: item.id, reverse=True)
        return render(request, 'provider/orders-company.html', {'orders': orders})
    else:
        return HttpResponseForbidden()

@login_required(login_url='/login/')
def provider_quantity(request):
    quantitys = request.user.profile.provider.quantity_set.all().order_by('-id')
    return render(request, 'provider/send-company.html', {'quantitys': quantitys})




#DILER
#============================================================================

@login_required(login_url='/login/')
def diler_response(request, id):
    if request.user.profile.spec == 'D':
        q = Quantity.objects.get(id=id)
        if request.user.profile.diler.id == q.order.user_id:
            q.isresponse = True
            q.save()
            msg = 'Дилер выбрал Ваше коммерческое предложение, для связи с ним войдите в сервис todotodo.' + '\n' + 'В разделе заказы в работе, Вы сможете взять контакты дилера.' + '\n' + 'Спасибо'
            send_mail('Ваше Коммерческое предложение выбрали', msg, settings.EMAIL_HOST_USER, [q.author.service_email], fail_silently=False)
            return redirect('diler_work')
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()

@login_required(login_url='/login/')
def diler_work(request):
    if request.user.profile.spec == 'D':
        return render(request, 'diler/processed-diler.html', {'orders': request.user.profile.diler.order_set.all()})
    else:
        return HttpResponseForbidden()

@login_required(login_url='/login/')
def diler_archive(request):
    if request.user.profile.spec == 'D':
        review = Review.objects.filter(fr_id=request.user.profile.diler)
        to = list(map(lambda item: item.to.id, review))
        return render(request, 'diler/archive-diler.html', {'orders': request.user.profile.diler.order_set.all(),'send_review': to})
    else:
        return HttpResponseForbidden()
    

@login_required(login_url='/login/')
def company_card(request, id):
    if request.user.profile.spec == 'D':
        p = Provider.objects.get(id=id)
        reviews = Review.objects.filter(to_id=id)
        return render(request, 'diler/company-profile.html', {'provider': p, 'reviews': reviews})
    else:
        return HttpResponseForbidden()




@login_required(login_url='/login/')
def order_delete(request, id):
    if request.user.profile.spec == 'D':
        o = Order.objects.get(id=id)
        if request.user.profile.diler.id == o.user_id:
            o.delete()
            return redirect(diler_orders)
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()






#PROVIDER
#============================================================================


@login_required(login_url='/login/')
def provider_check(request, id):
    if request.user.profile.spec == 'P':
        o = Quantity.objects.get(id=id)
        if o.author_id == request.user.profile.provider.id:
            o.order.isactive = False
            o.order.save()
            return redirect(provider_archive)
    else:
        return HttpResponseForbidden()



#DILER
#============================================================================


@require_POST
@login_required(login_url='/login/')
def diler_review(request):
    if request.user.profile.spec == 'D':
        r = Review()
        r.to_id = int(request.POST['to'])
        r.fr = request.user.profile.diler
        r.product_quality = int(request.POST['product_quality'])
        r.delivery_quality = int(request.POST['delivery_quality'])
        r.supplier_loyalty = int(request.POST['supplier_loyalty'])
        r.save()
        return redirect(diler_archive)
    else:
        return HttpResponseForbidden()



@login_required(login_url='/login/')
@require_POST
@csrf_exempt
def diler_check(request):
    if request.user.profile.spec == 'D':
        if request.user.profile.diler.organization == '' or request.user.profile.diler.warehouse_address == '' or request.user.profile.diler.region == None:
            return JsonResponse({'res': False})
        else:
            return JsonResponse({'res': True})
    else:
        return HttpResponseForbidden()

