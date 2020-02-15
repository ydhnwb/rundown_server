from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import filters
from django.db.models import Q
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.transaction import atomic
from rest_framework.decorators import action
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
    serializer_class = (serializers.UserProfileSerializer,)
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('name', 'email')


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
        try:
            user = models.UserProfile.objects.filter(id = pk).first()
            if user is None:
                return Response({'message':'User not found', 'status':False, 'data':{}},
                                status = status.HTTP_404_NOT_FOUND)

            self.check_object_permissions(request, user)
            user.delete()
            return Response({'message': 'Successfully deleted', 'status': True, 'data': {}})
        except Exception as e:
            print(e)
            pass



class RundownViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.RundownSerializer
    permission_classes = (permissions.PostOnRundown,IsAuthenticated)

    def list(self, request):
        rundowns = models.Rundown.objects.filter(user_profile = request.user).order_by('-updated_on')
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
            rundown_details = models.RundownDetail.objects.filter(rundown_id= rundown.id).order_by('order_num')
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

            already_stored_item = models.RundownDetail.objects.filter(rundown = rundown.id).order_by('-order_num').first()
            i = 0
            if already_stored_item is not None:
                i = already_stored_item.order_num+1

            rundown_item = models.RundownDetail(title = serializer.data.get('title'),description = serializer.data.get('description'),
                                     rundown = rundown, order_num = i)
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


    @action(detail=False, methods=['get'])
    def friend_requests(self, request):
        friend_request = models.Friend.objects.filter(Q(friend = request.user) & Q(is_accepted = False))
        requests_serializer = serializers.FriendSerializer(friend_request, many=True)
        return Response({'message':'OK!', 'status':True, 'data':requests_serializer.data})

    @action(detail=False, methods=['get'])
    def requested(self, request):
        friends_requested = models.Friend.objects.filter(Q(user=request.user) & Q(is_accepted = False))
        requested_serializer = serializers.FriendSerializer(friends_requested, many=True)
        return Response({'message':'OK!', 'status':True, 'data':requested_serializer.data})

    def list(self,request):
        friends = models.Friend.objects.filter(user=request.user)
        accepted_serializer = serializers.FriendSerializer(friends, many=True)
        return Response({'message': 'OK!', 'status': True, 'data': accepted_serializer.data })


    def destroy(self, request, pk=None):
        friendship = models.Friend.objects.filter(id=pk).first()
        targeted_friend = models.Friend.objects.filter(Q(user = friendship.friend) & Q(friend = friendship.user))
        friendship.delete()
        targeted_friend.delete()
        return Response({'message': 'Successfully deleted', 'status': True, 'data': {}})


    def retrieve(self, request, pk=None):
        friend = models.Friend.objects.filter(id=pk).first()
        if friend is None:
            return Response({'message': 'Friend not found', 'status': False, 'data': {}}, status = status.HTTP_404_NOT_FOUND)
        else:
            serializer = serializers.FriendSerializer(friend)
            return Response({'message': 'OK!', 'status': True, 'data': serializer.data})


    def partial_update(self, request, pk=None):
        try:
            friend = models.Friend.objects.filter(id=pk).first()
            if friend is None:
                return Response({'message': 'User item not found', 'status': False, 'data': {}}, status=status.HTTP_404_NOT_FOUND)
            else:
                if friend.user == request.user:
                    with atomic():
                        serializer = serializers.FriendSerializer(friend, data = request.data, partial=True)
                        target_friend = models.Friend.objects.filter(Q(user = friend.friend.id) & Q(friend = request.user)).first()
                        print(target_friend)
                        print(friend)
                        target_serializer = serializers.FriendSerializer(target_friend, data=request.data, partial=True)
                        if serializer.is_valid() and target_serializer.is_valid():
                            serializer.save()
                            target_serializer.save()
                            return Response({'message': 'Accepted', 'status': True, 'data': serializer.data})
                        else:
                            return Response({'message': 'An error due to bad request', 'status': False,
                                             'errors': serializer.errors},
                                            status=status.HTTP_400_BAD_REQUEST)

                else:
                    return Response({'message': 'Cannot change other preference', 'status': False, 'data': {}})
        except Exception as e:
            return Response({'message': 'An error due to bad request', 'status': False, 'errors': str(e)},status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        serializer = serializers.FriendSerializer(data = request.data)
        if serializer.is_valid():
            user_instance = models.UserProfile.objects.filter(id = request.data.get('friend')).first()
            if user_instance is None or request.user is None or user_instance.id == request.user.id:
                return Response(
                    {'message': 'An error due to user not found', 'status': False, 'errors': serializer.errors},
                    status=status.HTTP_404_NOT_FOUND)
            # target = models.
            exists = models.Friend.objects.filter(Q(user = request.user) & Q(friend = request.data.get('friend'))).first()
            if exists is None:
                try:
                    with atomic():
                        friend = models.Friend(user = request.user, friend = user_instance)
                        friend.save()
                        target_friend = models.Friend(user = user_instance, friend = request.user)
                        target_friend.save()
                        return Response({'message': 'Successfully created', 'status': True, 'data': serializer.data})
                except Exception as e:
                    print(e)
                    return Response(
                        {'message': 'An error due to bad request', 'status': False, 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {'message': 'Already requested or friend', 'status': False, 'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'An error due to bad request', 'status': False, 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class ReoderRundownDetailViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.ReorderRundownDetailSerializer
    permission_classes = (permissions.PostOnRundown,IsAuthenticated)

    def create(self,request):
        # its actually update
        try:
            serializer = serializers.ReorderRundownDetailSerializer(data=request.data, many=True)
            if serializer.is_valid():
                datas = serializer.data
                with atomic():
                    for data in datas:
                        rundown = models.Rundown.objects.filter(id=data['rundown_id']).first()
                        if rundown is not None:
                            self.check_object_permissions(request, rundown)
                            rundown_detail = models.RundownDetail.objects.filter(id = data['id']).first()
                            if rundown_detail is not None:
                                s = serializers.RundownDetailSerializer(rundown_detail, data=data,partial=True)
                                if s.is_valid(raise_exception=True):
                                    s.save()

                return Response({'message':"Success reorder!", 'status':False, 'data':serializer.data})

            return Response({'message':'Data given is not valid', 'status':False, 'errors':serializer.errors})
        except Exception as e:
            print(e)
            return Response({'message':str(e), 'status':False, 'data':{}})


class SearchViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        users = models.UserProfile.objects.filter(Q(name__istartswith = request.data.get('query')) | Q(email = request.data.get('query')))
        user_serializer = serializers.UserProfileSerializer(users, many = True)
        rundowns = models.Rundown.objects.filter(Q(user_profile=request.user) & Q(title__istartswith = request.data.get('query'))).order_by('-updated_on')
        rundown_serializer = serializers.RundownSerializer(rundowns, many=True)
        # rundowns = models.Rundown.objects.filter(user_profile = request.user).order_by('-updated_on')
        # serializer = serializers.RundownSerializer(rundowns, many=True)
        return Response({'message':'OK!', 'status': True, 'data':{
            'users':user_serializer.data,
            'rundowns' : rundown_serializer.data
        }})