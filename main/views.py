from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from main.choices import DOCTOR, NURSE, STUDENT_CLINICIAN

from main.models import Admission, Patient,\
    Prescription, Referral, User, Ward
from main.view_helpers import generate_clinician_stats,\
    generate_receptionist_stats
from .serializers import AdmissionSerializer,\
    PatientSerializer, PrescriptionSerializer,\
    ReferralSerializer, UserSerializer, WardSerializer
from .permissions import IsNurse, IsReceptionist, IsDoctor, IsStudent_Clinician


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    queryset = Patient.objects.all()
    permission_classes = [IsReceptionist | IsDoctor]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user,
                        updated_at=timezone.now())

    def perform_update(self, serializer):
        return super().perform_update(serializer)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]


class ReceptionistPatientView(viewsets.ReadOnlyModelViewSet):
    """ Get patients registered by a particular receptionist """
    serializer_class = PatientSerializer
    permission_classes = [IsReceptionist]

    def get_queryset(self):
        user = self.request.user
        return Patient.objects.filter(created_by=user)


class ReferralViewSet(viewsets.ModelViewSet):
    serializer_class = ReferralSerializer
    permission_classes = [IsReceptionist]
    queryset = Referral.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user,
                        updated_at=timezone.now())


class ClinicianAssignedPatientsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReferralSerializer
    permission_classes = [IsDoctor | IsNurse | IsStudent_Clinician]

    def get_queryset(self):
        return Referral.objects.filter(doctor=self.request.user)


class PrescriptionViewSet(viewsets.ModelViewSet):
    serializer_class = PrescriptionSerializer
    queryset = Prescription.objects.all()

    def get_permissions(self):
        if self.action == 'destroy':
            permission_classes = [IsDoctor]
        else:
            permission_classes = [IsDoctor | IsNurse | IsStudent_Clinician]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now(),
                        updated_by=self.request.user)


class AdmissionViewSet(viewsets.ModelViewSet):
    serializer_class = AdmissionSerializer
    queryset = Admission.objects.all()

    def get_permissions(self):
        if self.action == 'destroy':
            permission_classes = [IsDoctor]
        else:
            permission_classes = [IsDoctor | IsNurse | IsStudent_Clinician]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now(),
                        updated_by=self.request.user)


class WardViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WardSerializer
    queryset = Ward.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None


class ReceptionistStatAPIView(APIView):
    permission_classes = [IsReceptionist]

    def get(self, request, format=None):
        stats = generate_receptionist_stats(request)
        return Response(stats)


class ClinicianStatAPIView(APIView):
    permission_classes = [IsDoctor | IsNurse | IsStudent_Clinician]

    def get(self, request, format=None):
        stats = generate_clinician_stats(request)
        return Response(stats)


class ClinicianInfoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return User.objects.filter(role__in=[DOCTOR, NURSE, STUDENT_CLINICIAN])
