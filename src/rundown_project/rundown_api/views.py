from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import filters
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import IsAuthenticated
from . import serializers
from . import permissions
from . import models

class LoginViewSet(viewsets.ViewSet):
    serializer_class = AuthTokenSerializer

    def create(self, request):
        user = models.UserProfile.objects.filter(email = request.data.get('username')).first()
        if user is None:
            return Response({'message':'No user registered with this email.', 'status':False},
                            status = status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data=request.data,context={'request': request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({'message':'Login success!', 'status':True, 'data':{
                'id':user.id,
                'name':user.name,
                'email':user.email,
                'token':token.key
            }})
        return Response({'message':'Login failed', 'status':False, 'data':{}})

class RegisterViewSet(viewsets.ViewSet):
    serializer_class = serializers.UserProfileSerializer

    def create(self, request):
        serializer = serializers.UserProfileSerializer(data = request.data)
        if serializer.is_valid():
            user = models.UserProfile(
                email = serializer.data.get('email'),
                name = serializer.data.get('name')
            )
            user.set_password(request.data.get('password'))
            user.save()
            return Response({'message': 'Register successful', 'status': True, 'data':{
                'name':user.name,
                'email':user.email
            }})
        else:
            return Response({'message': 'An error due to bad request', 'status':False, 'errors': serializer.errors},
                            status= status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsTheOwner,IsAuthenticated)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'email')
    serializer_class = (serializers.UserProfileSerializer,)

    def list(self, request):
        serializer = serializers.UserProfileSerializer(models.UserProfile.objects.all(), many=True)
        return Response({'message':'OK!', 'status': True, 'data':serializer.data})

    def retrieve(self, request, pk=None):
        user = models.UserProfile.objects.filter(id = pk).first()
        if user is None:
            return Response({'message':'User not found', 'status': False, 'data':{}},
                            status = status.HTTP_404_NOT_FOUND)
        else:
            serializer = serializers.UserProfileSerializer(user)
            return Response({'message':'OK!', 'status': True, 'data': serializer.data})

    def update(self, request, pk = None):
        validated_data = serializers.UserProfileSerializer(data=request.data)
        if validated_data.is_valid():
            user = models.UserProfile.objects.filter(id = pk).first()
            if user is None:
                return Response({'message':'User not found', 'status':False, 'data':{}},
                                status = status.HTTP_404_NOT_FOUND)
            else:
                self.check_object_permissions(request, user)
                user.name = validated_data.data.get('name', user.name)
                user.email = validated_data.data.get('email', user.email)
                user.set_password(request.data.get('password', user.password))
                user.save()
                serializer = serializers.UserProfileSerializer(user)
                return Response({'message': 'Successfully updated!', 'status': True, 'data':serializer.data})

        return Response({'message': 'An error due to bad request', 'status':False, 'errors': validated_data.errors},status= status.HTTP_400_BAD_REQUEST)



    def partial_update(self, request, pk = None):
        user = models.UserProfile.objects.filter(id = pk).first()
        if user is None:
            return Response({'message':'User not found', 'status':False, 'data':{}},
                            status = status.HTTP_404_NOT_FOUND)
        else:
            self.check_object_permissions(request, user)
            serializer = serializers.UserProfileSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                if request.data.get('password') is not None:
                    user.set_password(request.data.get('password'))
                    user.save()
                return Response({'message': 'Successfully partial update!', 'status': True, 'data':serializer.data})

            return Response({'message': 'An error due to bad request', 'status': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        user = models.UserProfile.objects.filter(id = pk).first()
        if user is None:
            return Response({'message':'User not found', 'status':False, 'data':{}},
                            status = status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, user)
        user.delete()
        return Response({'message': 'Successfully deleted', 'status': True, 'data': {}})


class RundownViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.RundownSerializer
    permission_classes = (permissions.PostOnRundown,IsAuthenticated)

    def list(self, request):
        rundowns = models.Rundown.objects.filter(user_profile = request.user)
        serializer = serializers.RundownSerializer(rundowns, many=True)
        return Response({'message':'OK!', 'status': True, 'data':serializer.data})

    def create(self, request):
        serializer = serializers.RundownSerializer(data = request.data)
        if serializer.is_valid():
            rundown = models.Rundown(title = serializer.data.get('title'),
                                     description = serializer.data.get('description'),
                                     user_profile = request.user)
            self.check_object_permissions(request, rundown)
            rundown.save()
            return Response({'message':'Successfully created', 'status': True, 'data': serializer.data})

        return Response({'message': 'An error due to bad request', 'status':False, 'errors': serializer.errors},status= status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk = None):
        rundown = models.Rundown.objects.filter(id=pk).first()
        if rundown is None:
            return Response({'message': 'Rundown not found', 'status': False, 'data': {}}, status = status.HTTP_404_NOT_FOUND)
        else:
            rundown_details = models.RundownDetail.objects.filter(rundown_id= rundown.id)
            rundown_details = serializers.RundownDetailSerializer(rundown_details, many=True)
            serializer = serializers.RundownSerializer(rundown)
            return Response({'message': 'OK!', 'status': True, 'data': {
                "id": serializer.data.get('id'),
                "user_profile": serializer.data.get('user_profile'),
                "title": serializer.data.get('title'),
                "description": serializer.data.get('description'),
                "is_trashed": serializer.data.get('is_trashed'),
                "rundown_details": rundown_details.data
            }})


    def update(self, request, pk = None):
        validated_data = serializers.RundownSerializer(data=request.data)
        if validated_data.is_valid():
            rundown = models.Rundown.objects.filter(id = pk).first()
            if rundown is None:
                return Response({'message':'Rundown not found', 'status':False, 'data':{}}, status = status.HTTP_404_NOT_FOUND)
            else:
                self.check_object_permissions(request, rundown)
                rundown.title = validated_data.data.get('title', rundown.title)
                rundown.description = validated_data.data.get('description', rundown.description)
                rundown.save()
                serializer = serializers.RundownSerializer(rundown)
                return Response({'message': 'Successfully updated!', 'status': True, 'data':serializer.data})

    def partial_update(self, request, pk = None):
        rundown = models.Rundown.objects.filter(id = pk).first()
        if rundown is None:
            return Response({'message':'User not found', 'status':False, 'data':{}},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            self.check_object_permissions(request, rundown)
            serializer = serializers.RundownSerializer(rundown, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Successfully partial update!', 'status': True, 'data':serializer.data})

            return Response({'message': 'An error due to bad request', 'status': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk = None):
        rundown = models.Rundown.objects.filter(id = pk).first()
        if rundown is None:
            return Response({'message':'Rundown not found', 'status':False, 'data':{}},
                            status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, rundown)
        rundown.delete()
        return Response({'message': 'Successfully deleted', 'status': True, 'data': {}})


class RundownDetailViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.RundownDetailSerializer
    permission_classes = (permissions.PostOnRundown,IsAuthenticated)

    def create(self, request):
        serializer = serializers.RundownDetailSerializer(data = request.data)
        if serializer.is_valid():
            rundown = models.Rundown.objects.filter(id = serializer.data.get('rundown')).first()
            if rundown is None:
                return Response(
                    {'message': 'An error due to bad request',
                     'status': False,
                     'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST)

            rundown_item = models.RundownDetail(title = serializer.data.get('title'),
                                     description = serializer.data.get('description'),
                                     rundown = rundown)
            rundown_item.save()
            return Response({'message':'Successfully created', 'status': True, 'data': serializer.data})

        return Response({'message': 'An error due to bad request', 'status':False, 'errors': serializer.errors},status= status.HTTP_400_BAD_REQUEST)

    def retrieve(self,request,pk=None):
        rundown_item = models.RundownDetail.objects.filter(id=pk).first()
        if rundown_item is None:
            return Response({'message': 'Rundown item not found', 'status': False, 'data': {}})
        else:
            serializer = serializers.RundownDetailSerializer(rundown_item)
            return Response({'message': 'OK!', 'status': True, 'data': serializer.data})

    def update(self, request, pk=None):
        validated_data = serializers.RundownDetailSerializer(data=request.data)
        if validated_data.is_valid():
            rundown_item = models.RundownDetail.objects.filter(id=pk).first()
            if rundown_item is None:
                return Response({'message': 'Rundown item not found', 'status': False, 'data': {}})
            else:
                rundown = models.Rundown.objects.filter(id=rundown_item.rundown_id).first()
                self.check_object_permissions(request, rundown)
                rundown_item.title = validated_data.data.get('title', rundown_item.title)
                rundown_item.description = validated_data.data.get('description', rundown_item.description)
                rundown_item.with_date = validated_data.data.get('with_date', rundown_item.with_date)
                rundown_item.order_num = validated_data.data.get('order_num', rundown_item.order_num)
                rundown_item.save()
                serializer = serializers.RundownDetailSerializer(rundown_item)
                return Response({'message': 'Successfully updated!', 'status': True, 'data': serializer.data})

        return Response({'message': 'An error due to bad request', 'status': False, 'errors': validated_data.errors},
                        status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, pk = None):
        rundown_item = models.RundownDetail.objects.filter(id = pk).first()
        if rundown_item is None:
            return Response({'message':'Rundown item not found', 'status':False, 'data':{}},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            rundown = models.Rundown.objects.filter(id=rundown_item.rundown_id).first()
            self.check_object_permissions(request, rundown)
            serializer = serializers.RundownDetailSerializer(rundown_item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Successfully partial update!', 'status': True, 'data':serializer.data})

            return Response({'message': 'An error due to bad request', 'status': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        rundown_item = models.RundownDetail.objects.filter(id = pk).first()
        if rundown_item is None:
            return Response({'message':'Rundown item not found', 'status':False, 'data':{}},
                            status=status.HTTP_404_NOT_FOUND)
        rundown = models.Rundown.objects.filter(id = rundown_item.rundown_id).first()
        self.check_object_permissions(request, rundown)
        rundown_item.delete()
        return Response({'message': 'Successfully deleted', 'status': True, 'data': {}})


class FriendViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsTheOwnerOfFriend, IsAuthenticated)
    serializer_class = serializers.FriendSerializer

    def list(self,request):
        friends = models.Friend.objects.filter(user=request.user)
        serializer = serializers.FriendSerializer(friends, many=True)
        return Response({'message': 'OK!', 'status': True, 'data':serializer.data })

    def create(self, request):
        serializer = serializers.FriendSerializer(data = request.data)
        if serializer.is_valid():
            current_user = models.UserProfile.objects.filter(id = request.user.id).first()
            user_instance = models.UserProfile.objects.filter(id = request.data.get('friend')).first()
            if user_instance is None or current_user is None or user_instance.id == request.user.id:
                return Response(
                    {'message': 'An error due to user not found', 'status': False, 'errors': serializer.errors},
                    status=status.HTTP_404_NOT_FOUND)

            self.check_object_permissions(request, current_user)
            friend = models.Friend(user = request.user, friend = user_instance)
            friend.save()
            return Response({'message':'Successfully created', 'status': True, 'data': serializer.data})

        return Response({'message': 'An error due to bad request', 'status': False, 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


