# Pandas

Pandas is the standard tool for **tabular data** in Python: sensor logs, experiment results, flight records, financial series, anything with rows and named columns. It adds labelled axes, heterogeneous column types, missing-data handling, group-by aggregation, joins and time-series tools on top of NumPy. This lesson targets **pandas 3**. Copy-on-write is the default, and strings get a dedicated dtype, so code written for old versions sometimes behaves differently. We cover Series and DataFrames, selection, cleaning, group-by, merges, reshaping and time series, plus the idioms that keep pandas code fast and unambiguous.

## 1. Series and DataFrame

```python
import pandas as pd
import numpy as np

s = pd.Series([0.5, 0.7, 0.2], index=["lidar", "camera", "imu"], name="latency_s")
s["camera"]            # 0.7: label-based lookup
s.mean(), s.idxmax()   # 0.4666…, 'camera'

df = pd.DataFrame({
    "robot":  ["r1", "r2", "r1", "r3", "r2"],
    "task":   ["pick", "move", "move", "pick", "pick"],
    "secs":   [12.5, 30.1, 25.0, 11.2, np.nan],
    "ok":     [True, True, False, True, True],
})
df.shape, df.dtypes, df.head(3), df.describe()
```

A DataFrame is a dict-like collection of **columns** (each a Series) sharing a row **index**. Columns can have different dtypes. Within a column, operations are vectorised NumPy.

## 2. Reading and writing data

```python
df = pd.read_csv("runs.csv", parse_dates=["start"])     # also read_parquet, read_json, read_excel, read_sql
df.to_csv("out.csv", index=False)
df.to_parquet("runs.parquet")                           # columnar, typed, compressed: prefer it for big data
```

## 3. Selection: `loc`, `iloc`, boolean masks

| Syntax | Selects |
|---|---|
| `df["secs"]` | one column → Series |
| `df[["robot", "secs"]]` | several columns → DataFrame |
| `df.loc[row_labels, col_labels]` | **label-based** (slices *include* the end label) |
| `df.iloc[row_pos, col_pos]` | **position-based** (half-open slices like Python) |
| `df[df["ok"]]` | rows where a boolean Series is True |
| `df.query("secs > 20 and ok")` | expression syntax |

```python
df.loc[df["task"] == "pick", ["robot", "secs"]]
df.iloc[0:2, 1:3]
df[(df["secs"] > 12) & df["ok"]]        # & | ~ with parentheses (not and/or)
df.loc[df["robot"] == "r1", "secs"] *= 1.1   # assignment through loc: the correct way
```

> [!KEY]
> **Copy-on-write (pandas 3).** Every indexing result behaves like an independent copy: modifying it never changes the original, and chained assignment such as `df[df.ok]["secs"] = 0` **does nothing** to `df` (pandas warns). Always assign through a single `.loc[rows, cols] = value` on the frame you mean to change. Under the hood, copies are lazy (data is copied only when you write), so this costs nothing until mutation.

## 4. Missing data

```python
df["secs"].isna()                 # boolean mask
df.dropna(subset=["secs"])        # drop rows missing secs
df["secs"].fillna(df["secs"].median())
df["secs"].interpolate()          # linear fill between neighbours (time series)
df["secs"].ffill()                # carry the last observation forward (sensor holds)
```

`NaN` propagates through arithmetic, and aggregations skip it by default (`skipna=True`). Integer columns with missing values use the nullable `Int64` dtype (capital I) instead of silently becoming float.

## 5. New columns and vectorised transforms

```python
df["mins"] = df["secs"] / 60
df["fast"] = np.where(df["secs"] < 15, "fast", "slow")
df["robot_upper"] = df["robot"].str.upper()            # .str accessor for string ops
df = df.assign(rate=lambda d: 1 / d["secs"])           # chainable
```

> [!WARNING]
> Avoid `df.apply(f, axis=1)` and `iterrows()` for arithmetic. They call Python per row and can be 100× slower than column operations. Reach for vectorised column maths, `np.where`/`np.select`, `.str`/`.dt` accessors, or `map` with a dict.

## 6. Group-by: split → apply → combine

```python
by_robot = df.groupby("robot")["secs"].agg(["count", "mean", "max"])
summary = (df.groupby(["robot", "task"], as_index=False)
             .agg(runs=("secs", "size"), mean_secs=("secs", "mean"), success=("ok", "mean")))
df["secs_vs_robot_mean"] = df["secs"] - df.groupby("robot")["secs"].transform("mean")   # broadcast back
```

| Method | Output shape |
|---|---|
| `agg` | one row per group |
| `transform` | same shape as the input (a group statistic per row) |
| `filter` | the rows of the groups passing a predicate |
| `apply` | anything (flexible but slow) |

## 7. Combining tables

```python
robots = pd.DataFrame({"robot": ["r1", "r2", "r4"], "model": ["arm", "rover", "drone"]})
merged = df.merge(robots, on="robot", how="left", validate="many_to_one")   # SQL-style join
pd.concat([df_jan, df_feb], ignore_index=True)                            # stack rows
```

| `how=` | Keeps |
|---|---|
| `inner` | keys in both |
| `left` / `right` | all keys of one side (missing → NaN) |
| `outer` | all keys |

`validate="many_to_one"` raises if the right table has duplicate keys. It catches the classic silent row-explosion bug. `indicator=True` adds a column showing where each row came from.

## 8. Reshaping

```python
wide = df.pivot_table(index="robot", columns="task", values="secs", aggfunc="mean")
long = wide.reset_index().melt(id_vars="robot", var_name="task", value_name="secs")
df.sort_values(["robot", "secs"], ascending=[True, False])
df["task"].value_counts()
```

## 9. Time series

```python
idx = pd.date_range("2026-01-01 08:00", periods=6, freq="10min")
temp = pd.Series([20.1, 20.4, np.nan, 21.0, 22.5, 22.1], index=idx)
temp.resample("30min").mean()          # downsample to 30-minute means
temp.rolling(3, min_periods=1).mean()  # moving average
temp.diff(), temp.pct_change()
temp.index.hour                         # datetime components; on a column use .dt.hour
temp["2026-01-01 08:10":"2026-01-01 08:40"]   # label slicing by time
```

Resampling with `.resample(...).ohlc()` or `.agg`, rolling windows, `shift` for lags, and timezone handling (`tz_localize`/`tz_convert`) make pandas the first stop for robot telemetry analysis.

## 10. Performance and correctness habits

- Use categorical dtype for repeated strings: `df["robot"] = df["robot"].astype("category")`.
- Read only the columns you need (`usecols=`), and use Parquet for big files.
- Vectorise; avoid per-row Python.
- Keep tidy data: one row per observation, one column per variable.
- Use `validate=` on merges, and check `df.duplicated()` and `df.isna().sum()` early.
- For data beyond RAM or for speed, use Polars, DuckDB or Arrow-backed dtypes (`dtype_backend="pyarrow"`).

## 11. Exam-ready answers

> [!EXAM]
> **The pandas DataFrame and group-by.** A DataFrame is a two-dimensional labelled data structure whose columns are Series sharing a common row index; columns may have different dtypes, and operations within a column are vectorised over NumPy or Arrow arrays. Rows and columns are selected by label with `loc`, by position with `iloc`, or with boolean masks. Group-by implements split–apply–combine: rows are partitioned by key values, a function is applied to each group, and the results are combined, either reduced to one row per group (`agg`), broadcast back to the original shape (`transform`), or filtered. Joins are performed with `merge`, analogous to SQL joins, and time-indexed data supports resampling and rolling-window computations.

## 12. Cheat sheet

| Need | Code |
|---|---|
| filter rows | `df[df.secs > 10]` / `df.query("secs > 10")` |
| set values | `df.loc[mask, "col"] = v` |
| per-group stats | `df.groupby("k").agg(m=("x", "mean"))` |
| group stat on every row | `groupby(...).transform("mean")` |
| join | `df.merge(other, on="k", how="left", validate="m:1")` |
| wide ↔ long | `pivot_table` / `melt` |
| missing values | `isna`, `fillna`, `dropna`, `interpolate` |
| time buckets | `resample("1min").mean()` |
| moving average | `rolling(w).mean()` |

> [!INTERVIEW]
> **"Why did my assignment `df[df.x > 0]["y"] = 1` not change `df`?"** That's chained indexing. The first `[]` produces a new object (with copy-on-write in pandas 3, always effectively a copy), and the assignment modifies that temporary. Use one indexing operation on the original: `df.loc[df.x > 0, "y"] = 1`. In pandas 1.x the behaviour was unpredictable (sometimes a view, sometimes a copy, with SettingWithCopyWarning). Pandas 3's copy-on-write makes it consistently a no-op, which is why the `.loc` form is the only correct idiom.
