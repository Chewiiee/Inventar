#!/usr/bin/env python

import pandas as pd
import qrcode
from jinja2 import Template
import os
import subprocess

def clear_directory(target_dir):
    for file in os.listdir(target_dir):
        os.remove(os.path.join(target_dir, file))


if __name__ == "__main__":
    working_dir = "/Users/matthiasfruth/projects/inventar"
    target_ssh_user = "root"
    target_hostmane = "vm249139"
    target_path = "/var/www/html/"
    target_domain = "https://vm249139.ur.de"

    excel_file = os.path.join(working_dir, "inventar.xlsm")
    sheet_name = "inventar_sheet"

    html_output_dir = os.path.join(working_dir, "html")
    img_output_dir = os.path.join(working_dir, "qrcodes")

    template_file = os.path.join(working_dir, "templates/item.html")


    # Make sure output dirs exists
    os.makedirs(html_output_dir, exist_ok = True)
    os.makedirs(img_output_dir, exist_ok = True)

    # Read the Excel table
    xls = pd.ExcelFile(excel_file)
    df = pd.read_excel(xls, sheet_name=sheet_name)
    df = df[['Zimmer', 'Gerät']]
    df = df.dropna(how='any') # alternive is 'all'

    # Load HTML template
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    template = Template(template_content)

    clear_directory(html_output_dir)
    clear_directory(img_output_dir)
    
    # Generate HTML files
    for idx, row in df.iterrows():
        html_content = template.render(zimmer=row['Zimmer'], geraet=row['Gerät'])

        http_target = f"row_{idx + 2}.html"

        # Create the html snippets
        file_path = os.path.join(html_output_dir, http_target)
        with open(file_path, 'w', encoding='utf-8') as f:
           f.write(html_content)

        # Create the QR Codes
        file_url = f"{target_domain}/{http_target}"
        img = qrcode.make(file_url)
        img.save(os.path.join(img_output_dir, f"qrcode_row_{idx + 2}.png"))


    print(f"Generated {len(df)} HTML files in {html_output_dir}")
    print(f"Generated {len(df)} QR Codes in {img_output_dir} ")

    # ToDo: Copy files to webserver...
    # subprocess run rsync -avh inventar@
    cmd = [
        "rsync",
        "-a",
        "--delete",
        f"{html_output_dir}/",
        f"{target_ssh_user}@{target_hostmane}:{target_path}"
    ]
    subprocess.run(cmd, check=True)

    # Adapt the correct permissions on the target machine
    cmd = [
        "ssh",
        f"{target_ssh_user}@{target_hostmane}",
        "chown -R caddy:caddy /var/www/html"
    ]
    subprocess.run(cmd, check=True)
