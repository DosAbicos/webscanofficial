import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Download, Barcode, Package, Loader2 } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { toast, Toaster } from 'sonner';
import { ProductList } from './components/ProductList';
import { ScannerPage } from './components/ScannerPage';
import { db, initializeDatabase, getAllProducts, getProductsWithoutBarcode, getProductsWithBarcode } from './lib/db';
import { loadExcelFile } from './lib/excelLoader';
import { exportToExcel } from './lib/excelExport';

const Home = () => {
  const [loading, setLoading] = useState(true);
  const [products, setProducts] = useState([]);
  const [withoutBarcode, setWithoutBarcode] = useState([]);
  const [withBarcode, setWithBarcode] = useState([]);
  const [activeTab, setActiveTab] = useState('without');

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      setLoading(true);
      
      // Check if database already has data
      const count = await db.products.count();
      
      if (count === 0) {
        // Load Excel file and initialize database
        const productsData = await loadExcelFile();
        await initializeDatabase(productsData);
        toast.success(`Загружено ${productsData.length} товаров`);
      }
      
      // Load products from database
      await loadProducts();
    } catch (error) {
      console.error('Error initializing app:', error);
      toast.error('Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  const loadProducts = async () => {
    try {
      const all = await getAllProducts();
      const without = await getProductsWithoutBarcode();
      const withB = await getProductsWithBarcode();
      
      setProducts(all);
      setWithoutBarcode(without);
      setWithBarcode(withB);
    } catch (error) {
      console.error('Error loading products:', error);
    }
  };

  const handleExport = async () => {
    try {
      // Export only products with barcodes
      const productsWithBarcodes = await getProductsWithBarcode();
      
      if (productsWithBarcodes.length === 0) {
        toast.error('Нет товаров со штрихкодами для экспорта');
        return;
      }
      
      toast.info('Экспорт начат...');
      await exportToExcel(productsWithBarcodes);
      toast.success(`Экспортировано: ${productsWithBarcodes.length} товаров`);
    } catch (error) {
      console.error('Export error:', error);
      toast.error('Ошибка при экспорте файла');
    }
  };

  if (loading) {
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
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <div className="sticky top-0 z-20 bg-gradient-to-r from-primary to-secondary shadow-lg">
        <div className="max-w-4xl mx-auto p-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">Управление складом</h1>
              <p className="text-sm text-white/90 mt-1">Всего товаров: {products.length}</p>
            </div>
            <Button
              onClick={handleExport}
              variant="secondary"
              size="sm"
              className="shadow-md"
            >
              <Download className="h-4 w-4 mr-2" />
              Экспорт
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-4 space-y-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-card border border-border rounded-lg p-4 space-y-2">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-warning/10 rounded-lg">
                <Package className="h-5 w-5 text-warning" />
              </div>
              <span className="text-sm font-medium text-muted-foreground">Без штрихкода</span>
            </div>
            <p className="text-2xl font-bold">{withoutBarcode.length}</p>
          </div>
          
          <div className="bg-card border border-border rounded-lg p-4 space-y-2">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-success/10 rounded-lg">
                <Barcode className="h-5 w-5 text-success" />
              </div>
              <span className="text-sm font-medium text-muted-foreground">Со штрихкодом</span>
            </div>
            <p className="text-2xl font-bold">{withBarcode.length}</p>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 h-12">
            <TabsTrigger value="without" className="text-base">
              Без штрихкода
            </TabsTrigger>
            <TabsTrigger value="with" className="text-base">
              Со штрихкодом
            </TabsTrigger>
          </TabsList>

          <TabsContent value="without" className="mt-6">
            <ProductList
              products={withoutBarcode}
              hasBarcode={false}
              onUpdate={loadProducts}
            />
          </TabsContent>

          <TabsContent value="with" className="mt-6">
            <ProductList
              products={withBarcode}
              hasBarcode={true}
              onUpdate={loadProducts}
            />
          </TabsContent>
        </Tabs>
      </div>

      {/* Floating Scanner Button */}
      <div className="fixed bottom-6 right-6 z-30">
        <Button
          size="lg"
          onClick={() => window.location.href = '/scanner'}
          className="scan-button h-14 px-6 rounded-full shadow-2xl"
        >
          <Barcode className="h-6 w-6 mr-2" />
          Сканировать
        </Button>
      </div>
    </div>
  );
};

function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/scanner" element={<ScannerPage />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-center" richColors />
    </>
  );
}

export default App;