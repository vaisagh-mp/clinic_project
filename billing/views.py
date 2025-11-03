from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from admin_panel.models import Clinic
from .models import (
    MaterialPurchaseBill, ClinicBill, LabBill, PharmacyBill, Medicine, Procedure, ProcedurePayment
)
from .serializers import (
    MaterialPurchaseBillSerializer, ClinicBillSerializer, LabBillSerializer, PharmacyBillSerializer, MedicineSerializer, ProcedureSerializer, ProcedurePaymentSerializer, ClinicPanelBillSerializer, LabPanelBillSerializer, ClinicPharmacyBillSerializer
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
        bills = MaterialPurchaseBill.objects.all().order_by("-created_at")
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
        bills = ClinicBill.objects.all().order_by("-created_at")
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
        bills = LabBill.objects.all().order_by("-created_at")
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
        bills = PharmacyBill.objects.all().order_by("-created_at")
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

    def get_clinic(self, request):
        """ Determine clinic for this request (superadmin or clinic user)."""
        user = request.user
        if user.role.lower() == "superadmin":
            clinic_id = request.query_params.get("clinic_id")
            if not clinic_id:
                return None
            return get_object_or_404(Clinic, id=clinic_id)
        return getattr(user, "clinic_profile", None)

    def get(self, request):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        bills = MaterialPurchaseBill.objects.filter(clinic=clinic).order_by("-created_at")
        serializer = MaterialPurchaseBillSerializer(bills, many=True)
        return Response(serializer.data)

    def post(self, request):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        data = request.data.copy()
        data["clinic"] = clinic.id
        serializer = MaterialPurchaseBillSerializer(data=data)
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClinicMaterialPurchaseBillRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_clinic(self, request):
        """ Same logic for superadmin + clinic user."""
        user = request.user
        if user.role.lower() == "superadmin":
            clinic_id = request.query_params.get("clinic_id")
            if not clinic_id:
                return None
            return get_object_or_404(Clinic, id=clinic_id)
        return getattr(user, "clinic_profile", None)

    def get_object(self, pk, clinic):
        return get_object_or_404(MaterialPurchaseBill, pk=pk, clinic=clinic)

    def get(self, request, pk):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        bill = self.get_object(pk, clinic)
        serializer = MaterialPurchaseBillSerializer(bill)
        return Response(serializer.data)

    def put(self, request, pk):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        bill = self.get_object(pk, clinic)
        data = request.data.copy()
        data["clinic"] = clinic.id
        serializer = MaterialPurchaseBillSerializer(bill, data=data)
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        bill = self.get_object(pk, clinic)
        data = request.data.copy()
        data["clinic"] = clinic.id
        serializer = MaterialPurchaseBillSerializer(bill, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        bill = self.get_object(pk, clinic)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------- Clinic Bill --------------------
class ClinicClinicBillListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_clinic(self, request):
        """ Determine the clinic for this request (superadmin or clinic user)."""
        user = request.user
        if user.role.lower() == "superadmin":
            clinic_id = request.query_params.get("clinic_id")
            if not clinic_id:
                return None
            return get_object_or_404(Clinic, id=clinic_id)
        return getattr(user, "clinic_profile", None)

    def get(self, request):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        bills = ClinicBill.objects.filter(clinic=clinic).order_by("-created_at")
        serializer = ClinicPanelBillSerializer(bills, many=True)
        return Response(serializer.data)

    def post(self, request):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        data = request.data.copy()
        data["clinic"] = clinic.id
        serializer = ClinicPanelBillSerializer(data=data)
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClinicClinicBillRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_clinic(self, request):
        """ Same logic for superadmin + clinic user."""
        user = request.user
        if user.role.lower() == "superadmin":
            clinic_id = request.query_params.get("clinic_id")
            if not clinic_id:
                return None
            return get_object_or_404(Clinic, id=clinic_id)
        return getattr(user, "clinic_profile", None)

    def get_object(self, pk, clinic):
        return get_object_or_404(ClinicBill, pk=pk, clinic=clinic)

    def get(self, request, pk):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        bill = self.get_object(pk, clinic)
        serializer = ClinicPanelBillSerializer(bill)
        return Response(serializer.data)

    def put(self, request, pk):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        bill = self.get_object(pk, clinic)
        data = request.data.copy()
        data["clinic"] = clinic.id
        serializer = ClinicPanelBillSerializer(bill, data=data)
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        bill = self.get_object(pk, clinic)
        data = request.data.copy()
        data["clinic"] = clinic.id
        serializer = ClinicPanelBillSerializer(bill, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        bill = self.get_object(pk, clinic)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------- Lab Bill --------------------
class ClinicLabBillListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_clinic(self, request):
        """ Determine clinic based on user role."""
        user = request.user
        if user.role.lower() == "superadmin":
            clinic_id = request.query_params.get("clinic_id")
            if not clinic_id:
                return None
            return get_object_or_404(Clinic, id=clinic_id)
        return getattr(user, "clinic_profile", None)

    def get(self, request):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        bills = LabBill.objects.filter(clinic=clinic).order_by("-created_at")
        serializer = LabPanelBillSerializer(bills, many=True)
        return Response(serializer.data)

    def post(self, request):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        # ✅ FIX: include request in context
        serializer = LabPanelBillSerializer(
            data=request.data,
            context={"clinic": clinic, "request": request}
        )

        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClinicLabBillRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_clinic(self, request):
        """ Superadmin can switch clinic via ?clinic_id=, clinic user uses their own."""
        user = request.user
        if user.role.lower() == "superadmin":
            clinic_id = request.query_params.get("clinic_id")
            if not clinic_id:
                return None
            return get_object_or_404(Clinic, id=clinic_id)
        return getattr(user, "clinic_profile", None)

    def get_object(self, pk, clinic):
        return get_object_or_404(LabBill, pk=pk, clinic=clinic)

    def get(self, request, pk):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        bill = self.get_object(pk, clinic)
        serializer = LabPanelBillSerializer(bill)
        return Response(serializer.data)

    def put(self, request, pk):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        bill = self.get_object(pk, clinic)
        serializer = LabPanelBillSerializer(bill, data=request.data, context={"clinic": clinic})
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        bill = self.get_object(pk, clinic)
        serializer = LabPanelBillSerializer(bill, data=request.data, partial=True, context={"clinic": clinic})
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "Clinic not found or not authorized"}, status=403)

        bill = self.get_object(pk, clinic)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------- Pharmacy Bill --------------------
class ClinicPharmacyBillListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_clinic(self, request):
        user = request.user
        if user.role.lower() == "superadmin":
            clinic_id = request.query_params.get("clinic_id")
            if clinic_id:
                return get_object_or_404(Clinic, id=clinic_id)
            return None
        return user.clinic_profile

    def get(self, request):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "clinic_id required for superadmin"}, status=400)

        bills = PharmacyBill.objects.filter(clinic=clinic).order_by("-created_at")
        serializer = ClinicPharmacyBillSerializer(bills, many=True)
        return Response(serializer.data)

    def post(self, request):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "clinic_id required for superadmin"}, status=400)

        serializer = ClinicPharmacyBillSerializer(
            data=request.data,
            context={'clinic': clinic}
        )
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClinicPharmacyBillRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_clinic(self, request):
        user = request.user
        if user.role.lower() == "superadmin":
            clinic_id = request.query_params.get("clinic_id")
            if clinic_id:
                return get_object_or_404(Clinic, id=clinic_id)
            return None
        return user.clinic_profile

    def get_object(self, pk, clinic):
        return get_object_or_404(PharmacyBill, pk=pk, clinic=clinic)

    def get(self, request, pk):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "clinic_id required for superadmin"}, status=400)
        bill = self.get_object(pk, clinic)
        serializer = ClinicPharmacyBillSerializer(bill)
        return Response(serializer.data)

    def put(self, request, pk):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "clinic_id required for superadmin"}, status=400)
        bill = self.get_object(pk, clinic)
        serializer = ClinicPharmacyBillSerializer(
            bill,
            data=request.data,
            context={'clinic': clinic}
        )
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "clinic_id required for superadmin"}, status=400)
        bill = self.get_object(pk, clinic)
        serializer = ClinicPharmacyBillSerializer(
            bill,
            data=request.data,
            partial=True,
            context={'clinic': clinic}
        )
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        clinic = self.get_clinic(request)
        if not clinic:
            return Response({"error": "clinic_id required for superadmin"}, status=400)
        bill = self.get_object(pk, clinic)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ----------------- Medicine CRUD -----------------    
def get_user_clinic(request):

    user = request.user

    # 🔹 Superadmin - check for clinic_id in query params
    if getattr(user, "role", "").lower() == "superadmin":
        clinic_id = request.query_params.get("clinic_id")
        if clinic_id:
            return get_object_or_404(Clinic, id=clinic_id)
        return None  # Must specify clinic_id

    # 🔹 Clinic user
    if hasattr(user, "clinic_profile") and user.clinic_profile:
        return user.clinic_profile

    # 🔹 Doctor user
    if hasattr(user, "doctor_profile") and user.doctor_profile and user.doctor_profile.clinic:
        return user.doctor_profile.clinic

    return None


# ----------------- Medicine List & Create -----------------
class MedicineListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        clinic = get_user_clinic(request)

        if not clinic:
            return Response(
                {"detail": "clinic_id required for superadmin or user has no clinic."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        medicines = Medicine.objects.filter(clinic=clinic).order_by("-created_at")
        serializer = MedicineSerializer(medicines, many=True)
        return Response(serializer.data)

    def post(self, request):
        clinic = get_user_clinic(request)

        if not clinic:
            return Response(
                {"detail": "clinic_id required for superadmin or user has no clinic."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = MedicineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------- Medicine Retrieve / Update / Delete -----------------
class MedicineRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, clinic):
        return get_object_or_404(Medicine, pk=pk, clinic=clinic)

    def get(self, request, pk):
        clinic = get_user_clinic(request)
        if not clinic:
            return Response(
                {"detail": "clinic_id required for superadmin or user has no clinic."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        medicine = self.get_object(pk, clinic)
        serializer = MedicineSerializer(medicine)
        return Response(serializer.data)

    def put(self, request, pk):
        clinic = get_user_clinic(request)
        if not clinic:
            return Response(
                {"detail": "clinic_id required for superadmin or user has no clinic."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        medicine = self.get_object(pk, clinic)
        serializer = MedicineSerializer(medicine, data=request.data)
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        clinic = get_user_clinic(request)
        if not clinic:
            return Response(
                {"detail": "clinic_id required for superadmin or user has no clinic."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        medicine = self.get_object(pk, clinic)
        serializer = MedicineSerializer(medicine, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        clinic = get_user_clinic(request)
        if not clinic:
            return Response(
                {"detail": "clinic_id required for superadmin or user has no clinic."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        medicine = self.get_object(pk, clinic)
        medicine.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ----------------- Procedure List & Create -----------------
class ProcedureListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        clinic = get_user_clinic(request)
        if not clinic:
            return Response(
                {"detail": "clinic_id required for superadmin or user has no clinic."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        procedures = Procedure.objects.filter(clinic=clinic).order_by("-created_at")
        serializer = ProcedureSerializer(procedures, many=True)
        return Response(serializer.data)

    def post(self, request):
        clinic = get_user_clinic(request)
        if not clinic:
            return Response(
                {"detail": "clinic_id required for superadmin or user has no clinic."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ProcedureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------- Procedure Retrieve / Update / Delete -----------------
class ProcedureRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, clinic):
        return get_object_or_404(Procedure, pk=pk, clinic=clinic)

    def get(self, request, pk):
        clinic = get_user_clinic(request)
        if not clinic:
            return Response(
                {"detail": "clinic_id required for superadmin or user has no clinic."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        procedure = self.get_object(pk, clinic)
        serializer = ProcedureSerializer(procedure)
        return Response(serializer.data)

    def put(self, request, pk):
        clinic = get_user_clinic(request)
        if not clinic:
            return Response(
                {"detail": "clinic_id required for superadmin or user has no clinic."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        procedure = self.get_object(pk, clinic)
        serializer = ProcedureSerializer(procedure, data=request.data)
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        clinic = get_user_clinic(request)
        if not clinic:
            return Response(
                {"detail": "clinic_id required for superadmin or user has no clinic."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        procedure = self.get_object(pk, clinic)
        serializer = ProcedureSerializer(procedure, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(clinic=clinic)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        clinic = get_user_clinic(request)
        if not clinic:
            return Response(
                {"detail": "clinic_id required for superadmin or user has no clinic."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        procedure = self.get_object(pk, clinic)
        procedure.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# Admin: Full access
class AdminProcedurePaymentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProcedurePaymentSerializer

    def get_queryset(self):
        queryset = ProcedurePayment.objects.all().select_related(
            "bill_item__bill", "bill_item__procedure"
        )
        clinic_id = self.request.query_params.get("clinic")
        if clinic_id:  # Optional filtering by clinic
            queryset = queryset.filter(bill_item__bill__clinic_id=clinic_id)
        return queryset


class AdminProcedurePaymentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProcedurePaymentSerializer

    def get_queryset(self):
        return ProcedurePayment.objects.all().select_related(
            "bill_item__bill", "bill_item__procedure"
        )

class PatientPharmacyBillListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, patient_id):
        # Fetch only bills for the specific patient
        bills = PharmacyBill.objects.filter(patient_id=patient_id).order_by("-created_at")
        serializer = PharmacyBillSerializer(bills, many=True)
        return Response(serializer.data)

# Clinic: Restricted to their own clinic
class ClinicProcedurePaymentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProcedurePaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        clinic = get_user_clinic(user)

        # ✅ Superadmin can view all or specific clinic data
        if clinic == "ALL":
            clinic_id = self.request.query_params.get("clinic_id")
            if clinic_id:
                return ProcedurePayment.objects.filter(
                    bill_item__bill__clinic_id=clinic_id
                ).select_related("bill_item__bill", "bill_item__procedure")
            return ProcedurePayment.objects.all().select_related("bill_item__bill", "bill_item__procedure")

        # ✅ Clinic user can only see their clinic data
        elif clinic:
            return ProcedurePayment.objects.filter(
                bill_item__bill__clinic_id=clinic.id
            ).select_related("bill_item__bill", "bill_item__procedure")

        else:
            raise PermissionDenied("This user has no clinic assigned.")

    def perform_create(self, serializer):
        user = self.request.user
        clinic = get_user_clinic(user)

        # ✅ Superadmin: must provide clinic_id
        if clinic == "ALL":
            clinic_id = self.request.data.get("clinic_id")
            if not clinic_id:
                raise PermissionDenied("clinic_id is required for superadmin.")
            try:
                clinic = Clinic.objects.get(id=clinic_id)
            except Clinic.DoesNotExist:
                raise PermissionDenied("Clinic not found.")

        elif not clinic:
            raise PermissionDenied("This user has no clinic assigned.")

        bill_item = serializer.validated_data["bill_item"]

        # ✅ Ensure bill item belongs to this clinic
        if bill_item.bill.clinic_id != clinic.id:
            raise PermissionDenied("You cannot create payments for another clinic's bills.")

        serializer.save()


class ClinicProcedurePaymentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProcedurePaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        clinic = get_user_clinic(user)

        # ✅ Superadmin access
        if clinic == "ALL":
            clinic_id = self.request.query_params.get("clinic_id")
            if clinic_id:
                return ProcedurePayment.objects.filter(
                    bill_item__bill__clinic_id=clinic_id
                ).select_related("bill_item__bill", "bill_item__procedure")
            return ProcedurePayment.objects.all().select_related("bill_item__bill", "bill_item__procedure")

        # ✅ Clinic access
        elif clinic:
            return ProcedurePayment.objects.filter(
                bill_item__bill__clinic_id=clinic.id
            ).select_related("bill_item__bill", "bill_item__procedure")

        raise PermissionDenied("This user has no clinic assigned.")
