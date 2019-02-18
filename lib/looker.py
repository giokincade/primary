import certifi
import requests
import urllib3
from IPython.display import IFrame

from lib.settings import LOOKER_CLIENT_ID, LOOKER_SECRET


def looker_to_df(look_id: str) -> pd.DataFrame:
    return Looker(look_id).get_data()


class Looker(object):
    """
    Connect to Looker. Get a Look's data or display it's Visualization.
    """

    def __init__(self, look_id: str = None):
        self.host = 'https://primarykids.looker.com:19999/api/3.0/'
        self.session = requests.Session()
        self._auth()
        self.look_id = look_id
        self.look_metadata = self._get_metadata()
        self.embed_url = 'https://primarykids.looker.com/embed/looks/{}'.format(
            self.look_id
        )

    def _auth(self):
        url = '{}{}'.format(self.host, 'login')
        params = {'client_id': LOOKER_CLIENT_ID, 'client_secret': LOOKER_SECRET}
        r = self.session.post(url, params=params)
        access_token = r.json().get('access_token')
        self.session.headers.update({'Authorization': 'token {}'.format(access_token)})

    def _get_metadata(self):
        """
        adds metadata on the Look to self.
        """
        url = '{}{}/{}'.format(self.host, 'looks', self.look_id)
        r = self.session.get(url)
        if r.status_code == requests.codes.ok:
            return r.json()

    def get_data(self, format='json', limit=200000000):
        """
        Return a Look's data as a pandas dataframe.
        Limit defaults to 200M rows (unlimited) as a limit must be set else Looker's default 500-5k limit will be used.
        """
        url = '{}{}/{}/run/{}'.format(self.host, 'looks', self.look_id, format)
        params = {'limit': limit}
        r = self.session.get(url, params=params, stream=True)
        if r.status_code == requests.codes.ok:
            df = pd.DataFrame(r.json())
            df.columns = [col.split('.')[-1] for col in df.columns]
            return df

    def get_viz(self, width=900, height=350):
        """
        Display the Look's Visualization.
        Adjust width / height parameters as needed.
        """
        viz = IFrame(self.embed_url, width=width, height=height)
        return viz
