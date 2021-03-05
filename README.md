# Audio Arch
RESTful Microservice of Audio Archival

## API
The API is as follows:

- `audio_type` is a category of a given audio file, which can be one of `songs` , `podcasts` or `audiobooks`
- Each entry must the following meta data
    - `title` : Title of the audio
    - `creator`: Author of the book or artist of the song or host of the podcast
    - `duration_s`: Duration of the audio in seconds
- For `podcasts` the additional required fields are
    - `podcast_guests` : Coma separated list of guests on the podcast

- For `audiobooks` the additional required fields are
    - `narrator` : Narator of the audiobook


#### GET : `archapi/<audio_type>/`
- Returns a list of meta data of all the audio files for given `audio_type`
- For `audiobooks` it meta data will also have a field `guests` which is a list of names of podcast guests


#### POST : `archapi/<audio_type>/`
- Creates a new entry
- Apart of required fields for given `audio_type`, it required `file` field which is the file to be uploaded

#### GET : `archapi/<audio_type>/<audio_id>/`
- Return audion file bearing the id `audio_id`

#### PATCH: `archapi/<audio_type>/<audio_id>/`
- Updated a entry. Any of the expeceted fields can be passed and it will be updated accordingly.
- If `file` is passed, the old file will be replaced by the new file


## Setup
Following is how to setup a developer environment for the project
- Install Python > 3.8
- `python3.8 -m pip install virtualenv`
- Go to project dir and create virtual env with `python3.8 -m pip virtualenv venv` and activate with `source venv/bin/activate`
- Install requirements: `pip install -r requirements.txt`
- Create DB and migrate: `cd aa_backend && python manage.py migrate`
- Create superuser (optional) : `python manage.py migrate createsuperuser`
- Start dev server `python manage.py runserver`

## Run tests
- Go to project dir and run `source venv/bin/activate`
- `cd aa_backend && python manage.py test`

## Design
The API is designed to conform to REST. Following are details of how it works

#### Models
- There is an abstract Django model which holds all the common required fields. All other concrete models inherits from this model to define additional fields.
- The files are stored in a direcotory configured in `settings.FILE_STORE_DIR`
- In the models the path are stored reletive to `settings.FILE_STORE_DIR` in field `rel_path`
- While writing, `upload_time` and `audio_type` is also added to the models, where `update_time` is the time of upload.

#### Validation
- There are two level of validation done while updating or creating an entity.
- First one is done by `AudionSerializer` to see if all the common required fields are present and are of correct data type
- The second level is done by the writer to check if additional fields required by a given model is provided or not

#### Reading and writing
- The common reading and writing functionalities are abstracted into `AbstractWriter` and `GenericReader` which are then inherited by all the concrete readers and writer of models.
- Interface of `AbstractWriter` is as follows
    - Fields required to be defined by childen
        - model : The model class of a given audio type
        - audio_type : one of `song`,`podcast` or `audiobook`
        - extra_fields = list of extra field required by a given audio type

    - Methods
        - write : takes `validated_data` from `AudionSerializer` and creates new entry
        - update : takes `id` of an audio_type and `validated_data` from `AudionSerializer` and update and entry

- Interface of `GenricReader` is as follows
    - Fields required to be defined by childen
        - MODEL: model of the given audio type
        - SERIALIZER : serilizer for the given audio type
    - Methods
        - readall : Returns a list of all the entires for a given audio type
        - download : takes `id` of a given audio type and returns the file
        - delete : takes `id` and deleted an entry

-  The `ReaderFactory.get_reader` is a factory method which returns appropiate reader to handle reading functionality for given `audio_type`
- The `WriterFactory.get_writer` is a factory method which returns appropiate writer to handle writing functionality for given `audio_type`