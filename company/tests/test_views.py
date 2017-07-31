import http
from unittest.mock import call, patch, Mock

import pytest
import requests

from django.core.urlresolvers import reverse

from company import helpers, views


@pytest.fixture
def api_response_200():
    response = requests.Response()
    response.status_code = http.client.OK
    return response


@pytest.fixture
def api_response_400():
    response = requests.Response()
    response.status_code = http.client.BAD_REQUEST
    return response


@pytest.fixture
def api_response_404(*args, **kwargs):
    response = requests.Response()
    response.status_code = http.client.NOT_FOUND
    return response


@pytest.fixture
def retrieve_public_case_study_200(api_response_200):
    response = api_response_200
    response.json = lambda: {'field': 'value'}
    return response


@pytest.fixture
def valid_contact_company_data(captcha_stub):
    return {
        'full_name': 'Jim Example',
        'company_name': 'Example Corp',
        'country': 'China',
        'email_address': 'jim@example.com',
        'sector': 'AEROSPACE',
        'subject': 'greetings',
        'body': 'and salutations',
        'recaptcha_response_field': captcha_stub,
        'terms': True,
    }


@pytest.fixture
def search_results(retrieve_profile_data):
    return {
        'hits': {
            'total': 1,
            'hits': [
                {
                    '_source': retrieve_profile_data

                }
            ]
        }
    }


@pytest.fixture
def api_response_search_200(api_response_200, search_results):
    api_response_200.json = lambda: search_results
    return api_response_200


def test_public_profile_different_slug_redirected(
    client, retrieve_profile_data
):
    url = reverse(
        'public-company-profiles-detail',
        kwargs={
            'company_number': retrieve_profile_data['number'],
            'slug': retrieve_profile_data['slug'] + 'thing',
        }
    )
    expected_redirect_url = reverse(
        'public-company-profiles-detail',
        kwargs={
            'company_number': retrieve_profile_data['number'],
            'slug': retrieve_profile_data['slug'],
        }
    )

    response = client.get(url)

    assert response.status_code == http.client.MOVED_PERMANENTLY
    assert response.get('Location') == expected_redirect_url


def test_public_profile_missing_slug_redirected(client, retrieve_profile_data):
    url = reverse(
        'public-company-profiles-detail-slugless',
        kwargs={
            'company_number': retrieve_profile_data['number'],
        }
    )
    expected_redirect_url = reverse(
        'public-company-profiles-detail',
        kwargs={
            'company_number': retrieve_profile_data['number'],
            'slug': retrieve_profile_data['slug'],
        }
    )

    response = client.get(url)

    assert response.status_code == http.client.MOVED_PERMANENTLY
    assert response.get('Location') == expected_redirect_url


def test_public_profile_same_slug_not_redirected(
    client, retrieve_profile_data
):
    url = reverse(
        'public-company-profiles-detail',
        kwargs={
            'company_number': retrieve_profile_data['number'],
            'slug': retrieve_profile_data['slug'],
        }
    )

    response = client.get(url)
    assert response.status_code == http.client.OK


def test_public_profile_details_verbose_context(client, retrieve_profile_data):
    url = reverse(
        'public-company-profiles-detail',
        kwargs={
            'company_number': retrieve_profile_data['number'],
            'slug': retrieve_profile_data['slug'],
        }
    )
    response = client.get(url + '?verbose=true')
    assert response.status_code == http.client.OK
    assert response.context_data['show_description'] is True


def test_public_profile_details_non_verbose_context(
    client, retrieve_profile_data
):
    url = reverse(
        'public-company-profiles-detail',
        kwargs={
            'company_number': retrieve_profile_data['number'],
            'slug': retrieve_profile_data['slug'],
        }
    )
    response = client.get(url)
    assert response.status_code == http.client.OK
    assert response.context_data['show_description'] is False


@patch.object(views.api_client.company, 'retrieve_public_profile', Mock)
@patch.object(helpers, 'get_public_company_profile_from_response')
def test_public_profile_details_exposes_context(
    mock_get_public_company_profile_from_response, client
):
    company = {
        'name': 'Example corp',
        'logo': 'logo.png',
        'summary': 'summary summary',
        'slug': 'thing',
    }
    mock_get_public_company_profile_from_response.return_value = company
    url = reverse(
        'public-company-profiles-detail',
        kwargs={'company_number': '01234567', 'slug': 'thing'},
    )
    response = client.get(url)
    assert response.status_code == http.client.OK
    assert response.template_name == [
        views.PublishedProfileDetailView.template_name
    ]
    assert response.context_data['company'] == company
    assert response.context_data['social'] == {
        'description': company['summary'],
        'image': company['logo'],
        'title': 'International trade profile: {}'.format(company['name']),
    }


def test_company_profile_list_with_params_redirects_to_search(client):
    url = reverse('public-company-profiles-list')
    response = client.get(url, {'sectors': 'AEROSPACE'})

    assert response.status_code == 302
    assert response.get('Location') == '/search?sector=AEROSPACE'


def test_company_profile_list_redirects_to_search(client):
    url = reverse('public-company-profiles-list')
    response = client.get(url)

    assert response.status_code == 302
    assert response.get('Location') == '/search'


@patch.object(helpers, 'get_public_company_profile_from_response')
def test_public_profile_details_calls_api(mock_retrieve_profile, client):
    url = reverse(
        'public-company-profiles-detail',
        kwargs={'company_number': '01234567', 'slug': 'thing'}
    )
    client.get(url)

    assert mock_retrieve_profile.called_once_with(1)


@patch.object(views.api_client.company, 'retrieve_public_profile')
def test_public_profile_details_handles_bad_status(
    mock_retrieve_public_profile, client, api_response_400
):
    mock_retrieve_public_profile.return_value = api_response_400
    url = reverse(
        'public-company-profiles-detail',
        kwargs={'company_number': '01234567', 'slug': 'thing'}
    )

    with pytest.raises(requests.exceptions.HTTPError):
        client.get(url)


@patch.object(views.api_client.company, 'retrieve_public_profile')
def test_public_profile_details_handles_404(
    mock_retrieve_public_profile, client, api_response_404
):
    mock_retrieve_public_profile.return_value = api_response_404
    url = reverse(
        'public-company-profiles-detail',
        kwargs={'company_number': '01234567', 'slug': 'thing'}
    )

    response = client.get(url)

    assert response.status_code == http.client.NOT_FOUND


@patch.object(views.api_client.company, 'retrieve_public_case_study')
def test_supplier_case_study_exposes_context(
    mock_retrieve_public_case_study, client, supplier_case_study_data,
    api_response_retrieve_public_case_study_200
):
    mock_retrieve_public_case_study.return_value = (
        api_response_retrieve_public_case_study_200
    )
    expected_case_study = helpers.get_case_study_details_from_response(
        api_response_retrieve_public_case_study_200
    )
    url = reverse(
        'case-study-details',
        kwargs={
            'id': supplier_case_study_data['pk'],
            'slug': supplier_case_study_data['slug'],
        }
    )
    response = client.get(url)

    assert response.status_code == http.client.OK
    assert response.template_name == [
        views.CaseStudyDetailView.template_name
    ]
    assert response.context_data['case_study'] == expected_case_study
    assert response.context_data['social'] == {
        'description': expected_case_study['description'],
        'image': expected_case_study['image_one'],
        'title': 'Project: {}'.format(expected_case_study['title']),
    }


@patch.object(views.api_client.company, 'retrieve_public_case_study')
def test_supplier_case_study_calls_api(
    mock_retrieve_public_case_study, client, supplier_case_study_data,
    api_response_retrieve_public_case_study_200
):
    mock_retrieve_public_case_study.return_value = (
        api_response_retrieve_public_case_study_200
    )
    url = reverse(
        'case-study-details',
        kwargs={
            'id': supplier_case_study_data['pk'],
            'slug': supplier_case_study_data['slug'],
        }
    )

    client.get(url)

    assert mock_retrieve_public_case_study.called_once_with(pk='2')


def test_case_study_different_slug_redirected(
    supplier_case_study_data, client
):
    url = reverse(
        'case-study-details',
        kwargs={
            'id': supplier_case_study_data['pk'],
            'slug': supplier_case_study_data['slug'] + 'thing',
        }
    )
    expected_redirect_url = reverse(
        'case-study-details',
        kwargs={
            'id': supplier_case_study_data['pk'],
            'slug': supplier_case_study_data['slug'],
        }
    )

    response = client.get(url)

    assert response.status_code == http.client.MOVED_PERMANENTLY
    assert response.get('Location') == expected_redirect_url


def test_case_study_missing_slug_redirected(supplier_case_study_data, client):
    url = reverse(
        'case-study-details-slugless',
        kwargs={
            'id': supplier_case_study_data['pk'],
        }
    )
    expected_redirect_url = reverse(
        'case-study-details',
        kwargs={
            'id': supplier_case_study_data['pk'],
            'slug': supplier_case_study_data['slug'],
        }
    )

    response = client.get(url)

    assert response.status_code == http.client.MOVED_PERMANENTLY
    assert response.get('Location') == expected_redirect_url


def test_case_study_same_slug_not_redirected(supplier_case_study_data, client):
    url = reverse(
        'case-study-details',
        kwargs={
            'id': supplier_case_study_data['pk'],
            'slug': supplier_case_study_data['slug'],
        }
    )

    response = client.get(url)
    assert response.status_code == http.client.OK


@patch.object(views.api_client.company, 'retrieve_public_case_study')
def test_supplier_case_study_handles_bad_status(
    mock_retrieve_public_case_study, client, api_response_400,
    supplier_case_study_data
):
    mock_retrieve_public_case_study.return_value = api_response_400
    url = reverse(
        'case-study-details',
        kwargs={
            'id': supplier_case_study_data['pk'],
            'slug': supplier_case_study_data['slug'],
        }
    )

    with pytest.raises(requests.exceptions.HTTPError):
        client.get(url)


@patch.object(views.api_client.company, 'retrieve_public_case_study')
def test_supplier_case_study_handles_404(
    mock_retrieve_public_case_study, client, api_response_404,
    supplier_case_study_data
):
    mock_retrieve_public_case_study.return_value = api_response_404
    url = reverse(
        'case-study-details',
        kwargs={
            'id': supplier_case_study_data['pk'],
            'slug': supplier_case_study_data['slug'],
        }
    )
    response = client.get(url)

    assert response.status_code == http.client.NOT_FOUND


def test_contact_company_view(client, retrieve_profile_data):
    url = reverse(
        'contact-company',
        kwargs={'company_number': retrieve_profile_data['number']},
    )
    response = client.get(url)

    assert response.status_code == http.client.OK


@patch.object(views.api_client.company, 'send_email')
def test_contact_company_view_feature_submit_success(
    mock_send_email, settings, client, valid_contact_company_data,
    retrieve_profile_data
):
    settings.FEATURE_CONTACT_COMPANY_FORM_ENABLED = True

    view = views.ContactCompanyView
    url = reverse(
        'contact-company',
        kwargs={
            'company_number': retrieve_profile_data['number'],
        },
    )
    response = client.post(url, valid_contact_company_data)

    expected_data = {
        'sender_email': valid_contact_company_data['email_address'],
        'sender_name': valid_contact_company_data['full_name'],
        'sender_company_name': valid_contact_company_data['company_name'],
        'sender_country': valid_contact_company_data['country'],
        'sector': valid_contact_company_data['sector'],
        'subject': valid_contact_company_data['subject'],
        'body': valid_contact_company_data['body'],
        'recipient_company_number': '01234567',
    }

    assert response.status_code == http.client.OK
    assert response.template_name == view.success_template_name
    assert mock_send_email.call_count == 1
    assert mock_send_email.call_args == call(expected_data)


@patch.object(views.api_client.company, 'send_email')
def test_contact_company_view_feature_submit_failure(
    mock_send_email, api_response_400, settings, client,
    valid_contact_company_data, retrieve_profile_data
):
    settings.FEATURE_CONTACT_COMPANY_FORM_ENABLED = True
    mock_send_email.return_value = api_response_400
    view = views.ContactCompanyView
    url = reverse(
        'contact-company',
        kwargs={
            'company_number': retrieve_profile_data['number'],
        },
    )

    response = client.post(url, valid_contact_company_data)

    assert response.status_code == http.client.OK
    assert response.template_name == view.failure_template_name


@patch.object(views.api_client.company, 'retrieve_public_profile', Mock)
@patch.object(helpers, 'get_public_company_profile_from_response')
def test_contact_company_exposes_context(
    mock_get_public_company_profile_from_response, client
):
    mock_get_public_company_profile_from_response.return_value = expected = {
        'number': '01234567',
        'slug': 'thing',
    }
    url = reverse(
        'contact-company',
        kwargs={'company_number': '01234567'}
    )

    response = client.get(url)
    assert response.status_code == http.client.OK
    assert response.template_name == [views.ContactCompanyView.template_name]
    assert response.context_data['company'] == expected


def test_company_search_404_feature_flag_disabled(client, settings):
    settings.FEATURE_COMPANY_SEARCH_VIEW_ENABLED = False

    response = client.get(reverse('company-search'))

    assert response.status_code == 404


def test_company_search_200_feature_flag_enabled(client, settings):
    settings.FEATURE_COMPANY_SEARCH_VIEW_ENABLED = True

    response = client.get(reverse('company-search'))

    assert response.status_code == 200


@patch('company.views.CompanySearchView.get_results_and_count')
def test_company_search_submit_form_on_get(
    mock_get_results_and_count, settings, client, search_results
):
    settings.FEATURE_COMPANY_SEARCH_VIEW_ENABLED = True
    results = [{'number': '1234567', 'slug': 'thing'}]
    mock_get_results_and_count.return_value = (results, 20)

    response = client.get(reverse('company-search'), {'term': '123'})

    assert response.status_code == 200
    assert response.context_data['results'] == results


@patch('company.views.CompanySearchView.get_results_and_count')
def test_company_search_pagination_count(
    mock_get_results_and_count, settings, client, search_results
):
    settings.FEATURE_COMPANY_SEARCH_VIEW_ENABLED = True
    results = [{'number': '1234567', 'slug': 'thing'}]
    mock_get_results_and_count.return_value = (results, 20)

    response = client.get(reverse('company-search'), {'term': '123'})

    assert response.status_code == 200
    assert response.context_data['pagination'].paginator.count == 20


@patch('api_client.api_client.company.search')
def test_company_search_pagination_param(
    mock_search, settings, client, search_results, api_response_search_200
):
    settings.FEATURE_COMPANY_SEARCH_VIEW_ENABLED = True
    mock_search.return_value = api_response_search_200

    url = reverse('company-search')
    response = client.get(
        url, {'term': '123', 'page': 1, 'sectors': ['AEROSPACE']}
    )

    assert response.status_code == 200
    assert mock_search.call_count == 1
    assert mock_search.call_args == call(
        page=1, size=10, term='123', sectors=['AEROSPACE'],
    )


@patch('api_client.api_client.company.search')
def test_company_search_pagination_empty_page(
    mock_search, settings, client, search_results, api_response_search_200
):
    settings.FEATURE_COMPANY_SEARCH_VIEW_ENABLED = True
    mock_search.return_value = api_response_search_200

    url = reverse('company-search')
    response = client.get(url, {'term': '123', 'page': 100})

    assert response.status_code == 302
    assert response.get('Location') == '/search?term=123'


@patch('company.views.CompanySearchView.get_results_and_count')
def test_company_search_not_submit_without_params(
    mock_get_results_and_count, settings, client
):
    settings.FEATURE_COMPANY_SEARCH_VIEW_ENABLED = True

    response = client.get(reverse('company-search'))

    assert response.status_code == 200
    mock_get_results_and_count.assert_not_called()


def test_company_search_sets_active_view_name(settings, client):
    settings.FEATURE_COMPANY_SEARCH_VIEW_ENABLED = True
    expected_value = 'public-company-profiles-list'

    response = client.get(reverse('company-search'))

    assert response.status_code == 200
    assert response.context_data['active_view_name'] == expected_value


@patch('api_client.api_client.company.search')
def test_company_search_api_call_error(mock_search, api_response_400, client):
    mock_search.return_value = api_response_400

    with pytest.raises(requests.exceptions.HTTPError):
        client.get(reverse('company-search'), {'term': '123'})


@patch('api_client.api_client.company.search')
@patch('company.helpers.get_results_from_search_response')
def test_company_search_api_success(
    mock_get_results_from_search_response, mock_search,
    api_response_search_200, client
):
    mock_search.return_value = api_response_search_200
    mock_get_results_from_search_response.return_value = {
        'results': [],
        'hits': {'total': 2}
    }
    response = client.get(reverse('company-search'), {'term': '123'})

    assert response.status_code == 200
    assert mock_get_results_from_search_response.call_count == 1
    assert mock_get_results_from_search_response.call_args == call(
        api_response_search_200
    )
