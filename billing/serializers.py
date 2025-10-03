from rest_framework import serializers
from .models import (
    MaterialPurchaseBill, MaterialPurchaseItem,
    ClinicBill, ClinicBillItem,
    LabBill, LabBillItem,
    PharmacyBill, PharmacyBillItem, ProcedurePayment,
    Medicine, Procedure, Clinic, Patient
)


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
        fields = ['id', 'bill_number', 'clinic', 'bill_date', 'status',
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
        fields = ['id', 'bill_number', 'clinic', 'bill_date', 'status', 'total_amount', 'vendor_name', 'items']
        read_only_fields = ['bill_number', 'total_amount']

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
        fields = ['id', 'bill_number', 'clinic', 'bill_date', 'status', 'total_amount',
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


# -------------------- Pharmacy --------------------
class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ['id', 'name', 'dosage', 'stock', 'unit_price', 'expiry_date']


class ProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = ['id', 'name', 'description', 'price']


class ProcedurePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedurePayment
        fields = ['id', 'bill_item', 'amount_paid', 'payment_date', 'notes']

# ------------------------------------------------------------------------------------------------

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

    # Show names on read
    clinic = serializers.StringRelatedField(read_only=True)   # will call Clinic.__str__()
    patient = serializers.SerializerMethodField()

    items = PharmacyBillItemSerializer(many=True, required=False)

    class Meta:
        model = PharmacyBill
        fields = [
            'id', 'bill_number',
            'clinic_id', 'clinic',
            'patient_id', 'patient',
            'bill_date', 'status', 'total_amount',
            'items'
        ]
        read_only_fields = ['bill_number', 'total_amount']

    def get_patient(self, obj):
        if obj.patient:
            return f"{obj.patient.first_name} {obj.patient.last_name}".strip()
        return None

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        bill = PharmacyBill.objects.create(**validated_data)

        for item_data in items_data:
            item_type = item_data.get('item_type')
            quantity = item_data.get('quantity', 1)

            if item_type == 'MEDICINE':
                PharmacyBillItem.objects.create(
                    bill=bill,
                    item_type='MEDICINE',
                    medicine=item_data.get('medicine'),  # ✅ already an instance
                    quantity=quantity
                )
            elif item_type == 'PROCEDURE':
                PharmacyBillItem.objects.create(
                    bill=bill,
                    item_type='PROCEDURE',
                    procedure=item_data.get('procedure'),  # ✅ already an instance
                    quantity=quantity
                )

        bill.total_amount = sum(item.subtotal for item in bill.items.all())
        bill.save()
        return bill


    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        # Update bill fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            # Delete old items
            instance.items.all().delete()
            # Add new items
            for item_data in items_data:
                PharmacyBillItem.objects.create(bill=instance, **item_data)

            # Update total_amount
            instance.total_amount = sum(item.subtotal for item in instance.items.all())
            instance.save()

        return instance

