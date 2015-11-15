from glob import glob
import numpy as np
import pocketsphinx as ps
from pablo.mutate import vocal_eq
from sklearn import metrics
from sklearn.externals import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import train_test_split

hmm_dir = 'data/model/en-us/en-us'
lm = 'data/model/en-us/en-us.lm.dmp'
dic = 'data/model/en-us/cmudict-en-us.dict'

config = ps.Decoder.default_config()
config.set_string('-hmm', hmm_dir)
config.set_string('-lm', lm)
config.set_string('-dict', dic)
config.set_string('-logfn', '/dev/null')


def recognize_speech(wav_file):
    decoder = ps.Decoder(config)
    stream = open(wav_file, 'rb')
    decoder.start_utt()
    while True:
        buf = stream.read(1024)
        if buf:
            decoder.process_raw(buf, False, False)
        else:
            break
    decoder.end_utt()
    return [seg.word for seg in decoder.seg()]


def featurize(words):
    real_words = [w for w in words if w not in ['<s>', '</s>', '<sil>', '[NOISE]']]

    return np.array([
        # number of non-tag words/sils
        len([w for w in words if w not in ['<s>', '</s>']]),

        # if the last element is a closing tag
        int(words[-1] == '</s>' if words else False),

        # longest "real" word
        max(len(w) for w in real_words) if real_words else 0,

        # number of <sil>s
        sum(1 for _ in words if _ == '<sil>')
    ], dtype=float)


if __name__ == '__main__':
    tmp = '/tmp/pablo_recog_{0}.wav'
    i = 0

    feats = []
    labels = []
    model = LogisticRegression()

    print('===========\nNo vocals\n===========')
    for sound in glob('training/no_vocals/*.wav'):
        i += 1
        out = tmp.format(i)
        vocal_eq(sound, out)

        print(sound)
        words = recognize_speech(out)
        vec = featurize(words)
        print('\t{}'.format(words))
        print('\t{}'.format(vec))

        feats.append(vec)
        labels.append(0)

    print('===========\nVocals\n===========')
    for sound in glob('training/vocals/*.wav'):
        i += 1
        out = tmp.format(i)
        vocal_eq(sound, out)

        print(sound)
        words = recognize_speech(out)
        vec = featurize(words)
        print('\t{}'.format(words))
        print('\t{}'.format(vec))

        feats.append(vec)
        labels.append(1)

    # Split train/test set
    X_train, X_test, y_train, y_test = train_test_split(feats, labels, test_size=0.2)

    model.fit(X_train, y_train)

    predicted = model.predict(X_test)
    print(metrics.classification_report(y_test, predicted))

    # Persist the model
    joblib.dump(model, 'data/vocal_detect.pkl')