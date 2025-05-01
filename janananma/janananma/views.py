from django.shortcuts import render

def index(request):
    return render (request,"dashboard/owner_dashboard.html",{})