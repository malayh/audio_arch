from django.test import TestCase
from rest_framework.test import APIClient
from aa_backend import settings
from .models import Songs
import os

resource_dir = settings.BASE_DIR.joinpath('test_resouces').resolve()


class TestCRUD(TestCase):
    def setUp(self):
        self.filepath = resource_dir.joinpath("sample.mp3").resolve()
        client = APIClient()
        self.data = {
            "title"     : "Test",
            "creator"   : "Malay",
            "duration_s": 100,
            "file"      : open(self.filepath,"rb")
        }
        resp = client.post('/archapi/songs/',self.data)
        assert resp.status_code == 200

    def test_get(self):
        client = APIClient()
        resp = client.get('/archapi/songs/')
        assert resp.status_code == 200        

        for i in resp.data[0]:
            if i in self.data :
             assert resp.data[0][i] == self.data[i]

    def test_download(self):
        client = APIClient()
        resp = client.get('/archapi/songs/1/')
        assert resp.status_code == 200
        assert int(resp._headers["content-length"][1]) == os.path.getsize(self.filepath)

    def test_update(self):
        client = APIClient()
        resp = client.patch('/archapi/songs/1/',{"title":"NewTitle"})
        assert resp.status_code == 200

        resp = client.get('/archapi/songs/')
        assert resp.data[0]["title"] == "NewTitle"

    def doCleanups(self):
        songs = Songs.objects.all()
        for i in songs:
            path = settings.FILE_STORE_DIR.joinpath(i.rel_path)
            assert os.path.isfile(path)
            os.remove(path)
        
        


        
