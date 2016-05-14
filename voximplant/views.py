# coding: utf-8
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from . import models
from . import serializers


# class CallList(ModelViewSet):
#     authentication_classes = (SessionAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     queryset = models.CallList.objects.all()
#     serializer_class = serializers.CallList
