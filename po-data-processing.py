import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk  # Importing PIL for image handling
import pandas as pd
import os
from datetime import datetime
import re


def show_tutorial():
    tutorial_text = """
    Langkah-langkah:

    1. Upload File Shipment, BATMIS (csv delimeter titik koma";"), dan Procurement di tempat yang sudah disediakan.
    2. Klik tombol "Submit & Process Merge Data" untuk melakukan proses penggabungan data.
    3. Tunggu hingga proses selesai dilakukan , dan hasil penggabungan data akan otomatis ter-download.
    4. Jika ingin lanjut untuk proses pivoting data, silakan klik tombol "Process Pivot Data", tunggu hingga selesai dan hasil akan otomatis ter-download.
    5. Seluruh file hasil akan tersimpan di folder yang sama dengan tempat aplikasi ini tersimpan.
    """
    messagebox.showinfo("Tutorial Penggunaan", tutorial_text)
    
def browse_file(entry):
    filename = filedialog.askopenfilename()
    if filename:
        entry.delete(0, tk.END)
        entry.insert(0, filename)

def download_file(file_path):
    if os.path.exists(file_path):
        os.startfile(file_path)
    else:
        messagebox.showerror("Error", f"File {file_path} tidak ditemukan.")

def process_merge_data(fileShipment, fileBatmis, fileProcurement, progress_var, root):
    try:
        progress_var.set(10)
        root.update_idletasks()
        # Read Data Shipment & BATMIS
        dataShipmentRaw_1 = pd.read_excel(fileShipment, sheet_name='KUL-VENDOR 2025', skiprows=2)
        dataShipmentRaw_2 = pd.read_excel(fileShipment, sheet_name='BTH-VENDOR', skiprows=2)
        dataShipmentRaw_3 = pd.read_excel(fileShipment, sheet_name='PLB MONITORING')

        dataShipmentRaw = pd.concat([dataShipmentRaw_1, dataShipmentRaw_2])

        dataBatmisRaw = pd.read_csv(fileBatmis, on_bad_lines='skip', quoting=3, delimiter=";")

        # Preparasi Data Procurement
        dataProcurementRaw_1 = pd.read_excel(fileProcurement, sheet_name='AFM')
        dataProcurementRaw_2 = pd.read_excel(fileProcurement, sheet_name='CMA')
        dataProcurementRaw_3 = pd.read_excel(fileProcurement, sheet_name='PPM')
        dataProcurementRaw_4 = pd.read_excel(fileProcurement, sheet_name='PO')
        dataProcurementRaw_5 = pd.read_excel(fileProcurement, sheet_name='TOOLS')
        dataProcurementRaw_6 = pd.read_excel(fileProcurement, sheet_name='FAST MOVING')

        dataProcurementRaw_4.rename({'ORDER NUMBER':'ORDER', 'PN DESCRIPTION':'DESCRIPTION', 'STANDARD STATUS ORDER':'STANDARD STATUS', 'CURRENCY':'CURR'}, axis=1, inplace=True)
        dataProcurementRaw_5.rename({'ORDER NUMBER':'ORDER', 'PN DESCRIPTION':'DESCRIPTION', 'STANDARD STATUS ORDER':'STANDARD STATUS', 'CURRENCY':'CURR'}, axis=1, inplace=True)
        dataProcurementRaw_6.rename({'ORDER NUMBER':'ORDER', 'PN DESCRIPTION':'DESCRIPTION', 'STANDARD STATUS ORDER':'STANDARD STATUS', 'CURRENCY':'CURR'}, axis=1, inplace=True)

        # Merging Data Procurement (6 Sheets) menjadi 1
        dataProcurementRaw = pd.concat([dataProcurementRaw_1, dataProcurementRaw_2, dataProcurementRaw_3, dataProcurementRaw_4, dataProcurementRaw_5, dataProcurementRaw_6])

        dataProcurementRaw['LINE'] = pd.to_numeric(dataProcurementRaw['LINE'], errors='coerce').astype('Int64')

        # Remove quotes from the header if they appear at both ends
        dataBatmisRaw.columns = dataBatmisRaw.columns.map(lambda x: re.sub('^"(.*)"$', r'\1', x))
        progress_var.set(10)
        root.update_idletasks()
        # Remove quotes from the data if they appear at both ends
        # Also remove excessive internal quotes (like "" -> ")
        dataBatmisRaw = dataBatmisRaw.applymap(lambda x: re.sub(r'^"(.*)"$', r'\1', re.sub(r'""+', '"', x)) if isinstance(x, str) else x)

        # Pengolahan data BATMIS
        #dataBatmisProcessed = dataBatmisRaw[['REQUISITION', 'ORDER TYPE', 'ORDER NUMBER', 'ORDER LINE', 'STATUS', 'CREATED DATE', 'DATE AWB OUT', 'AUTHORIZATION_DATE', 'AUTHRQ_DATE', 'AUTHRQ_ID', 'AUTHRQ_BY', 'ORDER PN', 'PN DESCRIPTION', 'GRB_HISTORY', 'QTY', 'QTY_RCVD', 'UOM', 'AWB IN NUMBER', 'RRP_DATE', 'RRP_BY', 'NAME_RRPBY']]
        dataBatmisProcessed = dataBatmisRaw[['REQUISITION', 'ORDER TYPE', 'ORDER NUMBER', 'ORDER LINE', 'STATUS', 'CREATED DATE', 'DATE AWB OUT', 'AUTHORIZATION_DATE', 'AUTHRQ_DATE', 'AUTHRQ_ID', 'AUTHRQ_BY', 'ORDER PN', 'PN DESCRIPTION', 'GRB_HISTORY', 'QTY', 'QTY_RCVD', 'UOM', 'AWB IN NUMBER', 'RRP_DATE', 'RRP_BY', 'NAME_RRPBY']]

        dataBatmisProcessed['ORDER_TYPE-NUMBER-LINE'] = dataBatmisProcessed['ORDER TYPE'] + '-' + dataBatmisProcessed['ORDER NUMBER'].astype(str) + '-' + dataBatmisProcessed['ORDER LINE'].astype(str)
        dataBatmisProcessed['ORDER_TYPE-NUMBER-PN'] = dataBatmisProcessed['ORDER TYPE'] + '-' + dataBatmisProcessed['ORDER NUMBER'].astype(str)+ '-' + dataBatmisProcessed['ORDER PN'].astype(str)
        
        dataBatmisProcessed = dataBatmisProcessed.set_index('ORDER_TYPE-NUMBER-LINE')
        dataBatmisProcessed['ORDER_TYPE-NUMBER-LINE'] = dataBatmisProcessed['ORDER TYPE'] + '-' + dataBatmisProcessed['ORDER NUMBER'].astype(str) + '-' + dataBatmisProcessed['ORDER LINE'].astype(str)

        # Pengolahan data Procurement
        dataProcurement = dataProcurementRaw[['TYPE', 'ORDER', 'LINE', 'ORDER CREATED DATE', 'ETA', 'STANDARD STATUS', 'GENERAL STATUS', 'PN']]
        dataProcurement['ORDER_TYPE-NUMBER-LINE'] = dataProcurement['TYPE'] + '-' + dataProcurement['ORDER'].astype(str) + '-' + dataProcurement['LINE'].astype(str)
        #dataProcurement['ORDER_TYPE-NUMBER-PN'] = dataProcurement['TYPE'] + '-' + dataProcurement['ORDER'].astype(str)+ '-' + dataProcurement['PN'].astype(str)

        dataProcurement = dataProcurement.set_index('ORDER_TYPE-NUMBER-LINE')
        dataProcurement['ORDER_TYPE-NUMBER-LINE'] = dataProcurement['TYPE'] + '-' + dataProcurement['ORDER'].astype(str) + '-' + dataProcurement['LINE'].astype(str)

        dataProcurement = dataProcurement.rename({'TYPE':'ORDER TYPE', 'ORDER':'ORDER NUMBER', 'LINE':'ORDER LINE', 'ORDER CREATED DATE':'CREATED DATE'}, axis=1)
        dataProcurement.drop(columns=['PN'], inplace=True)

        dataProcurement['CREATED DATE'] = pd.to_datetime(dataProcurement['CREATED DATE'], errors='coerce', format='%Y-%m-%d')

        dataProcurement['ETA'] = pd.to_datetime(dataProcurement['ETA'], errors='coerce', format='%Y-%m-%d')

        dataProcurement.rename({'TYPE':'ORDER TYPE', 'ORDER':'ORDER NUMBER', 'LINE':'ORDER LINE', 'ORDER CREATED DATE':'CREATED DATE', 'PN':'ORDER PN'}, axis=1, inplace=True)

        # Pengolahan data Shipment
        # Mengolah data Shipment Tab PLB Monitoring
        dataShipmentRaw_4 = dataShipmentRaw_3[['ORDER TYPE', 'ORDER NUMBER', 'PN', 'AWB', 'PICK UP DATE', 'PART STATUS']]
        dataShipmentRaw_4 = dataShipmentRaw_4.rename({'AWB':'AWB/BL NUMBER', 'PICK UP DATE':'DELIVERY DATE', 'PART STATUS':'STATUS NEW'}, axis=1)
        dataShipmentRaw_4['ORDER_TYPE-NUMBER-PN'] = dataShipmentRaw_4['ORDER TYPE'] + '-' + dataShipmentRaw_4['ORDER NUMBER'].astype(str)+ '-' + dataShipmentRaw_4['PN'].astype(str)
        dataShipmentRaw_4.set_index(['ORDER_TYPE-NUMBER-PN'], inplace=True)
        dataShipmentRaw_4['ORDER_TYPE-NUMBER-PN'] = dataShipmentRaw_4['ORDER TYPE'] + '-' + dataShipmentRaw_4['ORDER NUMBER'].astype(str)+ '-' + dataShipmentRaw_4['PN'].astype(str)

        #dataShipmentRaw_4['DELIVERY DATE'] = pd.to_datetime(dataShipmentRaw_4['DELIVERY DATE'], format="%d/%m/%Y", errors="ignore").astype('str')

        progress_var.set(20)
        root.update_idletasks()
        def swap_day_month(date):
            if isinstance(date, datetime):
                # Swap day and month
                return datetime(date.year, date.day, date.month, date.hour, date.minute, date.second)
            return date  # Return the string unchanged

        swapped_data = [swap_day_month(d) for d in dataShipmentRaw_4['DELIVERY DATE']]

        dataShipmentRaw_4['DELIVERY DATE'] = swapped_data


        dataShipmentRaw_4['DELIVERY DATE'] = pd.to_datetime(dataShipmentRaw_4['DELIVERY DATE'], errors="coerce", dayfirst=False)
        dataShipmentRaw_4['DELIVERY DATE'] = dataShipmentRaw_4['DELIVERY DATE'].dt.strftime('%Y-%m-%d')
        dataShipmentRaw_4['DELIVERY DATE']= pd.to_datetime(dataShipmentRaw_4['DELIVERY DATE'], errors='ignore')

        #dataShipmentRaw_4['DELIVERY DATE'] = pd.to_datetime(dataShipmentRaw_4['DELIVERY DATE'], errors='coerce', format='%d/%m/%Y')
        #dataShipmentRaw_4['DELIVERY DATE'] = pd.to_datetime(dataShipmentRaw_4['DELIVERY DATE'], errors='coerce')
         # Convert to datetime, handle errors
        #dataShipmentRaw_4['DELIVERY DATE'] = dataShipmentRaw_4['DELIVERY DATE'].dt.strftime('%Y-%m-%d')

        # Mengolah data ShipmentRaw
        dataShipmentRaw = dataShipmentRaw[['ORDER TYPE', 'ORDER NUMBER', 'PN', 'AWB/BL NUMBER', 'DELIVERY DATE', 'STATUS NEW']]
        dataShipmentRaw['ORDER_TYPE-NUMBER-PN'] = dataShipmentRaw['ORDER TYPE'] + '-' + dataShipmentRaw['ORDER NUMBER'].astype(str)+ '-' + dataShipmentRaw['PN'].astype(str)
        dataShipmentRaw.set_index(['ORDER_TYPE-NUMBER-PN'], inplace=True)
        dataShipmentRaw['ORDER_TYPE-NUMBER-PN'] = dataShipmentRaw['ORDER TYPE'] + '-' + dataShipmentRaw['ORDER NUMBER'].astype(str)+ '-' + dataShipmentRaw['PN'].astype(str)

        dataShipment = pd.concat([dataShipmentRaw, dataShipmentRaw_4])

        # Mengolah data Shipment Merged
        dataShipment.rename({'STATUS NEW':'STATUS', 'DELIVERY DATE':'DATE AWB OUT'}, axis=1, inplace=True)
        dataShipment2 = dataShipment
        dataShipment2 = dataShipment2[['ORDER TYPE', 'ORDER NUMBER', 'PN', 'DATE AWB OUT', 'AWB/BL NUMBER', 'STATUS']]
        dataShipment2['ORDER_TYPE-NUMBER-PN'] = dataShipment2['ORDER TYPE'] + '-' + dataShipment2['ORDER NUMBER'].astype(str)+ '-' + dataShipment2['PN'].astype(str)
        dataShipment2 = dataShipment2.set_index('ORDER_TYPE-NUMBER-PN')
        dataShipment2['ORDER_TYPE-NUMBER-PN'] = dataShipment2['ORDER TYPE'] + '-' + dataShipment2['ORDER NUMBER'].astype(str)+ '-' + dataShipment2['PN'].astype(str)
        progress_var.set(40)
        root.update_idletasks()
        # Merging Data BATMIS & Procurement
        dataMerge = dataBatmisProcessed.merge(dataProcurement, how='left', left_index=True, right_index=True)
        dataMerge.reset_index(inplace=True)
        dataMerge.set_index('ORDER_TYPE-NUMBER-PN', inplace=True)
        dataMerge['ORDER_TYPE-NUMBER-PN'] = dataMerge['ORDER TYPE_x'] + '-' + dataMerge['ORDER NUMBER_x'].astype(str)+ '-' + dataMerge['ORDER PN'].astype(str)

        # Merging DataMerge dengan data Shipment
        dataMergeAll = dataMerge.merge(dataShipment2, how='left', left_index=True, right_index=True)

        dataMergeAll['DATE AWB OUT_x'] = dataMergeAll['DATE AWB OUT_y'].fillna(dataMergeAll['DATE AWB OUT_x'])
        dataMergeAll['AWB IN NUMBER'] = dataMergeAll['AWB/BL NUMBER'].fillna(dataMergeAll['AWB IN NUMBER'])
        # Pengolahan data MergeAllFiltered dan export data Merged

        dataMergeAllFiltered = dataMergeAll[[
             'ORDER_TYPE-NUMBER-LINE', 'REQUISITION', 'ORDER TYPE_x', 'ORDER NUMBER_x', 'ORDER LINE_x', 'STATUS_x', 'CREATED DATE_x',
             'DATE AWB OUT_x', 'AUTHORIZATION_DATE', 'AUTHRQ_DATE', 'AUTHRQ_BY', 'ORDER PN', 'PN DESCRIPTION', 'GRB_HISTORY',
             'QTY', 'QTY_RCVD', 'UOM', 'AWB IN NUMBER', 'AWB/BL NUMBER', 'RRP_DATE', 'RRP_BY', 'NAME_RRPBY', 'ETA', 'STANDARD STATUS', 'GENERAL STATUS', 'STATUS_y']]

        dataMergeAllFiltered.reset_index(drop=True,inplace=True)

        # Menyeragamkan tanggal menjadi Y-m-d
        def convert_date_format(date_str):
            if pd.isna(date_str):
                return date_str
            try:
                date_obj = pd.to_datetime(date_str, format='%d-%b-%y')
                return date_obj.strftime('%d-%m-%y')
            except ValueError:
                return date_str

        def convert_date_format2(date_str):
            if pd.isna(date_str):
                return date_str
            try:
                date_obj = pd.to_datetime(date_str, format='%d-%m-%y')
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                return date_str

        dataMergeAllFiltered['DATE AWB OUT_x'] = dataMergeAllFiltered['DATE AWB OUT_x'].apply(convert_date_format)
        dataMergeAllFiltered['DATE AWB OUT_x'] = dataMergeAllFiltered['DATE AWB OUT_x'].apply(convert_date_format2)

        dataMergeAllFiltered['AUTHORIZATION_DATE'] = dataMergeAllFiltered['AUTHORIZATION_DATE'].apply(convert_date_format)
        dataMergeAllFiltered['AUTHORIZATION_DATE'] = dataMergeAllFiltered['AUTHORIZATION_DATE'].apply(convert_date_format2)

        dataMergeAllFiltered['AUTHRQ_DATE'] = dataMergeAllFiltered['AUTHRQ_DATE'].apply(convert_date_format)
        dataMergeAllFiltered['AUTHRQ_DATE'] = dataMergeAllFiltered['AUTHRQ_DATE'].apply(convert_date_format2)

        dataMergeAllFiltered['RRP_DATE'] = dataMergeAllFiltered['RRP_DATE'].apply(convert_date_format)
        dataMergeAllFiltered['RRP_DATE'] = dataMergeAllFiltered['RRP_DATE'].apply(convert_date_format2)

        
        #dataMergeAllFiltered['CREATED DATE_x'] = pd.to_datetime(dataMergeAllFiltered['CREATED DATE_x'], errors='coerce', format='%d/%m/%Y')
        dataMergeAllFiltered['CREATED DATE_x'] = dataMergeAllFiltered['CREATED DATE_x'].apply(convert_date_format2)
        # prompt: Create a function to check the feature 'RRP DATE' in file 'dataMerge.xlsx' in sheet 'Sheet 1' according to the quartile of the day. I would like 3 quartiles of the day, day 1-10 (named Q1), 11-20 (named Q2), and 21-30 (named Q3). Then apply the function to the dataframe in a new column 'Quartile' with the formula YYYY-MM-Quartile, so for example 5 March 2025 the data in the column 'Quartile' would be 2025-03-Q1
        progress_var.set(60)
        root.update_idletasks()
        # Assigning quartile to created Date
        def assign_quartile_created(date_str):
            try:
                date_obj = pd.to_datetime(date_str)
                day = date_obj.day
                year = date_obj.year
                month = date_obj.month
                if 1 <= day <= 10:
                    return f"{year}-{month:02}-Q1"
                elif 11 <= day <= 20:
                    return f"{year}-{month:02}-Q2"
                elif 21 <= day <= 31:
                    return f"{year}-{month:02}-Q3"
                else:
                    return "Invalid Date"
            except (ValueError, TypeError):
                return "Invalid Date"

        def assign_quartile_rrp(date_str):
            try:
                date_obj = pd.to_datetime(date_str)
                day = date_obj.day
                year = date_obj.year
                month = date_obj.month
                if 1 <= day <= 10:
                    return f"{year}-{month:02}-Q1"
                elif 11 <= day <= 20:
                    return f"{year}-{month:02}-Q2"
                elif 21 <= day <= 31:
                    return f"{year}-{month:02}-Q3"
                else:
                    return "Invalid Date"
            except (ValueError, TypeError):
                return "Invalid Date"

        dataMergeAllFiltered['Quartile_RRP'] = dataMergeAllFiltered['RRP_DATE'].apply(assign_quartile_rrp)
        dataMergeAllFiltered['Quartile_Shipped'] = dataMergeAllFiltered['DATE AWB OUT_x'].apply(assign_quartile_rrp)
        dataMergeAllFiltered['Quartile_Created'] = dataMergeAllFiltered['CREATED DATE_x'].apply(assign_quartile_created)
        dataMergeAllFiltered['Date_Shipped'] = dataMergeAllFiltered['DATE AWB OUT_x'].fillna('Invalid Date')

        dataMergeAllFiltered.drop_duplicates(subset=['ORDER_TYPE-NUMBER-LINE'], inplace=True, keep='last')

        oldNewDate = pd.to_datetime(dataMergeAllFiltered['CREATED DATE_x'], errors='coerce')
        progress_var.set(80)
        root.update_idletasks()
        oldestDate = oldNewDate.min()
        oldestDate = oldestDate.strftime('%Y-%m-%d')
        newestDate = oldNewDate.max()
        newestDate = newestDate.strftime('%Y-%m-%d') # DENSUU

        dataMergeAllFiltered.to_excel('PROCESSED DATA_%s_%s.xlsx' %(oldestDate, newestDate), index=False)
        dataMergeAllFiltered.to_excel('[IGNORE]TEMP FILE.xlsx', index=False)
 
        # return dataMergeAllFiltered, oldestDate, newestDate
        progress_var.set(100)
        messagebox.showinfo("Sukses", "Proses merge selesai! File disimpan sebagai PROCESSED DATA_%s_%s.xlsx"  %(oldestDate, newestDate))

    except Exception as e:
        messagebox.showerror("Error", f"Terjadi kesalahan saat memproses merge data: {e}")

def run_merge():
    file_shipment = entry_shipment.get()
    file_batmis = entry_batmis.get()
    file_procurement = entry_procurement.get()
    if file_shipment and file_batmis and file_procurement:
        progress_var.set(0)
        process_merge_data(file_shipment, file_batmis, file_procurement, progress_var, root)
    else:
        messagebox.showerror("Error", "Harap pilih semua file terlebih dahulu.")

def run_pivot():
    try:

        progress_var2.set(10)
        root.update_idletasks()
        dataMergeAllFiltered = pd.read_excel("[IGNORE]TEMP FILE.xlsx")
        ## --- Beginning of pivotCreated_RRP --- 
        pivotCreated_RRP = dataMergeAllFiltered.pivot_table(index='Quartile_Created', columns='Quartile_RRP', values='ORDER_TYPE-NUMBER-LINE', aggfunc='count')

        cancelCountCreated_RRP = dataMergeAllFiltered[
            (dataMergeAllFiltered['Quartile_RRP'].notna()) &
            (dataMergeAllFiltered['Quartile_RRP'] != '') &
            (dataMergeAllFiltered['STATUS_x'] == 'CANCEL')
        ].groupby('Quartile_Created')['ORDER_TYPE-NUMBER-LINE'].count()
        pivotCreated_RRP.insert(0, 'Cancelled', value = cancelCountCreated_RRP)

        totalCountCreated_RRP = dataMergeAllFiltered[
            (dataMergeAllFiltered['Quartile_RRP'].notna()) &
            (dataMergeAllFiltered['Quartile_RRP'] != '') &
            (dataMergeAllFiltered['STATUS_x'] != 'CANCEL')
        ].groupby('Quartile_Created')['ORDER_TYPE-NUMBER-LINE'].count()
        pivotCreated_RRP.insert(0, 'Beginning Balance', value = totalCountCreated_RRP)

        nfDateCreated_RRP = dataMergeAllFiltered[
            (dataMergeAllFiltered['Quartile_RRP'].isna() | (dataMergeAllFiltered['Quartile_RRP'] == 'Invalid Date')) &
            (dataMergeAllFiltered['STATUS_x'] != 'CANCEL')
        ].groupby('Quartile_Created')['ORDER_TYPE-NUMBER-LINE'].count()
        pivotCreated_RRP.insert(2, 'Part Not Yet Received', value = nfDateCreated_RRP)

        pivotCreated_RRP.drop(columns='Invalid Date', inplace=True)
        
        # Add MultiIndex as Header of Header
        pivotCreated_RRP = pivotCreated_RRP.rename_axis(None, axis=1)
        new_columns = []

        for col in pivotCreated_RRP.columns:
            if col != 'Beginning Balance' and col != 'Cancelled' and col != 'Part Not Yet Received':
                new_columns.append(('Received Date', col))
            else:
              new_columns.append(('Status', col))

        pivotCreated_RRP.columns = pd.MultiIndex.from_tuples(new_columns)
        ## --- End of pivotCreated_RRP --- 
        progress_var2.set(20)
        root.update_idletasks()
        ## --- Beginning of pivotCreated_Shipment --- 

        pivotCreated_Shipment = dataMergeAllFiltered.pivot_table(index='Quartile_Created', columns='Date_Shipped', values='ORDER_TYPE-NUMBER-LINE', aggfunc='count')
        pivotCreated_Shipment = pivotCreated_Shipment.sort_index(axis=1)

        cancelCountCreated_Shipment = dataMergeAllFiltered[
            (dataMergeAllFiltered['Date_Shipped'].notna()) &
            (dataMergeAllFiltered['Date_Shipped'] != '') &
            (dataMergeAllFiltered['STATUS_x'] == 'CANCEL')
        ].groupby('Quartile_Created')['ORDER_TYPE-NUMBER-LINE'].count()
        pivotCreated_Shipment.insert(0, 'Cancelled', value = cancelCountCreated_Shipment)

        totalCountCreated_Shipment = dataMergeAllFiltered[
            (dataMergeAllFiltered['Date_Shipped'].notna()) &
            (dataMergeAllFiltered['Date_Shipped'] != '') &
            (dataMergeAllFiltered['STATUS_x'] != 'CANCEL')
        ].groupby('Quartile_Created')['ORDER_TYPE-NUMBER-LINE'].count()
        pivotCreated_Shipment.insert(0, 'Beginning Balance', value = totalCountCreated_Shipment)

        nfDateCreated_Shipment = dataMergeAllFiltered[
            (dataMergeAllFiltered['Date_Shipped'].isna() | (dataMergeAllFiltered['Date_Shipped'] == 'Invalid Date')) &
            (dataMergeAllFiltered['STATUS_x'] != 'CANCEL')
        ].groupby('Quartile_Created')['ORDER_TYPE-NUMBER-LINE'].count()
        pivotCreated_Shipment.insert(2, 'Part Not Yet Received', value = nfDateCreated_Shipment)

        pivotCreated_Shipment.drop(columns='Invalid Date', inplace=True)


        pivotCreated_Shipment = pivotCreated_Shipment.rename_axis(None, axis=1)
        new_columns = []

        for col in pivotCreated_Shipment.columns:
            if col != 'Beginning Balance' and col != 'Cancelled' and col != 'Part Not Yet Received':
                new_columns.append(('Received Date', col))
            else:
              new_columns.append(('Status', col))

        # pivotCreated_Shipment = pivotCreated_Shipment
        pivotCreated_Shipment.columns = pd.MultiIndex.from_tuples(new_columns)
        

        ## --- End of  pivotCreated_Shipment --- 
        progress_var2.set(40)
        root.update_idletasks()
        ## --- Beginning of  pivotCreated_ShipmentQ --- 

        pivotCreated_ShipmentQ = dataMergeAllFiltered.pivot_table(index='Quartile_Created', columns='Quartile_Shipped', values='ORDER_TYPE-NUMBER-LINE', aggfunc='count')

        cancelCountCreated_ShipmentQ = dataMergeAllFiltered[
            (dataMergeAllFiltered['Quartile_Shipped'].notna()) &
            (dataMergeAllFiltered['Quartile_Shipped'] != '') &
            (dataMergeAllFiltered['STATUS_x'] == 'CANCEL')
        ].groupby('Quartile_Created')['ORDER_TYPE-NUMBER-LINE'].count()
        pivotCreated_ShipmentQ.insert(0, 'Cancelled', value = cancelCountCreated_ShipmentQ)

        totalCountCreated_ShipmentQ = dataMergeAllFiltered[
            (dataMergeAllFiltered['Quartile_Shipped'].notna()) &
            (dataMergeAllFiltered['Quartile_Shipped'] != '') &
            (dataMergeAllFiltered['STATUS_x'] != 'CANCEL')
        ].groupby('Quartile_Created')['ORDER_TYPE-NUMBER-LINE'].count()
        pivotCreated_ShipmentQ.insert(0, 'Beginning Balance', value = totalCountCreated_ShipmentQ)

        nfDateCreated_ShipmentQ = dataMergeAllFiltered[
            (dataMergeAllFiltered['Quartile_Shipped'].isna() | (dataMergeAllFiltered['Quartile_Shipped'] == 'Invalid Date')) &
            (dataMergeAllFiltered['STATUS_x'] != 'CANCEL')
        ].groupby('Quartile_Created')['ORDER_TYPE-NUMBER-LINE'].count()
        pivotCreated_ShipmentQ.insert(2, 'Part Not Yet Received', value = nfDateCreated_ShipmentQ)

        pivotCreated_ShipmentQ.drop(columns='Invalid Date', inplace=True)

        # Add MultiIndex as Header of Header
        pivotCreated_ShipmentQ = pivotCreated_ShipmentQ.rename_axis(None, axis=1)
        new_columns = []

        for col in pivotCreated_ShipmentQ.columns:
            if col != 'Beginning Balance' and col != 'Cancelled' and col != 'Part Not Yet Received':
                new_columns.append(('Received Date', col))
            else:
              new_columns.append(('Status', col))

        pivotCreated_ShipmentQ.columns = pd.MultiIndex.from_tuples(new_columns)

        ## --- End of  pivotCreated_ShipmentQ --- 
        progress_var2.set(60)
        root.update_idletasks()
        
        oldNewDate = pd.to_datetime(dataMergeAllFiltered['CREATED DATE_x'], errors='coerce')
        oldestDate = oldNewDate.min()
        oldestDate = oldestDate.strftime('%Y-%m-%d')
        newestDate = oldNewDate.max()
        newestDate = newestDate.strftime('%Y-%m-%d')

        progress_var2.set(80)
        root.update_idletasks()
        with pd.ExcelWriter('TIMETABLE ORDER_%s_%s.xlsx' %(oldestDate,newestDate), engine='xlsxwriter') as writer:
            pivotCreated_RRP.to_excel(writer, sheet_name='Timeline RRP Table', index=True)
            pivotCreated_Shipment.to_excel(writer, sheet_name='Shipment Movement (Per Date)', index=True)
            pivotCreated_ShipmentQ.to_excel(writer, sheet_name='Shipment Movement (Per Q)', index=True)
        progress_var2.set(100)
        
        messagebox.showinfo("Sukses", "Proses pivot selesai! File disimpan sebagai TIMETABLE ORDER_%s_%s.xlsx" %(oldestDate,newestDate))
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi kesalahan saat memproses pivot data: {e}")

def reset_fields():
    entry_shipment.delete(0, tk.END)
    entry_batmis.delete(0, tk.END)
    entry_procurement.delete(0, tk.END)
    progress_var.set(0)
    progress_var2.set(0)

root = tk.Tk()
root.title("PO Data Processing App")

# Tombol Tutorial
tutorial_button  = tk.Button(root, text="Tutorial", command=show_tutorial, padx=10, pady=5)
tutorial_button.place(relx=1.0, y=10, anchor="ne", x=-10)
# Load image logo
logo_image = Image.open('LOGO-LION-AIR.png')  # Make sure the logo is in the same directory as the script
logo_image = logo_image.resize((175, 50), Image.LANCZOS)  # Resize the image if needed
logo_photo = ImageTk.PhotoImage(logo_image)

# Add logo at the top of the window
logo_label = tk.Label(root, image=logo_photo)
logo_label.pack(pady=10)

# Frame container with padding
frame = tk.Frame(root, padx=10, pady=10)
frame.pack(pady=10)

progress_var = tk.IntVar()
progress_var2 = tk.IntVar()

# Labels and Entry fields with padding
tk.Label(frame, text="File Shipment (excel) :").grid(row=0, column=0, padx=5, pady=5)
entry_shipment = tk.Entry(frame, width=50)
entry_shipment.grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame, text="Browse", command=lambda: browse_file(entry_shipment)).grid(row=0, column=2, padx=5, pady=5)

tk.Label(frame, text="File Batmis (csv delimeter titik koma ';') :").grid(row=1, column=0, padx=5, pady=5)
entry_batmis = tk.Entry(frame, width=50)
entry_batmis.grid(row=1, column=1, padx=5, pady=5)
tk.Button(frame, text="Browse", command=lambda: browse_file(entry_batmis)).grid(row=1, column=2, padx=5, pady=5)

tk.Label(frame, text="File Procurement (excel) :").grid(row=2, column=0, padx=5, pady=5)
entry_procurement = tk.Entry(frame, width=50)
entry_procurement.grid(row=2, column=1, padx=5, pady=5)
tk.Button(frame, text="Browse", command=lambda: browse_file(entry_procurement)).grid(row=2, column=2, padx=5, pady=5)

# Buttons with padding
tk.Button(root, text="Submit & Process Merge Data", command=run_merge, padx=10, pady=5).pack(pady=10)
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=300)
progress_bar.pack(pady=5)

tk.Button(root, text="Process Pivot Data", command=run_pivot, padx=10, pady=5).pack(pady=10)
progress_bar2 = ttk.Progressbar(root, variable=progress_var2, maximum=100, length=300)
progress_bar2.pack(pady=5)

# Reset Button with padding
tk.Button(root, text="Reset", command=reset_fields, padx=10, pady=5).pack(pady=10)

root.mainloop()
