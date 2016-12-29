from copy import deepcopy
import http
from unittest.mock import patch

import requests
import pytest


@pytest.fixture
def retrieve_profile_data():
    return {
        'website': 'http://example.com',
        'description': 'Ecommerce website',
        'number': '01234567',
        'sectors': ['SECURITY'],
        'logo': 'nice.jpg',
        'name': 'Great company',
        'keywords': 'word1 word2',
        'employees': '501-1000',
        'date_of_creation': '2015-03-02',
        'verified_with_code': True,
        'twitter_url': 'http://www.twitter.com',
        'facebook_url': 'http://www.facebook.com',
        'linkedin_url': 'http://www.linkedin.com',
        'supplier_case_studies': [],
        'modified': '2016-11-23T11:21:10.977518Z',
        'contact_details': {
            'email_full_name': 'Jeremy',
            'email_address': 'test@example.com',
            'postal_full_name': 'Jeremy',
            'address_line_1': '123 Fake Street',
            'address_line_2': 'Fakeville',
            'locality': 'London',
            'postal_code': 'E14 6XK',
            'po_box': 'abc',
            'country': 'GB',
        },
    }


@pytest.fixture
def list_public_profiles_data(retrieve_profile_data):
    return {
        'results': [
            retrieve_profile_data,
        ],
        'count': 20
    }


@pytest.fixture
def supplier_case_study_data(retrieve_profile_data):
    return {
        'description': 'Damn great',
        'sector': 'SOFTWARE_AND_COMPUTER_SERVICES',
        'image_three': 'https://image_three.jpg',
        'website': 'http://www.google.com',
        'video_one': 'https://video_one.wav',
        'title': 'Two',
        'company': retrieve_profile_data,
        'image_one': 'https://image_one.jpg',
        'testimonial': 'I found it most pleasing.',
        'keywords': 'great',
        'pk': 2,
        'year': '2000',
        'image_two': 'https://image_two.jpg'
    }


@pytest.fixture
def company_profile_companies_house_data():
    return {
        'email_full_name': 'Jeremy Companies House',
        'email_address': 'test@example.com',
        'postal_full_name': 'Jeremy',
        'address_line_1': '123 Fake Street',
        'address_line_2': 'Fakeville',
        'locality': 'London',
        'postal_code': 'E14 6XK',
        'po_box': 'abc',
        'country': 'GB',
    }


@pytest.fixture
def api_response_company_profile_companies_house_200(
    company_profile_companies_house_data
):
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: deepcopy(company_profile_companies_house_data)
    return response


@pytest.fixture
def api_response_company_profile_200(retrieve_profile_data):
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: deepcopy(retrieve_profile_data)
    return response


@pytest.fixture
def api_response_company_profile_no_contact_details(retrieve_profile_data):
    data = retrieve_profile_data.copy()
    data['contact_details'] = {}
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: deepcopy(data)
    return response


@pytest.fixture
def api_response_200():
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: deepcopy({})
    return response


@pytest.fixture
def api_response_list_public_profile_200(
    api_response_200, list_public_profiles_data
):
    response = api_response_200
    response.json = lambda: deepcopy(list_public_profiles_data)
    return response


@pytest.fixture
def api_response_retrieve_supplier_case_study_200(supplier_case_study_data):
    response = api_response_200()
    response.json = lambda: deepcopy(supplier_case_study_data)
    return response


@pytest.fixture(autouse=True)
def retrieve_supplier_case_study_response(api_response_200):
    stub = patch(
        'api_client.api_client.company.retrieve_supplier_case_study',
        return_value=api_response_200,
    )
    stub.start()
    yield
    stub.stop()


@pytest.fixture(autouse=True)
def list_public_profiles(api_response_list_public_profile_200):
    stub = patch(
        'api_client.api_client.company.list_public_profiles',
        return_value=api_response_list_public_profile_200,
    )
    stub.start()
    yield
    stub.stop()


@pytest.fixture(autouse=True)
def retrieve_supplier_case_study(
    api_response_retrieve_supplier_case_study_200
):
    stub = patch(
        'api_client.api_client.company.retrieve_supplier_case_study',
        return_value=api_response_retrieve_supplier_case_study_200,
    )
    stub.start()
    yield
    stub.stop()


@pytest.fixture(autouse=True)
def retrieve_profile(api_response_company_profile_200):
    stub = patch(
        'api_client.api_client.company.retrieve_profile',
        return_value=api_response_company_profile_200,
    )
    stub.start()
    yield
    stub.stop()


@pytest.fixture(autouse=True)
def get_companies_house_office_address(
    api_response_company_profile_companies_house_200
):
    stub = patch(
        'company.helpers.get_companies_house_office_address',
        return_value=api_response_company_profile_companies_house_200,
    )
    stub.start()
    yield
    stub.stop()
