from rest_framework import status
from rest_framework.reverse import reverse
from shared.serializers import UserSerializer
from rest_framework.test import (APIClient, APITestCase)

"""
IMPORTANT: to run the tests, you need to have the Basic Authentication activated in your Django settings.
"""


class JwtAuthTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

        cls.test_user = {'email': 'test@test.com', 'password': 'testtest', 'first_name': 'test_fn',
                         'last_name': 'test_ln'}

        serializer = UserSerializer(data=cls.test_user)
        serializer.is_valid()
        serializer.save()


class RegistrationTests(JwtAuthTests):
    def test_successful_registration(self):
        payload = {'email': 'user@user.com', 'password': 'useruser', 'first_name': 'user_fn', 'last_name': 'user_ln'}
        response = self.client.post(reverse('register'), payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        payload = {'email': 'user@user.com', 'password': 'useruser'}
        response = self.client.post(reverse('token'), payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_registration_with_missing_fields(self):
        response = self.client.post(reverse('register'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_with_invalid_fields(self):
        payload = {
            'email': 'bad email',
            'password': 'short',
            'first_name': 'hahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahaha',
            'last_name': 'hahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahaha'
        }

        response = self.client.post(reverse('register'), payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_with_existing_email(self):
        payload = {'email': 'test@test.com', 'password': 'testtest', 'first_name': 'test_fn', 'last_name': 'test_ln'}
        response = self.client.post(reverse('register'), payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthenticationTests(JwtAuthTests):
    def test_successful_login(self):
        payload = {'email': 'test@test.com', 'password': 'testtest', }
        response = self.client.post(reverse('token'), payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_with_missing_fields(self):
        response = self.client.post(reverse('token'), {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_invalid_credentials(self):
        payload = {'email': 'inexistant@inexistant.com', 'password': 'inexistant'}
        response = self.client.post(reverse('token'), payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_access_token(self):
        payload = {'email': 'test@test.com', 'password': 'testtest', }
        response = self.client.post(reverse('token'), payload)

        payload = {'refresh': response.data['refresh']}
        response = self.client.post(reverse('token_refresh'), payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_access_token_with_missing_fields(self):
        response = self.client.post(reverse('token_refresh'), {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_access_token_with_invalid_token(self):
        response = self.client.post(reverse('token_refresh'), {'refresh': 'ey...'})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserUpdateTests(JwtAuthTests):
    def test_successful_password_update(self):
        payload = {'password': 'test1test1'}
        headers = {'Authorization': 'Basic dGVzdEB0ZXN0LmNvbTp0ZXN0dGVzdA=='}  # test@test.com:testtest as base64
        response = self.client.put(reverse('update_password'), payload, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        headers = {'Authorization': 'Basic dGVzdEB0ZXN0LmNvbTp0ZXN0MXRlc3Qx'}  # test@test.com:test1test1 as base64
        response = self.client.get(reverse('who_am_i'), headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_update_with_invalid_field(self):
        payload = {'password': 'short'}
        headers = {'Authorization': 'Basic dGVzdEB0ZXN0LmNvbTp0ZXN0dGVzdA=='}  # test@test.com:testtest as base64
        response = self.client.put(reverse('update_password'), payload, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_update_with_missing_field(self):
        payload = {}
        headers = {'Authorization': 'Basic dGVzdEB0ZXN0LmNvbTp0ZXN0dGVzdA=='}  # test@test.com:testtest as base64
        response = self.client.put(reverse('update_password'), payload, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_update_with_invalid_credentials(self):
        payload = {'password': 'test1test1'}
        headers = {'Authorization': 'Basic aW52YWxpZEB1c2VyLmNvbTppbnZhbGlk'}  # Invalid credentials as base64
        response = self.client.put(reverse('update_password'), payload, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_successful_user_update(self):
        payload = {'email': 'test1@test1.com', 'password': 'test1test1',
                   'first_name': 'test1_fn', 'last_name': 'test1_ln'}

        headers = {'Authorization': 'Basic dGVzdEB0ZXN0LmNvbTp0ZXN0dGVzdA=='}  # test@test.com:testtest as base64
        response = self.client.put(reverse('update_user'), payload, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        headers = {'Authorization': 'Basic dGVzdDFAdGVzdDEuY29tOnRlc3R0ZXN0'}  # test1@test1.com:testtest as base64
        response = self.client.get(reverse('who_am_i'), headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_update_with_invalid_field(self):
        payload = {'email': 'bad email', 'first_name': 'x' * 31, 'last_name': 'x' * 31}
        headers = {'Authorization': 'Basic dGVzdEB0ZXN0LmNvbTp0ZXN0dGVzdA=='}  # test@test.com:testtest as base64
        response = self.client.put(reverse('update_user'), payload, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_update_with_missing_field(self):
        payload = {'first_name': 'updated_fn', 'last_name': 'updated_ln'}
        headers = {'Authorization': 'Basic dGVzdEB0ZXN0LmNvbTp0ZXN0dGVzdA=='}  # test@test.com:testtest as base64
        response = self.client.put(reverse('update_user'), payload, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_update_with_invalid_credentials(self):
        payload = {'email': 'test1@test1.com', 'first_name': 'test1_fn', 'last_name': 'test1_ln'}
        headers = {'Authorization': 'Basic aW52YWxpZEB1c2VyLmNvbTppbnZhbGlk'}  # Invalid credentials as base64
        response = self.client.put(reverse('update_user'), payload, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_update_with_existing_email(self):
        existing_user_payload = {
            'email': 'existing@test.com',
            'password': 'existingpass',
            'first_name': 'existing_fn',
            'last_name': 'existing_ln'
        }

        self.client.post(reverse('register'), existing_user_payload)

        payload = {'email': 'existing@test.com', 'first_name': 'test1_fn', 'last_name': 'test1_ln'}
        headers = {'Authorization': 'Basic dGVzdEB0ZXN0LmNvbTp0ZXN0dGVzdA=='}  # test@test.com:testtest as base64
        response = self.client.put(reverse('update_user'), payload, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
