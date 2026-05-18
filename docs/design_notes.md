# Design Notes

Bu dosya Bolum 2 makineleri tamamlandikca doldurulacak.

## Bolum 1 - Motor

Serit list yerine sparse sozluk ile tutuldu. Bunun sebebi hem saga dogru
genislemeyi kolaylastirmak hem de kafa sola gittiginde Python'daki negatif indeks
karisikligini yasamamaktir. Bos sembol hucrede saklanmiyor; okunurken varsayilan
olarak `B` donuyor.

`RunResult.history` icinde baslangic konfigurasyonu dahil tutulur. Bu yuzden
calisma `n` adim surerse history uzunlugu `n + 1` olur.
