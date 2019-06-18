from .models import Profile

def profile(request):
    if request.user.is_authenticated:
        prof = Profile.objects.filter(user=request.user).first()
        return {'profile': prof}
    return {'nothing': None}