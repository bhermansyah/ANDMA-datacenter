import json
import time, copy
import operator

from django.conf.urls import url
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db.models import Count

from avatar.templatetags.avatar_tags import avatar_url
from guardian.shortcuts import get_objects_for_user

from geonode.base.models import ResourceBase
from geonode.base.models import TopicCategory
from geonode.base.models import Region
from geonode.layers.models import Layer
from geonode.maps.models import Map
from geonode.documents.models import Document
from geonode.groups.models import GroupProfile

from taggit.models import Tag
from django.core.serializers.json import DjangoJSONEncoder
from tastypie.serializers import Serializer
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL
from tastypie.utils import trailing_slash

from django.utils.translation import ugettext as _

FILTER_TYPES = {
    'layer': Layer,
    'map': Map,
    'document': Document
}


class CountJSONSerializer(Serializer):
    """Custom serializer to post process the api and add counts"""

    def get_resources_counts(self, options):
        if settings.SKIP_PERMS_FILTER:
            resources = ResourceBase.objects.all()
        else:
            resources = get_objects_for_user(
                options['user'],
                'base.view_resourcebase'
            )
        if settings.RESOURCE_PUBLISHING:
            resources = resources.filter(is_published=True)

        if options['title_filter']:
            resources = resources.filter(title__icontains=options['title_filter'])

        if options['category_filter']:
            resources = resources.filter(category__identifier__in=options['category_filter'])

        if options['keyword_filter']:
            resources = resources.filter(keywords__slug__in=options['keyword_filter'])

        if options['region_filter']:
            resources = resources.filter(regions__name__in=options['region_filter'])

        if options['date_gte_filter']:
            resources = resources.filter(date__gte=options['date_gte_filter'])

        if options['date_lte_filter']:
            resources = resources.filter(date__lte=options['date_lte_filter'])

        if options['date_range_filter']:
            resources = resources.filter(date__range=options['date_range_filter'])

        if options['type_filter']:
            resources = resources.instance_of(options['type_filter'])

        counts = list(resources.values(options['count_type']).annotate(count=Count(options['count_type'])))

        return dict([(c[options['count_type']], c['count']) for c in counts])

    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        counts = self.get_resources_counts(options)
        for item in data['objects']:
            item['count'] = counts.get(item['id'], 0)

        # Add in the current time.
        data['requested_time'] = time.time()

        cloned_data = copy.copy(data)
        cloned_data['objects'] = []

        if options['count_type']=='regions':
            lev3 = [z for z in data['objects'] if z['level'] == 3 and (z['code']=='AFG' or z['code']=='AFG01'  or z['code']=='AFG02'  or z['code']=='AFG03'  or z['code']=='AFG04'  or z['code']=='AFG05' or z['code']=='AFG06')]
            i = 0
            for lev3item in lev3:
                i = i+1
                lev3item['children']=[]
                if i == 7:
                    lev4 = [x for x in data['objects'] if x['level'] == 4]
                    for lev4item in lev4:
                        lev4item['children']=[]
                        lev4item['show']=False
                        lev5 = [y for y in data['objects'] if y['level'] == 5 and y['code'][:2]==lev4item['code'] and y['count']>0]
                        for lev5item in lev5:
                            lev4item['children'].append(lev5item)
                        lev3item['children'].append(lev4item)
                cloned_data['objects'].append(lev3item)

            return json.dumps(cloned_data, cls=DjangoJSONEncoder, sort_keys=True)
        elif options['count_type']=='category':
            group = []
            group.append({'count': 0, 'gn_description_en': _('Agriculture'), 'description': _('Agriculture'), 'gn_description': _('Agriculture'), 'is_choice': True, 'description_en': _('Agriculture'), 'identifier': 'agr', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Avalanches'), 'description': _('Avalanches'), 'gn_description': _('Avalanches'), 'is_choice': True, 'description_en': _('Avalanches'), 'identifier': 'av', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Administrative'), 'description': _('Administrative'), 'gn_description': _('Administrative'), 'is_choice': True, 'description_en': _('Administrative'), 'identifier': 'bnd', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Droughts'), 'description': _('Droughts'), 'gn_description': _('Droughts'), 'is_choice': True, 'description_en': _('Droughts'), 'identifier': 'dr', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Earthquake'), 'description': _('Earthquake'), 'gn_description': _('Earthquake'), 'is_choice': True, 'description_en': _('Earthquake'), 'identifier': 'eq', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Education'), 'description': _('Education'), 'gn_description': _('Education'), 'is_choice': True, 'description_en': _('Education'), 'identifier': 'edu', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Emergency Response'), 'description': _('Emergency Response'), 'gn_description': _('Emergency Response'), 'is_choice': True, 'description_en': _('Emergency Response'), 'identifier': 'erm', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Floods'), 'description': _('Floods'), 'gn_description': _('Floods'), 'is_choice': True, 'description_en': _('Floods'), 'identifier': 'fl', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Physical Environment'), 'description': _('Physical Environment'), 'gn_description': _('Physical Environment'), 'is_choice': True, 'description_en': _('Physical Environment'), 'identifier': 'geo', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Health'), 'description': _('Health'), 'gn_description': _('Health'), 'is_choice': True, 'description_en': _('Health'), 'identifier': 'hlt', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Hydrology'), 'description': _('Hydrology'), 'gn_description': _('Hydrology'), 'is_choice': True, 'description_en': _('Hydrology'), 'identifier': 'hydro', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Hazard'), 'description': _('Hazard'), 'gn_description': _('Hazard'), 'is_choice': True, 'description_en': _('Hazard'), 'identifier': 'hz', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('IDP'), 'description': _('IDP'), 'gn_description': _('IDP'), 'is_choice': True, 'description_en': _('IDP'), 'identifier': 'idp', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Imagery'), 'description': _('Imagery'), 'gn_description': _('Imagery'), 'is_choice': True, 'description_en': _('Imagery'), 'identifier': 'img', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Infrastructure'), 'description': _('Infrastructure'), 'gn_description': _('Infrastructure'), 'is_choice': True, 'description_en': _('Infrastructure'), 'identifier': 'infr', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Meteorology'), 'description': _('Meteorology'), 'gn_description': _('Meteorology'), 'is_choice': True, 'description_en': _('Meteorology'), 'identifier': 'met', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Settlements'), 'description': _('Settlements'), 'gn_description': _('Settlements'), 'is_choice': True, 'description_en': _('Settlements'), 'identifier': 'ppl', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Security'), 'description': _('Security'), 'gn_description': _('Security'), 'is_choice': True, 'description_en': _('Security'), 'identifier': 'sec', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Socio-demographics'), 'description': _('Socio-demographics'), 'gn_description': _('Socio-demographics'), 'is_choice': True, 'description_en': _('Socio-demographics'), 'identifier': 'sos', 'id': 0, u'resource_uri': '','children':[]})
            group.append({'count': 0, 'gn_description_en': _('Others'), 'description': _('Others'), 'gn_description': _('Others'), 'is_choice': True, 'description_en': _('Others'), 'identifier': 'ot', 'id': 0, u'resource_uri': '','children':[]})
            for group_state in group:
                filteredItems = [x for x in data['objects'] if x['identifier'].split('-', 1 )[0] == group_state['identifier']]

                test = copy.copy(sorted(filteredItems, key=lambda filteredItem:filteredItem['gn_description'] ))
                for filteredItem in test:
                    group_state['children'].append(filteredItem)
                    group_state['count'] = group_state['count'] + filteredItem['count']
                    group_state['show']=False
            cloned_data['objects'] = group
            return json.dumps(cloned_data, cls=DjangoJSONEncoder, sort_keys=True)
        else:
            return json.dumps(data, cls=DjangoJSONEncoder, sort_keys=True)


class TypeFilteredResource(ModelResource):
    """ Common resource used to apply faceting to categories, keywords, and
    regions based on the type passed as query parameter in the form
    type:layer/map/document"""

    count = fields.IntegerField()

    def build_filters(self, filters={}):
        self.type_filter = None
        self.title_filter = None
        self.category_filter = None
        self.keyword_filter = None
        self.region_filter = None
        self.date_gte_filter = None
        self.date_lte_filter = None
        self.date_range_filter = None

        orm_filters = super(TypeFilteredResource, self).build_filters(filters)

        if 'type' in filters and filters['type'] in FILTER_TYPES.keys():
            self.type_filter = FILTER_TYPES[filters['type']]
        else:
            self.type_filter = None
        if 'title__icontains' in filters:
            self.title_filter = filters['title__icontains']
        if 'category__identifier__in' in filters:
            self.category_filter = filters.getlist('category__identifier__in')
        if 'keywords__slug__in' in filters:
            self.keyword_filter = filters.getlist('keywords__slug__in')
        if 'regions__name__in' in filters:
            self.region_filter = filters.getlist('regions__name__in')
        if 'date__gte' in filters:
            self.date_gte_filter = filters['date__gte']
        if 'date__lte' in filters:
            self.date_lte_filter = filters['date__lte']
        if 'date__range' in filters:
            self.date_range_filter = filters['date__range']
        return orm_filters

    def serialize(self, request, data, format, options={}):
        options['title_filter'] = self.title_filter
        options['category_filter'] = self.category_filter
        options['keyword_filter'] = self.keyword_filter
        options['region_filter'] = self.region_filter
        options['date_gte_filter'] = self.date_gte_filter
        options['date_lte_filter'] = self.date_lte_filter
        options['date_range_filter'] = self.date_range_filter
        options['type_filter'] = self.type_filter
        options['user'] = request.user

        return super(TypeFilteredResource, self).serialize(request, data, format, options)


class TagResource(TypeFilteredResource):
    """Tags api"""

    def serialize(self, request, data, format, options={}):
        options['count_type'] = 'keywords'

        return super(TagResource, self).serialize(request, data, format, options)

    class Meta:
        queryset = Tag.objects.all().order_by('name')
        resource_name = 'keywords'
        allowed_methods = ['get']
        filtering = {
            'slug': ALL,
        }
        serializer = CountJSONSerializer()


class RegionResource(TypeFilteredResource):
    """Regions api"""

    def serialize(self, request, data, format, options={}):
        options['count_type'] = 'regions'

        return super(RegionResource, self).serialize(request, data, format, options)

    class Meta:
        queryset = Region.objects.all().order_by('name')
        resource_name = 'regions'
        allowed_methods = ['get']
        filtering = {
            'name': ALL,
        }
        # To activate the counts on regions uncomment the following line
        serializer = CountJSONSerializer()


class TopicCategoryResource(TypeFilteredResource):
    """Category api"""

    def serialize(self, request, data, format, options={}):
        options['count_type'] = 'category'

        return super(TopicCategoryResource, self).serialize(request, data, format, options)

    class Meta:
        queryset = TopicCategory.objects.all().order_by('identifier')
        resource_name = 'categories'
        allowed_methods = ['get']
        filtering = {
            'identifier': ALL,
        }
        serializer = CountJSONSerializer()


class GroupResource(ModelResource):
    """Groups api"""

    detail_url = fields.CharField()
    member_count = fields.IntegerField()
    manager_count = fields.IntegerField()

    def dehydrate_member_count(self, bundle):
        return bundle.obj.member_queryset().count()

    def dehydrate_manager_count(self, bundle):
        return bundle.obj.get_managers().count()

    def dehydrate_detail_url(self, bundle):
        return reverse('group_detail', args=[bundle.obj.slug])

    class Meta:
        queryset = GroupProfile.objects.all()
        resource_name = 'groups'
        allowed_methods = ['get']
        filtering = {
            'name': ALL
        }
        ordering = ['title', 'last_modified']


class ProfileResource(ModelResource):
    """Profile api"""

    avatar_100 = fields.CharField(null=True)
    profile_detail_url = fields.CharField()
    email = fields.CharField(default='')
    layers_count = fields.IntegerField(default=0)
    maps_count = fields.IntegerField(default=0)
    documents_count = fields.IntegerField(default=0)
    current_user = fields.BooleanField(default=False)
    activity_stream_url = fields.CharField(null=True)

    def build_filters(self, filters={}):
        """adds filtering by group functionality"""

        orm_filters = super(ProfileResource, self).build_filters(filters)

        if 'group' in filters:
            orm_filters['group'] = filters['group']

        return orm_filters

    def apply_filters(self, request, applicable_filters):
        """filter by group if applicable by group functionality"""

        group = applicable_filters.pop('group', None)

        semi_filtered = super(
            ProfileResource,
            self).apply_filters(
            request,
            applicable_filters)

        if group is not None:
            semi_filtered = semi_filtered.filter(
                groupmember__group__slug=group)

        return semi_filtered

    def dehydrate_email(self, bundle):
        email = ''
        if bundle.request.user.is_authenticated():
            email = bundle.obj.email
        return email

    def dehydrate_layers_count(self, bundle):
        obj_with_perms = get_objects_for_user(bundle.request.user,
                                              'base.view_resourcebase').instance_of(Layer)
        return bundle.obj.resourcebase_set.filter(id__in=obj_with_perms.values('id')).distinct().count()

    def dehydrate_maps_count(self, bundle):
        obj_with_perms = get_objects_for_user(bundle.request.user,
                                              'base.view_resourcebase').instance_of(Map)
        return bundle.obj.resourcebase_set.filter(id__in=obj_with_perms.values('id')).distinct().count()

    def dehydrate_documents_count(self, bundle):
        obj_with_perms = get_objects_for_user(bundle.request.user,
                                              'base.view_resourcebase').instance_of(Document)
        return bundle.obj.resourcebase_set.filter(id__in=obj_with_perms.values('id')).distinct().count()

    def dehydrate_avatar_100(self, bundle):
        return avatar_url(bundle.obj, 100)

    def dehydrate_profile_detail_url(self, bundle):
        return bundle.obj.get_absolute_url()

    def dehydrate_current_user(self, bundle):
        return bundle.request.user.username == bundle.obj.username

    def dehydrate_activity_stream_url(self, bundle):
        return reverse(
            'actstream_actor',
            kwargs={
                'content_type_id': ContentType.objects.get_for_model(
                    bundle.obj).pk,
                'object_id': bundle.obj.pk})

    def prepend_urls(self):
        if settings.HAYSTACK_SEARCH:
            return [
                url(r"^(?P<resource_name>%s)/search%s$" % (
                    self._meta.resource_name, trailing_slash()
                ),
                    self.wrap_view('get_search'), name="api_get_search"),
            ]
        else:
            return []

    class Meta:
        queryset = get_user_model().objects.exclude(username='AnonymousUser')
        resource_name = 'profiles'
        allowed_methods = ['get']
        ordering = ['username', 'date_joined']
        excludes = ['is_staff', 'password', 'is_superuser',
                    'is_active', 'last_login']

        filtering = {
            'username': ALL,
        }
