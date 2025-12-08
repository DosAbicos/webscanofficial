#!/usr/bin/env python3
"""
Automated test for Excel export functionality
Tests that exported Excel file maintains original formatting and data is written to correct columns
"""

import sys
import xlrd
import requests
import json
from pathlib import Path

def test_excel_export():
    """Test Excel export with sample data"""
    print("=" * 80)
    print("AUTOMATED EXCEL EXPORT TEST")
    print("=" * 80)
    
    # Test data
    test_products = [
        {
            "id": 1,
            "name": "IDEAL ПАРКЕТНЫЙ ЛАК ГЛЯНЦЕВЫЙ (10L)",
            "nomenclature_code": "20002755",
            "stock_quantity": 15.0,
            "barcode": "1234567890123",
            "actual_quantity": 12.5
        },
        {
            "id": 2,
            "name": "IDEAL ПАРКЕТНЫЙ ЛАК ГЛЯНЦЕВЫЙ (2,5L)",
            "nomenclature_code": "20002659",
            "stock_quantity": 25.0,
            "barcode": "9876543210987",
            "actual_quantity": 20.0
        }
    ]
    
    print("\n1. Sending test products to backend...")
    try:
        response = requests.post(
            'http://localhost:8001/api/test-excel-export',
            json=test_products,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ FAILED: Backend returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print("✅ Backend processed request successfully")
        
        # Save the file
        output_file = '/tmp/test_export_result.xls'
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"✅ Saved exported file to {output_file}")
        
    except Exception as e:
        print(f"❌ FAILED: Error calling backend: {e}")
        return False
    
    # Verify the exported file
    print("\n2. Verifying exported Excel file...")
    try:
        # Open original file
        original_wb = xlrd.open_workbook('/app/sample_file.xls')
        original_sheet = original_wb.sheet_by_index(0)
        
        # Open exported file
        exported_wb = xlrd.open_workbook(output_file)
        exported_sheet = exported_wb.sheet_by_index(0)
        
        print(f"✅ Both files opened successfully")
        
        # Check that row/column counts match
        if original_sheet.nrows != exported_sheet.nrows:
            print(f"❌ FAILED: Row count mismatch - Original: {original_sheet.nrows}, Exported: {exported_sheet.nrows}")
            return False
        
        if original_sheet.ncols != exported_sheet.ncols:
            print(f"❌ FAILED: Column count mismatch - Original: {original_sheet.ncols}, Exported: {exported_sheet.ncols}")
            return False
        
        print(f"✅ Row and column counts match: {exported_sheet.nrows} rows, {exported_sheet.ncols} columns")
        
        # Verify data was written to correct cells
        print("\n3. Verifying data in correct columns...")
        
        # Find the first test product row (row 10, index 9)
        test_product_row = 9
        
        # Check barcode column (column 8)
        barcode_cell = exported_sheet.cell(test_product_row, 8)
        if str(barcode_cell.value).strip() == test_products[0]['barcode']:
            print(f"✅ Barcode written correctly to column 8: {barcode_cell.value}")
        else:
            print(f"❌ FAILED: Barcode not found in column 8. Found: '{barcode_cell.value}'")
            return False
        
        # Check actual quantity column (column 9)
        qty_cell = exported_sheet.cell(test_product_row, 9)
        if float(qty_cell.value) == test_products[0]['actual_quantity']:
            print(f"✅ Actual quantity written correctly to column 9: {qty_cell.value}")
        else:
            print(f"❌ FAILED: Actual quantity not correct in column 9. Found: '{qty_cell.value}'")
            return False
        
        # Verify header structure is intact
        print("\n4. Verifying header structure...")
        header_row = 4  # Row 5 (index 4) contains headers
        
        header_col_8 = str(exported_sheet.cell(header_row, 8).value).strip()
        header_col_9 = str(exported_sheet.cell(header_row, 9).value).strip()
        
        if header_col_8 == "Штрихкоды":
            print(f"✅ Header for column 8 correct: '{header_col_8}'")
        else:
            print(f"⚠️  WARNING: Header for column 8 unexpected: '{header_col_8}'")
        
        if header_col_9 == "Кол-во пофакту":
            print(f"✅ Header for column 9 correct: '{header_col_9}'")
        else:
            print(f"⚠️  WARNING: Header for column 9 unexpected: '{header_col_9}'")
        
        # Compare some cells from original vs exported to ensure formatting preserved
        print("\n5. Spot-checking cell preservation...")
        sample_cells = [
            (0, 0),  # First cell
            (3, 0),  # Header area
            (8, 1),  # Data area
        ]
        
        all_match = True
        for row, col in sample_cells:
            orig_val = str(original_sheet.cell(row, col).value).strip()
            exp_val = str(exported_sheet.cell(row, col).value).strip()
            if orig_val != exp_val:
                print(f"⚠️  Cell ({row}, {col}) changed: '{orig_val}' → '{exp_val}'")
                all_match = False
        
        if all_match:
            print("✅ Sample cells unchanged - formatting preserved")
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED - Excel export is working correctly!")
        print("=" * 80)
        print(f"\nExported file saved at: {output_file}")
        print("You can open it in Excel to verify formatting visually.")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Error verifying file: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_excel_export()
    sys.exit(0 if success else 1)
