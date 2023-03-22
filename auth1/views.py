from auth1.forms import *
from django.contrib.auth import logout,login
from django.urls import reverse_lazy
from django.shortcuts import redirect,render
from django.views import View,generic
from django.views.generic import TemplateView
from auth1.backends import MyUserBackend
from django.db.models import Sum
    
class HomeView2(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "HandsForHunger | Home"
        return context
    
def my_view(request):
    lives=donations.objects.filter(donor_id=request.user).aggregate(Sum('quantity'))
    count=donations.objects.filter(donor_id=request.user).count()
    context = {
        'count':count,
        'lives': lives,
    }
    return render(request, 'd_h.html', context)

class donor_home(TemplateView):
    template_name = "d_h.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "HandsForHunger | Home"
        return context

class ngo_home(TemplateView):
    template_name = "n_h.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "HandsForHunger | Home"
        return context
    
       
def NgoLoginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = MyUserBackend.authenticate(request,username=username, password=password, backend='auth1.backends.MyUserBackend')
       
        if user is not None and user.is_ngo:
            login(request, user,backend='auth1.backends.MyUserBackend')
            return redirect('ngo_home')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid login credentials'})
    else:
        return render(request, 'login.html')
    
def DonorLoginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = MyUserBackend.authenticate(request,username=username, password=password, backend='auth1.backends.MyUserBackend')
        if user is not None and not user.is_ngo:
            login(request, user,backend= 'django.contrib.auth.backends.ModelBackend')
            return redirect('donor_home')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid login credentials'})
    else:
        return render(request, 'login.html')

class NgoSignUpView(generic.CreateView):
    form_class = ngoUserCreationForm
    template_name = "signup.html"
    success_url = reverse_lazy('ngo_login')
    
    def form_valid(self, form):
        if form.is_valid():
            donation = form.save(commit=False)
            donation.latitude = form.cleaned_data['latitude']
            donation.longitude = form.cleaned_data['longitude']
            donation.save()
            return super().form_valid(form)

class DonorSignUpView(generic.CreateView):
    form_class = donorUserCreationForm
    template_name = "signup.html"
    success_url = reverse_lazy('donor_login')
    def form_valid(self, form):
        if form.is_valid():
            donation = form.save(commit=False)
            donation.latitude = form.cleaned_data['latitude']
            donation.longitude = form.cleaned_data['longitude']
            donation.save()
            response = super().form_valid(form)
            user = form.save()
            user.save()
            return response

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("/")
    

