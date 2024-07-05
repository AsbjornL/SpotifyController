from requests.utils import quote
import conf
import webbrowser


def autherize():
    url = "https://accounts.spotify.com/authorize"
    url += "?response_type=code"
    url += f"&client_id={quote(conf.client_id)}"
    url += f"&scope={quote(conf.scope)}"
    url += f"&redirect_uri={quote(conf.url + '/login')}"
    webbrowser.open(url, new=2)


if __name__ == '__main__':
    autherize()

