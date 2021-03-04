from django.db import migrations, models


def insertAudioTypes(apps, schema_editor):
    AudioTypes = apps.get_model("arch_api", "AudioTypes")
    AudioTypes(id=1, audio_type='song').save()
    AudioTypes(id=2, audio_type='podcast').save()
    AudioTypes(id=3, audio_type='audiobook').save()

def deleteAudioTypes(apps, schema_editor):
    AudioTypes = apps.get_model("arch_api", "AudioTypes")
    AudioTypes.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('arch_api', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(insertAudioTypes,deleteAudioTypes),
    ]