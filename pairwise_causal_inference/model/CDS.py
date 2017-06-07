"""
Conditional Distribution Similarity Statistic
Used to infer causal directions
Author : José A.R. Fonollosa
Ref : Fonollosa, José AR, "Conditional distribution variability measures for causality detection", 2016.
"""

import numpy as np
from collections import Counter

BINARY = "Binary"
CATEGORICAL = "Categorical"
NUMERICAL = "Numerical"


def count_unique(x):
    try:
        return len(set(x))
    except TypeError as e:
        print(x)
        raise e


def numerical(tp):
    assert type(tp) is str
    return tp == NUMERICAL


def len_discretized_values(x, tx, ffactor, maxdev):
    return len(discretized_values(x, tx, ffactor, maxdev))


def discretized_values(x, tx, ffactor, maxdev):
    if numerical(tx) and count_unique(x) > (2 * ffactor * maxdev + 1):
        vmax = ffactor * maxdev
        vmin = -ffactor * maxdev
        return range(vmin, vmax + 1)
    else:
        return sorted(list(set(x)))


def discretized_sequence(x, tx, ffactor, maxdev, norm=True):
    if not norm or (numerical(tx) and count_unique(x) > len_discretized_values(x, tx, ffactor, maxdev)):
        if norm:
            x = (x - np.mean(x)) / np.std(x)
            xf = x[abs(x) < maxdev]
            x = (x - np.mean(xf)) / np.std(xf)
        x = np.round(x * ffactor)
        vmax = ffactor * maxdev
        vmin = -ffactor * maxdev
        x[x > vmax] = vmax
        x[x < vmin] = vmin
    return x


def discretized_sequences(x, y, ffactor=3, maxdev=3):
    return discretized_sequence(x, "Numerical", ffactor, maxdev), discretized_sequence(y, "Numerical", ffactor,
                                                                                       maxdev)


class CDS(object):
    """
    Conditional Distribution Similarity Statistic

    Measuring the std. of the rescaled values of y (resp. x) after binning in the x (resp. y) direction.
    The lower the std. the more likely the pair to be x->y (resp. y->x).
    Ref : Fonollosa, José AR, "Conditional distribution variability measures for causality detection", 2016.
    """
    def __init__(self):
        super(CDS, self).__init__()

    def predict_proba(self, df, ffactor=2, maxdev=3, minc=12):
        """ Predict probabilities of x->y :1 or y<-x :-1

        :param x_te: CEPC-format DataFrame containing pairs of variables
        :param ffactor:
        :param maxdev:
        :param minc:
        :return:
        """

    def predict_pair(self, x_te, y_te, ffactor=2, maxdev=3, minc=12):
        """ Infer causal relationships between 2 variables x_te and y_te

        If   returns = 1  : x_te -> y_te
        elif returns = -1 : x_te <- y_te

        :param x_te: Input variable 1
        :param y_te: Input variable 2
        :param ffactor:
        :param maxdev:
        :param minc:
        :return:
        """

        xd, yd = discretized_sequences(x_te,  y_te,  ffactor, maxdev)
        cx = Counter(xd)
        cy = Counter(yd)
        yrange = sorted(cy.keys())
        ny = len(yrange)
        py = np.array([cy[i] for i in yrange], dtype=float)
        py = py / py.sum()
        pyx = []
        for a in cx.iterkeys():
            if cx[a] > minc:
                yx = y_te[xd == a]
                # if not numerical(ty):
                #     cyx = Counter(yx)
                #     pyxa = np.array([cyx[i] for i in yrange], dtype=float)
                #     pyxa.sort()
                if count_unique(y_te) > len_discretized_values(y_te, "Numerical", ffactor, maxdev):

                    yx = (yx - np.mean(yx)) / np.std(y_te)
                    yx = discretized_sequence(yx, "Numerical", ffactor, maxdev, norm=False)
                    cyx = Counter(yx.astype(int))
                    pyxa = np.array([cyx[i] for i in discretized_values(y_te, "Numerical", ffactor, maxdev)],
                                    dtype=float)

                else:
                    print("OK22")
                    cyx = Counter(yx)
                    pyxa = [cyx[i] for i in yrange]
                    pyxax = np.array([0] * (ny - 1) + pyxa + [0] * (ny - 1), dtype=float)
                    xcorr = [sum(py * pyxax[i:i + ny]) for i in range(2 * ny - 1)]
                    imax = xcorr.index(max(xcorr))
                    pyxa = np.array([0] * (2 * ny - 2 - imax) + pyxa + [0] * imax, dtype=float)
                assert pyxa.sum() == cx[a]
                pyxa = pyxa / pyxa.sum()

                pyx.append(pyxa)

        if len(pyx) == 0:
            return 0

        pyx = np.array(pyx)
        pyx = pyx - pyx.mean(axis=0)
        return np.std(pyx)