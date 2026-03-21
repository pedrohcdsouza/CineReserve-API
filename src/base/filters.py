from django_filters import rest_framework as filters


class UUIDInFilter(filters.BaseInFilter, filters.UUIDFilter):
    pass
