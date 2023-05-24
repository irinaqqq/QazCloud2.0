# Create your views here.
# myapp/views.py
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.conf import settings
import cloudinary
from cloudinary import api
import cloudinary.uploader
from django.contrib.auth.decorators import login_required
from pathlib import Path
def registration_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect or render a success message
            return redirect('main_view')  # Redirect to the main view
    else:
        form = UserCreationForm()
    
    # Render the registration form
    return render(request, 'registration.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main_view')
    return render(request, 'login.html')

import cloudinary

@login_required
def main_view(request):
    # Get the user's Cloudinary directory
    cloudinary_directory = f'{settings.CLOUDINARY_DIRECTORY}/{request.user.username}'

    # Get all files in the user's directory
    response = cloudinary.api.resources(
        type='upload',
        prefix=cloudinary_directory,
        resource_type='raw',
        max_results=50  # Adjust the maximum number of results if needed
    )
    files = response['resources']
    
    # Extract file names
    for file in files:
        file_path = Path(file['public_id'])
        file['file_name'] = file_path.name

    context = {
        'files': files
    }

    if request.method == 'POST':
        # Handle file deletion
        file_id = request.POST.get('file_id')
        if file_id:
            # Delete the file from Cloudinary
            cloudinary.uploader.destroy(file_id, resource_type='raw')
            # Redirect or render a success message
            return redirect('main_view')  # Redirect to the main view

        # Handle file upload
        uploaded_file = request.FILES['file']
        # Generate a unique file name using the original file name
        file_name = uploaded_file.name
        
        # Upload the file with its original name to Cloudinary
        upload_result = cloudinary.uploader.upload(
            uploaded_file,
            resource_type="raw",
            folder=cloudinary_directory,
            public_id=file_name  # Set the public ID to the file name
        )

        # Redirect or render a success message
        return redirect('main_view')  # Redirect to the main view

    return render(request, 'main.html', context)



def index_view(request):
    return render(request, 'index.html')