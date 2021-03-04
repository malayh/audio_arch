from django.db import models

class AudioTypes(models.Model):
    audio_type = models.TextField()


# Instead of creating different field for artist in song, host in podcast, author in audiobook, I am creating
# a field 'creator' for all this
#
# Audio files will be stored in settings.FILE_STORE_DIR. Paths to files will be stored reletive to 
# settings.FILE_STORE_DIR in 'rel_path'
class AbstractAudio(models.Model):
    audio_type_fk = models.ForeignKey(AudioTypes,on_delete=models.PROTECT)
    title = models.TextField(max_length=100)
    creator = models.TextField()
    duration_s = models.IntegerField()
    upload_time = models.DateTimeField()
    rel_path = models.TextField()
    file_format = models.TextField()

    class Meta:
        abstract = True

class Songs(AbstractAudio):
    pass

class Audiobooks(AbstractAudio):
    narrator = models.TextField()

class Podcasts(AbstractAudio):
    pass

class PodcastGuests(models.Model):
    podcast_fk = models.ForeignKey(Podcasts,on_delete=models.CASCADE)
    guest_name = models.TextField(max_length=100)