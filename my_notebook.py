import marimo

__generated_with = "0.17.7"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd
    return


@app.cell
def _():
    k ='david'
    return (k,)


@app.cell
def _(k):
    print('kibet ' + k)
    return


app._unparsable_cell(
    r"""
    marimo import /home/dataopske/Desktop/jav/notebooks/08_feature_engineering.ipynb 
    """,
    name="_"
)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
