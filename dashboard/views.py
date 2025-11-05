from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Avg, F, ExpressionWrapper, DurationField
from django.utils import timezone
from datetime import timedelta
from tickets.models import Ticket, Category, TicketFeedback, BeforeAfterPhoto, TechnicianPresence, TicketStatusHistory
from authentication.models import User, LoginLog
import json

@login_required
def admin_summary(request):
    """Admin Summary Dashboard with comprehensive statistics"""
    if request.user.role != 'admin':
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('dashboard:map')

    # === Basic Statistics ===
    total_tickets = Ticket.objects.count()
    pending_tickets = Ticket.objects.filter(status='PENDING').count()
    in_progress_tickets = Ticket.objects.filter(status__in=['IN_PROGRESS', 'INSPECTING', 'WORKING']).count()
    completed_tickets = Ticket.objects.filter(status__in=['COMPLETED', 'CLOSED']).count()
    rejected_tickets = Ticket.objects.filter(status='REJECTED').count()

    # === Tickets by Status ===
    tickets_by_status = {
        'PENDING': pending_tickets,
        'IN_PROGRESS': in_progress_tickets,
        'COMPLETED': completed_tickets,
        'REJECTED': rejected_tickets,
    }

    # === Tickets by Category ===
    tickets_by_category = list(Ticket.objects.values('category__name').annotate(count=Count('id')).order_by('-count'))

    # === Tickets by Urgency ===
    tickets_by_urgency = list(Ticket.objects.values('urgency_level').annotate(count=Count('id')).order_by('urgency_level'))

    # === Average Response Time (time from created to first assignment) ===
    # Calculate average time for tickets that have been assigned
    assigned_tickets = Ticket.objects.filter(assigned_to__isnull=False).exclude(status='PENDING')
    avg_response_seconds = 0
    if assigned_tickets.exists():
        # Rough estimate using created_at and updated_at
        total_response = sum([
            (ticket.updated_at - ticket.created_at).total_seconds()
            for ticket in assigned_tickets[:100]  # Sample for performance
        ])
        avg_response_seconds = total_response / min(assigned_tickets.count(), 100)
    avg_response_hours = round(avg_response_seconds / 3600, 1) if avg_response_seconds else 0

    # === Average Completion Time ===
    completed_with_time = Ticket.objects.filter(
        status__in=['COMPLETED', 'CLOSED'],
        completed_at__isnull=False
    )
    avg_completion_seconds = 0
    if completed_with_time.exists():
        total_completion = sum([
            (ticket.completed_at - ticket.created_at).total_seconds()
            for ticket in completed_with_time[:100]
        ])
        avg_completion_seconds = total_completion / min(completed_with_time.count(), 100)
    avg_completion_hours = round(avg_completion_seconds / 3600, 1) if avg_completion_seconds else 0

    # === Technician Performance ===
    technicians = User.objects.filter(role='technician')
    technician_stats = []
    for tech in technicians:
        assigned_count = Ticket.objects.filter(assigned_to=tech).count()
        completed_count = Ticket.objects.filter(
            assigned_to=tech,
            status__in=['COMPLETED', 'CLOSED']
        ).count()

        # Calculate completion rate
        completion_rate = round((completed_count / assigned_count * 100), 1) if assigned_count > 0 else 0

        # Average rating
        avg_rating = TicketFeedback.objects.filter(
            ticket__assigned_to=tech
        ).aggregate(avg=Avg('overall_rating'))['avg']
        avg_rating = round(avg_rating, 1) if avg_rating else 0

        # Check availability
        try:
            presence = TechnicianPresence.objects.get(technician=tech)
            is_available = presence.is_available
        except TechnicianPresence.DoesNotExist:
            is_available = True

        technician_stats.append({
            'name': tech.get_display_name(),
            'username': tech.username,
            'assigned': assigned_count,
            'completed': completed_count,
            'completion_rate': completion_rate,
            'avg_rating': avg_rating,
            'is_available': is_available,
        })

    # Sort by completion rate
    technician_stats.sort(key=lambda x: x['completion_rate'], reverse=True)

    # === Feedback Summary ===
    total_feedbacks = TicketFeedback.objects.count()
    avg_overall_rating = TicketFeedback.objects.aggregate(avg=Avg('overall_rating'))['avg']
    avg_overall_rating = round(avg_overall_rating, 1) if avg_overall_rating else 0

    # Recent feedbacks
    recent_feedbacks = TicketFeedback.objects.select_related(
        'ticket', 'ticket__assigned_to', 'ticket__created_by'
    ).order_by('-created_at')[:5]

    # === Recent Tickets ===
    recent_tickets = Ticket.objects.select_related(
        'created_by', 'assigned_to', 'category'
    ).order_by('-created_at')[:10]

    # === User Statistics ===
    total_users = User.objects.count()
    total_technicians = technicians.count()
    total_regular_users = User.objects.filter(role='user').count()

    # === Prepare data for charts (JSON) ===
    status_chart_data = json.dumps({
        'labels': list(tickets_by_status.keys()),
        'data': list(tickets_by_status.values())
    })

    category_chart_data = json.dumps({
        'labels': [item['category__name'] for item in tickets_by_category],
        'data': [item['count'] for item in tickets_by_category]
    })

    urgency_chart_data = json.dumps({
        'labels': [dict(Ticket.URGENCY_CHOICES).get(item['urgency_level'], '') for item in tickets_by_urgency],
        'data': [item['count'] for item in tickets_by_urgency]
    })

    context = {
        # Basic stats
        'total_tickets': total_tickets,
        'pending_tickets': pending_tickets,
        'in_progress_tickets': in_progress_tickets,
        'completed_tickets': completed_tickets,
        'rejected_tickets': rejected_tickets,

        # Performance metrics
        'avg_response_hours': avg_response_hours,
        'avg_completion_hours': avg_completion_hours,

        # Charts data
        'status_chart_data': status_chart_data,
        'category_chart_data': category_chart_data,
        'urgency_chart_data': urgency_chart_data,

        # Technician performance
        'technician_stats': technician_stats,

        # Feedback summary
        'total_feedbacks': total_feedbacks,
        'avg_overall_rating': avg_overall_rating,
        'recent_feedbacks': recent_feedbacks,

        # Recent activity
        'recent_tickets': recent_tickets,

        # User stats
        'total_users': total_users,
        'total_technicians': total_technicians,
        'total_regular_users': total_regular_users,
    }

    return render(request, 'dashboard/admin_summary.html', context)

@login_required
def map_view(request):
    """Main Page - แผนที่หลักแสดง Tickets ทั้งหมด (สำหรับทุก role)"""
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    category_filter = request.GET.get('category', 'all')

    # Base queryset with prefetch for photos
    tickets = Ticket.objects.exclude(location__isnull=True).select_related(
        'category', 'created_by', 'assigned_to'
    ).prefetch_related('before_after_photos', 'attachments')

    # Apply filters
    if status_filter == 'pending':
        tickets = tickets.filter(status='PENDING')
    elif status_filter == 'in_progress':
        tickets = tickets.filter(status__in=['IN_PROGRESS', 'INSPECTING', 'WORKING'])
    elif status_filter == 'completed':
        tickets = tickets.filter(status__in=['COMPLETED', 'CLOSED'])

    if category_filter != 'all':
        tickets = tickets.filter(category_id=category_filter)

    tickets = tickets.order_by('-created_at')

    # Statistics
    total_tickets = Ticket.objects.count()
    pending_count = Ticket.objects.filter(status='PENDING').count()
    in_progress_count = Ticket.objects.filter(status__in=['IN_PROGRESS', 'INSPECTING', 'WORKING']).count()
    completed_count = Ticket.objects.filter(status__in=['COMPLETED', 'CLOSED']).count()

    # Convert to GeoJSON for Leaflet
    tickets_geojson = []
    for ticket in tickets:
        if ticket.location:
            # Get photos from BeforeAfterPhoto model
            before_photo = None
            after_photo = None

            for photo in ticket.before_after_photos.all():
                if photo.photo_type == 'BEFORE' and not before_photo:
                    before_photo = photo.image.url
                elif photo.photo_type == 'AFTER' and not after_photo:
                    after_photo = photo.image.url

            # Get first attachment if no before photo
            if not before_photo:
                first_attachment = ticket.attachments.first()
                if first_attachment:
                    before_photo = first_attachment.file.url

            tickets_geojson.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [ticket.location.x, ticket.location.y]
                },
                'properties': {
                    'id': ticket.id,
                    'title': ticket.title,
                    'description': ticket.description,
                    'status': ticket.status,
                    'status_display': ticket.get_status_display(),
                    'category': ticket.category.name,
                    'category_id': ticket.category.id,
                    'category_color': ticket.category.color if hasattr(ticket.category, 'color') else '#3B82F6',
                    'urgency': ticket.urgency_level,
                    'urgency_display': ticket.get_urgency_level_display(),
                    'created_at': ticket.created_at.strftime('%d/%m/%Y %H:%M'),
                    'before_photo': before_photo,
                    'after_photo': after_photo,
                }
            })

    # Get categories for filter
    categories = Category.objects.filter(is_active=True)

    # === Latest 10 Tickets Section ===
    latest_status_filter = request.GET.get('latest_status', 'all')
    latest_tickets = Ticket.objects.select_related(
        'category', 'created_by', 'assigned_to'
    ).order_by('-created_at')

    # Apply status filter for latest tickets
    if latest_status_filter == 'pending':
        latest_tickets = latest_tickets.filter(status='PENDING')
    elif latest_status_filter == 'in_progress':
        latest_tickets = latest_tickets.filter(status__in=['IN_PROGRESS', 'INSPECTING', 'WORKING'])
    elif latest_status_filter == 'completed':
        latest_tickets = latest_tickets.filter(status__in=['COMPLETED', 'CLOSED'])

    latest_tickets = latest_tickets[:10]

    context = {
        'tickets_geojson': json.dumps(tickets_geojson),  # Convert to JSON string
        'tickets': tickets,
        'total_tickets': total_tickets,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'categories': categories,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'latest_tickets': latest_tickets,
        'latest_status_filter': latest_status_filter,
    }

    return render(request, 'dashboard/main_page.html', context)


@login_required
def admin_change_status(request):
    """Admin changes ticket status"""
    if request.user.role != 'admin':
        messages.error(request, 'คุณไม่มีสิทธิ์ทำรายการนี้')
        return redirect('dashboard:map')

    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        new_status = request.POST.get('new_status')
        admin_comment = request.POST.get('admin_comment', '').strip()

        if not ticket_id or not new_status:
            messages.error(request, 'ข้อมูลไม่ครบถ้วน')
            return redirect('dashboard:admin_summary')

        try:
            ticket = get_object_or_404(Ticket, id=ticket_id)
            old_status = ticket.status

            # Update ticket status
            ticket.status = new_status
            if new_status == 'COMPLETED':
                ticket.completed_at = timezone.now()
            ticket.save()

            # Create status history
            comment = admin_comment if admin_comment else f'Admin เปลี่ยนสถานะเป็น {ticket.get_status_display()}'
            TicketStatusHistory.objects.create(
                ticket=ticket,
                old_status=old_status,
                new_status=new_status,
                changed_by=request.user,
                comment=comment
            )

            messages.success(request, f'เปลี่ยนสถานะ Ticket #{ticket.id} เป็น "{ticket.get_status_display()}" สำเร็จ')

        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')

    return redirect('dashboard:admin_summary')


@login_required
def admin_close_ticket(request):
    """Admin closes ticket (set status to CLOSED)"""
    if request.user.role != 'admin':
        messages.error(request, 'คุณไม่มีสิทธิ์ทำรายการนี้')
        return redirect('dashboard:map')

    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')

        if not ticket_id:
            messages.error(request, 'ข้อมูลไม่ครบถ้วน')
            return redirect('dashboard:admin_summary')

        try:
            ticket = get_object_or_404(Ticket, id=ticket_id)

            # Check if ticket is completed first
            if ticket.status != 'COMPLETED':
                messages.warning(request, f'Ticket #{ticket.id} ต้องเป็นสถานะ "เสร็จสิ้น" ก่อนถึงจะปิดงานได้')
                return redirect('dashboard:admin_summary')

            old_status = ticket.status
            ticket.status = 'CLOSED'
            ticket.save()

            # Create status history
            TicketStatusHistory.objects.create(
                ticket=ticket,
                old_status=old_status,
                new_status='CLOSED',
                changed_by=request.user,
                comment='Admin ปิดงาน'
            )

            messages.success(request, f'ปิดงาน Ticket #{ticket.id} สำเร็จ')

        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')

    return redirect('dashboard:admin_summary')
