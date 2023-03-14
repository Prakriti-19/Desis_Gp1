from auth1.forms import *
from django.contrib.auth import logout,login
from django.urls import reverse_lazy
from django.shortcuts import redirect,render
from django.views import View,generic
from django.views.generic import TemplateView
from auth1.backends import MyUserBackend
    
class HomeView2(TemplateView):
    template_name = "auth1/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "HandsForHunger | Home"
        return context

class d_h(TemplateView):
    template_name = "auth1/d_h.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "HandsForHunger | Home"
        return context

class n_h(TemplateView):
    template_name = "auth1/n_h.html"

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
            return redirect('n_home')
        else:
            return render(request, 'auth1/login.html', {'error_message': 'Invalid login credentials'})
    else:
        return render(request, 'auth1/login.html')
    
def DonorLoginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = MyUserBackend.authenticate(request,username=username, password=password, backend='auth1.backends.MyUserBackend')
        if user is not None and not user.is_ngo:
            login(request, user,backend= 'django.contrib.auth.backends.ModelBackend')
            return redirect('d_home')
        else:
            return render(request, 'auth1/login.html', {'error_message': 'Invalid login credentials'})
    else:
        return render(request, 'auth1/login.html')

class NgoSignUpView(generic.CreateView):
    form_class = ngoUserCreationForm
    template_name = "auth1/signup.html"
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
    template_name = "auth1/signup.html"
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
    

