from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from clinic_panel.models import Clinic, Patient


# -----------------------
# Base Bill
# -----------------------
class BaseBill(models.Model):
    BILL_STATUS = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="%(class)s_bills")
    bill_number = models.CharField(max_length=20, unique=True, editable=False)
    bill_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=BILL_STATUS, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.bill_number} ({self.clinic.name})"


# -----------------------
# 1. Material Purchase Bill
# -----------------------
class MaterialPurchaseBill(BaseBill):
    supplier_name = models.CharField(max_length=200)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Generate Bill Number if not exists
        if not self.bill_number:
            last = MaterialPurchaseBill.objects.order_by('id').last()
            if last and last.bill_number:
                try:
                    number = int(last.bill_number.split('-')[-1]) + 1
                except ValueError:
                    number = 1
            else:
                number = 1
            self.bill_number = f"MPB-{number:05d}"

        super().save(*args, **kwargs)


class MaterialPurchaseItem(models.Model):
    bill = models.ForeignKey(MaterialPurchaseBill, on_delete=models.CASCADE, related_name="items")
    item_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

        # Update bill total_amount automatically after saving item
        bill = self.bill
        bill.total_amount = sum(item.subtotal for item in bill.items.all())
        bill.save()


# -----------------------
# 2. Clinic Bill
# -----------------------
class ClinicBill(BaseBill):
    vendor_name = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        # Generate Bill Number if not exists
        if not self.bill_number:
            last = ClinicBill.objects.order_by('id').last()
            if last and last.bill_number:
                try:
                    number = int(last.bill_number.split('-')[-1]) + 1
                except ValueError:
                    number = 1
            else:
                number = 1
            self.bill_number = f"CB-{number:05d}"

        super().save(*args, **kwargs)  



class ClinicBillItem(models.Model):
    bill = models.ForeignKey(ClinicBill, on_delete=models.CASCADE, related_name="items")
    item_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

        # Update bill total_amount automatically after saving item
        bill = self.bill
        bill.total_amount = sum(item.subtotal for item in bill.items.all())
        bill.save()


# -----------------------
# 3. Lab Bill
# -----------------------
class LabBill(BaseBill):
    lab_name = models.CharField(max_length=200)
    work_description = models.TextField()

    def save(self, *args, **kwargs):
        # Generate Bill Number if not exists
        if not self.bill_number:
            last = LabBill.objects.order_by('id').last()
            if last and last.bill_number:
                try:
                    number = int(last.bill_number.split('-')[-1]) + 1
                except ValueError:
                    number = 1
            else:
                number = 1
            self.bill_number = f"LB-{number:05d}"

        # DO NOT calculate total here on creation
        super().save(*args, **kwargs)


class LabBillItem(models.Model):
    bill = models.ForeignKey(LabBill, on_delete=models.CASCADE, related_name="items")
    test_or_service = models.CharField(max_length=200)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Update bill total_amount automatically after saving item
        bill = self.bill
        bill.total_amount = sum(item.cost for item in bill.items.all())
        bill.save()

    def __str__(self):
        return f"{self.test_or_service} - {self.cost}"


# -----------------------
# 4. Pharmacy - Medicines & Procedures
# -----------------------
class Medicine(models.Model):
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=50, blank=True, null=True)  # e.g., "500mg"
    stock = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.dosage})" if self.dosage else self.name


class Procedure(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class PharmacyBill(BaseBill):
    patient = models.ForeignKey("clinic_panel.Patient", on_delete=models.CASCADE, related_name="pharmacy_bills")
    bill_number = models.CharField(max_length=20, unique=True, editable=False)

    def __str__(self):
        return f"Pharmacy Bill #{self.bill_number} - {self.patient.first_name} {self.patient.last_name}"

    def save(self, *args, **kwargs):
        if not self.bill_number:
            # Get the last valid bill number
            last_bill = PharmacyBill.objects.exclude(bill_number='').order_by('id').last()
            if last_bill and last_bill.bill_number.startswith('PB-'):
                try:
                    last_number = int(last_bill.bill_number.split('-')[-1])
                except ValueError:
                    last_number = 0
            else:
                last_number = 0
            # Generate new bill number
            self.bill_number = f"PB-{last_number + 1:05d}"

        super().save(*args, **kwargs)



class PharmacyBillItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('MEDICINE', 'Medicine'),
        ('PROCEDURE', 'Procedure'),
    ]

    bill = models.ForeignKey("PharmacyBill", on_delete=models.CASCADE, related_name="items")
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    medicine = models.ForeignKey("Medicine", on_delete=models.SET_NULL, null=True, blank=True)
    procedure = models.ForeignKey("Procedure", on_delete=models.SET_NULL, null=True, blank=True)

    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def clean(self):
        if self.item_type == "MEDICINE" and not self.medicine:
            raise ValidationError("Medicine must be selected for medicine items.")
        if self.item_type == "PROCEDURE" and not self.procedure:
            raise ValidationError("Procedure must be selected for procedure items.")

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        # Auto-fill unit_price if not set
        if self.item_type == 'MEDICINE' and self.medicine:
            self.unit_price = self.medicine.unit_price
        elif self.item_type == 'PROCEDURE' and self.procedure:
            self.unit_price = self.procedure.price

        self.subtotal = self.quantity * self.unit_price

        # Handle medicine stock only when creating a new item
        if is_new and self.item_type == 'MEDICINE' and self.medicine:
            if self.medicine.stock < self.quantity:
                raise ValueError("Not enough stock available")
            self.medicine.stock -= self.quantity
            self.medicine.save()

        super().save(*args, **kwargs)

        # Update bill total
        total = sum(item.subtotal for item in self.bill.items.all())
        self.bill.total_amount = total
        self.bill.save()

    def __str__(self):
        if self.item_type == "PROCEDURE" and self.procedure:
            return f"{self.procedure.name} - {self.subtotal}"
        elif self.item_type == "MEDICINE" and self.medicine:
            return f"{self.medicine.name} - {self.subtotal}"
        return f"{self.item_type} - {self.subtotal}"

    @property
    def total_paid(self):
        if self.item_type == "PROCEDURE":
            return sum(payment.amount_paid for payment in self.payments.all())
        return self.subtotal  # Medicines are assumed to be fully paid

    @property
    def balance_due(self):
        return self.subtotal - self.total_paid



class ProcedurePayment(models.Model):
    bill_item = models.ForeignKey(
        PharmacyBillItem,
        on_delete=models.CASCADE,
        related_name="payments",
        limit_choices_to={'item_type': 'PROCEDURE'}
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        bill_number = self.bill_item.bill.bill_number if self.bill_item.bill else "N/A"
        procedure_name = self.bill_item.procedure.name if self.bill_item.procedure else "Procedure"
        return f"{bill_number} - Payment of {self.amount_paid} for {procedure_name}"

