import londonriots.models as models
import nltk
import itertools as it
from sqlalchemy.orm.exc import NoResultFound
import htmllib
from justext.core import justext
from pprint import pprint

def tag_article(article):
    for word_frequency in article.entity_frequencies:
        models.DBSession.delete(word_frequency)
    named_entities = extract_named_entities(article)

    for text, matches in it.groupby(sorted(named_entities)):
        try:
            named_entity =  models.DBSession.query(models.NamedEntity).filter(
                    (models.NamedEntity.text == text)).one()
        except NoResultFound:
            named_entity = models.NamedEntity(text)
        models.NamedEntityFrequency(article, named_entity, len(list(matches)))

    return article.entity_frequencies

def extract_named_entities(article):
    paragraphs = justext(article.source_text.encode("utf-8"), "English")

    pprint(paragraphs)
    text = u" ".join(p["text"] for p in paragraphs 
                     if p["class"] == "good" and not p.get("heading"))
    sentences =  nltk.sent_tokenize(text)
    print sentences
    tokenized_sentences = [nltk.word_tokenize(sent) for sent in sentences]
    tagged_sentences = [nltk.pos_tag(sent) for sent in tokenized_sentences]
    named_entity_chunks = [nltk.ne_chunk(sent, binary=True) for sent in tagged_sentences]
    for chunk in named_entity_chunks:
        for pos in chunk:
            if isinstance(pos, tuple): continue
            yield u" ".join((w for (w,p) in pos))
