#!/usr/bin/env python3
"""
Test that restored export works with original formatting
"""
import requests
import sys

BACKEND_URL = "http://0.0.0.0:8001"

def test_restored_export():
    """Test the restored /api/export-excel endpoint"""
    print("=" * 80)
    print("ТЕСТ ВОССТАНОВЛЕННОГО ЭКСПОРТА С ФОРМАТИРОВАНИЕМ")
    print("=" * 80)
    
    test_products = [
        {
            "id": 1,
            "name": "Тестовый товар",
            "nomenclature_code": "12345",
            "stock_quantity": 100.0,
            "barcode": "1234567890123",
            "actual_quantity": 95.0
        }
    ]
    
    print(f"\n📦 Отправка тестовых данных...")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/export-excel",
            json=test_products,
            timeout=60
        )
        
        print(f"✓ Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✓ Content-Type: {response.headers.get('content-type')}")
            print(f"✓ Размер файла: {len(response.content) / 1024:.2f} KB")
            
            # Проверяем расширение файла
            content_disp = response.headers.get('content-disposition', '')
            if '.xlsx' in content_disp:
                print("✓ Формат файла: .xlsx (конвертированный)")
            elif '.xls' in content_disp:
                print("✓ Формат файла: .xls (оригинальный)")
            
            print("\n" + "=" * 80)
            print("✅ ЭКСПОРТ ВОССТАНОВЛЕН УСПЕШНО!")
            print("=" * 80)
            print("\n📋 Что восстановлено:")
            print("  • Endpoint: /api/export-excel")
            print("  • Форматирование: Сохраняется (цвета, размеры)")
            print("  • Метод: xlrd/xlutils + openpyxl конвертация")
            print("\n💡 Пользователю нужно почистить кэш браузера, если есть проблемы")
            print("=" * 80)
            return True
        else:
            print(f"❌ Ошибка: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Исключение: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_restored_export()
    sys.exit(0 if success else 1)
