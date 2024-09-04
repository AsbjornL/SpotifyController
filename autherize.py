from urllib.parse import quote
import conf
import webbrowser



def auth_url(redirect_uri=conf.redirect_uri):
	base_url = "https://accounts.spotify.com/authorize"
	response_type = "code"
	client_id = conf.client_id
	scope = conf.scope
	
	url = f"{base_url}?"
	url += f"response_type={quote(response_type)}"
	url += f"&client_id={quote(client_id)}"
	url += f"&scope={quote(scope)}"
	url += f"&redirect_uri={quote(redirect_uri, safe='')}"
	
	return url


def autherize():
	webbrowser.open(auth_url(), new=2)


if __name__ == '__main__':
	autherize()

