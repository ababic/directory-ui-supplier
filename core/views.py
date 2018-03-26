from django.conf import settings
from django.shortcuts import Http404
from django.utils import translation
from django.views.generic import TemplateView

from core import forms, helpers, mixins


class CMSFeatureFlagViewNegotiator(TemplateView):
    default_view_class = None
    feature_flagged_view_class = None

    def __new__(cls, *args, **kwargs):
        if settings.FEATURE_CMS_ENABLED:
            ViewClass = cls.feature_flagged_view_class
        else:
            ViewClass = cls.default_view_class
        return ViewClass(*args, **kwargs)


class BaseCMSView(mixins.ConditionalEnableTranslationsMixin, TemplateView):

    def dispatch(self, *args, **kwargs):
        if not settings.FEATURE_CMS_ENABLED:
            raise Http404()
        return super().dispatch(*args, **kwargs)


class LandingPageCMSView(mixins.ActiveViewNameMixin, BaseCMSView):
    active_view_name = 'index'
    template_name = 'core/landing-page.html'

    def list_pages(self):
        response = helpers.cms_client.find_a_supplier.list_industry_pages(
            language_code=translation.get_language(),
            draft_token=self.request.GET.get('draft_token'),
        )
        return helpers.handle_cms_response(response)

    def get_cms_page(self):
        response = helpers.cms_client.find_a_supplier.get_landing_page(
            language_code=translation.get_language(),
            draft_token=self.request.GET.get('draft_token'),
        )
        return helpers.handle_cms_response(response)

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            pages=self.list_pages()['items'],
            page=self.get_cms_page(),
            search_form=forms.SearchForm(),
            *args,
            **kwargs
        )