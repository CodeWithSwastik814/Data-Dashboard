import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np

# ── Dataset ────────────────────────────────────────────
DataSet = pd.read_csv('netflix_titles.csv')

# ── Global Style ───────────────────────────────────────
sns.set_theme(style="darkgrid")
plt.rcParams.update({
    "figure.facecolor": "#141414",
    "axes.facecolor":   "#1f1f1f",
    "axes.labelcolor":  "white",
    "xtick.color":      "white",
    "ytick.color":      "white",
    "text.color":       "white",
    "grid.color":       "#6B8F71",
    "axes.titlecolor":  "#3B5041",
    "font.family":      "sans-serif",
})
RED  = "#6B8F71"
BLUE = "#D4C9A8"


# ── 1. Data Info ───────────────────────────────────────
def dataInfo():
    print(f"Rows    : {DataSet.shape[0]}")
    print(f"Columns : {DataSet.shape[1]}")
    print(f"Shape   : {DataSet.shape}")


# ── 2. Data Preview ────────────────────────────────────
def dataPre():
    print(DataSet.head(10))


# ── 3. Pie Chart ───────────────────────────────────────
def pieChart():
    type_counts = DataSet["type"].value_counts()

    fig, ax = plt.subplots(figsize=(6, 6), facecolor="#141414")

    wedges, texts, autotexts = ax.pie(
        type_counts.values,
        labels=type_counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=[RED, BLUE],
        explode=(0.05, 0),
        wedgeprops={"linewidth": 2, "edgecolor": "#141414"}
    )

    for t in texts:
        t.set_color("white")
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(12)

    ax.set_title("🥧 Content Type Distribution", fontsize=15, pad=20)
    plt.tight_layout()
    plt.savefig("1_pie_chart.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Saved: 1_pie_chart.png")


# ── 4. Bar Chart ───────────────────────────────────────
def barChart():
    top_countries = (
        DataSet["country"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_countries.columns = ["country", "count"]

    fig, ax = plt.subplots(figsize=(10, 5), facecolor="#141414")

    sns.barplot(
        data=top_countries,
        x="country",
        y="count",
        palette=["#3B5041", "#4E6B57", "#6B8F71", "#A8C5A0",
                 "#F5F0E8", "#EDE8DD", "#FFFFFF", "#D4C9A8",
                 "#C9A84C", "#2C3E30"],
        ax=ax
    )

    ax.set_title("📊 Top 10 Countries by Number of Titles", fontsize=14)
    ax.set_xlabel("Country")
    ax.set_ylabel("Number of Titles")
    ax.tick_params(axis="x", rotation=30)

    for bar in ax.patches:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 20,
            int(bar.get_height()),
            ha="center", va="bottom", fontsize=9, color="white"
        )

    plt.tight_layout()
    plt.savefig("2_bar_chart.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Saved: 2_bar_chart.png")


# ── 5. Line Chart ──────────────────────────────────────
def lineChart():
    yearly = (
        DataSet[DataSet["release_year"].between(2010, 2021)]
        .groupby(["release_year", "type"])
        .size()
        .reset_index(name="count")
    )

    fig, ax = plt.subplots(figsize=(10, 5), facecolor="#141414")

    for content_type, color, marker in [("Movie", RED, "o"), ("TV Show", BLUE, "s")]:
        subset = yearly[yearly["type"] == content_type]
        ax.plot(
            subset["release_year"], subset["count"],
            label=content_type,
            color=color,
            marker=marker,
            linewidth=2.5,
            markersize=7
        )
        ax.fill_between(subset["release_year"], subset["count"],
                        alpha=0.15, color=color)

    ax.set_title("📈 Content Added by Year (2010–2021)", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Titles")
    ax.legend(facecolor="#1f1f1f", labelcolor="white")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(1))

    plt.tight_layout()
    plt.savefig("3_line_chart.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Saved: 3_line_chart.png")


# ── 6. Heatmap ─────────────────────────────────────────
def heatMap():
    heat_data = (
        DataSet[DataSet["release_year"].between(2012, 2021)]
        .groupby(["type", "release_year"])
        .size()
        .unstack(fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(12, 3.5), facecolor="#141414")

    sns.heatmap(
        heat_data,
        annot=True,
        fmt="d",
        cmap="Reds",
        linewidths=0.5,
        linecolor="#141414",
        cbar_kws={"label": "Number of Titles"},
        ax=ax
    )

    ax.set_title("🔥 Heatmap — Content Volume by Year & Type", fontsize=14)
    ax.set_xlabel("Release Year")
    ax.set_ylabel("Content Type")
    ax.tick_params(axis="x", rotation=0)

    plt.tight_layout()
    plt.savefig("4_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Saved: 4_heatmap.png")


# ── 7. Scatter Chart ───────────────────────────────────
def scatterChart():
    scatter_df = (
        DataSet[DataSet["release_year"].between(2010, 2021)]
        .groupby(["release_year", "type"])
        .size()
        .reset_index(name="count")
    )

    fig, ax = plt.subplots(figsize=(10, 5), facecolor="#141414")

    for content_type, color, marker in [("Movie", RED, "o"), ("TV Show", BLUE, "^")]:
        subset = scatter_df[scatter_df["type"] == content_type]
        ax.scatter(
            subset["release_year"],
            subset["count"],
            label=content_type,
            color=color,
            s=120,
            marker=marker,
            edgecolors="white",
            linewidths=0.5,
            zorder=5
        )

    ax.set_title("🔵 Scatter Chart — Movies vs TV Shows by Year", fontsize=14)
    ax.set_xlabel("Release Year")
    ax.set_ylabel("Number of Titles")
    ax.legend(facecolor="#1f1f1f", labelcolor="white")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(1))

    plt.tight_layout()
    plt.savefig("5_scatter_chart.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Saved: 5_scatter_chart.png")


# ── 8. Histogram ───────────────────────────────────────
def histogram():
    valid_ratings = ["TV-MA", "TV-14", "TV-PG", "R", "PG-13",
                     "TV-Y7", "TV-Y", "PG", "TV-G", "NR"]
    rating_df = DataSet[DataSet["rating"].isin(valid_ratings)]

    fig, ax = plt.subplots(figsize=(10, 5), facecolor="#141414")

    sns.countplot(
        data=rating_df,
        x="rating",
        order=valid_ratings,
        palette=["#3B5041"] * 4 + ["#4E6B57"] * 3 + ["#A8C5A0"] * 3,
        ax=ax
    )

    ax.set_title("📉 Histogram — Content Rating Distribution", fontsize=14)
    ax.set_xlabel("Rating")
    ax.set_ylabel("Number of Titles")

    for bar in ax.patches:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 30,
            int(bar.get_height()),
            ha="center", va="bottom", fontsize=9, color="white"
        )

    plt.tight_layout()
    plt.savefig("6_histogram.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Saved: 6_histogram.png")


# ── Run All Charts ─────────────────────────────────────
if __name__ == "__main__":
    dataInfo()
    dataPre()
    pieChart()
    barChart()
    lineChart()
    heatMap()
    scatterChart()
    histogram()
    print('workings')
    