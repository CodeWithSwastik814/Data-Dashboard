import sys 
import os 
import importlib.util
import threading

# ── PyQt5 / PyQt6 shim ───────────────────────────────────────────────────────
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QFrame, QScrollArea, QSizePolicy,
        QStackedWidget, QGridLayout, QSpacerItem, QMessageBox
    )
    from PyQt5.QtCore    import Qt, QTimer, QThread, pyqtSignal
    from PyQt5.QtGui     import QFont, QCursor
    PYQT = 5
except ImportError:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QFrame, QScrollArea, QSizePolicy,
        QStackedWidget, QGridLayout, QSpacerItem, QMessageBox
    )
    from PyQt6.QtCore    import Qt, QTimer, QThread, pyqtSignal
    from PyQt6.QtGui     import QFont, QCursor
    PYQT = 6

import matplotlib
matplotlib.use("Qt5Agg" if PYQT == 5 else "QtAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.ticker as mticker
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
import numpy as np
import seaborn as sns


# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
ORIG_SCRIPT = os.path.join(BASE_DIR, "Data_A.py")
CSV_PATH    = os.path.join(BASE_DIR, "netflix_titles.csv")


# ── Palette ───────────────────────────────────────────────────────────────────
G_DARK  = "#3B5041"
G_MID   = "#4E6B57"
G_LIGHT = "#6B8F71"
G_PALE  = "#A8C5A0"
CREAM   = "#F5F0E8"
CREAM2  = "#EDE8DD"
WHITE   = "#FFFFFF"
SAND    = "#D4C9A8"
GOLD    = "#C9A84C"
TEXT_D  = "#2C3E30"
TEXT_M  = "#5A6B5A"
CHART_PAL = [G_DARK, G_MID, G_LIGHT, GOLD, "#D4663A", "#C0392B",
             G_PALE, "#8B6F47", "#7A9E7E", SAND]

# ── Global QSS ────────────────────────────────────────────────────────────────
QSS = f"""
QMainWindow, QWidget#root {{ background: {CREAM}; }}

QWidget#sidebar {{
    background: {G_DARK};
    border-right: 1px solid {G_MID};
}}
QLabel#logo {{
    font-size: 22px;
    color: {CREAM};
    padding: 24px 18px 2px 18px;
}}
QLabel#logo-sub {{
    font-size: 10px;
    color: {G_PALE};
    padding: 0 18px 18px 18px;
    letter-spacing: 1px;
}}
QLabel#nav-group {{
    font-size: 9px;
    color: {G_LIGHT};
    padding: 10px 18px 4px 18px;
    letter-spacing: 1px;
}}
QPushButton#nav-btn {{
    background: transparent;
    color: {CREAM2};
    border: none;
    text-align: left;
    padding: 9px 14px 9px 18px;
    font-size: 11px;
    border-radius: 0px;
}}
QPushButton#nav-btn:hover {{
    background: {G_MID};
}}
QPushButton#nav-btn[active="true"] {{
    background: {G_LIGHT};
    color: {WHITE};
}}
QPushButton#export-btn {{
    background: {G_MID};
    color: {G_PALE};
    border: none;
    border-radius: 7px;
    font-size: 9px;
    padding: 6px 14px;
    text-align: left;
    margin: 2px 12px;
}}
QPushButton#export-btn:hover {{
    background: {G_LIGHT};
    color: {WHITE};
}}
QWidget#topbar {{
    background: {CREAM};
    border-bottom: 1px solid {SAND};
}}
QLabel#topbar-title {{
    font-size: 18px;
    color: {TEXT_D};
    padding: 0 0 0 4px;
}}
QLabel#pill {{
    background: {G_PALE};
    color: {G_DARK};
    font-size: 9px;
    font-weight: bold;
    padding: 4px 14px;
    border-radius: 12px;
    margin-right: 10px;
}}
QLabel#pill-warn {{
    background: {SAND};
    color: {TEXT_M};
    font-size: 9px;
    font-weight: bold;
    padding: 4px 14px;
    border-radius: 12px;
    margin-right: 10px;
}}
QWidget#content-area {{
    background: {CREAM};
}}
QFrame#stat-card {{
    background: {WHITE};
    border: 1px solid {SAND};
    border-radius: 12px;
}}
QLabel#stat-label {{
    font-size: 9px;
    color: {TEXT_M};
    padding: 12px 16px 2px 16px;
}}
QLabel#stat-value {{
    font-size: 26px;
    padding: 0 16px 4px 16px;
}}
QFrame#accent-bar {{
    border-radius: 2px;
    margin: 0 10px 8px 10px;
    max-height: 3px;
    min-height: 3px;
}}
QFrame#sidebar-divider {{
    background: {G_MID};
    max-height: 1px;
    min-height: 1px;
    margin: 8px 16px;
}}
QScrollArea {{ border: none; background: {CREAM}; }}
QScrollBar:vertical {{
    background: {CREAM2};
    width: 6px;
    border-radius: 3px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {SAND};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""


# ── Helpers ───────────────────────────────────────────────────────────────────
def load_module():
    if not os.path.exists(ORIG_SCRIPT):
        return None
    spec = importlib.util.spec_from_file_location("netflix_analysis", ORIG_SCRIPT)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_csv():
    return pd.read_csv(CSV_PATH) if os.path.exists(CSV_PATH) else None


def styled_fig(w=9, h=4.6):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=CREAM)
    ax.set_facecolor(WHITE)
    for sp in ax.spines.values():
        sp.set_edgecolor(SAND); sp.set_linewidth(0.8)
    ax.tick_params(colors=TEXT_M, labelsize=9)
    ax.xaxis.label.set_color(TEXT_M)
    ax.yaxis.label.set_color(TEXT_M)
    ax.title.set_color(G_DARK)
    ax.grid(color=SAND, linewidth=0.4, linestyle="--", alpha=0.55)
    fig.tight_layout(pad=2)
    return fig, ax


def anim_bars(fig, ax, cats, vals, colors=None):
    cols = (colors or CHART_PAL)[:len(vals)]
    bars = ax.bar(cats, [0]*len(vals), color=cols,
                  edgecolor=WHITE, linewidth=1.4, width=0.6)
    ax.set_ylim(0, max(vals)*1.18)
    N = 45
    def upd(f):
        e = 1 - (1-(f+1)/N)**3
        for b, v in zip(bars, vals):
            b.set_height(v * e)
        return bars
    return animation.FuncAnimation(fig, upd, frames=N,
                                   interval=22, blit=False, repeat=False)


def anim_lines(fig, ax, xs, datasets):
    ax.set_xlim(min(xs)-.5, max(xs)+.5)
    ax.set_ylim(0, max(max(d["y"]) for d in datasets)*1.2)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
    refs = []
    for d in datasets:
        ln, = ax.plot([], [], label=d["label"], color=d["color"],
                      marker=d.get("marker","o"), linewidth=2.2, markersize=5)
        refs.append((ln, d))
    ax.legend(facecolor=CREAM2, labelcolor=TEXT_D, edgecolor=SAND, fontsize=9)
    fills = []
    def upd(f):
        n = f+1
        for fl in fills:
            try: fl.remove()
            except: pass
        fills.clear()
        for ln, d in refs:
            ln.set_data(xs[:n], d["y"][:n])
            fills.append(ax.fill_between(xs[:n], d["y"][:n],
                                          alpha=0.10, color=d["color"]))
        return [ln for ln,_ in refs]
    return animation.FuncAnimation(fig, upd, frames=len(xs),
                                   interval=55, blit=False, repeat=False)


# ── Canvas widget ─────────────────────────────────────────────────────────────
class ChartCanvas(QWidget):
    def __init__(self, fig, parent=None):
        super().__init__(parent)
        self.canvas = FigureCanvas(fig)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding,
                                   QSizePolicy.Policy.Expanding)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.canvas)


# ── Stat card ─────────────────────────────────────────────────────────────────
def make_stat_card(label, value, color):
    card = QFrame(); card.setObjectName("stat-card")
    lay  = QVBoxLayout(card); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)

    lbl = QLabel(label.upper()); lbl.setObjectName("stat-label")
    val = QLabel(value);         val.setObjectName("stat-value")
    val.setStyleSheet(f"color: {color}; font-family: Georgia; font-weight: bold;")

    bar = QFrame(); bar.setObjectName("accent-bar")
    bar.setStyleSheet(f"background: {color}; border-radius: 2px; "
                      f"margin: 0 10px 8px 10px; max-height: 3px; min-height: 3px;")

    lay.addWidget(lbl)
    lay.addWidget(val)
    lay.addStretch()
    lay.addWidget(bar)
    return card


# ── Main window ───────────────────────────────────────────────────────────────
class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("florest  ·  Netflix Analytics")
        self.resize(1260, 780)
        self.setStyleSheet(QSS)

        self.mod     = load_module()
        self.dataset = load_csv()
        self._anims  = []
        self._active = "overview"
        self._nav_btns = {}

        root = QWidget(); root.setObjectName("root")
        self.setCentralWidget(root)
        main_lay = QHBoxLayout(root)
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.setSpacing(0)

        main_lay.addWidget(self._build_sidebar())
        main_lay.addWidget(self._build_right(), 1)

        self._show("overview")

    # ── Sidebar ───────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sb = QWidget(); sb.setObjectName("sidebar"); sb.setFixedWidth(210)
        lay = QVBoxLayout(sb)
        lay.setContentsMargins(0,0,0,0)
        lay.setSpacing(0)

        logo = QLabel("🌿  florest"); logo.setObjectName("logo")
        logo.setFont(QFont("Georgia", 20))
        sub  = QLabel("Netflix Analytics"); sub.setObjectName("logo-sub")
        lay.addWidget(logo)
        lay.addWidget(sub)

        self._sidebar_section(lay, "EXPLORE")
        nav = [
            ("overview",  "All",       "16"),
            ("pie",       "Type Split", "2"),
            ("bar",       "Countries", "10"),
            ("line",      "Trend",      "↑"),
            ("scatter",   "Scatter",    "⊕"),
            ("histogram", "Ratings",    "6"),
            ("heatmap",   "Heatmap",    "✦"),
        ]
        for key, label, badge in nav:
            self._nav_item(lay, key, label, badge)

        div = QFrame(); div.setObjectName("sidebar-divider")
        lay.addWidget(div)
        self._sidebar_section(lay, "EXPORT  (.py)")

        exports = [("pieChart","Pie Chart"),("barChart","Bar Chart"),
                   ("lineChart","Line Chart"),("heatMap","Heatmap"),
                   ("scatterChart","Scatter"),("histogram","Histogram")]
        for fn, lbl in exports:
            btn = QPushButton(f"↗  {lbl}"); btn.setObjectName("export-btn")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda _, n=fn: self._call_orig(n))
            lay.addWidget(btn)

        lay.addStretch()
        return sb

    def _sidebar_section(self, lay, text):
        lbl = QLabel(text); lbl.setObjectName("nav-group")
        lay.addWidget(lbl)

    def _nav_item(self, lay, key, label, badge):
        row = QWidget()
        hl  = QHBoxLayout(row)
        hl.setContentsMargins(0,0,0,0)
        hl.setSpacing(0)

        btn = QPushButton(label); btn.setObjectName("nav-btn")
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(lambda _, k=key: self._show(k))

        bdg = QLabel(badge)
        bdg.setStyleSheet(
            f"background:{G_MID};color:{CREAM};font-size:8px;font-weight:bold;"
            f"padding:2px 8px;border-radius:10px;margin:6px 12px 6px 0;"
        )
        bdg.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hl.addWidget(btn, 1)
        hl.addWidget(bdg)
        lay.addWidget(row)
        self._nav_btns[key] = btn

    # ── Right panel ───────────────────────────────────────────────────────
    def _build_right(self):
        right = QWidget()
        vl = QVBoxLayout(right)
        vl.setContentsMargins(0,0,0,0)
        vl.setSpacing(0)

        # Topbar
        tb = QWidget(); tb.setObjectName("topbar"); tb.setFixedHeight(52)
        tl = QHBoxLayout(tb); tl.setContentsMargins(24,0,16,0)
        self._title_lbl = QLabel("Overview")
        self._title_lbl.setObjectName("topbar-title")
        self._title_lbl.setFont(QFont("Georgia", 17))
        tl.addWidget(self._title_lbl)
        tl.addStretch()

        ds_ok    = self.dataset is not None
        pill_txt = f"● {len(self.dataset):,} titles" if ds_ok else "○ CSV not found"
        pill     = QLabel(pill_txt)
        pill.setObjectName("pill" if ds_ok else "pill-warn")
        tl.addWidget(pill)
        vl.addWidget(tb)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{SAND};"); vl.addWidget(sep)

        # Scrollable content
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        self._content = QWidget(); self._content.setObjectName("content-area")
        self._content_lay = QVBoxLayout(self._content)
        self._content_lay.setContentsMargins(20,16,20,20)
        self._content_lay.setSpacing(14)
        scroll.setWidget(self._content)
        vl.addWidget(scroll, 1)
        return right

    # ── Nav helpers ───────────────────────────────────────────────────────
    def _refresh_nav(self):
        for k, btn in self._nav_btns.items():
            btn.setProperty("active", k == self._active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _call_orig(self, fn):
        if self.mod is None:
            QMessageBox.critical(self, "Not found",
                                 f"Cannot load:\n{ORIG_SCRIPT}")
            return
        f = getattr(self.mod, fn, None)
        if f is None:
            QMessageBox.critical(self, "Not found",
                                 f"'{fn}' not in module")
            return
        threading.Thread(target=f, daemon=True).start()

    def _clear(self):
        self._anims.clear()
        plt.close("all")
        while self._content_lay.count():
            item = self._content_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show(self, key):
        self._active = key
        self._refresh_nav()
        self._clear()
        titles = {
            "overview":"Overview",    "pie":"Type Distribution",
            "bar":"Top Countries",    "line":"Yearly Trend",
            "scatter":"Scatter by Year","histogram":"Rating Distribution",
            "heatmap":"Content Heatmap",
        }
        self._title_lbl.setText(titles.get(key, key.title()))
        {
            "overview":  self._overview,
            "pie":       self._pie,
            "bar":       self._bar,
            "line":      self._line,
            "scatter":   self._scatter,
            "histogram": self._histogram,
            "heatmap":   self._heatmap,
        }.get(key, lambda: None)()
        self._content_lay.addStretch()

    def _add_chart(self, fig):
        canvas = ChartCanvas(fig, self._content)
        canvas.setMinimumHeight(340)
        self._content_lay.addWidget(canvas)
        canvas.canvas.draw()
        return canvas

    def _no_data(self):
        lbl = QLabel("⚠  Place netflix_titles.csv next to this script")
        lbl.setStyleSheet(f"color:{SAND};font-size:13px;font-style:italic;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._content_lay.addWidget(lbl)

    # ── Tabs ──────────────────────────────────────────────────────────────
    def _overview(self):
        if self.dataset is None:
            self._no_data(); return
        ds = self.dataset

        grid_w = QWidget()
        grid   = QGridLayout(grid_w)
        grid.setSpacing(12); grid.setContentsMargins(0,0,0,0)
        cards = [
            ("Total Titles", f"{len(ds):,}",                            G_DARK),
            ("Movies",       f"{int((ds['type']=='Movie').sum()):,}",   G_MID),
            ("TV Shows",     f"{int((ds['type']=='TV Show').sum()):,}", G_LIGHT),
            ("Countries",    f"{ds['country'].nunique()}",              GOLD),
        ]
        for i,(lbl,val,col) in enumerate(cards):
            grid.addWidget(make_stat_card(lbl,val,col), 0, i)
        self._content_lay.addWidget(grid_w)

        top5 = ds["country"].value_counts().head(5)
        fig, ax = styled_fig(9, 3.8)
        ax.set_title("Top 5 Countries", fontsize=12, fontweight="bold")
        ax.set_ylabel("Titles", fontsize=9)
        ani = anim_bars(fig, ax, list(top5.index), list(top5.values))
        self._anims.append(ani)
        self._add_chart(fig)

    def _pie(self):
        if self.dataset is None:
            self._no_data(); return
        counts = self.dataset["type"].value_counts()
        fig, ax = styled_fig(6, 5); fig.patch.set_facecolor(CREAM)
        N = 38
        def upd(f):
            t = min((f+1)/N, 1); e = 1-(1-t)**3
            ax.clear(); ax.set_facecolor(CREAM)
            w, texts, autos = ax.pie(
                [v*e for v in counts.values],
                labels=counts.index, autopct="%1.1f%%" if t>=1 else None,
                startangle=90-(1-e)*300, colors=[G_DARK, G_PALE],
                explode=[0.04]*len(counts),
                wedgeprops={"linewidth":2.5,"edgecolor":CREAM}
            )
            for t2 in texts:  t2.set_color(TEXT_D); t2.set_fontsize(11)
            for a  in autos:  a.set_color(WHITE);    a.set_fontsize(10)
            ax.set_title("Content Type Split", fontsize=13,
                         fontweight="bold", color=G_DARK, pad=14)
        ani = animation.FuncAnimation(fig, upd, frames=N,
                                      interval=35, blit=False, repeat=False)
        self._anims.append(ani)
        self._add_chart(fig)

    def _bar(self):
        if self.dataset is None:
            self._no_data(); return
        top = self.dataset["country"].value_counts().head(10)
        fig, ax = styled_fig(10, 5)
        ax.set_title("Top 10 Countries by Titles", fontsize=12, fontweight="bold")
        ax.set_xlabel("Country", fontsize=9); ax.set_ylabel("Titles", fontsize=9)
        ax.tick_params(axis="x", rotation=30)
        ani = anim_bars(fig, ax, list(top.index), list(top.values))
        self._anims.append(ani)
        self._add_chart(fig)

    def _line(self):
        if self.dataset is None:
            self._no_data(); return
        yearly = (self.dataset[self.dataset["release_year"].between(2010,2021)]
                  .groupby(["release_year","type"]).size().reset_index(name="count"))
        years = list(range(2010,2022))
        def gc(t):
            s = yearly[yearly["type"]==t]
            return [int(s[s["release_year"]==y]["count"].sum()) for y in years]
        fig, ax = styled_fig(10, 5)
        ax.set_title("Content Trend 2010–2021", fontsize=12, fontweight="bold")
        ax.set_xlabel("Year",fontsize=9); ax.set_ylabel("Titles",fontsize=9)
        ds2 = [{"label":"Movie",   "y":gc("Movie"),   "color":G_DARK,"marker":"o"},
               {"label":"TV Show", "y":gc("TV Show"), "color":GOLD,  "marker":"s"}]
        ani = anim_lines(fig, ax, years, ds2)
        self._anims.append(ani)
        self._add_chart(fig)

    def _scatter(self):
        if self.dataset is None:
            self._no_data(); return
        sdf = (self.dataset[self.dataset["release_year"].between(2010,2021)]
               .groupby(["release_year","type"]).size().reset_index(name="count"))
        fig, ax = styled_fig(10, 5)
        ax.set_title("Movies vs TV Shows — Scatter", fontsize=12, fontweight="bold")
        ax.set_xlabel("Year",fontsize=9); ax.set_ylabel("Titles",fontsize=9)
        ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
        N = 32
        def upd(f):
            ax.cla(); ax.set_facecolor(WHITE)
            for sp in ax.spines.values():
                sp.set_edgecolor(SAND); sp.set_linewidth(0.8)
            ax.tick_params(colors=TEXT_M, labelsize=9)
            ax.grid(color=SAND, linewidth=0.4, linestyle="--", alpha=0.55)
            e = 1-(1-(f+1)/N)**3
            for ct,col,mk in [("Movie",G_DARK,"o"),("TV Show",GOLD,"^")]:
                s = sdf[sdf["type"]==ct]
                ax.scatter(s["release_year"], s["count"]*e,
                           label=ct, color=col, s=100, marker=mk,
                           edgecolors=WHITE, linewidths=0.7, zorder=5)
            ax.legend(facecolor=CREAM2, labelcolor=TEXT_D, edgecolor=SAND, fontsize=9)
            ax.set_title("Movies vs TV Shows — Scatter",fontsize=12,
                         fontweight="bold",color=G_DARK)
            ax.set_xlabel("Year",fontsize=9); ax.set_ylabel("Titles",fontsize=9)
            ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
        ani = animation.FuncAnimation(fig, upd, frames=N,
                                      interval=45, blit=False, repeat=False)
        self._anims.append(ani)
        self._add_chart(fig)

    def _histogram(self):
        if self.dataset is None:
            self._no_data(); return
        valid = ["TV-MA","TV-14","TV-PG","R","PG-13","TV-Y7","TV-Y","PG","TV-G","NR"]
        rdf   = self.dataset[self.dataset["rating"].isin(valid)]
        counts = [int((rdf["rating"]==r).sum()) for r in valid]
        colors = [G_DARK]*4 + [GOLD]*3 + [G_PALE]*3
        fig, ax = styled_fig(10, 5)
        ax.set_title("Rating Distribution", fontsize=12, fontweight="bold")
        ax.set_xlabel("Rating",fontsize=9); ax.set_ylabel("Titles",fontsize=9)
        ani = anim_bars(fig, ax, valid, counts, colors=colors)
        self._anims.append(ani)
        self._add_chart(fig)

    def _heatmap(self):
        if self.dataset is None:
            self._no_data(); return
        heat = (self.dataset[self.dataset["release_year"].between(2012,2021)]
                .groupby(["type","release_year"]).size().unstack(fill_value=0))
        fig, ax = styled_fig(11, 3.6); fig.patch.set_facecolor(CREAM)
        cmap = LinearSegmentedColormap.from_list("olive",
                   [CREAM2, G_PALE, G_MID, G_DARK])
        def draw(alpha):
            ax.cla(); ax.set_facecolor(WHITE)
            sns.heatmap(heat, annot=True, fmt="d", cmap=cmap,
                        linewidths=0.6, linecolor=CREAM,
                        cbar_kws={"label":"Titles"}, ax=ax, alpha=alpha)
            ax.set_title("Content Volume by Year & Type", fontsize=12,
                         fontweight="bold", color=G_DARK)
            ax.tick_params(colors=TEXT_M, labelsize=9)
            ax.set_xlabel("Year",fontsize=9); ax.set_ylabel("",fontsize=9)
        draw(0.05)
        def upd(f): draw(min((f+1)/20, 1.0))
        ani = animation.FuncAnimation(fig, upd, frames=20,
                                      interval=55, blit=False, repeat=False)
        self._anims.append(ani)
        self._add_chart(fig)


# ── Entry ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    win = Dashboard()
    win.show()
    sys.exit(app.exec() if PYQT == 6 else app.exec_())
