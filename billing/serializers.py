from rest_framework import serializers
from .models import (
    MaterialPurchaseBill, MaterialPurchaseItem,
    ClinicBill, ClinicBillItem,
    LabBill, LabBillItem,
    PharmacyBill, PharmacyBillItem, ProcedurePayment,
    Medicine, Procedure
)


# -------------------- Material Purchase --------------------
class MaterialPurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialPurchaseItem
        fields = ['id', 'item_name', 'quantity', 'unit_price', 'subtotal']


class MaterialPurchaseBillSerializer(serializers.ModelSerializer):
    items = MaterialPurchaseItemSerializer(many=True, read_only=True)

    class Meta:
        model = MaterialPurchaseBill
        fields = ['id', 'bill_number', 'clinic', 'bill_date', 'status', 'total_amount', 'supplier_name', 'invoice_number', 'items']


# -------------------- Clinic Bill --------------------
class ClinicBillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicBillItem
        fields = ['id', 'item_name', 'quantity', 'unit_price', 'subtotal']


class ClinicBillSerializer(serializers.ModelSerializer):
    items = ClinicBillItemSerializer(many=True, read_only=True)

    class Meta:
        model = ClinicBill
        fields = ['id', 'bill_number', 'clinic', 'bill_date', 'status', 'total_amount', 'vendor_name', 'items']


# -------------------- Lab Bill --------------------
class LabBillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabBillItem
        fields = ['id', 'test_or_service', 'cost']


class LabBillSerializer(serializers.ModelSerializer):
    items = LabBillItemSerializer(many=True, read_only=True)

    class Meta:
        model = LabBill
        fields = ['id', 'bill_number', 'clinic', 'bill_date', 'status', 'total_amount', 'lab_name', 'work_description', 'items']


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


class PharmacyBillItemSerializer(serializers.ModelSerializer):
    medicine = MedicineSerializer(read_only=True)
    procedure = ProcedureSerializer(read_only=True)
    total_paid = serializers.ReadOnlyField()
    balance_due = serializers.ReadOnlyField()

    class Meta:
        model = PharmacyBillItem
        fields = ['id', 'bill', 'item_type', 'medicine', 'procedure', 'quantity', 'unit_price', 'subtotal', 'total_paid', 'balance_due']


class PharmacyBillSerializer(serializers.ModelSerializer):
    items = PharmacyBillItemSerializer(many=True, read_only=True)

    class Meta:
        model = PharmacyBill
        fields = ['id', 'bill_number', 'clinic', 'patient', 'bill_date', 'status', 'total_amount', 'items']
