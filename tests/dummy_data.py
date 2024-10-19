from typing import TypeVar

from faker import Faker
from pydantic import BaseModel

from learnle_site.application.model import Lemma, LemmaDraft

faker = Faker()


T = TypeVar('T', bound=BaseModel)


def merge(instance: T, **kwargs):
    return instance.__class__(**{**instance.model_dump()} | kwargs)


def dummy_string():
    return faker.text(10)


def dummy_lemma(
    uid: str | None = None,
    word: str | None = None,
    definition: str | None = None,
    example: str | None = None,
) -> Lemma:
    return Lemma(
        uid=uid or str(faker.uuid4()),
        word=word or faker.word(),
        definition=definition or faker.bs(),
        example=example or faker.bs(),
    )


def dummy_lemma_draft(
    uid: str | None = None,
    word: str | None = None,
    definition: str | None = None,
    example: str | None = None,
) -> LemmaDraft:
    return LemmaDraft(**dummy_lemma(uid, word, definition, example).model_dump())


def dummy_lemmas(size: int = 5) -> list[Lemma]:
    return [dummy_lemma() for _ in range(size)]
