from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import *
from .forms import *


@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.save()
            messages.success(request, 'Изображение добавлено успешно')
            return redirect(new_image.get_absolute_url())
    else:
        form = ImageCreateForm(data=request.GET)
    return render(request=request,
                  template_name='images/image/create.html',
                  context={'section': 'images',
                           'form': form
                           })


def image_detail(request, id, slug=None):
    image = get_object_or_404(Image, id=id, 
                            #   slug=slug
                              )
    return render(request=request,
                  template_name='images/image/detail.html',
                  context={'section': 'images',
                           'image': image
                           })
            

@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)
    if images_only:
        return render(request,
                      'images/image/list_images.html',
                      {'section': 'images',
                       'images': images}) # JS запросы
    return render(request,
                  'images/image/list.html',
                   {'section': 'images',
                    'images': images}) # браузерные запросы
