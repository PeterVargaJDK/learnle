from fastapi import FastAPI

from learnle_site.domain.crosswords import UnpackedCrossWordsGrid
from learnle_site.domain.crosswords.domain_model import CrosswordsPuzzle
from learnle_site.utils import Dimensions

app = FastAPI()


@app.get('/ping')
def ping():
    return 'OK'


@app.get('/daily-crosswords')
def get_daily_crosswords() -> CrosswordsPuzzle:
    pass
