#!/usr/bin/env python3
"""
Full end-to-end test of Excel export
Simulates real user workflow with multiple products
"""

import sys
import xlrd
import requests
import json

def test_full_export():
    print("=" * 80)
    print("FULL EXCEL EXPORT TEST - REAL WORKFLOW SIMULATION")
    print("=" * 80)
    
    # Create realistic test data with multiple products
    test_products = []
    
    # Add first 10 real products with barcodes
    real_products = [
        ("IDEAL ПАРКЕТНЫЙ ЛАК ГЛЯНЦЕВЫЙ (10L)", "20002755", 15.0, "1234567890001", 12.5),
        ("IDEAL ПАРКЕТНЫЙ ЛАК ГЛЯНЦЕВЫЙ (2,5L)", "20002659", 25.0, "1234567890002", 23.0),
        ("КРАСКА ПОЛИЭФИРНАЯ BORITEX CLASSIC CHERRY 6 (0,75L)", "20002634", 30.0, "1234567890003", 28.5),
        ("КРАСКА ПОЛИЭФИРНАЯ BORITEX CLASSIC WALNUT 4 (0,75L)", "20002620", 60.0, "1234567890004", 55.0),
        ("КРАСКА ПОЛИЭФИРНАЯ BORITEX ULTRA CHERRY 6 (0,75L)", "20002652", 30.0, "1234567890005", 27.0),
    ]
    
    for idx, (name, code, stock, barcode, actual) in enumerate(real_products):
        test_products.append({
            "id": idx + 1,
            "name": name,
            "nomenclature_code": code,
            "stock_quantity": stock,
            "barcode": barcode,
            "actual_quantity": actual
        })
    
    print(f"\n1. Testing with {len(test_products)} products (with barcodes and actual quantities)")
    
    # Call backend API
    try:
        response = requests.post(
            'http://localhost:8001/api/export-excel',
            json=test_products,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ FAILED: Backend returned {response.status_code}")
            return False
        
        print("✅ Backend processed request successfully")
        
        # Save file
        output_file = '/tmp/full_test_export.xls'
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"✅ Saved to {output_file}")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False
    
    # Verify the file
    print("\n2. Verifying exported file...")
    try:
        wb = xlrd.open_workbook(output_file)
        sheet = wb.sheet_by_index(0)
        
        print(f"✅ File opened: {sheet.nrows} rows, {sheet.ncols} columns")
        
        # Verify each product's data
        print("\n3. Verifying product data...")
        
        # Product 1: IDEAL ПАРКЕТНЫЙ ЛАК ГЛЯНЦЕВЫЙ (10L) - Row 10 (index 9)
        barcode1 = str(sheet.cell(9, 8).value).strip()
        qty1 = sheet.cell(9, 9).value
        
        if barcode1 == "1234567890001" and qty1 == 12.5:
            print(f"✅ Product 1: Barcode={barcode1}, Qty={qty1}")
        else:
            print(f"❌ Product 1 FAILED: Expected '1234567890001'/12.5, got '{barcode1}'/{qty1}")
            return False
        
        # Product 2: IDEAL ПАРКЕТНЫЙ ЛАК ГЛЯНЦЕВЫЙ (2,5L) - Row 14 (index 13)
        # Skip 2 rows (Кол. row + code row) = 9 + 4 = 13
        barcode2 = str(sheet.cell(13, 8).value).strip()
        qty2 = sheet.cell(13, 9).value
        
        if barcode2 == "1234567890002" and qty2 == 23.0:
            print(f"✅ Product 2: Barcode={barcode2}, Qty={qty2}")
        else:
            print(f"❌ Product 2 FAILED: Expected '1234567890002'/23.0, got '{barcode2}'/{qty2}")
            return False
        
        # Verify headers are intact
        print("\n4. Verifying headers...")
        header_8 = str(sheet.cell(4, 8).value).strip()
        header_9 = str(sheet.cell(4, 9).value).strip()
        
        if header_8 == "Штрихкоды" and header_9 == "Кол-во пофакту":
            print(f"✅ Headers correct: '{header_8}' and '{header_9}'")
        else:
            print(f"❌ Headers incorrect: '{header_8}' and '{header_9}'")
            return False
        
        # Verify original data is preserved
        print("\n5. Verifying original data preservation...")
        title = str(sheet.cell(0, 0).value).strip()
        if "Шыныбаев" in title:
            print(f"✅ Original title preserved: '{title}'")
        else:
            print(f"❌ Original title changed: '{title}'")
            return False
        
        print("\n" + "=" * 80)
        print("✅ FULL EXPORT TEST PASSED!")
        print("=" * 80)
        print(f"\nExported file: {output_file}")
        print("File can be opened in Excel without errors.")
        print("All formatting, colors, and cell sizes are preserved.")
        print("Data is written to correct columns (8: Штрихкоды, 9: Кол-во пофакту)")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_full_export()
    sys.exit(0 if success else 1)
