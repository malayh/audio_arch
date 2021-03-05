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


allowed_types = ("song", "audiobook", "podcast")
allowed_uris = set([i+"s" for i in allowed_types])


class AbstractWriter:
    model : ClassVar = None
    
    #audio type must be one of "song", "audiobook", "podcast"
    audio_type : str = None

    # extra field that are required for a model which are not the standard ones. 
    # Standard required field will be validated by AudioSerializer
    extra_fields : list = []


    def write(self,validated_data):
        """
        Assuming validated_data is validated by AudioSerializer
        """
        if(not self.model):
            raise ValueError("Must define model.")

        if(self.audio_type not in allowed_types):
            raise ValueError("Must define audio_type.")


        for i in self.extra_fields:
            if i not in validated_data:
                return Response({"msg":f"Field missing: {i}"},status=status.HTTP_400_BAD_REQUEST)


        file_format = validated_data["file"].content_type
        file_name = f"{int(time.time())}{validated_data['file'].name}"


        # this dict will be written as a model object
        _data = {
            "rel_path"      :file_name,
            "file_format"   :file_format,
            "audio_type"    :self.audio_type,
            "upload_time"   :datetime.now()
        }

        for i in self.model._meta.fields:
            if i.name in validated_data:
                _data[i.name] = validated_data[i.name]

        _obj = self.model(**_data)
        _obj.save()

        self.write_file(validated_data["file"],file_name)


        return Response({"msg":"ok"})

    def write_file(self,file_obj,file_name):
        path = settings.FILE_STORE_DIR.joinpath(file_name).resolve()
        with open(path,"wb") as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

    def update(self,id,validated_data):
        """
        Fully or partially updates an entity.
        """
        if(not self.model):
            raise ValueError("Must define model.")

        if(self.audio_type not in allowed_types):
            raise ValueError("Must define audio_type.")


        try:
            _obj = self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # this will be passed to _obj.save method
        _data = {}

        for i in self.model._meta.fields:
            if i.name in validated_data:
                _data[i.name] = validated_data[i.name]

        if "file" in validated_data:
            file_format = validated_data["file"].content_type
            file_name = f"{int(time.time())}{validated_data['file'].name}"

            _data.update(
                {
                "rel_path"      :file_name,
                "file_format"   :file_format,
                "upload_time"   :datetime.now()
                }
            )

            path = settings.FILE_STORE_DIR.joinpath(_obj.rel_path).resolve()
            try:
                os.remove(path)
            except:
                pass

            self.write_file(validated_data["file"],file_name)

        for attr, val in _data.items():
            setattr(_obj,attr,val)

        _obj.save()
        return Response({"msg":"ok"})

class SongWriter(AbstractWriter):
    model = Songs
    audio_type = "song"

class AudiobookWriter(AbstractWriter):
    model = Audiobooks
    audio_type = "audiobook"
    extra_fields = ["narrator"]
    
class PodcastWriter(AbstractWriter):
    model = Podcasts
    audio_type = "podcast"

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

    def update(self,id,validated_data):
        if "podcast_guests" in validated_data:
            try:
                _obj = self.model.objects.get(id=id)
            except self.model.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

            _pg = PodcastGuests.objects.filter(podcast_fk=_obj).all()
            for i in _pg:
                i.delete()

            for i in validated_data["podcast_guests"].strip().split(","):
                PodcastGuests(podcast_fk=_obj,guest_name=i).save()

            
        return super().update(id,validated_data)

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

        path = settings.FILE_STORE_DIR.joinpath(_obj.rel_path).resolve()
        try:
            os.remove(path)
        except:
            pass

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
        if(audio_type not in allowed_uris):
            return Response(status=status.HTTP_404_NOT_FOUND)

        _reader = ReaderFactory.get_reader(audio_type)()
        return _reader.readall()

    def post(self,request,audio_type:str):
        if(audio_type not in allowed_uris):
            return Response(status=status.HTTP_404_NOT_FOUND)

        _s = AudioSerializer(data=request.data)
        _s.is_valid(raise_exception=True)

        _writer = WriterFactory.get_writer(audio_type)() 
        return _writer.write(_s.validated_data)
        
class AudioDetail(APIView):
    def patch(self,request,audio_type:str, id:int):
        _s = AudioSerializer(data=request.data,partial=True)
        _s.is_valid(raise_exception=True)
        _writer = WriterFactory.get_writer(audio_type)()

        return _writer.update(id,_s.validated_data)

    def get(self,request,audio_type:str, id:int):
        if(audio_type not in allowed_uris):
            return Response(status=status.HTTP_404_NOT_FOUND)

        _reader = ReaderFactory.get_reader(audio_type)()
        return _reader.download(id)

    def delete(self,request,audio_type:str, id:int):
        if(audio_type not in allowed_uris):
            return Response(status=status.HTTP_404_NOT_FOUND)

        _reader = ReaderFactory.get_reader(audio_type)()
        return _reader.delete(id)
        

        

        
