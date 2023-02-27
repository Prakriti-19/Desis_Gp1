from auth1.forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = "auth1/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "HandsForHunger | Home"
        return context
    
class RegisterView(TemplateView):
    template_name = "auth1/register.html"
    form_class = UserRegisterForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "HandsForHunger | Register"
        return context

    def get(self, request):
        form = self.form_class()
        context = self.get_context_data()
        context.update({"form": form})
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "You have been registered! Login now!")
            return redirect("/")
        context = self.get_context_data()
        context.update({"form": form})
        return render(request, self.template_name, context)


class LoginView(TemplateView):
    template_name = "auth1/login.html"
    form_class = UserLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "HandsForHunger | Login"
        return context

    def get(self, request):
        form = self.form_class()
        context = self.get_context_data()
        context.update({"form": form})
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Successfully logged in")
                return redirect("/")
            else:
                messages.error(request, "Invalid credentials")
        context = self.get_context_data()
        context.update({"form": form})
        return render(request, self.template_name, context)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("/")