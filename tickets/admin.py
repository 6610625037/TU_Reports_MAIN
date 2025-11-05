from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import (
    Category, Department, Ticket, TicketStatusHistory, Attachment,
    TechnicianPresence, AssignmentRule, TicketFeedback, BeforeAfterPhoto
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('dep_name', 'org_name_th', 'dep_code', 'is_active', 'last_synced')
    list_filter = ('is_active', 'org_code')
    search_fields = ('dep_name', 'org_name_th', 'dep_code')


@admin.register(Ticket)
class TicketAdmin(GISModelAdmin):
    list_display = ('id', 'title', 'category', 'status', 'urgency_level', 'created_by', 'assigned_to', 'created_at')
    list_filter = ('status', 'urgency_level', 'category', 'created_at')
    search_fields = ('title', 'description', 'id')
    readonly_fields = ('created_at', 'updated_at', 'priority_score')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('ข้อมูลพื้นฐาน', {
            'fields': ('title', 'description', 'category')
        }),
        ('ผู้ใช้งาน', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('สถานที่', {
            'fields': ('location', 'address_description')
        }),
        ('ลำดับความสำคัญ', {
            'fields': ('urgency_level', 'priority_score', 'status')
        }),
        ('การปฏิเสธ', {
            'fields': ('reject_reason',)
        }),
        ('เวลา', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )


@admin.register(TicketStatusHistory)
class TicketStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'old_status', 'new_status', 'changed_by', 'timestamp')
    list_filter = ('new_status', 'timestamp')
    search_fields = ('ticket__title', 'comment')
    readonly_fields = ('timestamp',)


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'file', 'uploaded_by', 'file_size', 'uploaded_at')
    list_filter = ('uploaded_at',)
    readonly_fields = ('uploaded_at', 'file_size')


@admin.register(TechnicianPresence)
class TechnicianPresenceAdmin(GISModelAdmin):
    list_display = ('technician', 'is_available', 'updated_at')
    list_filter = ('is_available',)
    search_fields = ('technician__username',)


@admin.register(AssignmentRule)
class AssignmentRuleAdmin(admin.ModelAdmin):
    list_display = ('max_open_tickets', 'weight_distance', 'weight_workload', 'is_active', 'created_at')
    list_filter = ('is_active',)


@admin.register(TicketFeedback)
class TicketFeedbackAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'technician', 'overall_rating', 'created_by', 'created_at')
    list_filter = ('overall_rating', 'created_at')
    search_fields = ('ticket__title', 'technician__username', 'comment')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Ticket Info', {
            'fields': ('ticket', 'created_by', 'technician')
        }),
        ('Overall Rating', {
            'fields': ('overall_rating',)
        }),
        ('Detailed Ratings', {
            'fields': ('response_speed_rating', 'work_quality_rating', 'politeness_rating', 'cleanliness_rating'),
            'classes': ('collapse',)
        }),
        ('Comment', {
            'fields': ('comment',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(BeforeAfterPhoto)
class BeforeAfterPhotoAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'photo_type', 'uploaded_by', 'file_size', 'uploaded_at')
    list_filter = ('photo_type', 'uploaded_at')
    search_fields = ('ticket__title',)
    readonly_fields = ('uploaded_at', 'file_size')

    fieldsets = (
        ('Photo Info', {
            'fields': ('ticket', 'photo_type', 'image')
        }),
        ('Upload Info', {
            'fields': ('uploaded_by', 'file_size', 'uploaded_at')
        }),
    )
