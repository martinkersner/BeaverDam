BeaverDam
=========

Video annotation tool for deep learning training labels


## Installation

 1. Clone this repository.
 2. `cd BeaverDam`
 3. Make sure Python 3 is installed.  
    If not: `brew install python3` (Mac) or `sudo apt-get install python3` (Ubuntu)
 3. Make sure virtualenv is installed.  
    If not: `pip3 install virtualenv` or maybe `sudo pip3 install virtualenv`
 4. Make the Python virtualenv for this project:  
    `scripts/setup`
 5. Download sample data:  
    `scripts/seed -f`
 6. Clear database
     `./clear_database`

When running any `./manage.py` commands, use `source venv/bin/activate` to enter venv first.

## Add new user
Run command:
`./add_user name password`

## Add video
Move video file (\*.mp4) to *annotator/static/videos* directory and run command:
`./add_video path/to/video/file`

## Running the server

```shell
scripts/serve
```

Then navigate to [localhost:5000](http://localhost:5000/) in your browser.

Need to run on a custom port? `env PORT=1234 scripts/serve`

### Making accounts

To make a superuser account for testing, or for production, run inside venv `./manage.py createsuperuser`
If you are using sample data, login with username `test` and password `password`
