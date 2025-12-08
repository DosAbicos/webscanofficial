import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Html5Qrcode } from 'html5-qrcode';
import { ArrowLeft, Camera, CameraOff, Save, Search, Loader2, Package } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { toast } from 'sonner';
import { searchProducts, updateProductBarcode, db, initializeDatabase } from '../lib/db';
import { loadExcelFile } from '../lib/excelLoader';

export const ScannerPage = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1); // 1: scanning, 2: search product, 3: enter quantity
  const [isScanning, setIsScanning] = useState(false);
  const [scannedBarcode, setScannedBarcode] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [actualQuantity, setActualQuantity] = useState('');
  const [dbLoading, setDbLoading] = useState(true);
  const scannerRef = useRef(null);
  const html5QrCodeRef = useRef(null);

  useEffect(() => {
    initDB();
    
    // Check if we're coming from edit mode
    const editingProduct = sessionStorage.getItem('editingProduct');
    if (editingProduct) {
      try {
        const product = JSON.parse(editingProduct);
        setSelectedProduct(product);
        toast.info(`Пересканирование штрихкода для: ${product.name}`);
      } catch (error) {
        console.error('Error parsing editing product:', error);
      }
    }
    
    return () => {
      stopScanner();
    };
  }, []);

  const initDB = async () => {
    try {
      const count = await db.products.count();
      
      if (count === 0) {
        const productsData = await loadExcelFile();
        await initializeDatabase(productsData);
      }
      
      setDbLoading(false);
    } catch (error) {
      console.error('Error initializing database:', error);
      toast.error('Ошибка загрузки данных');
      setDbLoading(false);
    }
  };

  const startScanner = async () => {
    try {
      if (!html5QrCodeRef.current) {
        html5QrCodeRef.current = new Html5Qrcode('scanner-container');
      }

      const config = { fps: 10, qrbox: { width: 250, height: 250 } };
      
      await html5QrCodeRef.current.start(
        { facingMode: 'environment' },
        config,
        (decodedText) => {
          setScannedBarcode(decodedText);
          stopScanner();
          setStep(2); // Move to product search step
          toast.success('Штрихкод отсканирован!');
        },
        (errorMessage) => {
          // Ignore scan errors
        }
      );
      
      setIsScanning(true);
    } catch (error) {
      console.error('Error starting scanner:', error);
      toast.error('Не удалось запустить камеру');
    }
  };

  const stopScanner = async () => {
    try {
      if (html5QrCodeRef.current && html5QrCodeRef.current.isScanning) {
        await html5QrCodeRef.current.stop();
      }
      setIsScanning(false);
    } catch (error) {
      console.error('Error stopping scanner:', error);
    }
  };

  const handleSearch = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      const results = await searchProducts(query);
      setSearchResults(results);
    } catch (error) {
      toast.error('Ошибка поиска');
    }
  };

  useEffect(() => {
    if (step === 2 && searchQuery) {
      const debounceTimer = setTimeout(() => {
        handleSearch(searchQuery);
      }, 300);
      return () => clearTimeout(debounceTimer);
    }
  }, [searchQuery, step]);

  const handleProductSelect = (product) => {
    setSelectedProduct(product);
    setSearchResults([]);
    setSearchQuery('');
    setStep(3); // Move to quantity input step
  };

  const handleSave = async () => {
    if (!selectedProduct || !scannedBarcode) {
      toast.error('Выберите товар и отсканируйте штрихкод');
      return;
    }

    try {
      await updateProductBarcode(
        selectedProduct.id,
        scannedBarcode,
        actualQuantity ? parseFloat(actualQuantity) : null
      );
      toast.success('Данные сохранены');
      
      // Clear editing product from session storage
      sessionStorage.removeItem('editingProduct');
      
      // Check if we should return to home page (if coming from edit mode)
      const wasEditing = sessionStorage.getItem('editingProduct') !== null;
      
      // Reset form to step 1
      setScannedBarcode('');
      setSelectedProduct(null);
      setActualQuantity('');
      setStep(1);
      
      // If we were editing, go back to home page
      if (wasEditing) {
        navigate('/');
      }
    } catch (error) {
      toast.error('Ошибка сохранения');
    }
  };

  const handleReset = () => {
    setScannedBarcode('');
    setSelectedProduct(null);
    setActualQuantity('');
    setSearchQuery('');
    setSearchResults([]);
    setStep(1);
  };

  if (dbLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto" />
          <p className="text-lg font-medium text-muted-foreground">Загрузка данных...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pb-6">
      {/* Header */}
      <div className="sticky top-0 z-20 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80 border-b">
        <div className="flex items-center gap-3 p-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate('/')}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="text-xl font-bold">Сканер штрихкодов</h1>
        </div>
      </div>

      <div className="max-w-2xl mx-auto p-4 space-y-4">

        {/* Step 1: Scanner Section */}
        {step === 1 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Шаг 1: Сканирование штрихкода</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div
                id="scanner-container"
                ref={scannerRef}
                className="w-full aspect-square bg-black rounded-lg overflow-hidden"
              />
              
              <Button
                onClick={isScanning ? stopScanner : startScanner}
                className="w-full scan-button h-12"
              >
                {isScanning ? (
                  <>
                    <CameraOff className="h-5 w-5 mr-2" />
                    Остановить сканирование
                  </>
                ) : (
                  <>
                    <Camera className="h-5 w-5 mr-2" />
                    Начать сканирование
                  </>
                )}
              </Button>

              {scannedBarcode && (
                <div className="p-3 bg-success/10 border border-success/20 rounded-lg">
                  <p className="text-sm font-medium text-success">Отсканировано:</p>
                  <p className="text-lg font-mono mt-1">{scannedBarcode}</p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Step 2: Product Search */}
        {step === 2 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Шаг 2: Найдите товар</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {scannedBarcode && (
                <div className="p-3 bg-success/10 border border-success/20 rounded-lg mb-4">
                  <p className="text-sm font-medium text-success">Штрихкод:</p>
                  <p className="text-lg font-mono mt-1">{scannedBarcode}</p>
                </div>
              )}

              <Input
                placeholder="Введите название или номер накладной..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full"
                autoFocus
              />

              {searchResults.length > 0 && (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {searchResults.map((product) => (
                    <Card
                      key={product.id}
                      className="cursor-pointer hover:bg-accent/50 transition-colors"
                      onClick={() => handleProductSelect(product)}
                    >
                      <CardContent className="p-3">
                        <p className="font-medium text-sm line-clamp-1">{product.name}</p>
                        <div className="flex items-center gap-2 mt-1">
                          {product.nomenclature_code && (
                            <span className="text-xs text-muted-foreground">№ {product.nomenclature_code}</span>
                          )}
                          <Badge variant="secondary" className="text-xs">
                            {product.stock_quantity} шт
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}

              {searchQuery && searchResults.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <Package className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>Товары не найдены</p>
                </div>
              )}

              <Button
                onClick={handleReset}
                variant="outline"
                className="w-full"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Вернуться к сканированию
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Step 3: Quantity Input */}
        {step === 3 && selectedProduct && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Шаг 3: Количество по факту</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {scannedBarcode && (
                <div className="p-3 bg-success/10 border border-success/20 rounded-lg">
                  <p className="text-sm font-medium text-success">Штрихкод:</p>
                  <p className="text-lg font-mono mt-1">{scannedBarcode}</p>
                </div>
              )}

              <div className="p-4 bg-primary/5 border border-primary/20 rounded-lg">
                <p className="text-sm font-medium text-muted-foreground">Выбранный товар:</p>
                <p className="font-semibold mt-1">{selectedProduct.name}</p>
                {selectedProduct.nomenclature_code && (
                  <p className="text-sm text-muted-foreground mt-1">№ {selectedProduct.nomenclature_code}</p>
                )}
                <Badge variant="secondary" className="mt-2">
                  На складе: {selectedProduct.stock_quantity} шт
                </Badge>
              </div>

              <div>
                <label className="text-sm font-medium block mb-2">
                  Количество по факту <span className="text-muted-foreground">(опционально)</span>
                </label>
                <Input
                  type="number"
                  step="0.01"
                  placeholder="Введите количество"
                  value={actualQuantity}
                  onChange={(e) => setActualQuantity(e.target.value)}
                  autoFocus
                />
              </div>

              <div className="flex gap-2">
                <Button
                  onClick={() => setStep(2)}
                  variant="outline"
                  className="flex-1"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Назад
                </Button>
                <Button
                  onClick={handleSave}
                  className="flex-1 scan-button"
                >
                  <Save className="h-5 w-5 mr-2" />
                  Сохранить
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};