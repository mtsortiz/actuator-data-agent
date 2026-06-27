import os
import json
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
file_path = "data/raw/series_76_tables.pdf"


def upload_pdf(file_path):
    file_ref = client.files.upload(file=file_path)
    print("pdf uploaded successfully.")
    return file_ref

def extract_data(file_ref):
    print("Extracting data from PDF...")
    system_prompt = """
Act as a data extraction expert. Analyze the attached PDF for the Series 76 actuators. 
Extract every single row from the technical tables and convert them into a single structured list in JSON format. 
It is essential that you associate each row with its page metadata: identify the Enclosure Type 
(Weatherproof or Explosionproof), the Voltage (110V, 220V, 24V), and the Phase (Single or 3-Phase) 
based on the headings of the page where the row is located. 
Explicitly separate the 50 Hz and 60 Hz values into independent numerical columns where applicable. 
Do not omit any model.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=file_ref,
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            temperature=0.0  
        )
    )
    print("Data extracted successfully.")
    return response.text


def clean_data(raw_json_string):
    json_data = json.loads(raw_json_string)
    df = pd.DataFrame(json_data)
    
    columns_to_drop = ['Operating Speed (sec)', 'Full Load Current (FLA) Amps', 'Locked Rotor Current (LRA) Amps']
    existing_columns = [col for col in columns_to_drop if col in df.columns]
    
    if existing_columns:
        df = df.drop(columns=existing_columns)
    df["Motor Power Watts"] = df["Motor Power Watts"].bfill().ffill()
        
    return df

def save_to_sqlite(df, db_path):
    conn = sqlite3.connect(db_path)
    df.to_sql("electric_data_table", conn, if_exists="replace", index=False)
    conn.close()

def main():
    file_ref = upload_pdf(file_path)
    try:
        raw_json = extract_data(file_ref)
        df = clean_data(raw_json)
        save_to_sqlite(df,"data/processed/electric_data_table.db")
    except Exception as e:
        print(f"Error crítico en el pipeline de ingesta: {e}")
        
    finally:
        try:
            print("Limpiando archivo temporal en Google AI Studio...")
            client.files.delete(name=file_ref.name)
            print("Temporary file deleted.")
        except Exception as e:
            print(f"Nota: No se pudo borrar el archivo en la API ({e}). Google lo limpiará automáticamente en 48hs.")
if __name__ == "__main__":
    main()