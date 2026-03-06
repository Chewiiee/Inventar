#!/usr/bin/env python

import pandas as pd
import qrcode
from jinja2 import Template
import os
import subprocess
import logging
import shutil
from dotenv import load_dotenv

COLUMNS = [
    "Inventarnummer",
    "SN",
    "Bezeichnung",
    "Kompatibilität",
    "Standort", 
    "In Nutzung",
    "Letzter Wartungstermin",
    "Nächster Wartungstermin",
    "Firma",
    "Bild",
]

def copy_image(src, dest, id):
    # Copy the image to the html directory
    if os.path.isfile(src):
        try:
            shutil.copy(src, dest)
            logger.info(f"Image copied: {src} -> {dest}")
        except Exception as e:
            logger.warning(f"Could not copy image for {id}: {e}")

def clear_directory(target_dir):
    for file in os.listdir(target_dir):
        file_path = os.path.join(target_dir, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                logger.info(f"Removed: {file_path}")
        except Exception as e:
            logger.warning(f"Could not remove {file_path}: {e}")

def read_excel_file(excel_file, sheet_name):
    try:
        logger.info(f"Reading Excel file: {excel_file}")
        xls = pd.ExcelFile(excel_file)
        df = pd.read_excel(xls, sheet_name=sheet_name)
        df = df[COLUMNS]
        df = df.fillna('---')            # replace NaN with dashes before further processing
        df["Inventarnummer"] = df["Inventarnummer"].astype(str)
        logger.info(f"Excel file read successfully, {len(df)} rows found")
        return df
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        raise

def load_html_template(template_file):
    try:
        logger.info(f"Loading template: {template_file}")
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        template = Template(template_content)
        logger.info("Template loaded successfully")
        return template
    except Exception as e:
        logger.error(f"Error loading template: {e}")
        raise

if __name__ == "__main__":
    # Load environment variables
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_file = os.path.join(script_dir, ".env")
    load_dotenv(env_file)
 
    # Setup logging
    log_file = os.path.join(script_dir, "generate.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("Script started")

    # Handle paths other constants
    desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    target_ssh_user = os.getenv("TARGET_SSH_USER")
    target_hostname = os.getenv("TARGET_HOSTNAME")
    target_path = os.getenv("TARGET_PATH")
    target_url = os.getenv("TARGET_URL")
    excel_file = os.path.join(desktop_dir, "inventar.xlsm")
    sheet_name = "inventar_sheet"
    html_output_dir = os.path.join(desktop_dir, "html")
    html_pictures_dir = os.path.join(desktop_dir, "html/pictures")
    img_output_dir = os.path.join(desktop_dir, "qrcodes")
    template_file = os.path.join(script_dir, "templates/item.html")
    logger.info(f"Desktop directory: {desktop_dir}") 
    logger.info(f"Target host: {target_ssh_user}@{target_hostname}")
    logger.info(f"Target path: {target_path}")

    # Make sure output dirs exists
    os.makedirs(html_output_dir, exist_ok = True)
    os.makedirs(html_pictures_dir, exist_ok = True)
    os.makedirs(img_output_dir, exist_ok = True)
    logger.info(f"Output directories created: {html_output_dir}, {img_output_dir}")

    # Actual Logic about Reading the Excel file and generating the HTML files
    df = read_excel_file(excel_file, sheet_name)
    # ensure inventarnummer is treated as string to prevent numeric formatting
    template = load_html_template(template_file)

    print(df)

    logger.info("Clearing output directories")
    clear_directory(html_output_dir)
    clear_directory(html_pictures_dir)
    clear_directory(img_output_dir)
    
    # Generate files
    for idx, row in df.iterrows():
        copy_image(row["Bild"], html_pictures_dir, row["Inventarnummer"])
        print(row)

        # Get image filename for template
        image_filename = os.path.basename(row["Bild"]) if pd.notna(row["Bild"]) else ""
        image_path = target_url + "/pictures/" + image_filename if image_filename else ""
        print(image_path)
        html_content = template.render(item=row, image_path=image_path)

        # Create the html snippets
        html_file_path = os.path.join(html_output_dir, row["Inventarnummer"] + ".html")
        with open(html_file_path, 'w', encoding='utf-8') as f:
           f.write(html_content)

        # Create the QR Codes
        file_url = f"{target_url}/{row['Inventarnummer']}.html"
        img = qrcode.make(file_url)
        img.save(os.path.join(img_output_dir, f"inventarnummer_{row['Inventarnummer']}.png"))

    logger.info(f"Generated {len(df)} HTML files in {html_output_dir}")
    logger.info(f"Generated {len(df)} QR Codes in {img_output_dir}")

    # Clear the files on the target machine
    try:
        logger.info(f"Clearing remote directory: {target_path}")
        cmd_clear = [
            "ssh",
            f"{target_ssh_user}@{target_hostname}",
            f"rm -rf {target_path}/*"
        ]
        out_clear = subprocess.run(cmd_clear, check=True, timeout=60)
        out_clear.check_returncode()
        logger.info("Remote directory cleared successfully")
    except subprocess.TimeoutExpired:
        logger.error("SSH command timed out while clearing remote directory")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Error clearing remote directory: {e}")
        raise

    # Copy the files to the target machine
    try:
        logger.info(f"Copying files to {target_ssh_user}@{target_hostname}:{target_path}")
        cmd = [
            "scp",
            "-r",
            f"{html_output_dir}/*",
            f"{target_ssh_user}@{target_hostname}:{target_path}"
        ]
        out = subprocess.run(cmd, check=True, timeout=120)
        out.check_returncode()
        logger.info("Files copied successfully")
    except subprocess.TimeoutExpired:
        logger.error("SCP command timed out while copying files")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Error copying files: {e}")
        raise
    
    # Set correct permissions on the target machine
    try:
        logger.info(f"Setting permissions on {target_path}")
        cmd_chmod = [
            "ssh",
            f"{target_ssh_user}@{target_hostname}",
            f"chmod -R 755 {target_path}"
        ]
        out_chmod = subprocess.run(cmd_chmod, check=True, timeout=60)
        out_chmod.check_returncode()
        logger.info("Permissions set successfully")
    except subprocess.TimeoutExpired:
        logger.error("SSH command timed out while setting permissions")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting permissions: {e}")
        raise
