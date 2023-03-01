from auth1.forms import *
from django.contrib.auth import logout,login
from django.urls import reverse_lazy
from django.shortcuts import redirect,render
from django.views import View,generic
from django.views.generic import TemplateView
from auth1.backends import *

class HomeView(TemplateView):
    template_name = "auth1/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "HandsForHunger | Home"
        return context
    
class HomeView2(TemplateView):
    template_name = "auth1/ngo_h.html"

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
            return redirect('log_home')
        else:
            return render(request, 'auth1/login.html', {'error_message': 'Invalid login credentials'})
    else:
        return render(request, 'auth1/login.html')
    
def DonorLoginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = MyUserBackend.authenticate(request,username=username, password=password, backend='auth1.backends.MyUserBackend')
        print(f"username: {username}")
        print(f"password: {password}")
        print(f"user: {user}") 
        print(user.is_donor)
        if user is not None and user.is_donor:
            login(request, user,backend= 'django.contrib.auth.backends.ModelBackend')
            return redirect('log_home')
        else:
            return render(request, 'auth1/login.html', {'error_message': 'Invalid login credentials'})
    else:
        return render(request, 'auth1/login.html')

class NgoSignUpView(generic.CreateView):
    form_class = ngoUserCreationForm
    template_name = "auth1/signup.html"
    success_url = reverse_lazy('ngo_login')
    
    def form_valid(self, form):
        return super().form_valid(form)

class DonorSignUpView(generic.CreateView):
    form_class = donorUserCreationForm
    template_name = "auth1/signup.html"
    success_url = reverse_lazy('donor_login')
    
    def form_valid(self, form):
        return super().form_valid(form)

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("/")
    

