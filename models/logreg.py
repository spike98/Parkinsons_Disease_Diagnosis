import numpy as np
import matplotlib.pyplot as plt
import itertools
import csv
import random

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import learning_curve
from sklearn.model_selection import GroupKFold
from sklearn.model_selection import KFold
import sklearn.metrics as metrics

def nav_to_index(index):
    with open('../sheets/features.csv', newline='\n') as features:
        return next(csv.reader(itertools.islice(features, index, index+1)))

def initialize_data(filename):
    X = []
    y = []
    groups = []

    with open(filename, newline='\n') as trials:
        reader = csv.reader(trials)

        #skip header
        next(reader)

        for r, curr_trial in enumerate(reader):
            X.append([float(i) for i in curr_trial[4:]])
            y.append(int(curr_trial[3]))
            groups.append(curr_trial[0])

            #if (r == 12000): break
    return np.array(X), np.array(y), np.array(groups)

# X2 = X.reshape(-1, X.shape[-1])

def plot_learning_curve(
    model,
    title,
    X,
    y,
    groups,
    cv,
    axes,
    train_sizes
):
    axes[0].set_title(title)
    axes[0].set_xlabel("Training examples")
    axes[0].set_ylabel("Score")

    train_sizes, train_scores, test_scores, fit_times, score_times = learning_curve(model, X, y, cv=cv, groups=groups, n_jobs=-1, train_sizes=train_sizes, return_times=True)

    print(len(fit_times))
    print(train_scores)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    fit_times_mean = np.mean(fit_times, axis=1)
    fit_times_std = np.std(fit_times, axis=1)

    axes[0].grid()
    axes[0].fill_between(
        train_sizes,
        train_scores_mean - train_scores_std,
        train_scores_mean + train_scores_std,
        alpha=0.1,
        color="r",
    )
    axes[0].fill_between(
        train_sizes,
        test_scores_mean - test_scores_std,
        test_scores_mean + test_scores_std,
        alpha=0.1,
        color="g",
    )
    axes[0].plot(
        train_sizes, train_scores_mean, "o-", color="r", label="Training score"
    )
    axes[0].plot(
        train_sizes, test_scores_mean, "o-", color="g", label="Cross-validation score"
    )
    axes[0].legend(loc="best")

    fold = 0
    for train, test in KFold().split(X, y):
        fold += 1
        model.fit(X[train], y[train])
        probas_1 = clf.predict_proba(X[test])[:,1]
        fpr, tpr, threshold = metrics.roc_curve(y[test], probas_1)
        auc = metrics.auc(fpr, tpr)
        axes[1].plot(fpr, tpr, lw=2, label = 'ROC fold %d (AUC = %0.2f)' % (fold, auc))


    # Plot ROC
    axes[1].grid()
    axes[1].plot([0,1],[0,1], linestyle = '--', lw=2, color = 'black', label = 'Random Guess')
    axes[1].set_xlabel('False Positive Rate')
    axes[1].set_ylabel('True Positive Rate')
    axes[1].set_title('ROC')
    axes[1].legend(loc="lower right")

        # Plot fit_time vs score
    fit_time_argsort = fit_times_mean.argsort()
    fit_time_sorted = fit_times_mean[fit_time_argsort]
    test_scores_mean_sorted = test_scores_mean[fit_time_argsort]
    test_scores_std_sorted = test_scores_std[fit_time_argsort]
    axes[2].grid()
    axes[2].plot(fit_time_sorted, test_scores_mean_sorted, "o-")
    axes[2].fill_between(
        fit_time_sorted,
        test_scores_mean_sorted - test_scores_std_sorted,
        test_scores_mean_sorted + test_scores_std_sorted,
        alpha=0.1,
    )
    axes[2].set_xlabel("fit_times")
    axes[2].set_ylabel("Score")
    axes[2].set_title("Performance of the model")

    return plt


figure, axes = plt.subplots(3, 2, figsize=(10, 15))
# auto margin between elements
X, y, groups = initialize_data("../sheets/features.csv")

cv = KFold()
train_sizes = np.linspace(0.1, 1.0, 5)
clf = LogisticRegression(random_state = 0, max_iter = 1000, multi_class = 'ovr', n_jobs = -1)

plot_learning_curve(clf, "Raw audio", X, y, groups=groups, cv=cv, axes=axes[:, 0], train_sizes=train_sizes)

X1, y1, groups1 = initialize_data("../sheets/spectral_dataset.csv")

plot_learning_curve(clf, "With background noise reduction", X1, y1, groups=groups1, cv=cv, axes=axes[:, 1], train_sizes=train_sizes)

figure.tight_layout()
plt.savefig('present.png')
plt.show()
