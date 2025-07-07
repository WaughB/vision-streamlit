import gradio as gr
import pandas as pd
import os
import folium
from folium.plugins import MarkerCluster

# --- Config ---
DATA_DIR = "data"


# --- Get available CSV files ---
def get_data_files():
    """
    Get the list of CSV files in the configured data directory.

    Returns
    -------
    list of str
        A list of CSV filenames found in the DATA_DIR.
    """
    return [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]


# --- Get resolved field files ---
def load_lookup_table(filepath):
    """
    Load a lookup table CSV file and convert it into a dictionary.

    Parameters
    ----------
    filepath : str
        Path to the CSV file with columns 'Code' and 'Description'.

    Returns
    -------
    dict
        A dictionary mapping integer codes to human-readable descriptions.
    """
    df = pd.read_csv(filepath)
    return dict(zip(df["Code"], df["Description"]))


# --- Load the lookups ---
VESSEL_TYPE_LOOKUP = load_lookup_table("vessel-type-lookup.csv")
CARGO_LOOKUP = load_lookup_table("cargo-lookup.csv")


# --- Load and filter AIS data ---
def explore_data(file_name, **filters):
    """
    Load AIS data from a CSV file and apply filters to it.

    Parameters
    ----------
    file_name : str
        The name of the CSV file to load from the DATA_DIR.
    **filters : dict
        Dictionary of column-value pairs for filtering rows. Filters are
        case-insensitive and support partial string matches.

    Returns
    -------
    pandas.DataFrame
        A DataFrame of the filtered AIS data with added human-readable
        columns: 'VesselTypeDesc' and 'CargoDesc'.
    """
    file_path = os.path.join(DATA_DIR, file_name)
    df = pd.read_csv(file_path)

    # Enrich fields
    df["VesselTypeDesc"] = df["VesselType"].map(VESSEL_TYPE_LOOKUP).fillna("Unknown")
    df["CargoDesc"] = df["Cargo"].map(CARGO_LOOKUP).fillna("Unknown")

    for column, value in filters.items():
        if value and column in df.columns:
            df = df[
                df[column].astype(str).str.contains(str(value), case=False, na=False)
            ]

    return df


# --- Generate vessel map with popups ---
def generate_map(df):
    """
    Generate an interactive folium map with vessel positions.

    Parameters
    ----------
    df : pandas.DataFrame
        A DataFrame containing latitude (`LAT`), longitude (`LON`),
        `VesselName`, and `IMO`.

    Returns
    -------
    str
        An HTML representation of the generated folium map.
        If the DataFrame is empty or lacks lat/lon, returns a message string.
    """
    if df.empty or "LAT" not in df.columns or "LON" not in df.columns:
        return "No position data available to map."

    avg_lat = df["LAT"].mean()
    avg_lon = df["LON"].mean()

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=4)
    cluster = MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        try:
            lat, lon = float(row["LAT"]), float(row["LON"])
            name = row.get("VesselName", "Unknown")
            imo = row.get("IMO", "N/A")
            popup = f"<b>{name}</b><br>IMO: {imo}"
            folium.Marker([lat, lon], popup=popup).add_to(cluster)
        except Exception:
            continue

    return m._repr_html_()


# --- Gradio app layout ---
def build_interface():
    """
    Build and return the Gradio interface for AIS data exploration.

    Returns
    -------
    gradio.Blocks
        A Gradio interface object with dropdown file selector, dynamic filters,
        data table, and interactive map display.
    """
    # Load all lookup values
    vessel_type_options = sorted(set(VESSEL_TYPE_LOOKUP.values()))
    cargo_type_options = sorted(set(CARGO_LOOKUP.values()))
    data_files = get_data_files()

    with gr.Blocks() as demo:
        gr.Markdown("# 🗺️ Marine Cadastre AIS Explorer")
        file_dropdown = gr.Dropdown(choices=data_files, label="Select AIS CSV File")

        # Define exact filters
        vessel_name = gr.Textbox(label="Vessel Name")
        vessel_type_desc = gr.Dropdown(
            choices=[""] + vessel_type_options,
            label="Vessel Type (description)",
            allow_custom_value=True,
        )
        cargo_desc = gr.Dropdown(
            choices=[""] + cargo_type_options,
            label="Cargo Type (description)",
            allow_custom_value=True,
        )
        mmsi = gr.Textbox(label="MMSI")
        imo = gr.Textbox(label="IMO")
        basedatetime = gr.Textbox(label="BaseDateTime (e.g. 2024-01-01)")

        output_table = gr.Dataframe(label="Filtered AIS Data", interactive=False)
        output_map = gr.HTML(label="Map of Vessel Positions")

        def search(
            file_name: str,
            vessel_name: str,
            vessel_type_desc: str,
            cargo_desc: str,
            mmsi: str,
            imo: str,
            basedatetime: str,
        ):
            """
            Filter AIS vessel data using specific fields and return tabular data
            and a map of matching vessel locations.

            Parameters
            ----------
            file_name : str
                The CSV file name from the /data directory to search.
                Example: "AIS_2024_01_01.csv"

            vessel_name : str
                Partial or full vessel name to match (case-insensitive).
                Example: "MAERSK"

            vessel_type_desc : str
                Description of the vessel type (e.g., "Tanker", "Cargo").
                Example: "Cargo"

            cargo_desc : str
                Description of cargo type (e.g., "Hazardous", "Tanker").
                Example: "Hazardous"

            mmsi : str
                Maritime Mobile Service Identity number (exact or partial match).
                Example: "367123456"

            imo : str
                IMO number for the vessel.
                Example: "1234567"

            basedatetime : str
                Substring or date (e.g., "2024-01-01") for filtering the timestamp.
                Example: "2024-01-01 13:00"

            Returns
            -------
            tuple
                A tuple containing:
                - pandas.DataFrame: Filtered data (first 500 rows).
                - str: Folium map rendered as HTML.
            """

            filters = {
                "VesselName": vessel_name,
                "VesselTypeDesc": vessel_type_desc,
                "CargoDesc": cargo_desc,
                "MMSI": mmsi,
                "IMO": imo,
                "BaseDateTime": basedatetime,
            }

            df = explore_data(file_name, **filters)
            map_html = generate_map(df)

            return df.head(500), map_html

        search_button = gr.Button("🔍 Apply Filters")
        search_button.click(
            fn=search,
            inputs=[
                file_dropdown,
                vessel_name,
                vessel_type_desc,
                cargo_desc,
                mmsi,
                imo,
                basedatetime,
            ],
            outputs=[output_table, output_map],
        )

    return demo


if __name__ == "__main__":
    build_interface().launch(mcp_server=True)
