#!/bin/bash

echo "🔧 CloudPepper İçin Teslimat Modülü Düzeltme Scripti"
echo "================================================="

# Mevcut dizini kontrol et
CURRENT_DIR=$(basename "$PWD")
echo "📁 Mevcut klasör: $CURRENT_DIR"

if [ "$CURRENT_DIR" != "delivery_module" ]; then
    echo "⚠️  Klasör adı 'delivery_module' olmalı, şu anda: $CURRENT_DIR"
    
    # Üst dizine çık ve yeniden adlandır
    cd ..
    
    if [ -d "delivery_module" ]; then
        echo "🗑️  Eski delivery_module klasörü siliniyor..."
        rm -rf delivery_module
    fi
    
    echo "📝 Klasör yeniden adlandırılıyor: $CURRENT_DIR -> delivery_module"
    mv "$CURRENT_DIR" delivery_module
    cd delivery_module
    echo "✅ Klasör adı düzeltildi"
else
    echo "✅ Klasör adı doğru: delivery_module"
fi

# Gereksiz dosyaları temizle
echo "🧹 Gereksiz dosyalar temizleniyor..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name ".DS_Store" -delete 2>/dev/null
rm -rf .git/hooks 2>/dev/null

# CloudPepper uyumlu zip oluştur
echo "📦 CloudPepper uyumlu zip dosyası oluşturuluyor..."
ZIP_NAME="delivery_module_cloudpepper.zip"

# Mevcut zip'i sil
rm -f "../$ZIP_NAME" 2>/dev/null

# Yeni zip oluştur
zip -r "../$ZIP_NAME" . \
    -x "*.git*" \
    -x "*.DS_Store*" \
    -x "*__pycache__*" \
    -x "*.pyc" \
    -x "auto_commit.sh" \
    -x "install_module.sh" \
    -x "fix_cloudpepper.sh"

if [ $? -eq 0 ]; then
    echo "✅ Zip dosyası oluşturuldu: ../$ZIP_NAME"
    echo "📊 Zip dosyası boyutu: $(du -h "../$ZIP_NAME" | cut -f1)"
else
    echo "❌ Zip dosyası oluşturulamadı!"
    exit 1
fi

echo ""
echo "🚀 CLOUDPEPPER KURULUM TALİMATLARI:"
echo "=================================="
echo "1. ../$ZIP_NAME dosyasını indirin"
echo "2. CloudPepper hesabınızda:"
echo "   - Uygulamalar > Özel Uygulamalar"
echo "   - 'Uygulama Yükle' butonuna tıklayın"
echo "   - $ZIP_NAME dosyasını seçin"
echo "   - 'Yükle' butonuna tıklayın"
echo "3. Yükleme sonrası:"
echo "   - Uygulamalar > Uygulamalar Güncelle"
echo "   - 'Teslimat Modülü' arayın"
echo "   - 'Yükle' butonuna tıklayın"
echo ""
echo "✅ CloudPepper düzeltmeleri tamamlandı!"
