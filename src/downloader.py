# src/downloader.py
import requests
import json
from urllib.parse import urljoin

class DownloaderClient:
    def __init__(self, downloader_type, url, token=None):
        self.type = downloader_type
        self.url = url
        self.token = token
        
        if downloader_type == 'aria2':
            self.client = Aria2Client(url, token)
        elif downloader_type == 'qbittorrent':
            self.client = QBittorrentClient(url, token)
        elif downloader_type == 'transmission':
            self.client = TransmissionClient(url, token)
        else:
            raise ValueError(f'不支持的下载器类型: {downloader_type}')
    
    def add_download(self, magnet, title=None):
        return self.client.add_download(magnet, title)

class Aria2Client:
    def __init__(self, url, token=None):
        self.url = url
        self.token = token
    
    def add_download(self, magnet, title=None):
        payload = {
            'jsonrpc': '2.0',
            'id': 'suppermedia',
            'method': 'aria2.addUri',
            'params': [
                f'token:{self.token}' if self.token else '',
                [magnet],
                {'out': title} if title else {}
            ]
        }
        
        response = requests.post(self.url, json=payload)
        if response.status_code == 200:
            return response.json().get('result')
        else:
            raise Exception(f'Aria2添加下载失败: {response.status_code}')

class QBittorrentClient:
    def __init__(self, url, username=None, password=None):
        self.url = url.rstrip('/')
        self.username = username or 'admin'
        self.password = password or 'adminadmin'
        self.cookies = None
        self._login()
    
    def _login(self):
        login_url = urljoin(self.url, '/api/v2/auth/login')
        response = requests.post(login_url, data={
            'username': self.username,
            'password': self.password
        })
        if response.status_code == 200:
            self.cookies = response.cookies
    
    def add_download(self, magnet, title=None):
        if not self.cookies:
            self._login()
        
        add_url = urljoin(self.url, '/api/v2/torrents/add')
        data = {
            'urls': magnet,
            'savepath': title if title else '',
            'category': 'suppermedia'
        }
        
        response = requests.post(add_url, data=data, cookies=self.cookies)
        if response.status_code == 200:
            return 'success'
        else:
            raise Exception(f'qBittorrent添加下载失败: {response.status_code}')

class TransmissionClient:
    def __init__(self, url, username=None, password=None):
        self.url = url
        self.session_id = None
        self.auth = None
        if username and password:
            self.auth = (username, password)
        self._get_session_id()
    
    def _get_session_id(self):
        response = requests.get(self.url, auth=self.auth)
        self.session_id = response.headers.get('X-Transmission-Session-Id')
    
    def add_download(self, magnet, title=None):
        payload = {
            'method': 'torrent-add',
            'arguments': {
                'filename': magnet,
                'download-dir': title if title else None
            }
        }
        
        headers = {
            'X-Transmission-Session-Id': self.session_id
        }
        
        response = requests.post(
            self.url, 
            json=payload, 
            headers=headers,
            auth=self.auth
        )
        
        if response.status_code == 409:  # Session ID过期
            self._get_session_id()
            headers['X-Transmission-Session-Id'] = self.session_id
            response = requests.post(self.url, json=payload, headers=headers, auth=self.auth)
        
        if response.status_code == 200:
            return response.json().get('arguments', {}).get('torrent-added', {}).get('id')
        else:
            raise Exception(f'Transmission添加下载失败: {response.status_code}')
