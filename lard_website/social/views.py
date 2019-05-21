import django
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect

# Create your views here.
from front.models import PipelineResultImage, PipelineResult
from social.models import UserProfile, Publication

PUB_BY_PAGE = 10


@login_required
def profile(request):
    context = {
        "profile": UserProfile.objects.get(user=request.user),
        "genders": UserProfile.GENRE_CHOICES,
        "scopes": UserProfile.SCOPE_CHOICES
    }
    return render(request, 'profile.html', context=context)


@login_required
def profile_username(request, username):
    if username == request.user.username:
        return redirect(profile)
    else:
        p = UserProfile.objects.get((Q(username=username) & ~Q(scope='u')))
    context = {
        "profile": p
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
        pubs = Publication.objects.filter((Q(user_profile=up) | ~Q(scope="u"))).order_by("-created_at")

        if "u" in request.GET:
            pubs = pubs.filter(user_profile__username=request.GET.get("u", ""))
        if "s" in request.GET:
            s = request.GET.get("s", "")
            if s == "f":
                pubs = pubs.filter((Q(user_profile__in=up.followings.all()) & ~Q(scope="u")))

        paginator = Paginator(pubs, PUB_BY_PAGE)
        page_obj = paginator.page(1)

        context = {
            "profile": UserProfile.objects.get(user=request.user),
            "pubs": page_obj.object_list,
            "page": page_obj,
            "scopes": UserProfile.SCOPE_CHOICES
        }
        return render(request, "feed.html", context=context)


@login_required
def feed_json(request, page):
    up = UserProfile.objects.get(user=request.user)
    pubs = Publication.objects.filter((Q(user_profile=up) | ~Q(scope="u"))).order_by("-created_at")

    if "u" in request.GET:
        pubs = pubs.filter(user_profile__username=request.GET.get("u", ""))
    if "s" in request.GET:
        s = request.GET.get("s", "")
        if s == "f":
            pubs = pubs.filter((Q(user_profile__in=up.followings.all()) & ~Q(scope="u")))

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
            "images": pub.get_images()
        }

        return render(request, "feed_card.html", context=context)
    except Publication.DoesNotExist:
        raise Http404


@login_required
def feed_publish(request):
    up = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        if "message" in request.POST and "scope" in request.POST:
            message = request.POST.get("message", "")
            scope = request.POST.get("scope", up.scope)

            pub = Publication.objects.create(user_profile=up, message=message, scope=scope)

            print(request.POST)
            if "result_id" in request.POST:
                result_id = request.POST.get("result_id")
                try:
                    print("TRY")
                    pr = PipelineResult.objects.get(user=request.user, id=result_id)
                    pub.associated_result = pr
                    pub.save()

                except PipelineResult.DoesNotExist:
                    raise django.http.HttpResponseBadRequest

            return redirect(feed)

    context={
        "profile": up,
        "associated_result": request.GET.get("associated_result", None)
    }
    return render(request, 'publish.html', context=context)


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


@login_required
def people(request):
    context = {
        "peoples": UserProfile.objects.filter(~Q(scope='u'))
    }
    return render(request, 'people.html', context=context)


@login_required
def people_add(request):
    if request.method == 'POST':
        if "user_profile" in request.POST:
            user_profile_id = request.POST.get("user_profile")
            try:
                up_to_add = UserProfile.objects.get(id=user_profile_id)
                up = UserProfile.objects.get(user=request.user)
                up.add_friend(up_to_add)
                up.save()
            except UserProfile.DoesNotExist:
                raise Http404
    return redirect(people)


@login_required
def people_delete(request):
    if request.method == 'POST':
        if "user_profile" in request.POST:
            user_profile_id = request.POST.get("user_profile")
            try:
                up_to_rm = UserProfile.objects.get(id=user_profile_id)
                up = UserProfile.objects.get(user=request.user)
                up.remove_friend(up_to_rm)
                up.save()
            except UserProfile.DoesNotExist:
                raise Http404
    return redirect(people)
