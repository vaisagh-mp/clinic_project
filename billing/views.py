from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import (
    MaterialPurchaseBill, ClinicBill, LabBill, PharmacyBill, Medicine, Procedure
)
from .serializers import (
    MaterialPurchaseBillSerializer, ClinicBillSerializer, LabBillSerializer, PharmacyBillSerializer, MedicineSerializer, ProcedureSerializer
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
class MaterialPurchaseBillListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        bills = MaterialPurchaseBill.objects.all()
        serializer = MaterialPurchaseBillSerializer(bills, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MaterialPurchaseBillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MaterialPurchaseBillRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(MaterialPurchaseBill, pk=pk)

    def get(self, request, pk):
        bill = self.get_object(pk)
        serializer = MaterialPurchaseBillSerializer(bill)
        return Response(serializer.data)

    def put(self, request, pk):
        bill = self.get_object(pk)
        serializer = MaterialPurchaseBillSerializer(bill, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        bill = self.get_object(pk)
        serializer = MaterialPurchaseBillSerializer(bill, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        bill = self.get_object(pk)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------- Clinic Bill --------------------
class ClinicBillListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        bills = ClinicBill.objects.all()
        serializer = ClinicBillSerializer(bills, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClinicBillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClinicBillRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(ClinicBill, pk=pk)

    def get(self, request, pk):
        bill = self.get_object(pk)
        serializer = ClinicBillSerializer(bill)
        return Response(serializer.data)

    def put(self, request, pk):
        bill = self.get_object(pk)
        serializer = ClinicBillSerializer(bill, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        bill = self.get_object(pk)
        serializer = ClinicBillSerializer(bill, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        bill = self.get_object(pk)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------- Lab Bill --------------------
class LabBillListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        bills = LabBill.objects.all()
        serializer = LabBillSerializer(bills, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LabBillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LabBillRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(LabBill, pk=pk)

    def get(self, request, pk):
        bill = self.get_object(pk)
        serializer = LabBillSerializer(bill)
        return Response(serializer.data)

    def put(self, request, pk):
        bill = self.get_object(pk)
        serializer = LabBillSerializer(bill, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        bill = self.get_object(pk)
        serializer = LabBillSerializer(bill, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        bill = self.get_object(pk)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------- Pharmacy Bill --------------------
class PharmacyBillListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        bills = PharmacyBill.objects.all()
        serializer = PharmacyBillSerializer(bills, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PharmacyBillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PharmacyBillRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(PharmacyBill, pk=pk)

    def get(self, request, pk):
        bill = self.get_object(pk)
        serializer = PharmacyBillSerializer(bill)
        return Response(serializer.data)

    def put(self, request, pk):
        bill = self.get_object(pk)
        serializer = PharmacyBillSerializer(bill, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        bill = self.get_object(pk)
        serializer = PharmacyBillSerializer(bill, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        bill = self.get_object(pk)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# --------------------------------------- Clinic ------------------------------------------------/

# -------------------- Clinic Material Purchase --------------------
class ClinicMaterialPurchaseBillListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        clinic = request.user.clinic_profile
        bills = MaterialPurchaseBill.objects.filter(clinic=clinic)
        serializer = MaterialPurchaseBillSerializer(bills, many=True)
        return Response(serializer.data)

    def post(self, request):
        clinic = request.user.clinic_profile
        serializer = MaterialPurchaseBillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(clinic=clinic)  # auto-attach clinic
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClinicMaterialPurchaseBillRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, clinic):
        return get_object_or_404(MaterialPurchaseBill, pk=pk, clinic=clinic)

    def get(self, request, pk):
        bill = self.get_object(pk, request.user.clinic_profile)
        serializer = MaterialPurchaseBillSerializer(bill)
        return Response(serializer.data)

    def put(self, request, pk):
        bill = self.get_object(pk, request.user.clinic_profile)
        serializer = MaterialPurchaseBillSerializer(bill, data=request.data)
        if serializer.is_valid():
            serializer.save(clinic=request.user.clinic_profile)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        bill = self.get_object(pk, request.user.clinic_profile)
        serializer = MaterialPurchaseBillSerializer(bill, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(clinic=request.user.clinic_profile)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        bill = self.get_object(pk, request.user.clinic_profile)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------- Clinic Bill --------------------
class ClinicClinicBillListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        clinic = request.user.clinic_profile
        bills = ClinicBill.objects.filter(clinic=clinic)
        serializer = ClinicBillSerializer(bills, many=True)
        return Response(serializer.data)

    def post(self, request):
        clinic = request.user.clinic_profile
        serializer = ClinicBillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClinicClinicBillRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, clinic):
        return get_object_or_404(ClinicBill, pk=pk, clinic=clinic)

    def get(self, request, pk):
        bill = self.get_object(pk, request.user.clinic_profile)
        serializer = ClinicBillSerializer(bill)
        return Response(serializer.data)

    def put(self, request, pk):
        bill = self.get_object(pk, request.user.clinic_profile)
        serializer = ClinicBillSerializer(bill, data=request.data)
        if serializer.is_valid():
            serializer.save(clinic=request.user.clinic_profile)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        bill = self.get_object(pk, request.user.clinic_profile)
        serializer = ClinicBillSerializer(bill, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(clinic=request.user.clinic_profile)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        bill = self.get_object(pk, request.user.clinic_profile)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------- Lab Bill --------------------
class ClinicLabBillListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        clinic = request.user.clinic_profile
        bills = LabBill.objects.filter(clinic=clinic)
        serializer = LabBillSerializer(bills, many=True)
        return Response(serializer.data)

    def post(self, request):
        clinic = request.user.clinic_profile
        serializer = LabBillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClinicLabBillRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, clinic):
        return get_object_or_404(LabBill, pk=pk, clinic=clinic)

    def get(self, request, pk):
        bill = self.get_object(pk, request.user.clinic_profile)
        serializer = LabBillSerializer(bill)
        return Response(serializer.data)

    def put(self, request, pk):
        bill = self.get_object(pk, request.user.clinic_profile)
        serializer = LabBillSerializer(bill, data=request.data)
        if serializer.is_valid():
            serializer.save(clinic=request.user.clinic_profile)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        bill = self.get_object(pk, request.user.clinic_profile)
        serializer = LabBillSerializer(bill, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(clinic=request.user.clinic_profile)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        bill = self.get_object(pk, request.user.clinic_profile)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------- Pharmacy Bill --------------------
class ClinicPharmacyBillListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        clinic = request.user.clinic_profile
        bills = PharmacyBill.objects.filter(clinic=clinic)
        serializer = PharmacyBillSerializer(bills, many=True)
        return Response(serializer.data)

    def post(self, request):
        clinic = request.user.clinic_profile
        serializer = PharmacyBillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClinicPharmacyBillRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, clinic):
        return get_object_or_404(PharmacyBill, pk=pk, clinic=clinic)

    def get(self, request, pk):
        bill = self.get_object(pk, request.user.clinic_profile)
        serializer = PharmacyBillSerializer(bill)
        return Response(serializer.data)

    def put(self, request, pk):
        bill = self.get_object(pk, request.user.clinic_profile)
        serializer = PharmacyBillSerializer(bill, data=request.data)
        if serializer.is_valid():
            serializer.save(clinic=request.user.clinic_profile)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        bill = self.get_object(pk, request.user.clinic_profile)
        serializer = PharmacyBillSerializer(bill, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(clinic=request.user.clinic_profile)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        bill = self.get_object(pk, request.user.clinic_profile)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# ----------------- Medicine CRUD -----------------
class MedicineListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        medicines = Medicine.objects.all()
        serializer = MedicineSerializer(medicines, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MedicineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MedicineRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        medicine = get_object_or_404(Medicine, pk=pk)
        serializer = MedicineSerializer(medicine)
        return Response(serializer.data)

    def put(self, request, pk):
        medicine = get_object_or_404(Medicine, pk=pk)
        serializer = MedicineSerializer(medicine, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        medicine = get_object_or_404(Medicine, pk=pk)
        serializer = MedicineSerializer(medicine, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        medicine = get_object_or_404(Medicine, pk=pk)
        medicine.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ----------------- Procedure CRUD -----------------
class ProcedureListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        procedures = Procedure.objects.all()
        serializer = ProcedureSerializer(procedures, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProcedureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcedureRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        procedure = get_object_or_404(Procedure, pk=pk)
        serializer = ProcedureSerializer(procedure)
        return Response(serializer.data)

    def put(self, request, pk):
        procedure = get_object_or_404(Procedure, pk=pk)
        serializer = ProcedureSerializer(procedure, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        procedure = get_object_or_404(Procedure, pk=pk)
        serializer = ProcedureSerializer(procedure, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        procedure = get_object_or_404(Procedure, pk=pk)
        procedure.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)