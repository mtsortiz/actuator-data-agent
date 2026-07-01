import os
import json
import sqlite3
import pandas as pd
import pdfplumber
from dotenv import load_dotenv
from google import genai
from google.genai import types
from langchain_chroma.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from schemas import ActuatorDataSet


load_dotenv()
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
file_path_tables = "data/raw/series_76_tables.pdf"
file_path_summary = "data/raw/series_76_summary.pdf"

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
            response_schema=ActuatorDataSet,
            temperature=0.0  
        )
    )
    print("Data extracted successfully.")
    return response.text


def get_motor_power(row):
    """
    Determines the exact motor power in watts using the model prefix, 
    the voltage and enclosure type.
    """
    model= str(row.get("base_part_number", "")).strip()
    voltage= str(row.get("voltage", "")).strip()
    enclosure_type= str(row.get("enclosure_type", "")).strip()

    if not model or model == "None":
        return None
    
    prefix = model[:4]

    #Explosionproof actuators
    if "Explosion" in enclosure_type:
        if "761" in prefix:
            return 15
        elif "762" in prefix or "763" in prefix:
            return 40
        elif "763Y" in prefix or "764" in prefix:
            return 90
        elif "765" in prefix:
            return 180
        return None
    
    #Weatherproof actuators
    else:
        if "761" in prefix:
            return 15
        elif "762" in prefix or "763A" in prefix:
            return 40
        elif "763B" in prefix or "763C" in prefix or "763X" in prefix or "763Y" in prefix:
            return 90
        elif "764" in prefix or "765" in prefix:
            return 180
        elif "766" in prefix or "767" in prefix:
            return 700
        return None
    

def clean_data(raw_json_string):
    json_data = json.loads(raw_json_string)
    df = pd.DataFrame(json_data["actuators"])


    df["motor_power_watts"] = df.apply(get_motor_power, axis=1)
    
    numeric_columns = [
        "on_off_output_torque_in_lbs", "on_off_output_torque_nm",
        "on_off_duty_cycle_percent", "on_off_cycles_per_hour",
        "modulating_output_torque_in_lbs", "modulating_output_torque_nm",
        "modulating_duty_cycle_percent", "modulating_starts_per_hour",
        "operating_speed_60hz_sec", "operating_speed_50hz_sec",
        "full_load_current_60hz_amps", "full_load_current_50hz_amps",
        "locked_rotor_current_60hz_amps", "locked_rotor_current_50hz_amps",
        "motor_power_watts"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

def save_to_sqlite(df, db_path):
    conn = sqlite3.connect(db_path)
    df.to_sql("electric_data_table", conn, if_exists="replace", index=False)
    conn.close()


def save_summary_to_chroma(file_path_summary):
    #Extract
    text = ""
    with pdfplumber.open(file_path_summary) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    #Chunking with 500 chuksize
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=50)
    docs = text_splitter.create_documents([text])

    #Embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    #ChromaDB
    Chroma.from_documents(docs, embeddings, persist_directory="data/processed/chroma_db")



def main_sqlite():
    file_ref = upload_pdf(file_path_tables)
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
    
def main_chroma():
    save_summary_to_chroma(file_path_summary)

if __name__ == "__main__":
    main_sqlite()
    main_chroma()