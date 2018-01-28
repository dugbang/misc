"""
출처; https://www.slideshare.net/lucypark/nltk-gensim
"""

import time
from konlpy.utils import pprint

from konlpy.tag import Twitter
import nltk

import pickle
import os


def read_data(filename):
    with open(filename, 'r', encoding='utf8') as f:
        data = [line.split('\t') for line in f.read().splitlines()]
        data = data[1:]
    return data


def tokenize(doc, pos_tagger):
    return ['/'.join(t) for t in pos_tagger.pos(doc, norm=True, stem=True)]


def load_tokenize(data, filename):
    # TODO; 맨뒤에 '0', '1' 등의 값이 붙는 것을 확인 > 버그로 확인되며 수정필요.
    # pos_tagger = Twitter()
    if os.path.exists(filename):
        docs = pickle.load(open(filename, 'rb'))
    else:
        docs = [(tokenize(row[1], Twitter()), row[2]) for row in data]
        # docs = [('/'.join(t), row[2]) for row in data for t in pos_tagger.pos(row[1], norm=True, stem=True)]
        pickle.dump(docs, open(filename, 'wb'))

    return docs


if __name__ == "__main__":
    s_t = time.time()

    base_data_path = 'd:/Documents/_date/'
    train_file = base_data_path + 'ratings_train.txt'
    test_file = base_data_path + 'ratings_test.txt'

    train_docs_dump = base_data_path + 'train_docs.dump'
    test_docs_dump = base_data_path + 'test_docs.dump'

    train_data = read_data(train_file)
    test_data = read_data(test_file)

    print(len(train_data))
    print(len(train_data[0]))

    print(len(test_data))
    print(len(test_data[0]))

    # tokenize; Elapsed 5.41 minute
    # pos_tagger = Twitter()
    train_docs = load_tokenize(train_data, train_docs_dump)
    test_docs = load_tokenize(test_data, test_docs_dump)
    pprint(train_docs[0])
    pprint(test_docs[0])

    tokens = [t for d in train_docs for t in d[0]]
    print('tokens length; ', len(tokens))

    text = nltk.Text(tokens, name='NMSC')
    print('nltk.Text; ', text)
    print('text.tokens length; ', len(text.tokens))
    print('text.tokens set length; ', len(set(text.tokens)))
    pprint(text.vocab().most_common(10))

    # from matplotlib import font_manager, rc
    # font_fname = 'c:/windows/fonts/malgun.ttf'
    # font_name = font_manager.FontProperties(fname=font_fname).get_name()
    # rc('font', family=font_name)
    # text.plot(50)

    # print('text.collocations')
    # text.collocations()  # 인접하여 빈번하게 등장하는 단어

    # selected_words = [f[0] for f in text.vocab().most_common(2000)]
    # print('selected_words')
    # pprint(selected_words)


    # =============================================================

    # def term_exists(doc):
    #     return {'exists({})'.format(word): (word in set(doc)) for word in selected_words}
    #
    # train_docs = train_docs[:10000]  # 시간단축을 위해...
    #
    # train_xy = [(term_exists(d), c) for d, c in train_docs]
    # test_xy = [(term_exists(d), c) for d, c in test_docs]
    #
    # # pprint(train_xy[0:2])
    # # pprint(train_docs)
    #
    # classifier = nltk.NaiveBayesClassifier.train(train_xy)
    # print(nltk.classify.accuracy(classifier, test_xy))
    # classifier.show_most_informative_features(10)

    # =============================================================
    from collections import namedtuple

    TaggedDocument = namedtuple('TaggedDocument', 'words tags')

    tagged_train_docs = [TaggedDocument(d, [c]) for d, c in train_docs]
    tagged_test_docs = [TaggedDocument(d, [c]) for d, c in test_docs]

    from gensim.models import doc2vec

    doc_vectorizer = doc2vec.Doc2Vec(size=300, alpha=0.025, min_alpha=0.025, seed=1234)
    doc_vectorizer.build_vocab(tagged_train_docs)

    for epoch in range(10):
        doc_vectorizer.train(tagged_train_docs)
        doc_vectorizer.alpha -= 0.002
        doc_vectorizer.min_alpha = doc_vectorizer.alpha

    doc_vectorizer.save('doc2vec.model')

    # =============================================================

    tm = time.localtime()
    process_time = (time.time() - s_t)
    if process_time < 100:
        print(__file__, 'Python Elapsed %.02f seconds, current time; %02d:%02d' %
              (process_time, tm.tm_hour, tm.tm_min))
    elif process_time < 6000:
        print(__file__, 'Python Elapsed %.02f minute, current time; %02d:%02d' %
              (process_time / 60, tm.tm_hour, tm.tm_min))
    else:
        print(__file__, 'Python Elapsed %.02f hours, current time; %02d:%02d' %
              (process_time / 3600, tm.tm_hour, tm.tm_min))
