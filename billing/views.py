from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import (
    MaterialPurchaseBill, ClinicBill, LabBill, PharmacyBill
)
from .serializers import (
    MaterialPurchaseBillSerializer, ClinicBillSerializer, LabBillSerializer, PharmacyBillSerializer
)


# -------------------- Generic CRUD View Template --------------------
class BaseBillListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    model_class = None
    serializer_class = None

    def get(self, request):
        bills = self.model_class.objects.all()
        serializer = self.serializer_class(bills, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseBillRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    model_class = None
    serializer_class = None

    def get_object(self, pk):
        return get_object_or_404(self.model_class, pk=pk)

    def get(self, request, pk):
        bill = self.get_object(pk)
        serializer = self.serializer_class(bill)
        return Response(serializer.data)

    def put(self, request, pk):
        bill = self.get_object(pk)
        serializer = self.serializer_class(bill, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        bill = self.get_object(pk)
        serializer = self.serializer_class(bill, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        bill = self.get_object(pk)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------- Material Purchase --------------------
class MaterialPurchaseBillListCreateAPIView(BaseBillListCreateAPIView):
    model_class = MaterialPurchaseBill
    serializer_class = MaterialPurchaseBillSerializer


class MaterialPurchaseBillRetrieveUpdateDeleteAPIView(BaseBillRetrieveUpdateDeleteAPIView):
    model_class = MaterialPurchaseBill
    serializer_class = MaterialPurchaseBillSerializer


# -------------------- Clinic Bill --------------------
class ClinicBillListCreateAPIView(BaseBillListCreateAPIView):
    model_class = ClinicBill
    serializer_class = ClinicBillSerializer


class ClinicBillRetrieveUpdateDeleteAPIView(BaseBillRetrieveUpdateDeleteAPIView):
    model_class = ClinicBill
    serializer_class = ClinicBillSerializer


# -------------------- Lab Bill --------------------
class LabBillListCreateAPIView(BaseBillListCreateAPIView):
    model_class = LabBill
    serializer_class = LabBillSerializer


class LabBillRetrieveUpdateDeleteAPIView(BaseBillRetrieveUpdateDeleteAPIView):
    model_class = LabBill
    serializer_class = LabBillSerializer


# -------------------- Pharmacy Bill --------------------
class PharmacyBillListCreateAPIView(BaseBillListCreateAPIView):
    model_class = PharmacyBill
    serializer_class = PharmacyBillSerializer


class PharmacyBillRetrieveUpdateDeleteAPIView(BaseBillRetrieveUpdateDeleteAPIView):
    model_class = PharmacyBill
    serializer_class = PharmacyBillSerializer



# -------------------- Clinic Panel --------------------
class ClinicBaseBillListCreateAPIView(BaseBillListCreateAPIView):

    def get(self, request):
        clinic = request.user.clinic_profile
        bills = self.model_class.objects.filter(clinic=clinic)
        serializer = self.serializer_class(bills, many=True)
        return Response(serializer.data)

    def post(self, request):
        clinic = request.user.clinic_profile
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(clinic=clinic)  # auto-set clinic
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClinicBaseBillRetrieveUpdateDeleteAPIView(BaseBillRetrieveUpdateDeleteAPIView):

    def get_object(self, pk):
        clinic = self.request.user.clinic_profile
        return get_object_or_404(self.model_class, pk=pk, clinic=clinic)


# Material Purchase Bills
class ClinicMaterialPurchaseBillListCreateAPIView(ClinicBaseBillListCreateAPIView):
    model_class = MaterialPurchaseBill
    serializer_class = MaterialPurchaseBillSerializer


class ClinicMaterialPurchaseBillRetrieveUpdateDeleteAPIView(ClinicBaseBillRetrieveUpdateDeleteAPIView):
    model_class = MaterialPurchaseBill
    serializer_class = MaterialPurchaseBillSerializer


# Clinic Bills
class ClinicClinicBillListCreateAPIView(ClinicBaseBillListCreateAPIView):
    model_class = ClinicBill
    serializer_class = ClinicBillSerializer


class ClinicClinicBillRetrieveUpdateDeleteAPIView(ClinicBaseBillRetrieveUpdateDeleteAPIView):
    model_class = ClinicBill
    serializer_class = ClinicBillSerializer


# Lab Bills
class ClinicLabBillListCreateAPIView(ClinicBaseBillListCreateAPIView):
    model_class = LabBill
    serializer_class = LabBillSerializer


class ClinicLabBillRetrieveUpdateDeleteAPIView(ClinicBaseBillRetrieveUpdateDeleteAPIView):
    model_class = LabBill
    serializer_class = LabBillSerializer


# Pharmacy Bills
class ClinicPharmacyBillListCreateAPIView(ClinicBaseBillListCreateAPIView):
    model_class = PharmacyBill
    serializer_class = PharmacyBillSerializer


class ClinicPharmacyBillRetrieveUpdateDeleteAPIView(ClinicBaseBillRetrieveUpdateDeleteAPIView):
    model_class = PharmacyBill
    serializer_class = PharmacyBillSerializer
