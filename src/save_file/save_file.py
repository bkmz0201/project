import pandas as pd


def save_file(file, sign_group):
    df = pd.DataFrame(columns=['filename', 'x', 'y', 'class_name', 'x_min', 'y_min', 'x_max', 'y_max'])
    for sign in sign_group:
        df.loc[len(df.index)] = [sign.file, sign.x, sign.y, sign.class_name, sign.x_min, sign.y_min, sign.x_max,
                                 sign.y_max]
    df.to_csv(file)
