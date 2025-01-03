import requests


def main():
    proxies = {
        'http': 'http://proxy.example.com:8080',
        'https': 'http://secureproxy.example.com:8090',
    }
    url = 'http://mywebsite.com/example'

    response = requests.post(url, proxies=proxies)
