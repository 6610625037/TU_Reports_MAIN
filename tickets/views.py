from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.gis.geos import Point
from django.utils import timezone
from .models import Ticket, TicketStatusHistory, BeforeAfterPhoto, TicketFeedback
from .forms import TicketForm
from .dispatcher import auto_dispatch_ticket

@login_required
def create_ticket(request):
    """สร้าง Ticket ใหม่"""
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user

            # Get GPS coordinates from form
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')

            if lat and lng:
                ticket.location = Point(float(lng), float(lat), srid=4326)

            ticket.save()

            # Save Before Photo
            if request.FILES.get('before_photo'):
                photo = request.FILES['before_photo']
                BeforeAfterPhoto.objects.create(
                    ticket=ticket,
                    photo_type='BEFORE',
                    image=photo,
                    uploaded_by=request.user,
                    file_size=photo.size
                )

            # Create initial status history
            TicketStatusHistory.objects.create(
                ticket=ticket,
                old_status='',
                new_status='PENDING',
                changed_by=request.user,
                comment='สร้าง Ticket ใหม่'
            )

            # Auto Dispatch
            auto_dispatch_ticket(ticket)

            # Refresh ticket to get updated data
            ticket.refresh_from_db()

            if ticket.assigned_to:
                messages.success(
                    request,
                    f'สร้าง Ticket #{ticket.id} เรียบร้อยแล้ว '
                    f'และมอบหมายให้ {ticket.assigned_to.get_display_name()}'
                )
            else:
                messages.info(
                    request,
                    f'สร้าง Ticket #{ticket.id} เรียบร้อยแล้ว '
                    f'(ยังไม่สามารถมอบหมายช่างได้ในขณะนี้)'
                )

            return redirect('tickets:my_tickets')
    else:
        form = TicketForm()

    return render(request, 'user/create_ticket.html', {'form': form})

@login_required
def my_tickets(request):
    """แสดง Ticket ทั้งหมดของผู้ใช้ พร้อม Search & Filter"""
    # Base queryset
    tickets = Ticket.objects.filter(created_by=request.user).select_related(
        'category', 'assigned_to'
    )

    # Get filter parameters
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    urgency_filter = request.GET.get('urgency', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    sort_by = request.GET.get('sort', '-created_at')

    # Apply search
    if search_query:
        from django.db.models import Q
        tickets = tickets.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Apply filters
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    if category_filter:
        tickets = tickets.filter(category_id=category_filter)

    if urgency_filter:
        tickets = tickets.filter(urgency_level=urgency_filter)

    if date_from:
        from datetime import datetime
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            tickets = tickets.filter(created_at__gte=date_from_obj)
        except ValueError:
            pass

    if date_to:
        from datetime import datetime, timedelta
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            # Add 1 day to include the entire end date
            tickets = tickets.filter(created_at__lt=date_to_obj + timedelta(days=1))
        except ValueError:
            pass

    # Apply sorting
    if sort_by in ['-created_at', 'created_at', '-urgency_level', 'urgency_level']:
        tickets = tickets.order_by(sort_by)
    else:
        tickets = tickets.order_by('-created_at')

    # Get categories for filter dropdown
    from tickets.models import Category
    categories = Category.objects.filter(is_active=True)

    # Count statistics (before filtering for accurate counts)
    all_tickets = Ticket.objects.filter(created_by=request.user)

    context = {
        'tickets': tickets,
        'categories': categories,
        'pending_count': all_tickets.filter(status='PENDING').count(),
        'in_progress_count': all_tickets.filter(status__in=['IN_PROGRESS', 'INSPECTING', 'WORKING']).count(),
        'completed_count': all_tickets.filter(status__in=['COMPLETED', 'CLOSED']).count(),
        # Pass filter values back to template
        'search_query': search_query,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'urgency_filter': urgency_filter,
        'date_from': date_from,
        'date_to': date_to,
        'sort_by': sort_by,
        'filtered_count': tickets.count(),
    }

    return render(request, 'user/my_tickets.html', context)

@login_required
def ticket_detail(request, ticket_id):
    """รายละเอียด Ticket"""
    ticket = get_object_or_404(
        Ticket.objects.select_related('category', 'created_by', 'assigned_to'),
        id=ticket_id
    )

    # ตรวจสอบสิทธิ์
    if ticket.created_by != request.user and request.user.role not in ['admin', 'technician']:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึง Ticket นี้')
        return redirect('tickets:my_tickets')

    # === Handle Technician POST Actions ===
    if request.method == 'POST' and request.user.role == 'technician' and ticket.assigned_to == request.user:
        action = request.POST.get('action')

        # Upload After Photo (if provided)
        if request.FILES.get('after_photo'):
            after_photo_file = request.FILES['after_photo']
            # Delete old after photo if exists
            old_after = ticket.before_after_photos.filter(photo_type='AFTER').first()
            if old_after:
                old_after.delete()

            # Create new after photo
            BeforeAfterPhoto.objects.create(
                ticket=ticket,
                photo_type='AFTER',
                image=after_photo_file,
                uploaded_by=request.user,
                file_size=after_photo_file.size
            )
            messages.success(request, '✓ อัปโหลดรูป After สำเร็จ')

        # Action: Update Status
        if action == 'update_status':
            new_status = request.POST.get('new_status')
            comment = request.POST.get('comment', '').strip()

            if new_status and new_status != ticket.status:
                old_status = ticket.status
                ticket.status = new_status
                ticket.save()

                # Create status history
                TicketStatusHistory.objects.create(
                    ticket=ticket,
                    old_status=old_status,
                    new_status=new_status,
                    changed_by=request.user,
                    comment=comment if comment else f'เปลี่ยนสถานะเป็น {ticket.get_status_display()}'
                )

                messages.success(request, f'✓ อัปเดตสถานะเป็น "{ticket.get_status_display()}" สำเร็จ')
            else:
                if not new_status:
                    messages.warning(request, 'กรุณาเลือกสถานะใหม่')
                else:
                    messages.info(request, 'สถานะไม่เปลี่ยนแปลง')

        # Action: Submit Work (Complete)
        elif action == 'submit_work':
            # Check if After photo exists
            after_photo_exists = ticket.before_after_photos.filter(photo_type='AFTER').exists()

            if not after_photo_exists:
                messages.error(request, '❌ ต้องอัปโหลดรูป After ก่อนส่งงาน')
            else:
                old_status = ticket.status
                ticket.status = 'COMPLETED'
                ticket.completed_at = timezone.now()
                ticket.save()

                comment = request.POST.get('comment', '').strip()
                TicketStatusHistory.objects.create(
                    ticket=ticket,
                    old_status=old_status,
                    new_status='COMPLETED',
                    changed_by=request.user,
                    comment=comment if comment else 'ส่งงานเสร็จสิ้น'
                )

                messages.success(request, '🎉 ส่งงานสำเร็จ! สถานะเปลี่ยนเป็น "เสร็จสิ้น"')

        return redirect('tickets:ticket_detail', ticket_id=ticket.id)

    # === GET Request - Display Ticket Detail ===
    history = ticket.status_history.all().order_by('timestamp')  # เปลี่ยนเป็นเรียงตามเวลา (ไม่ reverse)
    attachments = ticket.attachments.all()

    # Get before/after photos
    before_after_photos = ticket.before_after_photos.all()
    before_photo = before_after_photos.filter(photo_type='BEFORE').first()
    after_photo = before_after_photos.filter(photo_type='AFTER').first()

    context = {
        'ticket': ticket,
        'history': history,
        'attachments': attachments,
        'before_photo': before_photo,
        'after_photo': after_photo,
    }

    return render(request, 'user/ticket_detail.html', context)

@login_required
def edit_ticket(request, ticket_id):
    """แก้ไข Ticket (เฉพาะ PENDING)"""
    ticket = get_object_or_404(Ticket, id=ticket_id, created_by=request.user)

    # ตรวจสอบว่า ticket ยังเป็น PENDING อยู่หรือไม่
    if ticket.status != 'PENDING':
        messages.error(request, 'สามารถแก้ไขได้เฉพาะ Ticket ที่มีสถานะ "รอดำเนินการ" เท่านั้น')
        return redirect('tickets:ticket_detail', ticket_id=ticket_id)

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            # บันทึกการแก้ไข
            updated_ticket = form.save()

            # บันทึกประวัติการแก้ไข
            TicketStatusHistory.objects.create(
                ticket=updated_ticket,
                old_status=ticket.status,
                new_status=ticket.status,  # สถานะไม่เปลี่ยน
                changed_by=request.user,
                comment=f'แก้ไขข้อมูล Ticket โดย {request.user.get_display_name()}'
            )

            messages.success(request, 'แก้ไข Ticket สำเร็จ')
            return redirect('tickets:ticket_detail', ticket_id=ticket_id)
    else:
        form = TicketForm(instance=ticket)

    categories = Category.objects.filter(is_active=True)

    context = {
        'form': form,
        'ticket': ticket,
        'categories': categories,
    }

    return render(request, 'user/edit_ticket.html', context)

@login_required
def cancel_ticket(request, ticket_id):
    """ยกเลิก Ticket"""
    ticket = get_object_or_404(Ticket, id=ticket_id, created_by=request.user)

    # ตรวจสอบสถานะที่สามารถยกเลิกได้
    if ticket.status not in ['PENDING', 'IN_PROGRESS', 'INSPECTING', 'WORKING']:
        messages.error(request, 'ไม่สามารถยกเลิก Ticket ที่มีสถานะนี้ได้')
        return redirect('tickets:ticket_detail', ticket_id=ticket_id)

    if request.method == 'POST':
        old_status = ticket.status
        assigned_tech = ticket.assigned_to

        # เปลี่ยนสถานะเป็น REJECTED (ใช้เป็นการยกเลิก)
        ticket.status = 'REJECTED'
        ticket.reject_reason = f'ยกเลิกโดยผู้แจ้ง: {request.POST.get("reason", "ไม่ระบุเหตุผล")}'
        ticket.assigned_to = None  # unassign technician
        ticket.save()

        # บันทึกประวัติ
        TicketStatusHistory.objects.create(
            ticket=ticket,
            old_status=old_status,
            new_status='REJECTED',
            changed_by=request.user,
            comment=ticket.reject_reason
        )

        messages.success(request, f'ยกเลิก Ticket #{ticket.id} สำเร็จ')

        # TODO: ส่ง notification ให้ช่าง (ถ้ามีการ assign แล้ว)
        if assigned_tech:
            messages.info(request, f'ได้ทำการแจ้งช่าง {assigned_tech.get_display_name()} แล้ว')

        return redirect('tickets:my_tickets')

    return render(request, 'user/cancel_ticket.html', {'ticket': ticket})

@login_required
def submit_feedback(request, ticket_id):
    """ส่ง Feedback/Rating"""
    ticket = get_object_or_404(Ticket, id=ticket_id, created_by=request.user)

    if ticket.status not in ['COMPLETED', 'CLOSED']:
        messages.error(request, 'สามารถให้คะแนนได้เฉพาะงานที่เสร็จสิ้นแล้ว')
        return redirect('tickets:ticket_detail', ticket_id=ticket_id)

    if hasattr(ticket, 'feedback'):
        messages.info(request, 'คุณได้ให้คะแนน Ticket นี้แล้ว')
        return redirect('tickets:ticket_detail', ticket_id=ticket_id)

    if request.method == 'POST':
        TicketFeedback.objects.create(
            ticket=ticket, created_by=request.user, technician=ticket.assigned_to,
            overall_rating=int(request.POST['overall_rating']),
            response_speed_rating=int(request.POST['response_speed_rating']) if request.POST.get('response_speed_rating') else None,
            work_quality_rating=int(request.POST['work_quality_rating']) if request.POST.get('work_quality_rating') else None,
            politeness_rating=int(request.POST['politeness_rating']) if request.POST.get('politeness_rating') else None,
            cleanliness_rating=int(request.POST['cleanliness_rating']) if request.POST.get('cleanliness_rating') else None,
            comment=request.POST.get('comment', '')
        )
        messages.success(request, '⭐ ขอบคุณสำหรับความคิดเห็น!')
        return redirect('tickets:ticket_detail', ticket_id=ticket_id)

    return render(request, 'tickets/feedback_form.html', {'ticket': ticket})
