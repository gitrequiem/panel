# app/api_client.py
import requests

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None

    def authenticate(self, username, usernumdoc, password):
        response = requests.post(f'{self.base_url}/login', json={
            'username': username,
            'usernumdoc': usernumdoc,
            'password': password
        })
        response.raise_for_status()
        self.token = response.json().get('access_token')

    def get_data(self, endpoint, params=None):
        headers = {'Authorization': f'Bearer {self.token}'} if self.token else {}
        response = requests.get(f'{self.base_url}/{endpoint}', headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def post_data(self, endpoint, data):
        headers = {'Authorization': f'Bearer {self.token}'} if self.token else {}
        response = requests.post(f'{self.base_url}/{endpoint}', headers=headers, json=data)
        # # print("post_data.response: ", response)
        # print("post_data.response.json(): ", response.json())
        # muestro = response.json()
        # # muestro_data = muestro['data']
        # # print(muestro_data)
        # muestro_message = muestro['message']
        # print("muestro mensaje: ",muestro_message)
        # get = muestro.get('status')
        # # muestro_status = muestro['status']
        # print(get)
        # #response.raise_for_status()
        return response.json()

    