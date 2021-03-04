from rest_framework import serializers
from .models import *
import json

class AudioSerializer(serializers.Serializer):
    title = serializers.CharField()
    creator = serializers.CharField()
    duration_s = serializers.IntegerField()
    narrator = serializers.CharField(required=False) 
    podcast_guests = serializers.CharField(required=False)
    file = serializers.FileField(write_only=True)

    def validate(self,data):
        return data


# Model Serializer common fields 
fields = ["id","audio_type","title","creator","duration_s","upload_time"]

class SongsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Songs
        fields = fields

class AudiobooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audiobooks
        fields = fields + ['narrator']

class PodcastsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Podcasts
        fields = fields

    