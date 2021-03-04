from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from typing import ClassVar
from datetime import datetime
from aa_backend import settings
import time
from django.http import FileResponse
import os

class AbstractWriter:
    def write(self,validated_data):
        raise NotImplementedError("Implement write method in child classes.")

    def write_file(self,file_obj,file_name):
        path = settings.FILE_STORE_DIR.joinpath(file_name).resolve()
        with open(path,"wb") as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

class SongWriter(AbstractWriter):
    def write(self, validated_data):
        file_format = validated_data["file"].content_type
        file_name = f"{int(time.time())}{validated_data['file'].name}"
        Songs(
            audio_type  ="song",
            title=validated_data['title'],
            creator=validated_data["creator"],
            duration_s=validated_data["duration_s"],
            upload_time=datetime.now(),
            rel_path=file_name,
            file_format=file_format
        ).save()


        self.write_file(validated_data["file"],file_name)

        return Response({"msg":"ok"})

class AudiobookWriter(AbstractWriter):
    def write(self, validated_data):
        if 'narrator' not in validated_data:
            return Response({"msg":"Field missing: narrator: str"},status=status.HTTP_400_BAD_REQUEST)

        file_format = validated_data["file"].content_type
        file_name = f"{int(time.time())}{validated_data['file'].name}"

        Audiobooks(
            audio_type  ="audioboook",
            title=validated_data['title'],
            creator=validated_data["creator"],
            duration_s=validated_data["duration_s"],
            upload_time=datetime.now(),
            rel_path=file_name,
            file_format=file_format,
            narrator=validated_data["narrator"]
        ).save()

        self.write_file(validated_data["file"],file_name)
        return Response({"msg":"ok"})

class PodcastWriter(AbstractWriter):
    def write(self,validated_data):
        if 'podcast_guests' not in validated_data:
            return Response({"msg":"Field missing: podcast_guests: List of coma separated str"},status=status.HTTP_400_BAD_REQUEST)

        file_format = validated_data["file"].content_type
        file_name = f"{int(time.time())}{validated_data['file'].name}"

        _p = Podcasts(
            audio_type="podcast",
            title=validated_data['title'],
            creator=validated_data["creator"],
            duration_s=validated_data["duration_s"],
            upload_time=datetime.now(),
            rel_path=file_name,
            file_format=file_format
        )
        _p.save()

        for i in validated_data["podcast_guests"].strip().split(","):
            _pg = PodcastGuests(podcast_fk=_p,guest_name=i)
            _pg.save()

        self.write_file(validated_data["file"],file_name)
        return Response({"msg":"ok"})
        
class WriterFactory:
    # Define which class will handle writing for which type of audio
    WRITER_MAP = {
        "songs"     : SongWriter,
        "audiobooks": AudiobookWriter,
        "podcasts"  : PodcastWriter 
    }

    @staticmethod
    def get_writer(audio_type:str) -> AbstractWriter:
        return WriterFactory.WRITER_MAP[audio_type]



class GenericReader:
    MODEL : ClassVar = None
    SERIALIZER : ClassVar = None

    def readall(self):
        _objs = self.MODEL.objects.all()
        return Response(self.SERIALIZER(_objs,many=True).data)

    def download(self,id:int):
        try:
            _obj = self.MODEL.objects.get(id=id)
        except self.MODEL.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        file_path = settings.FILE_STORE_DIR.joinpath(_obj.rel_path).resolve()
        audio_file = open(file_path,"rb")
        resp = FileResponse(audio_file, content_type=_obj.file_format)
        resp['Content-Length'] = os.path.getsize(file_path)
        resp['Content-Disposition'] = f'attachment; filename="{file_path.name}"'

        return resp

    def delete(self, id:int):
        try:
            _obj = self.MODEL.objects.get(id=id)
        except self.MODEL.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        _obj.delete()
        return Response({"msg":"ok"})

class SongReader(GenericReader):
    MODEL = Songs
    SERIALIZER = SongsSerializer

class AudiobookReader(GenericReader):
    MODEL = Audiobooks
    SERIALIZER = AudiobooksSerializer

class PodcastReader(GenericReader):
    MODEL = Podcasts
    SERIALIZER = PodcastsSerializer

    def readall(self):
        _ret = []
        _objs = self.MODEL.objects.all()
        for i in _objs:
            _d = self.SERIALIZER(i).data
            _pg = PodcastGuests.objects.filter(podcast_fk=i,).all()
            _d.update({"guests":[x.guest_name for x in _pg]})
            _ret.append(_d)

        return Response(_ret)

    def delete(self,id:int):
        try:
            _obj = self.MODEL.objects.get(id=id)
        except self.MODEL.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        _pg = PodcastGuests.objects.filter(podcast_fk=_obj).all()
        for i in _pg:
            i.delete()

        _obj.delete()
        return Response({"msg":"ok"})

class ReaderFactory:
    READER_MAP = {
        "songs"     : SongReader,
        "audiobooks": AudiobookReader,
        "podcasts"  : PodcastReader 
    }

    @staticmethod
    def get_reader(audio_type:str) -> GenericReader:
        return ReaderFactory.READER_MAP[audio_type]



class AudioList(APIView):
    def get(self,request,audio_type:str):
        _objs = Songs.objects.all()
        _reader = ReaderFactory.get_reader(audio_type)()
        return _reader.readall()

    def post(self,request,audio_type:str):

        _s = AudioSerializer(data=request.data)
        _s.is_valid(raise_exception=True)

        _writer = WriterFactory.get_writer(audio_type)() 
        return _writer.write(_s.validated_data)
        
class AudioDetail(APIView):
    def put(self,request,audio_type:str, id:int):
        return Response({"msg":"tesing"})

    def get(self,request,audio_type:str, id:int):
        _reader = ReaderFactory.get_reader(audio_type)()
        return _reader.download(id)

    def delete(self,request,audio_type:str, id:int):
        _reader = ReaderFactory.get_reader(audio_type)()
        return _reader.delete(id)
        

        

        
