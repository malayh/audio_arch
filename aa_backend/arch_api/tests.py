from django.test import TestCase
from rest_framework.test import APIClient
from aa_backend import settings
from .models import *
import os

resource_dir = settings.BASE_DIR.joinpath('test_resouces').resolve()


class TestCRUD(TestCase):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.filepath = resource_dir.joinpath("sample.mp3").resolve()

        self.apiEndpoint = '/archapi/songs/'
        self.data = {
            "title"     : "Test",
            "creator"   : "Malay",
            "duration_s": 100,
            "file"      : open(self.filepath,"rb")
        }

        self.model = Songs

    def setUp(self):
        client = APIClient()
        resp = client.post(self.apiEndpoint,self.data)
        assert resp.status_code == 200

    def test_get(self):
        client = APIClient()
        resp = client.get(self.apiEndpoint)
        assert resp.status_code == 200        

        for i in resp.data[0]:
            if i in self.data :
             assert resp.data[0][i] == self.data[i]

    def test_download(self):
        client = APIClient()
        resp = client.get(self.apiEndpoint+'1/')
        assert resp.status_code == 200
        assert int(resp._headers["content-length"][1]) == os.path.getsize(self.filepath)

    def test_update(self):
        client = APIClient()
        resp = client.patch(self.apiEndpoint+'1/',{"title":"NewTitle"})
        assert resp.status_code == 200

        resp = client.get(self.apiEndpoint)
        assert resp.data[0]["title"] == "NewTitle"

    def doCleanups(self):
        _objs = self.model.objects.all()
        for i in _objs:
            path = settings.FILE_STORE_DIR.joinpath(i.rel_path)
            assert os.path.isfile(path)
            os.remove(path)

class TestCRUD_Podcast(TestCRUD):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.filepath = resource_dir.joinpath("sample.mp3").resolve()

        self.apiEndpoint = '/archapi/podcasts/'
        self.data = {
            "title"     : "TestPodcast",
            "creator"   : "Malay",
            "duration_s": 100,
            "file"      : open(self.filepath,"rb"),
            "podcast_guests": "malay,andrew"
        }

        self.model = Podcasts

    def test_guest_list(self):
        client = APIClient()
        resp = client.get(self.apiEndpoint)

        assert resp.data[0]["guests"][0] == "malay"
        assert resp.data[0]["guests"][1] == "andrew"


        

