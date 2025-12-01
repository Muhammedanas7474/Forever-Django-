from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
import math
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser,AllowAny
from users.models import User
from django.db.models import Q
from .serializer import AdminUserListSerializer
from rest_framework import status
# Create your views here.


class UserPagination(PageNumberPagination):
    page_size=10
    def get_paginated_response(self, data):
        total_users=self.page.paginator.count
        total_pages=math.ceil(total_users/self.page_size)
        return Response({
            "total_users": total_users,
            "total_pages": total_pages,
            "current_page": self.page.number,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data
        })
    
class AdminUserListView(APIView):
    permission_classes=[IsAdminUser]
    pagination_classes = UserPagination


    def get(self,request):
        users=User.objects.exclude(role="admin").order_by('-date_joined')
        search=request.query_params.get("search")
        if search:
            users=users.filter(
                Q(user_name__icontains=search) |
                Q(email__icontains=search) |
                Q(id__icontains=search)
            )
        paginator=self.pagination_classes()
        result_page=paginator.paginate_queryset(users,request)
        serialzier=AdminUserListSerializer(result_page,many=True)
        return paginator.get_paginated_response(serialzier.data)
    

class AdminDetailView(APIView):
    permission_classes=[IsAdminUser]

    def patch(self,request,pk):
        try:
            user=User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({"message": "User not found"},status=status.HTTP_404_NOT_FOUND)
        
        if user.role == "admin":
            return Response({"message": "Admin cannot be blocked"}, status=status.HTTP_400_BAD_REQUEST)
        
        new_status = request.data.get("blocked")
        if new_status is None:
            return Response({"message": "blocked field required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user.blocked = new_status
        user.save()
        return Response({"message": "Status updated", "status": new_status})
    
    def delete(self, request, pk):
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.role == "admin":
            return Response({"message": "Admin cannot be deleted"}, status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return Response({"message": "User removed successfully"})