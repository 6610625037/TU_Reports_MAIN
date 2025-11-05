"""
Auto Dispatcher System
คัดเลือกช่างที่เหมาะสมที่สุดสำหรับ Ticket ใหม่
"""

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from .models import Ticket, TechnicianPresence, AssignmentRule, TicketStatusHistory
from authentication.models import User
from notify.utils import notify_ticket_assigned
import logging

logger = logging.getLogger(__name__)


class AutoDispatcher:
    """
    Auto Dispatcher Logic

    Algorithm:
    1. คำนวณ priority_score จาก urgency, category, และ heat count
    2. หาช่างในหมวดเดียวกัน
    3. กรองช่างที่งานไม่เกิน max_open_tickets
    4. คำนวณ score จาก distance และ workload
    5. เลือกช่างที่ score ดีที่สุด
    """

    def __init__(self):
        # Get assignment rules
        self.rule = AssignmentRule.objects.filter(is_active=True).first()
        if not self.rule:
            # Create default rule
            self.rule = AssignmentRule.objects.create(
                max_open_tickets=5,
                weight_distance=0.6,
                weight_workload=0.4,
                is_active=True
            )

    def calculate_priority_score(self, ticket):
        """
        คำนวณ priority score ของ Ticket

        Formula:
        priority_score = urgency_weight + category_weight + heat_weight
        """
        score = 0.0

        # Urgency level weight
        urgency_weights = {
            'LOW': 1.0,
            'MEDIUM': 2.0,
            'HIGH': 3.0,
            'CRITICAL': 5.0,
        }
        score += urgency_weights.get(ticket.urgency_level, 2.0)

        # Category weight (customize based on business rules)
        category_weights = {
            'ไฟฟ้า': 1.5,
            'ประปา': 1.5,
            'IT/คอมพิวเตอร์': 1.0,
            'แอร์/ระบายอากาศ': 1.2,
            'อาคาร/โครงสร้าง': 1.3,
        }
        score += category_weights.get(ticket.category.name, 1.0)

        # Heat count (ความถี่ปัญหาในพื้นที่นั้น)
        if ticket.location:
            # Count tickets in 500m radius in last 30 days
            from django.utils import timezone
            from datetime import timedelta
            from django.contrib.gis.measure import D

            thirty_days_ago = timezone.now() - timedelta(days=30)
            nearby_count = Ticket.objects.filter(
                location__distance_lte=(ticket.location, D(m=500)),
                created_at__gte=thirty_days_ago
            ).count()

            score += min(nearby_count * 0.1, 2.0)  # Cap at 2.0

        return round(score, 2)

    def find_best_technician(self, ticket):
        """
        หาช่างที่เหมาะสมที่สุดสำหรับ Ticket

        Returns:
            (technician, reason) or (None, reason)
        """
        # 1. หาช่างในหมวดเดียวกัน
        # TODO: ในระบบจริงควรมีตาราง TechnicianCategory
        # สำหรับ MVP ใช้ทุกช่าง
        available_technicians = User.objects.filter(
            role='technician',
            is_active=True
        )

        if not available_technicians.exists():
            return None, "ไม่พบช่างในระบบ"

        # 2. กรองช่างที่พร้อมรับงาน (is_available) และงานไม่เกิน max_open_tickets
        candidates = []
        for tech in available_technicians:
            # Check availability
            try:
                presence = TechnicianPresence.objects.get(technician=tech)
                if not presence.is_available:
                    continue  # Skip unavailable technicians
            except TechnicianPresence.DoesNotExist:
                # If no presence record, assume available
                pass

            open_tickets_count = Ticket.objects.filter(
                assigned_to=tech
            ).exclude(status__in=['COMPLETED', 'CLOSED', 'REJECTED']).count()

            if open_tickets_count < self.rule.max_open_tickets:
                candidates.append({
                    'technician': tech,
                    'open_tickets': open_tickets_count
                })

        if not candidates:
            return None, f"ไม่พบช่างที่พร้อมรับงาน (งานเต็มหรือหยุดรับงานชั่วคราว)"

        # 3. คำนวณ score สำหรับแต่ละช่าง
        scored_candidates = []

        for candidate in candidates:
            tech = candidate['technician']
            score = 0.0
            distance_km = None

            # Distance score
            if ticket.location:
                try:
                    presence = TechnicianPresence.objects.get(technician=tech)
                    if presence.location:
                        # Calculate distance (in meters)
                        distance = ticket.location.distance(presence.location) * 111000  # approx meters
                        distance_km = distance / 1000

                        # Distance score (inverse - closer is better)
                        # Normalize: 0-1km = 1.0, 1-5km = 0.5, >5km = 0.1
                        if distance_km <= 1:
                            distance_score = 1.0
                        elif distance_km <= 5:
                            distance_score = 0.5
                        else:
                            distance_score = 0.1

                        score += distance_score * self.rule.weight_distance
                except TechnicianPresence.DoesNotExist:
                    # ถ้าไม่มีข้อมูล location ให้ score กลางๆ
                    score += 0.5 * self.rule.weight_distance

            # Workload score (ยิ่งงานน้อยยิ่งดี)
            workload_score = 1.0 - (candidate['open_tickets'] / self.rule.max_open_tickets)
            score += workload_score * self.rule.weight_workload

            scored_candidates.append({
                'technician': tech,
                'score': score,
                'open_tickets': candidate['open_tickets'],
                'distance_km': distance_km
            })

        # 4. เลือกช่างที่ score สูงที่สุด
        if scored_candidates:
            best = max(scored_candidates, key=lambda x: x['score'])
            tech = best['technician']
            distance_str = f"{best['distance_km']:.1f}km" if best['distance_km'] else "N/A"

            reason = (
                f"มอบหมายให้ {tech.get_display_name()} "
                f"(ระยะทาง: {distance_str}, "
                f"งานเปิด: {best['open_tickets']}, "
                f"คะแนน: {best['score']:.2f})"
            )

            return tech, reason

        return None, "ไม่สามารถหาช่างที่เหมาะสมได้"

    def dispatch(self, ticket):
        """
        Main dispatch function

        Process:
        1. Calculate priority score
        2. Find best technician
        3. Assign ticket
        4. Create status history

        Returns:
            bool: True if assigned successfully
        """
        # Calculate priority score
        ticket.priority_score = self.calculate_priority_score(ticket)

        # Find best technician
        technician, reason = self.find_best_technician(ticket)

        if technician:
            # Assign ticket
            old_status = ticket.status
            ticket.assigned_to = technician
            ticket.status = 'PENDING'  # Keep as PENDING until technician accepts
            ticket.save()

            # Create status history
            TicketStatusHistory.objects.create(
                ticket=ticket,
                old_status=old_status,
                new_status=ticket.status,
                changed_by=None,  # System auto-assign
                comment=f"[Auto Dispatcher] {reason}"
            )

            logger.info(f"Ticket #{ticket.id} dispatched to {technician.username}: {reason}")

            # Send notification to technician
            notify_ticket_assigned(ticket)

            return True
        else:
            # No technician available
            ticket.save()  # Save priority_score

            TicketStatusHistory.objects.create(
                ticket=ticket,
                old_status='',
                new_status='PENDING',
                changed_by=None,
                comment=f"[Auto Dispatcher] ไม่สามารถมอบหมายช่างได้: {reason}"
            )

            logger.warning(f"Ticket #{ticket.id} could not be assigned: {reason}")
            return False


def auto_dispatch_ticket(ticket):
    """
    Utility function to dispatch a ticket

    Usage:
        from tickets.dispatcher import auto_dispatch_ticket
        auto_dispatch_ticket(ticket)
    """
    dispatcher = AutoDispatcher()
    return dispatcher.dispatch(ticket)
