from dovpanda import base
from dovpanda.base import Ledger, Level

ledger = Ledger(level=Level.CORE)


@ledger.add_hook('DataFrame.__init__', level=Level.DEV)
def init_for_checks(*args, **kwargs):
    ledger.tell('you have construted a df')


@ledger.add_hook('DataFrame.__init__', level=Level.DEV)
def init_another(*args, **kwargs):
    ledger.tell('another pre hook for init')


@ledger.add_hook('DataFrame.iterrows')
def iterrows_is_bad(*args, **kwargs):
    ledger.tell("iterrows is not recommended, and in the majority of cases will have better alternatives")


@ledger.add_hook('DataFrame.groupby')
def time_grouping(*args, **kwargs):
    try:
        by = args[1]
    except IndexError:
        by = kwargs.get('by')
    base.listify(by)
    if 'hour' in by:
        ledger.tell('Seems like you are grouping by time, consider using resample')


@ledger.add_hook('concat', hook_type='post')
def duplicate_index_after_concat(res, *args, **kwargs):
    if res.index.nunique() != len(res.index):
        ledger.tell('After concatenation you have duplicated indexes values - pay attention')
    if res.columns.nunique() != len(res.columns):
        ledger.tell('After concatenation you have duplicated column names - pay attention')


@ledger.add_hook('concat')
def wrong_concat_axis(*args, **kwargs):
    objs = base.get_arg(args, kwargs, 0, 'objs')
    axis = base.get_arg(args, kwargs, 1, 'axis')
    rows = {df.shape[0] for df in objs}
    cols = {df.shape[1] for df in objs}
    col_names = set.union(*[set(df.columns) for df in objs])
    same_cols = (len(cols) == 1) and (len(col_names) == list(cols)[0])
    same_rows = (len(rows) == 1)
    axis_translation = {0: 'vertically', 1: 'horizontally'}
    if same_cols and not same_rows:
        if axis == 1:
            ledger.tell("All dataframes have the same columns, which hints for concat on axis 0."
                        "You specified <code>axis=1</code> which may result in an unwanted behaviour")
    elif same_rows and not same_cols:
        if axis == 0:
            ledger.tell("All dataframes have same number of rows, which hints for concat on axis 1."
                        "You specified <code>axis=0</code> which may result in an unwanted behaviour")

    elif same_rows and same_rows:
        ledger.tell("All dataframes have the same columns and same number of rows. "
                    f"Pay attention, your axis is {axis} which concatenates {axis_translation[axis]}")
