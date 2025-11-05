from django.contrib.gis.db import models as gis_models
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Category(models.Model):
    """หมวดหมู่ของ Ticket เช่น ไฟฟ้า, ประปา, IT"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Tailwind icon class
    color = models.CharField(max_length=20, default='blue')  # Tailwind color
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Department(models.Model):
    """แผนก/หน่วยงาน (sync จาก TU API)"""
    org_code = models.CharField(max_length=20)
    org_name_th = models.CharField(max_length=200)
    org_name_en = models.CharField(max_length=200)
    dep_code = models.CharField(max_length=20, unique=True)
    dep_name = models.CharField(max_length=200)
    last_synced = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'departments'
        indexes = [
            models.Index(fields=['org_code']),
            models.Index(fields=['dep_code']),
        ]

    def __str__(self):
        return f"{self.dep_name} ({self.org_name_th})"


class Ticket(models.Model):
    """Ticket สำหรับแจ้งปัญหา"""
    STATUS_CHOICES = [
        ('PENDING', 'รอดำเนินการ'),
        ('IN_PROGRESS', 'รับงานแล้ว'),
        ('INSPECTING', 'กำลังตรวจสอบ'),
        ('WORKING', 'กำลังดำเนินการ'),
        ('COMPLETED', 'เสร็จสิ้น'),
        ('CLOSED', 'ปิดงาน'),
        ('REJECTED', 'ปฏิเสธ'),
    ]

    URGENCY_CHOICES = [
        ('LOW', 'ต่ำ'),
        ('MEDIUM', 'ปกติ'),
        ('HIGH', 'สูง'),
        ('CRITICAL', 'ด่วนมาก'),
    ]

    # Basic Info
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='tickets'
    )

    # User & Assignment
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tickets'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )

    # Location (PostGIS Point)
    location = gis_models.PointField(null=True, blank=True, srid=4326)
    address_description = models.TextField(blank=True)  # คำอธิบายสถานที่

    # Priority & Status
    urgency_level = models.CharField(
        max_length=20,
        choices=URGENCY_CHOICES,
        default='MEDIUM'
    )
    priority_score = models.FloatField(default=0.0)  # คำนวณโดย Auto Dispatcher
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    # Rejection
    reject_reason = models.TextField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['-priority_score']),
        ]

    def __str__(self):
        return f"#{self.id} - {self.title} ({self.get_status_display()})"

    def is_overdue(self):
        """Check if ticket is overdue"""
        if self.status == 'CLOSED':
            return False

        now = timezone.now()

        if self.status == 'PENDING' and (now - self.created_at) > timedelta(hours=24):
            return True

        if self.status in ['IN_PROGRESS', 'INSPECTING', 'WORKING'] and (now - self.created_at) > timedelta(hours=72):
            return True

        return False


class TicketStatusHistory(models.Model):
    """ประวัติการเปลี่ยนสถานะของ Ticket"""
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    comment = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ticket_status_history'
        ordering = ['-timestamp']
        verbose_name_plural = 'Ticket Status Histories'

    def __str__(self):
        return f"Ticket #{self.ticket.id}: {self.old_status} → {self.new_status}"


class Attachment(models.Model):
    """ไฟล์แนบของ Ticket"""
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.ImageField(upload_to='ticket_images/%Y/%m/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField(default=0)  # bytes

    class Meta:
        db_table = 'attachments'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Attachment for Ticket #{self.ticket.id}"


class TechnicianPresence(models.Model):
    """ตำแหน่งปัจจุบันของช่าง (สำหรับ Auto Dispatcher)"""
    technician = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='presence'
    )
    location = gis_models.PointField(null=True, blank=True, srid=4326)
    updated_at = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = 'technician_presence'

    def __str__(self):
        return f"{self.technician.username} - Available: {self.is_available}"

    def active_tickets_count(self):
        """นับจำนวนงานที่ยังไม่เสร็จ"""
        return self.technician.assigned_tickets.exclude(
            status__in=['COMPLETED', 'CLOSED', 'REJECTED']
        ).count()


class AssignmentRule(models.Model):
    """กฎการมอบหมายงานอัตโนมัติ"""
    max_open_tickets = models.IntegerField(default=5)
    weight_distance = models.FloatField(default=0.6)  # น้ำหนักระยะทาง
    weight_workload = models.FloatField(default=0.4)  # น้ำหนักจำนวนงาน
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'assignment_rules'

    def __str__(self):
        return f"Assignment Rule (Max: {self.max_open_tickets} tickets)"


class TicketFeedback(models.Model):
    """
    Feedback/Rating หลังงานเสร็จ - PRIORITY 🔴
    """
    ticket = models.OneToOneField(
        Ticket,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks_given'
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks_received'
    )

    # Overall Rating (1-5 stars) - Required
    overall_rating = models.IntegerField(
        choices=[(i, f"{i} ดาว") for i in range(1, 6)]
    )

    # Detailed Ratings (optional)
    response_speed_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, f"{i} ดาว") for i in range(1, 6)]
    )
    work_quality_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, f"{i} ดาว") for i in range(1, 6)]
    )
    politeness_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, f"{i} ดาว") for i in range(1, 6)]
    )
    cleanliness_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, f"{i} ดาว") for i in range(1, 6)]
    )

    # Comment (optional)
    comment = models.TextField(blank=True, max_length=500)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ticket_feedbacks'
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback for Ticket #{self.ticket.id} - {self.overall_rating} stars"


class BeforeAfterPhoto(models.Model):
    """
    รูปภาพก่อน-หลังการทำงาน - PRIORITY 🔴
    """
    PHOTO_TYPE_CHOICES = [
        ('BEFORE', 'ก่อนทำงาน'),
        ('AFTER', 'หลังทำงาน'),
    ]

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='before_after_photos'
    )
    photo_type = models.CharField(max_length=10, choices=PHOTO_TYPE_CHOICES)
    image = models.ImageField(upload_to='before_after/%Y/%m/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField(default=0)  # bytes

    class Meta:
        db_table = 'before_after_photos'
        ordering = ['photo_type', 'uploaded_at']

    def __str__(self):
        return f"{self.get_photo_type_display()} - Ticket #{self.ticket.id}"
