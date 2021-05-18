# FakeImageDetector
A CNN based detector and segmenter trained using compression rate variations of pristine vs spliced images and blue channel of the ELAs vs Ground Truth masks respectively.

Datasets used : CASIA1 | CASIA1GroundTruth

## Installation
- Install Python 3.8
- Run `pip install --upgrade pip`
- Goto GUI folder
- Run `pip install -r requirements.txt`
- Start the program with `python FakeImageDetector.py`

For Django Web App
- Run `pip install -r requirements.txt`
- Start the server with `python manage.py runserver`
- Go to `localhost:8000` in your browser.
