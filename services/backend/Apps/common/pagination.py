"""Shared pagination utilities.

Consumer list endpoints that can grow unbounded must return a paginated
envelope (`count/next/previous/results`) instead of a bare array. APIViews use
``paginate`` directly; ``paginated_response_serializer`` provides a matching
OpenAPI response component so the schema stays accurate.
"""

from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


def paginate(view, request, queryset, serializer_class, *, context=None):
    """Paginate a queryset/list and return a DRF paginated Response."""
    paginator = DefaultPagination()
    page = paginator.paginate_queryset(queryset, request, view=view)
    serializer = serializer_class(page, many=True, context=context or {})
    return paginator.get_paginated_response(serializer.data)


_PAGINATED_CACHE: dict[str, type] = {}


def paginated_response_serializer(inner_serializer_class):
    """Build (and cache) a `{count,next,previous,results}` serializer for docs."""
    name = inner_serializer_class.__name__.replace("Serializer", "") + "PaginatedResponse"
    if name not in _PAGINATED_CACHE:
        _PAGINATED_CACHE[name] = type(
            name,
            (serializers.Serializer,),
            {
                "count": serializers.IntegerField(),
                "next": serializers.CharField(allow_null=True),
                "previous": serializers.CharField(allow_null=True),
                "results": inner_serializer_class(many=True),
            },
        )
    return _PAGINATED_CACHE[name]
