from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAuthenticationTests(APITestCase):
    
    def test_complete_auth_flow(self):
        # 1. S'inscrire
        register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post('/api/auth/register/', register_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. Se connecter
        login_data = {
            'username': 'newuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']
        refresh_token = response.data['refresh']
        
        # 3. Accéder au profil avec le token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'newuser')
        
        # 4. Rafraîchir le token
        response = self.client.post('/api/auth/refresh/', {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
