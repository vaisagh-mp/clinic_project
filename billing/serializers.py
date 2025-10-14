from rest_framework import serializers
from .models import (
    MaterialPurchaseBill, MaterialPurchaseItem,
    ClinicBill, ClinicBillItem,
    LabBill, LabBillItem,
    PharmacyBill, PharmacyBillItem, ProcedurePayment,
    Medicine, Procedure, Clinic, Patient,
)
from doctor_panel.models import Consultation 

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
class LabBillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabBillItem
        fields = ['id', 'test_or_service', 'cost']


class LabBillSerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(source="clinic.name", read_only=True)  # show name
    clinic = serializers.PrimaryKeyRelatedField(queryset=Clinic.objects.all())  # accept ID on write
    items = LabBillItemSerializer(many=True)

    class Meta:
        model = LabBill
        fields = ['id', 'bill_number', 'clinic', 'clinic_name', 'bill_date', 'status', 'total_amount',
                  'lab_name', 'work_description', 'items']
        read_only_fields = ['bill_number', 'total_amount']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])

        # Create bill first (gets primary key)
        bill = LabBill.objects.create(**validated_data)

        # Create items linked to bill
        for item_data in items_data:
            LabBillItem.objects.create(bill=bill, **item_data)

        # Update total_amount
        bill.total_amount = sum(item.cost for item in bill.items.all())
        bill.save()
        return bill

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        # Update main bill fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                LabBillItem.objects.create(bill=instance, **item_data)

            instance.total_amount = sum(item.cost for item in instance.items.all())
            instance.save()

        return instance

class LabPanelBillSerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(source="clinic.name", read_only=True)  # Show clinic name
    items = LabBillItemSerializer(many=True)  # Nested items

    class Meta:
        model = LabBill
        fields = ['id', 'bill_number', 'clinic_name', 'bill_date', 'status', 'total_amount',
                  'lab_name', 'work_description', 'items']
        read_only_fields = ['bill_number', 'total_amount', 'clinic_name', 'clinic']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])

        # Assign clinic automatically from context/user
        clinic = self.context['request'].user.clinic_profile
        bill = LabBill.objects.create(clinic=clinic, **validated_data)

        for item_data in items_data:
            LabBillItem.objects.create(bill=bill, **item_data)

        # Update total_amount
        bill.total_amount = sum(item.cost for item in bill.items.all())
        bill.save()
        return bill

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        # Update main bill fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                LabBillItem.objects.create(bill=instance, **item_data)

            instance.total_amount = sum(item.cost for item in instance.items.all())
            instance.save()

        return instance
# -------------------- Pharmacy --------------------
class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ['id', 'name', 'dosage', 'stock', 'unit_price', 'expiry_date']


class ProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = ['id', 'name', 'description', 'price']


# class ProcedurePaymentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProcedurePayment
#         fields = ['id', 'bill_item', 'amount_paid', 'payment_date', 'notes']

# ------------------------------------------------------------------------------------------------


class ProcedurePaymentSerializer(serializers.ModelSerializer):
    # Read-only computed fields
    bill_number = serializers.CharField(source="bill_item.bill.bill_number", read_only=True)
    procedure_name = serializers.CharField(source="bill_item.procedure.name", read_only=True)

    # Write-only field for linking to a bill item
    bill_item = serializers.PrimaryKeyRelatedField(
        queryset=PharmacyBillItem.objects.all(),
        required=True,
        write_only=True
    )

    class Meta:
        model = ProcedurePayment
        fields = [
            "id",
            "bill_item",       # write-only (required for POST)
            "amount_paid",
            "notes",
            "bill_number",     # read-only
            "procedure_name",  # read-only
        ]
        read_only_fields = ["bill_number", "procedure_name"]

    def validate_bill_item(self, value):
        # Ensure the selected bill item is a procedure
        if value.item_type != "PROCEDURE":
            raise serializers.ValidationError("Selected bill_item is not a procedure.")
        return value
    

# --------------------------------------------------------------------------------------------------------

class PharmacyBillItemSerializer(serializers.ModelSerializer):
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
    medicine = serializers.StringRelatedField(read_only=True)  # will call __str__()
    procedure = serializers.StringRelatedField(read_only=True)

    total_paid = serializers.ReadOnlyField()
    balance_due = serializers.ReadOnlyField()

    class Meta:
        model = PharmacyBillItem
        fields = [
            "id", "item_type",
            "medicine_id", "medicine",
            "procedure_id", "procedure",
            "quantity", "unit_price", "subtotal",
            "total_paid", "balance_due"
        ]

class PharmacyBillSerializer(serializers.ModelSerializer):
    # Accept IDs on write
    clinic_id = serializers.PrimaryKeyRelatedField(
        source="clinic",
        queryset=Clinic.objects.all(),
        write_only=True
    )
    patient_id = serializers.PrimaryKeyRelatedField(
        source="patient",
        queryset=Patient.objects.all(),
        write_only=True
    )

    # Show names and nested details on read
    clinic = serializers.StringRelatedField(read_only=True)
    patient = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()  # ✅ NEW
    items = PharmacyBillItemSerializer(many=True, required=False)

    class Meta:
        model = PharmacyBill
        fields = [
            'id', 'bill_number',
            'clinic_id', 'clinic',
            'patient_id', 'patient',
            'bill_date', 'status', 'total_amount',
            'doctor_name',  # ✅ NEW
            'items'
        ]
        read_only_fields = ['bill_number', 'total_amount']

    def get_patient(self, obj):
        """Return detailed patient info."""
        if obj.patient:
            return {
                "name": f"{obj.patient.first_name} {obj.patient.last_name}".strip(),
                "dob": obj.patient.dob,
                "gender": obj.patient.get_gender_display() if obj.patient.gender else None,
                "address": obj.patient.address,
            }
        return None

    def get_doctor_name(self, obj):
        """Return consulting doctor name if linked via consultation."""
        # Case 1: if PharmacyBill directly has a doctor field
        if hasattr(obj, "doctor") and obj.doctor:
            return obj.doctor.name

        # Case 2: if there is a related consultation object
        if hasattr(obj, "consultation") and obj.consultation and obj.consultation.doctor:
            return obj.consultation.doctor.name

        # Case 3: find latest consultation where doctor belongs to same clinic
        latest_consult = (
            Consultation.objects.filter(
                patient=obj.patient,
                doctor__clinic=obj.clinic  # ✅ FIXED lookup
            )
            .select_related("doctor")
            .order_by("-created_at")
            .first()
        )
        if latest_consult and latest_consult.doctor:
            return latest_consult.doctor.name

        return None

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        bill = PharmacyBill.objects.create(**validated_data)

        for item_data in items_data:
            item_type = item_data.get('item_type')
            quantity = item_data.get('quantity', 1)

            PharmacyBillItem.objects.create(
                bill=bill,
                item_type=item_type,
                medicine=item_data.get('medicine'),
                procedure=item_data.get('procedure'),
                quantity=quantity,
                unit_price=item_data.get('unit_price', 0)
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
            instance.items.all().delete()
            for item_data in items_data:
                PharmacyBillItem.objects.create(
                    bill=instance,
                    item_type=item_data.get('item_type'),
                    medicine=item_data.get('medicine'),
                    procedure=item_data.get('procedure'),
                    quantity=item_data.get('quantity', 1),
                    unit_price=item_data.get('unit_price', 0)
                )

            instance.total_amount = sum(item.subtotal for item in instance.items.all())
            instance.save()

        return instance


# serializers.py

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
