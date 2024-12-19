from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import SellerRequest
from .serializers import SellerRequestSerializer
from users.permissions import IsAdmin  # Pastikan Anda memiliki permission ini

class SellerRequestViewSet(viewsets.ModelViewSet):
    queryset = SellerRequest.objects.all()
    serializer_class = SellerRequestSerializer
    permission_classes = [IsAdmin]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        status = request.data.get('status')

        if status in ['approved', 'rejected']:
            instance.status = status
            instance.save()

            # Update user status jika disetujui
            if status == 'approved':
                instance.user.is_seller = True
                instance.user.save()  # Simpan perubahan pada user

            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        """Mengembalikan queryset berdasarkan peran pengguna."""
        user = self.request.user
        if user.role == 'admin':
            return SellerRequest.objects.all()
        return SellerRequest.objects.filter(user=user)
