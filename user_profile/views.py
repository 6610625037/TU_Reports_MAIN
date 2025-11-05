from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def profile_view(request):
    """ดูโปรไฟล์ - TODO: Implement"""
    context = {
        'user': request.user,
    }

    # TODO: Create profile template
    messages.info(request, 'หน้าโปรไฟล์กำลังพัฒนา')
    return render(request, 'profile/view.html', context)


@login_required
def edit_profile(request):
    """แก้ไขโปรไฟล์ - TODO: Implement"""
    if request.method == 'POST':
        # TODO: Handle profile update
        messages.info(request, 'ฟีเจอร์แก้ไขโปรไฟล์กำลังพัฒนา')
        return redirect('user_profile:view')

    context = {
        'user': request.user,
    }

    return render(request, 'profile/edit.html', context)


@login_required
def settings_view(request):
    """ตั้งค่าทั่วไป - TODO: Implement"""
    # TODO: Handle notification settings, preferences, etc.
    context = {
        'user': request.user,
    }

    messages.info(request, 'หน้าตั้งค่ากำลังพัฒนา')
    return render(request, 'profile/settings.html', context)


@login_required
def security_settings(request):
    """ตั้งค่าความปลอดภัย - TODO: Implement"""
    if request.method == 'POST':
        # TODO: Handle password change, 2FA, etc.
        messages.info(request, 'ฟีเจอร์ตั้งค่าความปลอดภัยกำลังพัฒนา')
        return redirect('user_profile:security')

    context = {
        'user': request.user,
    }

    return render(request, 'profile/security.html', context)
