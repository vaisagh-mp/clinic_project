from django.urls import path
from .views import *

urlpatterns = [

    # Medicine CRUD
    path("medicines/", MedicineListCreateAPIView.as_view(), name="medicine-list-create"),
    path("medicines/<int:pk>/", MedicineRetrieveUpdateDeleteAPIView.as_view(), name="medicine-detail"),

    # Procedure CRUD
    path("procedures/", ProcedureListCreateAPIView.as_view(), name="procedure-list-create"),
    path("procedures/<int:pk>/", ProcedureRetrieveUpdateDeleteAPIView.as_view(), name="procedure-detail"),
    
    # ---------------- Admin ----------------
    path("admin/material-purchase/", MaterialPurchaseBillListCreateAPIView.as_view(), name="admin-material-purchase-list-create"),
    path("admin/material-purchase/<int:pk>/", MaterialPurchaseBillRetrieveUpdateDeleteAPIView.as_view(), name="admin-material-purchase-detail"),

    path("admin/clinic-bill/", ClinicBillListCreateAPIView.as_view(), name="admin-clinic-bill-list-create"),
    path("admin/clinic-bill/<int:pk>/", ClinicBillRetrieveUpdateDeleteAPIView.as_view(), name="admin-clinic-bill-detail"),

    path("admin/lab-bill/", LabBillListCreateAPIView.as_view(), name="admin-lab-bill-list-create"),
    path("admin/lab-bill/<int:pk>/", LabBillRetrieveUpdateDeleteAPIView.as_view(), name="admin-lab-bill-detail"),

    path("admin/pharmacy-bill/", PharmacyBillListCreateAPIView.as_view(), name="admin-pharmacy-bill-list-create"),
    path("admin/pharmacy-bill/<int:pk>/", PharmacyBillRetrieveUpdateDeleteAPIView.as_view(), name="admin-pharmacy-bill-detail"),

    # ---------------- Clinic Panel ----------------
    path("clinic/material-purchase/", ClinicMaterialPurchaseBillListCreateAPIView.as_view(), name="clinic-material-purchase-list-create"),
    path("clinic/material-purchase/<int:pk>/", ClinicMaterialPurchaseBillRetrieveUpdateDeleteAPIView.as_view(), name="clinic-material-purchase-detail"),

    path("clinic/clinic-bill/", ClinicClinicBillListCreateAPIView.as_view(), name="clinic-clinic-bill-list-create"),
    path("clinic/clinic-bill/<int:pk>/", ClinicClinicBillRetrieveUpdateDeleteAPIView.as_view(), name="clinic-clinic-bill-detail"),

    path("clinic/lab-bill/", ClinicLabBillListCreateAPIView.as_view(), name="clinic-lab-bill-list-create"),
    path("clinic/lab-bill/<int:pk>/", ClinicLabBillRetrieveUpdateDeleteAPIView.as_view(), name="clinic-lab-bill-detail"),

    path("clinic/pharmacy-bill/", ClinicPharmacyBillListCreateAPIView.as_view(), name="clinic-pharmacy-bill-list-create"),
    path("clinic/pharmacy-bill/<int:pk>/", ClinicPharmacyBillRetrieveUpdateDeleteAPIView.as_view(), name="clinic-pharmacy-bill-detail"),

    
]
