from rest_framework import serializers
from .models import (
    MaterialPurchaseBill, MaterialPurchaseItem,
    ClinicBill, ClinicBillItem,
    LabBill,
    PharmacyBill, PharmacyBillItem, ProcedurePayment,
    Medicine, Procedure, Clinic, Patient,
)
from doctor_panel.models import Consultation 
from django.db.models import Sum

# -------------------- Material Purchase --------------------
class MaterialPurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialPurchaseItem
        fields = ['id', 'item_name', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['subtotal']  # subtotal is calculated automatically


class MaterialPurchaseBillSerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(source="clinic.name", read_only=True)  # show name
    clinic = serializers.PrimaryKeyRelatedField(queryset=Clinic.objects.all())  # accept ID on write
    items = MaterialPurchaseItemSerializer(many=True)

    class Meta:
        model = MaterialPurchaseBill
        fields = ['id', 'bill_number', 'clinic', 'clinic_name', 'bill_date', 'status',
                  'total_amount', 'supplier_name', 'invoice_number', 'items']
        read_only_fields = ['bill_number', 'total_amount']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])

        # First, create the bill (so it gets a primary key)
        bill = MaterialPurchaseBill.objects.create(**validated_data)

        # Now create items related to the saved bill
        for item_data in items_data:
            MaterialPurchaseItem.objects.create(bill=bill, **item_data)

        # Update total_amount
        bill.total_amount = sum(item.subtotal for item in bill.items.all())
        bill.save()
        return bill

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        # Update main bill fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            # Remove old items
            instance.items.all().delete()
            # Add new items
            for item_data in items_data:
                MaterialPurchaseItem.objects.create(bill=instance, **item_data)

            # Update total_amount
            instance.total_amount = sum(item.subtotal for item in instance.items.all())
            instance.save()

        return instance


# -------------------- Clinic Bill --------------------
class ClinicBillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicBillItem
        fields = ['id', 'item_name', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['subtotal']  # subtotal calculated automatically

class ClinicBillSerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(source="clinic.name", read_only=True)  # show name
    clinic = serializers.PrimaryKeyRelatedField(queryset=Clinic.objects.all())  # accept ID on write
    items = ClinicBillItemSerializer(many=True)

    class Meta:
        model = ClinicBill
        fields = ['id', 'bill_number', 'clinic', 'clinic_name', 'bill_date', 'status', 'total_amount', 'vendor_name', 'items']
        read_only_fields = ['bill_number', 'total_amount', 'clinic']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        bill = ClinicBill.objects.create(**validated_data)

        for item_data in items_data:
            ClinicBillItem.objects.create(bill=bill, **item_data)

        # Now calculate total_amount after items are created
        bill.total_amount = sum(item.subtotal for item in bill.items.all())
        bill.save()
        return bill

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            # Delete old items
            instance.items.all().delete()
            # Create new items
            for item_data in items_data:
                ClinicBillItem.objects.create(bill=instance, **item_data)
            # Update total_amount
            instance.total_amount = sum(item.subtotal for item in instance.items.all())
            instance.save()

        return instance


class ClinicPanelBillSerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(source="clinic.name", read_only=True)
    items = ClinicBillItemSerializer(many=True)

    class Meta:
        model = ClinicBill
        fields = [
            'id', 'bill_number', 'clinic_name',
            'bill_date', 'status', 'total_amount',
            'vendor_name', 'items'
        ]
        read_only_fields = ['bill_number', 'total_amount', 'clinic']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        bill = ClinicBill.objects.create(**validated_data)

        for item_data in items_data:
            ClinicBillItem.objects.create(bill=bill, **item_data)

        bill.total_amount = sum(item.subtotal for item in bill.items.all())
        bill.save()
        return bill

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                ClinicBillItem.objects.create(bill=instance, **item_data)
            instance.total_amount = sum(item.subtotal for item in instance.items.all())
            instance.save()

        return instance


# -------------------- Lab Bill --------------------
class LabBillSerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(
        source="clinic.name",
        read_only=True
    )

    class Meta:
        model = LabBill
        fields = [
            "id",

            # Auto / system
            "bill_number",
            "clinic",
            "clinic_name",
            "status",

            # Patient / reference
            "file_number",
            "patient",
            "patient_name",
            "doctor",

            # Lab details
            "lab_name",
            "work_description",

            # Amounts
            "lab_cost",
            "clinic_cost",
            "total_amount",

            # Invoice
            "invoice_number",
            "date",

            # Audit
            "created_at",
        ]

        read_only_fields = [
            "bill_number",
            "clinic",
            "clinic_name",
            "patient_name",
            "total_amount",
            "created_at",
        ]

    # -----------------------------------
    # CREATE
    # -----------------------------------
    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None

        # -------------------------
        # Resolve clinic
        # -------------------------
        clinic = None
        if user:
            if getattr(user, "role", "").lower() == "superadmin":
                clinic_id = request.query_params.get("clinic_id")
                if clinic_id:
                    clinic = Clinic.objects.filter(id=clinic_id).first()
            elif hasattr(user, "clinic_profile"):
                clinic = user.clinic_profile
            elif hasattr(user, "doctor_profile"):
                clinic = user.doctor_profile.clinic

        if not clinic:
            raise serializers.ValidationError(
                {"clinic": "Clinic not found or unauthorized"}
            )

        validated_data["clinic"] = clinic

        # -------------------------
        # Auto-fill patient_name
        # -------------------------
        patient = validated_data.get("patient")
        if patient:
            validated_data["patient_name"] = (
                f"{patient.first_name} {patient.last_name}".strip()
            )

            # Optional: auto-fill file_number from patient
            if not validated_data.get("file_number"):
                validated_data["file_number"] = patient.file_number

        # -------------------------
        # Total amount = clinic_cost
        # -------------------------
        validated_data["total_amount"] = validated_data.get("clinic_cost", 0)

        return super().create(validated_data)

    # -----------------------------------
    # UPDATE
    # -----------------------------------
    def update(self, instance, validated_data):
        # Prevent changing patient snapshot
        validated_data.pop("patient_name", None)
        validated_data.pop("clinic", None)
        validated_data.pop("bill_number", None)

        # Recalculate total if clinic_cost changes
        if "clinic_cost" in validated_data:
            validated_data["total_amount"] = validated_data["clinic_cost"]

        return super().update(instance, validated_data)

class LabPanelBillSerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(
        source="clinic.name",
        read_only=True
    )

    class Meta:
        model = LabBill
        fields = [
            "id",
            "bill_number",
            "clinic_name",
            "status",

            # Patient / reference
            "file_number",
            "patient",
            "patient_name",
            "doctor",

            # Lab details
            "lab_name",
            "work_description",

            # Amounts
            "lab_cost",
            "clinic_cost",
            "total_amount",

            # Invoice
            "invoice_number",
            "date",

            "created_at",
        ]

        read_only_fields = [
            "bill_number",
            "clinic_name",
            "patient_name",
            "total_amount",
            "created_at",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None

        # -------------------------
        # Resolve clinic
        # -------------------------
        clinic = None
        if getattr(user, "role", "").lower() == "superadmin":
            clinic_id = request.query_params.get("clinic_id")
            if clinic_id:
                clinic = Clinic.objects.filter(id=clinic_id).first()
        elif hasattr(user, "clinic_profile"):
            clinic = user.clinic_profile
        elif hasattr(user, "doctor_profile"):
            clinic = user.doctor_profile.clinic

        if not clinic:
            raise serializers.ValidationError(
                {"clinic": "Clinic not found or unauthorized"}
            )

        validated_data["clinic"] = clinic

        # -------------------------
        # Auto-fill patient_name
        # -------------------------
        patient = validated_data.get("patient")
        if patient:
            validated_data["patient_name"] = (
                f"{patient.first_name} {patient.last_name}".strip()
            )

            if not validated_data.get("file_number"):
                validated_data["file_number"] = patient.file_number

        # -------------------------
        # Total amount
        # -------------------------
        validated_data["total_amount"] = validated_data.get("clinic_cost", 0)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Prevent immutable changes
        validated_data.pop("clinic", None)
        validated_data.pop("bill_number", None)
        validated_data.pop("patient_name", None)

        if "clinic_cost" in validated_data:
            validated_data["total_amount"] = validated_data["clinic_cost"]

        return super().update(instance, validated_data)

# -------------------- Pharmacy --------------------
class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ['id', 'name', 'dosage', 'stock', 'unit_price', 'expiry_date', 'clinic']
        read_only_fields = ['clinic']

class ProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = ['id', 'name', 'description', 'price', 'clinic']
        read_only_fields = ['clinic']



# class ProcedurePaymentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProcedurePayment
#         fields = ['id', 'bill_item', 'amount_paid', 'payment_date', 'notes']

# ------------------------------------------------------------------------------------------------


class ProcedurePaymentSerializer(serializers.ModelSerializer):
    bill_number = serializers.CharField(source="bill_item.bill.bill_number", read_only=True)
    procedure_name = serializers.CharField(source="bill_item.procedure.name", read_only=True)
    balance_due = serializers.SerializerMethodField()
    payment_date = serializers.DateField(read_only=True)

    class Meta:
        model = ProcedurePayment
        fields = [
            "id",
            "amount_paid",
            "payment_date",
            "notes",
            "bill_item",       # include it for creation
            "bill_number",
            "procedure_name",
            "balance_due",     # include it in the response
        ]
        read_only_fields = ["bill_number", "procedure_name", "balance_due"]
        extra_kwargs = {
            "bill_item": {"required": False, "allow_null": True},
        }

    def validate_bill_item(self, value):
        if value and value.item_type != "PROCEDURE":
            raise serializers.ValidationError("Selected bill_item is not a procedure.")
        return value

    def get_balance_due(self, obj):
        """
        Balance due after THIS installment.
        """
        if not obj.bill_item:
            return None

        subtotal = obj.bill_item.subtotal or 0

        paid_till_now = (
            ProcedurePayment.objects
            .filter(
                bill_item=obj.bill_item,
                id__lte=obj.id
            )
            .aggregate(total=Sum("amount_paid"))["total"] or 0
        )

        return float(subtotal - paid_till_now)

    

# --------------------------------------------------------------------------------------------------------

class PharmacyBillItemSerializer(serializers.ModelSerializer):
    medicine_id = serializers.PrimaryKeyRelatedField(
        source="medicine", queryset=Medicine.objects.all(),
        required=False, allow_null=True, write_only=True
    )
    procedure_id = serializers.PrimaryKeyRelatedField(
        source="procedure", queryset=Procedure.objects.all(),
        required=False, allow_null=True, write_only=True
    )

    medicine = serializers.StringRelatedField(read_only=True)
    procedure = serializers.StringRelatedField(read_only=True)

    total_paid = serializers.ReadOnlyField()
    balance_due = serializers.ReadOnlyField()
    procedure_payments = ProcedurePaymentSerializer(many=True, required=False)

    class Meta:
        model = PharmacyBillItem
        fields = [
            "id", "item_type",
            "medicine_id", "medicine",
            "procedure_id", "procedure",
            "quantity", "unit_price", "subtotal",
            "total_paid", "balance_due",
            "procedure_payments",
        ]


class PharmacyBillSerializer(serializers.ModelSerializer):
    clinic_id = serializers.PrimaryKeyRelatedField(
        source="clinic", queryset=Clinic.objects.all(), write_only=True
    )
    patient_id = serializers.PrimaryKeyRelatedField(
        source="patient", queryset=Patient.objects.all(), write_only=True
    )

    clinic = serializers.StringRelatedField(read_only=True)
    patient = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    items = PharmacyBillItemSerializer(many=True, required=False)
    paid_amount = serializers.SerializerMethodField()

    class Meta:
        model = PharmacyBill
        fields = [
            'id', 'bill_number',
            'clinic_id', 'clinic',
            'patient_id', 'patient',
            'bill_date', 'status',
            'total_amount', 'paid_amount',
            'doctor_name', 'items'
        ]
        read_only_fields = ['bill_number', 'total_amount']

    def get_patient(self, obj):
        if obj.patient:
            return {
                "name": f"{obj.patient.first_name} {obj.patient.last_name}".strip(),
                "dob": obj.patient.dob,
                "gender": obj.patient.get_gender_display() if obj.patient.gender else None,
                "address": obj.patient.address,
            }
        return None

    def get_doctor_name(self, obj):
        if hasattr(obj, "doctor") and obj.doctor:
            return obj.doctor.name
        if hasattr(obj, "consultation") and obj.consultation and obj.consultation.doctor:
            return obj.consultation.doctor.name
        latest_consult = (
            Consultation.objects.filter(
                patient=obj.patient,
                doctor__clinic=obj.clinic
            )
            .select_related("doctor")
            .order_by("-created_at")
            .first()
        )
        if latest_consult and latest_consult.doctor:
            return latest_consult.doctor.name
        return None

    def get_paid_amount(self, obj):
        total_balance_due = sum(item.balance_due for item in obj.items.all())
        return obj.total_amount - total_balance_due

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        bill = PharmacyBill.objects.create(**validated_data)

        for item_data in items_data:
            procedure_payments_data = item_data.pop('procedure_payments', [])
            bill_item = PharmacyBillItem.objects.create(
                bill=bill,
                item_type=item_data.get('item_type'),
                medicine=item_data.get('medicine'),
                procedure=item_data.get('procedure'),
                quantity=item_data.get('quantity', 1),
                unit_price=item_data.get('unit_price', 0),
            )

            if bill_item.item_type == "PROCEDURE":
                for payment_data in procedure_payments_data:
                    ProcedurePayment.objects.create(
                        bill_item=bill_item,
                        amount_paid=payment_data.get('amount_paid', 0),
                        notes=payment_data.get('notes', '')
                    )

        bill.total_amount = sum(item.subtotal for item in bill.items.all())
        bill.save()
        return bill

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            # Delete old items & payments
            for item in instance.items.all():
                if item.item_type == "PROCEDURE":
                    item.payments.all().delete()
            instance.items.all().delete()

            # Recreate items & payments
            for item_data in items_data:
                procedure_payments_data = item_data.pop('procedure_payments', [])
                bill_item = PharmacyBillItem.objects.create(
                    bill=instance,
                    item_type=item_data.get('item_type'),
                    medicine=item_data.get('medicine'),
                    procedure=item_data.get('procedure'),
                    quantity=item_data.get('quantity', 1),
                    unit_price=item_data.get('unit_price', 0),
                )
                if bill_item.item_type == "PROCEDURE":
                    for payment_data in procedure_payments_data:
                        ProcedurePayment.objects.create(
                            bill_item=bill_item,
                            amount_paid=payment_data.get('amount_paid', 0),
                            notes=payment_data.get('notes', '')
                        )

        instance.total_amount = sum(item.subtotal for item in instance.items.all())
        instance.save()
        return instance


class ClinicPharmacyBillItemSerializer(serializers.ModelSerializer):
    # Accept medicine/procedure by ID for POST/PUT
    medicine_id = serializers.PrimaryKeyRelatedField(
        source="medicine",
        queryset=Medicine.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )
    procedure_id = serializers.PrimaryKeyRelatedField(
        source="procedure",
        queryset=Procedure.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )

    # Return full details for GET
    medicine = serializers.StringRelatedField(read_only=True)
    procedure = serializers.StringRelatedField(read_only=True)

    total_paid = serializers.ReadOnlyField()
    balance_due = serializers.ReadOnlyField()

    # Nested procedure payments
    procedure_payments = ProcedurePaymentSerializer(many=True, required=False)

    class Meta:
        model = PharmacyBillItem
        fields = [
            "id", "item_type",
            "medicine_id", "medicine",
            "procedure_id", "procedure",
            "quantity", "unit_price", "subtotal",
            "total_paid", "balance_due",
            "procedure_payments",
        ]

class ClinicPharmacyBillSerializer(serializers.ModelSerializer):
    clinic = serializers.StringRelatedField(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        source="patient",
        queryset=Patient.objects.all(),
        write_only=True
    )
    patient = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    items = ClinicPharmacyBillItemSerializer(many=True, required=False)
    paid_amount = serializers.SerializerMethodField()

    class Meta:
        model = PharmacyBill
        fields = [
            'id', 'bill_number',
            'clinic', 'patient_id', 'patient',
            'bill_date', 'status', 'total_amount', 'paid_amount',
            'doctor_name',
            'items',
        ]
        read_only_fields = ['bill_number', 'total_amount', 'clinic']

    def get_patient(self, obj):
        if obj.patient:
            return {
                "name": f"{obj.patient.first_name} {obj.patient.last_name}".strip(),
                "dob": obj.patient.dob,
                "gender": obj.patient.get_gender_display() if obj.patient.gender else None,
                "address": obj.patient.address,
            }
        return None

    def get_doctor_name(self, obj):
        if hasattr(obj, "doctor") and obj.doctor:
            return obj.doctor.name
        if hasattr(obj, "consultation") and obj.consultation and obj.consultation.doctor:
            return obj.consultation.doctor.name
        latest_consult = (
            Consultation.objects.filter(patient=obj.patient, doctor__clinic=obj.clinic)
            .select_related("doctor")
            .order_by("-created_at")
            .first()
        )
        if latest_consult and latest_consult.doctor:
            return latest_consult.doctor.name
        return None

    def get_paid_amount(self, obj):
        total_balance_due = sum(item.balance_due for item in obj.items.all())
        return obj.total_amount - total_balance_due

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        clinic = self.context['clinic']
        bill = PharmacyBill.objects.create(clinic=clinic, **validated_data)

        for item_data in items_data:
            procedure_payments_data = item_data.pop('procedure_payments', [])
            bill_item = PharmacyBillItem.objects.create(
                bill=bill,
                item_type=item_data.get('item_type'),
                medicine=item_data.get('medicine'),
                procedure=item_data.get('procedure'),
                quantity=item_data.get('quantity', 1),
                unit_price=item_data.get('unit_price', 0)
            )

            # Create procedure payments if this is a PROCEDURE item
            if bill_item.item_type == "PROCEDURE":
                for payment in procedure_payments_data:
                    ProcedurePayment.objects.create(
                        bill_item=bill_item,
                        amount_paid=payment.get('amount_paid', 0),
                        notes=payment.get('notes', '')
                    )

        # Update total amount
        bill.total_amount = sum(item.subtotal for item in bill.items.all())
        bill.save()
        return bill

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            # Delete existing items and their procedure payments
            for item in instance.items.all():
                if item.item_type == "PROCEDURE":
                    item.payments.all().delete()
            instance.items.all().delete()

            # Create new items and payments
            for item_data in items_data:
                procedure_payments_data = item_data.pop('procedure_payments', [])
                bill_item = PharmacyBillItem.objects.create(
                    bill=instance,
                    item_type=item_data.get('item_type'),
                    medicine=item_data.get('medicine'),
                    procedure=item_data.get('procedure'),
                    quantity=item_data.get('quantity', 1),
                    unit_price=item_data.get('unit_price', 0)
                )

                if bill_item.item_type == "PROCEDURE":
                    for payment in procedure_payments_data:
                        ProcedurePayment.objects.create(
                            bill_item=bill_item,
                            amount_paid=payment.get('amount_paid', 0),
                            notes=payment.get('notes', '')
                        )

        instance.total_amount = sum(item.subtotal for item in instance.items.all())
        instance.save()
        return instance


# ---------------------------------------------------------------------------------------------------
