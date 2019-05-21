import django
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect

# Create your views here.
from front.models import PipelineResultImage, PipelineResult
from social.models import UserProfile, Publication

PUB_BY_PAGE = 1


@login_required
def profile(request):
    context = {
        "profile": UserProfile.objects.get(user=request.user),
        "genders": UserProfile.GENRE_CHOICES,
        "scopes": UserProfile.SCOPE_CHOICES
    }
    return render(request, 'profile.html', context=context)


@login_required
def profile_update(request):
    if request.method == 'POST':
        up = UserProfile.objects.get(user=request.user)

        location = request.POST.get("location", "")
        gender = request.POST.get("gender", "")
        scope = request.POST.get("scope", "")
        up.locality = location
        up.genre = gender
        up.scope = scope

        up.save()
        return redirect(profile)

    return HttpResponse(status=403)


@login_required
def feed(request):
    if request.method == "POST":
        pass
    else:
        up = UserProfile.objects.get(user=request.user)
        pubs = Publication.objects.filter(
            Q(scope='p') | Q(user_profile=up) | (Q(user_profile__in=up.followings.all()) & Q(scope='f'))).order_by(
            "-created_at")

        paginator = Paginator(pubs, PUB_BY_PAGE)
        page_obj = paginator.page(1)

        context = {
            "profile": UserProfile.objects.get(user=request.user),
            "page": page_obj,
            "scopes": UserProfile.SCOPE_CHOICES
        }
        return render(request, "feed.html", context=context)


@login_required
def feed_json(request, page):
    up = UserProfile.objects.get(user=request.user)
    pubs = Publication.objects.filter(
        Q(scope='p') | Q(user_profile=up) | (Q(user_profile__in=up.followings.all()) & Q(scope='f'))).order_by(
        "-created_at")

    paginator = Paginator(pubs, PUB_BY_PAGE)
    try:
        page_obj = paginator.page(page)
    except InvalidPage:
        raise Http404

    context = {
        "pubs": page_obj.object_list,
        "page": page_obj
    }

    return render(request, "feed_entry.json", context=context, content_type="text/javascript")


@login_required
def feed_element(request, elt_id):
    try:
        up = UserProfile.objects.get(user=request.user)
        pubs = Publication.objects.filter(
            Q(scope='p') | Q(user_profile=up) | (Q(user_profile__in=up.followings.all()) & Q(scope='f')))
        pub = pubs.get(id=elt_id)

        context = {
            "pub": pub,
            "images": PipelineResultImage.objects.filter(pipeline_result=pub.associated_result)
        }

        return render(request, "feed_card.html", context=context)
    except Publication.DoesNotExist:
        raise Http404


@login_required
def feed_publish(request):
    if request.method == 'POST':
        if "message" in request.POST and "scope" in request.POST:
            message = request.POST.get("message", "")
            up = UserProfile.objects.get(user=request.user)
            scope = request.POST.get("scope", up.scope)

            pub = Publication.objects.create(user_profile=up, message=message, scope=scope)

            if "result_id" in request.POST:
                result_id = request.POST.get("result_id")
                try:
                    pr = PipelineResult.objects.get(user=request.user, id=result_id)
                    pub.associated_result = pr
                    pub.save()

                except PipelineResult.DoesNotExist:
                    raise django.http.HttpResponseBadRequest

            return redirect(feed)

    return redirect(feed)

@login_required
def feed_publish_delete(request, pub_id):
    if request.method == 'POST':
        try:
            pub = Publication.objects.get(user_profile__user=request.user, id=pub_id)
            pub.delete()
            return HttpResponse(status=200)

        except Publication.DoesNotExist:
            raise django.http.HttpResponseBadRequest

    return redirect(feed)