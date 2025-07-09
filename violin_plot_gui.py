import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import seaborn as sns
import sys

class ViolinPlotApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Violin Plotter")
        self.master.geometry("900x700")

        self.df = None
        self.fig = None
        self.ax = None
        self.canvas = None
        self.toolbar = None

        # 日本語フォントを自動設定し、文字化けを防止
        self.setup_japanese_font()
        
        # ダークモードのテーマを設定
        self.setup_dark_theme()

        sns.set_theme(style="ticks") # Seaborn theme, Matplotlib rcParams will override specifics

        self.create_widgets()

    def setup_japanese_font(self):
        """
        実行環境(OS)に応じて、利用可能な日本語フォントを自動で検索し、
        Matplotlibのデフォルトフォントに設定する。
        """
        try:
            # OSごとの一般的な日本語フォントリスト
            if sys.platform.startswith('win'):
                fonts = ['Meiryo', 'Yu Gothic', 'MS Gothic']
            elif sys.platform.startswith('darwin'):
                fonts = ['Hiragino Sans', 'Hiragino Maru Gothic ProN']
            else: # Linuxなど
                fonts = ['IPAexGothic', 'Noto Sans CJK JP']

            available_fonts = [f.name for f in mpl.font_manager.fontManager.ttflist]
            
            target_font = None
            # 定義したフォントリストの中から、利用可能なものを探す
            for font in fonts:
                if font in available_fonts:
                    target_font = font
                    break
            
            if target_font:
                mpl.rcParams['font.family'] = target_font
                # Unicodeのマイナス記号が文字化けするのを防ぐ
                mpl.rcParams['axes.unicode_minus'] = False 
                print(f"日本語フォントとして '{target_font}' を設定しました。")
            else:
                print("警告: 利用可能な日本語フォントが見つかりませんでした。グラフの日本語が文字化けする可能性があります。")
        except Exception as e:
            print(f"フォント設定中にエラーが発生しました: {e}")

    def setup_dark_theme(self):
        """
        TkinterウィジェットとMatplotlibグラフをダークモードにするためのスタイル設定。
        """
        # ダークモードのカラーパレットを定義
        self.dark_bg = "#2E2E2E"       # メインの背景色
        self.darker_bg = "#1E1E1E"     # ルートウィンドウ、図の背景色
        self.control_panel_bg = "#3A3A3A" # 設定パネルの背景色
        self.light_text = "#E0E0E0"    # テキストの色
        self.entry_bg = "#444444"      # エントリフィールドの背景色
        self.button_bg = "#555555"     # ボタンの背景色
        self.button_hover_bg = "#666666" # ボタンホバー時の背景色
        self.accent_color = "#007ACC"  # 強調色（コンボボックス選択など）
        self.separator_color = "#666666" # セパレータや境界線の色
        
        # Matplotlib特有のカラー設定
        self.dark_axes_bg = "#3C3C3C"  # プロット領域の背景色

        # --- Tkinter ttk スタイル設定 ---
        style = ttk.Style()
        
        # ダークモードに適した基本テーマ (clam) を使用
        style.theme_use("clam") 

        # ルートウィンドウの背景色を設定
        self.master.configure(bg=self.darker_bg)

        # 全てのウィジェットの一般的なスタイルを設定 (個別に上書きされない限り適用)
        style.configure('.', background=self.dark_bg, foreground=self.light_text, font=('Arial', 10))

        # 各ウィジェットのスタイルを詳細に設定
        style.configure('TFrame', background=self.dark_bg)
        
        style.configure('TLabelFrame', 
                        background=self.control_panel_bg, 
                        foreground=self.light_text, 
                        bordercolor=self.separator_color)
        style.configure('TLabelFrame.Label', 
                        foreground=self.light_text, 
                        background=self.control_panel_bg) # LabelFrameのラベル部分のスタイル
        
        style.configure('TLabel', background=self.dark_bg, foreground=self.light_text)
        # LabelFrame内のラベルは、LabelFrameの背景色に合わせるために専用のスタイルを定義
        style.configure('ControlPanel.TLabel', 
                        background=self.control_panel_bg, 
                        foreground=self.light_text)

        style.configure('TButton', 
                        background=self.button_bg, 
                        foreground=self.light_text, 
                        bordercolor=self.separator_color, 
                        focusthickness=0, 
                        focuscolor=self.button_bg) # フォーカス時のボーダー色をボタン色に合わせる
        style.map('TButton', 
                  background=[('active', self.button_hover_bg), ('!disabled', self.button_bg)],
                  foreground=[('active', self.light_text), ('!disabled', self.light_text)])

        style.configure('TCombobox', 
                        fieldbackground=self.entry_bg, 
                        background=self.button_bg, # ドロップダウン矢印部分の背景
                        foreground=self.light_text, 
                        selectbackground=self.accent_color, # ドロップダウンリストで選択されたアイテムの背景
                        selectforeground=self.light_text,
                        bordercolor=self.separator_color)
        style.map('TCombobox', 
                  fieldbackground=[('readonly', self.entry_bg)], 
                  background=[('readonly', self.button_bg)], 
                  foreground=[('readonly', self.light_text)],
                  selectbackground=[('readonly', self.accent_color)])
        
        style.configure('TEntry', 
                        fieldbackground=self.entry_bg, 
                        foreground=self.light_text, 
                        insertcolor=self.light_text, # カーソルの色
                        bordercolor=self.separator_color)
        
        style.configure('TCheckbutton', 
                        background=self.control_panel_bg, # テキストやインジケータの背後のエリア
                        foreground=self.light_text,
                        indicatorbackground=self.entry_bg, # チェックボックスの四角の背景
                        indicatorforeground=self.light_text) # チェックマークの色
        style.map('TCheckbutton',
                  background=[('active', self.control_panel_bg)], # アクティブ時も背景は変えない
                  foreground=[('active', self.light_text)],
                  indicatorbackground=[('active', self.button_hover_bg)]) # アクティブ時のインジケータ背景
        
        style.configure('TSeparator', background=self.separator_color)

        # --- Matplotlib rcParams によるダークモード設定 ---
        # 図の背景色とプロット領域の背景色を設定
        mpl.rcParams['figure.facecolor'] = self.darker_bg 
        mpl.rcParams['axes.facecolor'] = self.dark_axes_bg     
        
        # テキスト、軸ラベル、目盛りの色を設定
        mpl.rcParams['text.color'] = self.light_text
        mpl.rcParams['axes.labelcolor'] = self.light_text
        mpl.rcParams['xtick.color'] = self.light_text
        mpl.rcParams['ytick.color'] = self.light_text
        
        # グリッドラインの色とスタイル
        mpl.rcParams['grid.color'] = self.separator_color
        mpl.rcParams['grid.linewidth'] = 0.5
        mpl.rcParams['grid.alpha'] = 0.5

        # 軸の縁と線の太さ
        mpl.rcParams['axes.edgecolor'] = self.separator_color
        mpl.rcParams['axes.linewidth'] = 1.0

        # タイトルの色を黒に変更
        mpl.rcParams['axes.titlecolor'] = 'black' 

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        control_panel = ttk.LabelFrame(main_frame, text="設定", padding="10")
        control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Button(control_panel, text="CSVファイルを指定", command=self.load_csv).pack(fill=tk.X, pady=5)

        # ラベルにカスタムスタイルを適用して、LabelFrameの背景色に合わせる
        ttk.Label(control_panel, text="X軸 (カテゴリ):", style='ControlPanel.TLabel').pack(fill=tk.X, pady=(10, 0))
        self.x_column_var = tk.StringVar()
        self.x_column_combo = ttk.Combobox(control_panel, textvariable=self.x_column_var, state="readonly")
        self.x_column_combo.pack(fill=tk.X)

        ttk.Label(control_panel, text="Y軸 (値):", style='ControlPanel.TLabel').pack(fill=tk.X, pady=(5, 0))
        self.y_column_var = tk.StringVar()
        self.y_column_combo = ttk.Combobox(control_panel, textvariable=self.y_column_var, state="readonly")
        self.y_column_combo.pack(fill=tk.X)
        
        ttk.Separator(control_panel, orient='horizontal').pack(fill='x', pady=15)

        ttk.Label(control_panel, text="グラフタイトル:", style='ControlPanel.TLabel').pack(fill=tk.X, pady=(5, 0))
        self.title_var = tk.StringVar(value="violin plot")
        ttk.Entry(control_panel, textvariable=self.title_var).pack(fill=tk.X)
        
        ttk.Label(control_panel, text="カラーパレット:", style='ControlPanel.TLabel').pack(fill=tk.X, pady=(10, 0))
        self.palette_var = tk.StringVar(value="pastel")
        color_palettes = ['pastel', 'muted', 'deep', 'colorblind', 'viridis', 'rocket', 'crest', 'magma', 'Blues', 'Greens']
        self.palette_combo = ttk.Combobox(control_panel, textvariable=self.palette_var, values=color_palettes, state="readonly")
        self.palette_combo.pack(fill=tk.X)

        ttk.Separator(control_panel, orient='horizontal').pack(fill='x', pady=15)

        self.show_boxplot_var = tk.BooleanVar(value=True)
        # CheckbuttonもLabelFrameの背景色に合わせる
        ttk.Checkbutton(control_panel, text="箱ひげ図を表示する", variable=self.show_boxplot_var, 
                        style='TCheckbutton').pack(anchor='w', pady=2)
        
        self.show_points_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_panel, text="データ点を表示する (Jitter)", variable=self.show_points_var, 
                        style='TCheckbutton').pack(anchor='w', pady=2)
        
        ttk.Button(control_panel, text="グラフを生成", command=self.generate_plot).pack(fill=tk.X, pady=(20, 5))
        
        self.save_button = ttk.Button(control_panel, text="グラフを保存", command=self.save_plot, state="disabled")
        self.save_button.pack(fill=tk.X, pady=5)

        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(7, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        self.toolbar.update()
        
        # NavigationToolbar2Tk はTkinterのTk.Frameを使用するため、手動でスタイルを適用
        self.toolbar.config(background=self.dark_bg)
        for widget in self.toolbar.winfo_children():
            if isinstance(widget, (tk.Button, ttk.Button)):
                try:
                    # Tk.Button に直接スタイルを適用
                    widget.config(
                        background=self.button_bg,
                        foreground=self.light_text,
                        highlightbackground=self.dark_bg, # フォーカス時の白い枠を消す
                        highlightcolor=self.dark_bg
                    )
                except tk.TclError:
                    # ttk.Button の場合はttk.Styleが適用されるため、ここでは何もしない
                    pass
            elif isinstance(widget, (tk.Frame, ttk.Frame)):
                # ツールバー内のサブフレームにもスタイルを適用
                widget.config(background=self.dark_bg)
                for sub_widget in widget.winfo_children():
                    if isinstance(sub_widget, (tk.Button, ttk.Button)):
                        try:
                            sub_widget.config(
                                background=self.button_bg,
                                foreground=self.light_text,
                                highlightbackground=self.dark_bg,
                                highlightcolor=self.dark_bg
                            )
                        except tk.TclError:
                            pass

        # 初期表示テキストの色もダークモードに合わせる
        # ただし、今回は「出力エリアの表示は変えず」という指示に準じるため、
        # ここは元のlight_textのままにする。
        # ユーザーは「箱ひげ図、データ点、タイトルの文字の色」を黒と指定しており、
        # この初期テキストはプロットが生成されると消えるため、特に変更の必要はないと判断。
        self.ax.text(0.5, 0.5, "Plot Area", ha="center", va="center", fontsize=14, 
                     color=self.light_text, transform=self.ax.transAxes) 
        self.canvas.draw()
    
    def load_csv(self):
        filepath = filedialog.askopenfilename(
            title="CSVファイルを選択",
            filetypes=[("CSVファイル", "*.csv"), ("すべてのファイル", "*.*")]
        )
        if not filepath: return
        try:
            self.df = pd.read_csv(filepath)
            columns = list(self.df.columns)
            self.x_column_combo['values'] = columns
            self.y_column_combo['values'] = columns
            if len(columns) >= 2:
                self.x_column_var.set(columns[0])
                self.y_column_var.set(columns[1])
            messagebox.showinfo("成功", f"'{filepath.split('/')[-1]}' を読み込みました。")
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルの読み込みに失敗しました:\n{e}")
            self.df = None

    def generate_plot(self):
        if self.df is None:
            messagebox.showwarning("警告", "最初にCSVファイルを読み込んでください。")
            return

        x_col = self.x_column_var.get()
        y_col = self.y_column_var.get()
        if not x_col or not y_col:
            messagebox.showwarning("警告", "X軸とY軸の列を選択してください。")
            return

        try:
            self.ax.clear()

            # 複数のプロットで共通する引数を辞書にまとめる
            plot_common_args = {
                'x': x_col,
                'y': y_col,
                'data': self.df,
                'ax': self.ax
            }

            # 1. バイオリンプロット本体
            sns.violinplot(
                **plot_common_args,
                palette=self.palette_var.get(), 
                inner=None, # 内側のプロットは自分で重ね書きするためNoneにする
                linewidth=1.5
            )

            # 2. データ点の重ね書き (オプション)
            if self.show_points_var.get():
                sns.stripplot(
                    **plot_common_args,
                    jitter=True, 
                    color='black', # データ点の色を黒に変更
                    size=4, 
                    alpha=0.6
                )

            # 3. 箱ひげ図の重ね書き (オプション)
            if self.show_boxplot_var.get():
                boxplot_style = {
                    'boxprops': {'facecolor':'None', 'edgecolor':'black'}, # 枠線色を黒に変更
                    'medianprops': {'color':'black', 'linewidth':2},       # 中央値色を黒に変更
                    'whiskerprops': {'color':'black', 'linewidth':1.5},    # ウィスカー色を黒に変更
                    'capprops': {'color':'black', 'linewidth':1.5},       # キャップ色を黒に変更
                    'showfliers': False # 外れ値は表示しない
                }
                sns.boxplot(**plot_common_args, **boxplot_style)
            
            # Matplotlibのタイトル、ラベルはrcParamsにより自動でダークモード対応
            # axes.titlecolorはsetup_dark_themeで'black'に設定済み
            self.ax.set_title(self.title_var.get(), fontsize=16, pad=15)
            # 軸ラベルの色は引き続きlight_text (明るい色) のまま
            self.ax.set_xlabel(x_col, fontsize=12)
            self.ax.set_ylabel(y_col, fontsize=12)
            
            self.fig.tight_layout()
            self.canvas.draw()
            self.save_button.config(state="normal")

        except Exception as e:
            messagebox.showerror("エラー", f"グラフの生成に失敗しました:\n{e}")

    def save_plot(self):
        filepath = filedialog.asksaveasfilename(
            title="グラフを保存",
            filetypes=[
                ("PNGファイル", "*.png"), ("PDFファイル", "*.pdf"),
                ("SVGファイル", "*.svg"), ("JPEGファイル", "*.jpg"),
            ],
            defaultextension=".png"
        )
        if not filepath: return
        try:
            self.fig.savefig(filepath, dpi=300, bbox_inches='tight')
            messagebox.showinfo("成功", f"グラフを '{filepath}' に保存しました。")
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルの保存に失敗しました:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ViolinPlotApp(root)
    root.mainloop()