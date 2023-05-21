import pandas as pd
from scipy import stats


def has_keywords(row, keywords):
    match = False
    for keyword in keywords:
        match = (
            keyword in row["title"].lower()
            or keyword in row["description"].lower()
            or keyword in row["location"].lower()
            or keyword in row["link"].lower().split("-")
        )
        if match:
            break
    return match


def fill_nan_strings(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    cols = ["title", "description", "location"]
    data.loc[:, cols] = data.loc[:, cols].fillna("")
    return data


def drop_nan_prices(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    return data.dropna(subset=["price"])


def drop_nan_expenses(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    return data.dropna(subset=["expenses"])


def drop_duplicate_locations(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    return data.drop_duplicates("location")


def add_has_balcony(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data.loc[:, "has_balcony"] = data.apply(
        has_keywords, args=(["balcón", "balcon", "balcones"],), axis=1
    )
    return data


def add_has_terrace(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data.loc[:, "has_terrace"] = data.apply(
        has_keywords, args=(["terraza", "terrazas"],), axis=1
    )
    return data


def add_is_studio_apartment(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data.loc[:, "is_studio_apartment"] = data.apply(
        has_keywords, args=(["monoambiente", "monoambientes"],), axis=1
    )
    return data


def add_has_garage(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    keywords = ["cochera", "cocheras", "garage", "garaje"]
    data.loc[:, "has_garage"] = data.apply(has_keywords, args=(keywords,), axis=1)
    return data


def add_has_garden(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    keywords = ["jardin", "jardín", "jardines"]
    data.loc[:, "has_garden"] = data.apply(has_keywords, args=(keywords,), axis=1)
    return data


def capitalize_location(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data.loc[:, "location"] = data["location"].apply(lambda s: s.title())
    return data


def normalize_title(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data.loc[:, "title"] = data["title"].str.capitalize()
    return data


def remove_expenses_outliers(data: pd.DataFrame) -> pd.DataFrame:
    nan_expenses = data.query("expenses.isna()", engine="python").copy()
    data = data.dropna(subset=["expenses"])
    expenses = data["expenses"].copy()
    transform = stats.boxcox(expenses, 0)
    z = (transform - transform.mean()) / transform.std()
    clean = data[(-3 <= z) & (z <= 3)].copy()
    return pd.concat([clean, nan_expenses])


def remove_price_outliers(data: pd.DataFrame) -> pd.DataFrame:
    price = data["price"].copy()
    transform = stats.boxcox(price, 0)
    z = (transform - transform.mean()) / transform.std()
    return data[(-3 <= z) & (z <= 3)].copy()
