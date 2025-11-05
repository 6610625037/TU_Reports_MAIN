from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Avg
from tickets.models import Ticket, TicketFeedback
from authentication.models import User


@login_required
def analytics_dashboard(request):
    """Analytics Dashboard - TODO: Implement with Chart.js"""
    if request.user.role != 'admin':
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('tickets:my_tickets')

    # Basic statistics
    total_tickets = Ticket.objects.count()
    pending = Ticket.objects.filter(status='PENDING').count()
    in_progress = Ticket.objects.filter(status__in=['IN_PROGRESS', 'INSPECTING', 'WORKING']).count()
    completed = Ticket.objects.filter(status__in=['COMPLETED', 'CLOSED']).count()

    # Tickets by category
    by_category = Ticket.objects.values('category__name').annotate(count=Count('id'))

    # Average ratings
    avg_rating = TicketFeedback.objects.aggregate(avg=Avg('overall_rating'))

    # Technician performance
    technicians = User.objects.filter(role='technician').annotate(
        assigned_count=Count('assigned_tickets')
    )

    context = {
        'total_tickets': total_tickets,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed,
        'by_category': by_category,
        'avg_rating': avg_rating['avg'],
        'technicians': technicians,
    }

    # TODO: Create template with Chart.js visualizations
    messages.info(request, 'Analytics Dashboard กำลังพัฒนา')
    return render(request, 'reports/analytics.html', context)


@login_required
def export_report(request):
    """Export รายงาน PDF/Excel - TODO: Implement"""
    if request.user.role != 'admin':
        messages.error(request, 'คุณไม่มีสิทธิ์')
        return redirect('tickets:my_tickets')

    # TODO: Implement PDF/Excel export using ReportLab or openpyxl
    messages.info(request, 'ฟีเจอร์ Export รายงานกำลังพัฒนา')
    return redirect('reports:analytics')


@login_required
def heatmap_data(request):
    """Heatmap API endpoint - TODO: Implement"""
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # TODO: Return GeoJSON data for heatmap
    # Format: [lat, lng, intensity]
    heatmap_data = []

    tickets = Ticket.objects.exclude(location__isnull=True)
    for ticket in tickets:
        if ticket.location:
            heatmap_data.append([
                ticket.location.y,  # latitude
                ticket.location.x,  # longitude
                1.0  # intensity (can be weighted by urgency)
            ])

    return JsonResponse({'data': heatmap_data})
