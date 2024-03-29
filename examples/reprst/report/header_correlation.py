"""Get correlation

    Run in the terminal:
        python3.7 header_correlation.py
"""
import os
import pickle
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

######################################################################################################################
### add current path to system path
lib_path = os.path.abspath('.')
sys.path.append(lib_path)
# print(f"add \'{lib_path}\' into sys.path: {sys.path}")

######################################################################################################################
### set seaborn background colors
# sns.set_style("darkgrid")
sns.set_style("whitegrid")
sns.despine(bottom=True, left=True, top=False, right=False)


def load_data(file_in='data.dat'):
    """

    Parameters
    ----------
    file_in

    Returns
    -------

    """
    with open(file_in, 'rb') as f:
        data = pickle.load(f)
        return data


def dump_data(data, file_out='data.dat'):
    """

    Parameters
    ----------
    data
    file_out

    Returns
    -------

    """
    with open(file_out, 'wb') as f:
        pickle.dump(data, f)


def plot_correlation_multi(corr_results, out_dir, title=None, show=True):
    """ plot the data

    Parameters
    ----------
    corr_results
    out_dir
    title
    show

    Returns
    -------

    """
    # # only show the top 4 figures
    datasets = [
        ('UNB/CICIDS_2017/pc_192.168.10.5', 'UNB(PC1)'),  # data_name is unique
        # ('DS10_UNB_IDS/DS14-srcIP_192.168.10.14', 'UNB(PC4)'),
        ('CTU/IOT_2017/pc_10.0.2.15', 'CTU'),
        ('MAWI/WIDE_2019/pc_202.171.168.50', 'MAWI'),
        ('UCHI/IOT_2019/sfrig_192.168.143.43', 'SFrig'),
    ]
    new_corr_results = {}
    for i, (dataset, name) in enumerate(datasets):
        for j, (key, corrs) in enumerate(corr_results.items()):
            _key_path, _dataset, _feat_set, X_test_shape = key
            if dataset in key:
                new_corr_results[(_key_path, _dataset, name, _feat_set, X_test_shape)] = corrs
    t = 0
    cols = 2
    fontsize = 20
    ## http://jose-coto.com/styling-with-seaborn
    # colors = ["m", "#4374B3"]
    # palette = sns.color_palette('RdPu', 1)  # a list
    palette = [sns.color_palette('YlOrRd', 7)[4]]  # YlOrRd
    fig, axes = plt.subplots(2, cols, figsize=(18, 8))  # (width, height)
    # print(new_corr_results)
    for i, (key, corrs) in enumerate(new_corr_results.items()):
        print(f"i: {i}, {key}, corrs: {corrs}")  # hue = feat_set
        key_path, dataset, short_name, feat_set, X_test_shape = key
        HEADER = ['FIN', 'SYN', 'RST', 'PSH', 'ACK', 'URG', 'ECE', 'CWR', '1st-TTL']

        data = sorted(range(len(corrs)), key=lambda i: abs(corrs[i]), reverse=True)[:6]  # top 6 values
        data = [[f'({HEADER[_i]}, y)', feat_set, corrs[_i]] for _i in data]
        # print(f"i: {i}, {key}, corrs: {data}")

        new_yerrs = [1 / (np.sqrt(X_test_shape[0]))] * 6  # for err_bar
        # print(f'i: {i}, {new_yerrs}')
        df = pd.DataFrame(data, columns=[f'Xi_y', 'feat_set', 'corr_rho'])
        if i % cols == 0 and i > 0:
            t += 1
        g = sns.barplot(x=f"Xi_y", y="corr_rho", ax=axes[t, i % cols], hue='feat_set', data=df,
                        palette=palette)  # palette=palette,
        g.set(xlabel=None)
        g.set(ylim=(-1, 1))
        if i % cols == 0:
            # g.set_ylabel(r'$\rho$', fontsize=fontsize + 4)
            g.set_ylabel(r'Correlation', fontsize=fontsize + 4)
            # print(g.get_yticks())
            g.set_yticks([-1, -0.5, 0, 0.5, 1])
            g.set_yticklabels(g.get_yticks(), fontsize=fontsize + 6)  # set the number of each value in y axis
            # print(g.get_yticks())
        else:
            g.set(ylabel=None)
            g.set_yticklabels(['' for v_tmp in g.get_yticks()])
            g.set_ylabel('')

        # g.set_title(dataset_name)
        g.get_legend().set_visible(False)
        g.set_xticklabels(g.get_xticklabels(), fontsize=fontsize + 4, rotation=30, ha="center")

        ys = []
        xs = []
        width = 0
        for i_p, p in enumerate(g.patches):
            height = p.get_height()
            width = p.get_width()
            ys.append(height)
            xs.append(p.get_x())
            if i_p == 0:
                pre = p.get_x() + p.get_width()
            if i_p > 0:
                cur = p.get_x()
                g.axvline(color='black', linestyle='--', x=pre + (cur - pre) / 2, ymin=0, ymax=1, alpha=0.3)
                pre = cur + p.get_width()
            ## https://stackoverflow.com/questions/34888058/changing-width-of-bars-in-bar-chart-created-using-seaborn-factorplot
            p.set_width(width / 3)  # set the bar width
            # we recenter the bar
            p.set_x(p.get_x() + width / 3)
        g.set_title(short_name, fontsize=fontsize + 8)

        # add error bars
        g.errorbar(x=xs + width / 2, y=ys,
                   yerr=new_yerrs, fmt='none', c='b', capsize=3)

    # # get the legend and modify it
    # handles, labels = g.get_legend_handles_labels()
    # fig.legend(handles, ['IAT+SIZE'], title=None, loc='lower center', ncol=1,
    #  prop={'size': fontsize-2})  # loc='lower right',  loc = (0.74, 0.13)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)

    out_file = os.path.join(out_dir, feat_set, "header:True", 'correlation-bar.pdf')
    if not os.path.exists(os.path.dirname(out_file)): os.makedirs(os.path.dirname(out_file))
    print(out_file)
    plt.savefig(out_file)  # should use before plt.show()
    if show: plt.show()
    plt.close(fig)
    plt.close("all")


def main():
    in_file = 'correlation_results/correlation_all.dat'
    out_dir = 'correlation_results/'
    corr_results = load_data(in_file)
    plot_correlation_multi(corr_results, out_dir, show=True)


if __name__ == '__main__':
    main()
