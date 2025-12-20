from django.contrib import admin
from .models import (
    MaterialPurchaseBill, MaterialPurchaseItem,
    ClinicBill, ClinicBillItem,
    LabBill,
    Medicine, Procedure,
    PharmacyBill, PharmacyBillItem, ProcedurePayment
)

# -------------------------
# Inlines for Bill Items
# -------------------------
class MaterialPurchaseItemInline(admin.TabularInline):
    model = MaterialPurchaseItem
    extra = 1


class ClinicBillItemInline(admin.TabularInline):
    model = ClinicBillItem
    extra = 1



class ProcedurePaymentInline(admin.TabularInline):
    model = ProcedurePayment
    extra = 1


class PharmacyBillItemInline(admin.TabularInline):
    model = PharmacyBillItem
    extra = 1
    show_change_link = True  # allow opening the item to see related payments


# -------------------------
# Bill Admins
# -------------------------
@admin.register(MaterialPurchaseBill)
class MaterialPurchaseBillAdmin(admin.ModelAdmin):
    list_display = ("bill_number", "clinic", "supplier_name", "total_amount", "status", "bill_date")
    search_fields = ("bill_number", "supplier_name")
    list_filter = ("status", "bill_date")
    inlines = [MaterialPurchaseItemInline]


@admin.register(ClinicBill)
class ClinicBillAdmin(admin.ModelAdmin):
    list_display = ("bill_number", "clinic", "vendor_name", "total_amount", "status", "bill_date")
    search_fields = ("bill_number", "vendor_name")
    list_filter = ("status", "bill_date")
    inlines = [ClinicBillItemInline]


@admin.register(LabBill)
class LabBillAdmin(admin.ModelAdmin):
    list_display = ("bill_number", "clinic", "lab_name", "total_amount", "status", "bill_date")
    search_fields = ("bill_number", "lab_name")
    list_filter = ("status", "bill_date")


@admin.register(PharmacyBill)
class PharmacyBillAdmin(admin.ModelAdmin):
    list_display = ("bill_number", "clinic", "patient", "total_amount", "status", "bill_date")
    search_fields = ("bill_number", "patient__first_name", "patient__last_name")
    list_filter = ("status", "bill_date")
    inlines = [PharmacyBillItemInline]


@admin.register(PharmacyBillItem)
class PharmacyBillItemAdmin(admin.ModelAdmin):
    list_display = ("bill", "item_type", "medicine", "procedure", "quantity", "unit_price", "subtotal", "total_paid", "balance_due")
    list_filter = ("item_type",)
    search_fields = ("medicine__name", "procedure__name", "bill__bill_number")
    inlines = [ProcedurePaymentInline]


# -------------------------
# Supporting Models
# -------------------------
@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("name", "dosage", "stock", "unit_price", "expiry_date")
    search_fields = ("name", "dosage")
    list_filter = ("expiry_date",)


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
    search_fields = ("name",)


@admin.register(ProcedurePayment)
class ProcedurePaymentAdmin(admin.ModelAdmin):
    list_display = ("bill_item", "amount_paid", "payment_date", "notes")
    search_fields = ("bill_item__procedure__name", "bill_item__bill__bill_number")
    list_filter = ("payment_date",)
