from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseForbidden
from django.views.generic import View
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

import json

import mturk.utils
from annotator.models import *
from mturk.models import *


def home(request):
    if not (request.user.is_authenticated()):
        return redirect('/login/?next=' + request.path)
    else:
        videos = Video.objects.filter(id__gt=0, verified=False)[:25]
        return render(request, 'mturk.html', context={
            'videos':videos,
        })


@login_required
def status(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        raise Http404(
            'No video with id "{}". Possible fixes: \n1) Download an up to date DB, see README. \n2) Add this video to the DB via /admin'.format(
                video_id))


    try:
        fvts = (video.fullvideotask_set.all())
        sfts = (video.singleframetask_set.all())
        print(fvts, sfts)
    except Exception:
        pass
    return render(request, "mturk_status.html", context={
        'video':video,
        'fvts':fvts,
        'sfts':sfts,
    })

@login_required
def create_fvt(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        raise Http404(
            'No video with id "{}". Possible fixes: \n1) Download an up to date DB, see README. \n2) Add this video to the DB via /admin'.format(
                video_id))

    fvt = FullVideoTask()
    fvt.video = video
    fvt.save()
    return HttpResponse("Created FVT HIT!")

@login_required
def create_sft(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        raise Http404(
            'No video with id "{}". Possible fixes: \n1) Download an up to date DB, see README. \n2) Add this video to the DB via /admin'.format(
                video_id))

    sft = SingleFrameTask()
    sft.video = video
    sft.time = 0.0 #add form later
    sft.save()
    return HttpResponse("Created SFT HIT!")

@login_required
def publish_task(request):
    to_publish = json.loads(request.body.decode('utf-8'))
    print(to_publish)
    for id in to_publish:
        if to_publish[id] == "f":
            #fullvideotask
            try:
                fvt = FullVideoTask.objects.get(id=id)
            except FullVideoTask.DoesNotExist:
                raise Http404("FullVideoTask not found") #figure out how to display 404 error message to front end
            fvt.publish()
        elif to_publish[id] == "s":
            #singleframetask
            try:
                sft = SingleFrameTask.objects.get(id=id)
            except SingleFrameTask.DoesNotExist:
                raise Http404("SingleFrameTask not found")
            sft.publish()
        else:
            raise Http404("Malformed request, please check POST request")
    return HttpResponse("ok")
