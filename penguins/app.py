from shiny import App, ui, reactive, render
from palmerpenguins import load_penguins
import seaborn as sns
import matplotlib.pyplot as plt

# Load the dataset
penguins_df = load_penguins()

# UI Layout
app_ui = ui.page_fluid(
    ui.h1("🐧 Palmer Penguins Dashboard", class_="text-center text-primary"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h2("🔧 Filters"),
            ui.input_checkbox_group(
                id="selected_species",
                label="Select species:",
                choices=["Adelie", "Chinstrap", "Gentoo"],
                selected=["Adelie", "Chinstrap", "Gentoo"]
            ),
            ui.input_checkbox_group(
                id="selected_island",
                label="Select island:",
                choices=penguins_df["island"].dropna().unique().tolist(),
                selected=penguins_df["island"].dropna().unique().tolist()
            ),
            ui.input_slider(
                id="min_flipper_length",
                label="Minimum Flipper Length (mm):",
                min=170,
                max=235,
                value=180
            ),
            ui.input_slider(
                id="seaborn_bin_count",
                label="Seaborn Histogram Bins",
                min=5,
                max=50,
                value=20
            ),
            ui.a("🔗 GitHub Repo", href="https://github.com/sabrouch36/cintel-03-reactive", target="_blank")
        ),
        # Body layout in two rows (3 + 2 charts)
        ui.layout_columns(
            # Row 1
            ui.card(
                ui.h2("📊 Filtered Data Summary"),
                ui.output_text_verbatim("filtered_count"),
                ui.output_data_frame("filtered_table")
            ),
            ui.card(
                ui.h2("📉 Body Mass Histogram"),
                ui.output_plot("mass_histogram")
            ),
            ui.card(
                ui.h2("🥧 Species Pie Chart"),
                ui.output_plot("pie_chart")
            ),

            # Row 2
            ui.card(
                ui.h2("📏 Flipper Length Histogram"),
                ui.output_plot("seaborn_histogram")
            ),
            ui.card(
                ui.h2("📌 Scatter Plot"),
                ui.output_plot("scatterplot")
            )
        )
    )
)

# Server Logic
def server(input, output, session):

    @reactive.calc
    def filtered_data():
        return penguins_df[
            (penguins_df["species"].isin(input.selected_species())) &
            (penguins_df["island"].isin(input.selected_island())) &
            (penguins_df["flipper_length_mm"] >= input.min_flipper_length())
        ].dropna()

    @output
    @render.text
    def filtered_count():
        return f"Filtered rows: {len(filtered_data())}"

    @output
    @render.data_frame
    def filtered_table():
        return filtered_data()

    @output
    @render.plot
    def mass_histogram():
        df = filtered_data()
        fig, ax = plt.subplots()
        sns.histplot(data=df, x="body_mass_g", hue="species", multiple="stack", palette="Set2", ax=ax)
        ax.set_title("Body Mass Distribution")
        fig.tight_layout()
        return fig

    @output
    @render.plot
    def pie_chart():
        df = filtered_data()
        fig, ax = plt.subplots()
        df["species"].value_counts().plot.pie(autopct='%1.1f%%', ax=ax, colors=["#66c2a5", "#fc8d62", "#8da0cb"])
        ax.set_title("Species Distribution")
        ax.set_ylabel("")
        fig.tight_layout()
        return fig

    @output
    @render.plot
    def seaborn_histogram():
        df = filtered_data()
        fig, ax = plt.subplots()
        sns.histplot(data=df, x="flipper_length_mm", bins=input.seaborn_bin_count(), kde=True, ax=ax)
        ax.set_title("Seaborn Histogram: Flipper Length")
        fig.tight_layout()
        return fig

    @output
    @render.plot
    def scatterplot():
        df = filtered_data()
        fig, ax = plt.subplots()
        sns.scatterplot(data=df, x="bill_length_mm", y="flipper_length_mm", hue="species", style="island", ax=ax)
        ax.set_title("Bill Length vs Flipper Length")
        ax.set_xlabel("Bill Length (mm)")
        ax.set_ylabel("Flipper Length (mm)")
        fig.tight_layout()
        return fig

# Run the app
app = App(app_ui, server)
