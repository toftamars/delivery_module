#!/bin/bash

# Otomatik commit ve push için yardımcı script
# Bu script, düzenli olarak değişiklikleri kontrol eder ve varsa commit ve push yapar

echo "Otomatik commit ve push scripti başlatıldı..."
echo "Çalışma dizini: $(pwd)"

# Değişiklikleri kontrol et
CHANGES=$(git status --porcelain)

if [ -z "$CHANGES" ]; then
    echo "Commit edilecek değişiklik yok."
    exit 0
fi

echo "Değişiklikler tespit edildi:"
echo "$CHANGES"

# Değişiklikleri ekle
git add .

# Commit mesajını oluştur
COMMIT_MSG="Otomatik commit: $(date '+%Y-%m-%d %H:%M:%S')"

# Commit yap
git commit -m "$COMMIT_MSG"

if [ $? -eq 0 ]; then
    echo "Commit başarıyla tamamlandı: $COMMIT_MSG"
else
    echo "Commit sırasında hata oluştu!"
    exit 1
fi

# Push yap
git push origin main

if [ $? -eq 0 ]; then
    echo "Push başarıyla tamamlandı."
else
    echo "Push sırasında hata oluştu!"
    exit 1
fi

echo "İşlem tamamlandı."
