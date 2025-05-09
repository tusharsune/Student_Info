from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from studentapp.forms import CustomUserCreationForm  # Import from studentapp.forms

# --- Login View ---
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Ensure this URL name exists
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


# --- Signup View ---
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login after successful signup
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


# --- Logout View ---
def logout_view(request):
    logout(request)
    return redirect('index')
