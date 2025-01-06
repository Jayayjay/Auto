from django.shortcuts import render, redirect
from .forms import IDCardForm

def home(request):
    if request.method == 'POST':
        form = IDCardForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = IDCardForm()
    return render(request, 'collector/home.html', {'form': form})

def success(request):
    return render(request, 'collector/success.html')
