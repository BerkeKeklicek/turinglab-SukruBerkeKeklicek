# Design Notes

## Unary to Binary

Strateji olarak unary girdideki `1` sembollerini tek tek `X` ile isaretleyip
sag tarafta tuttugum binary sayaci her isaretlemede bir artirdim. Sayaci kolay
artirmak icin ilk asamada ters sirada tuttum; butun unary semboller bitince bu
sayaci sagdan sola okuyup sol taraftaki bosalan alana normal binary sira ile
yazdim. Makinede 19 durum var. Daha az durumla yazmak mumkun olabilir ama
artirma, ters cevirme ve temizlik adimlarini ayirmak hata ayiklamayi kolaylastirdi.
Serit alfabesinde `X` isaretleyici, `#` ise unary kisimla sayac arasinda ayirac
olarak kullanildi. Karmasiklik tek seritte cok iyi degil; her `1` icin seritte
gidip gelindigi ve sonunda ters cevirme yapildigi icin pratikte O(n^2) gibi
davranir. En cok zorlandigim nokta binary sayaci normal sirada artirmakti. Basa
elde eklemek tek seritte kaydirma gerektirdigi icin sayaci ters tutup en sonda
duzeltmek daha temiz oldu.

## Binary Compare

Bu makine `x#y` bicimindeki iki binary sayiyi karsilastirir ve `x > y` ise kabul
eder. Ilk adimda iki tarafin uzunlugunu karsilastirdim. Her turda soldan bir
basamak ve sagdan bir basamak isaretleniyor. Ilk sayida basamak kalip ikinci
sayida kalmazsa kabul, tersi olursa ret veriliyor. Uzunluklar esitse isaretler
geri aciliyor ve sayilar soldan saga leksikografik olarak karsilastiriliyor.
Bu makinede 19 durum kullandim. `X` sifiri, `Y` biri gecici olarak isaretlemek
icin secildi; boylece uzunluk kontrolu bittikten sonra asil sayiyi geri kurmak
kolay oldu. Karmasiklik yine tek seritli ileri geri tarama yuzunden O(n^2)
civarindadir. En zor bug, esit uzunluklu sayilarda bir basamak karsilastirdiktan
sonra yanlislikla tekrar uzunluk kontrolune donmemdi. Ayri bir geri donus durumu
kullaninca dongu problemi cozuldu. Karardan once `X/Y` isaretlerini geri acan
kisa bir temizlik gecisi de ekledim.

## String Copy

`string_copy` makinesi `w` girdisini `w#w` bicimine getirir. Once girdinin sonuna
`#` yazilir. Sonra soldaki bolumde henuz kopyalanmamis ilk karakter bulunur:
`a` ise `A`, `b` ise `B'` ile isaretlenir ve seridin sonuna ayni karakter eklenir.
Tum karakterler isaretlenince makine sol tarafa donup isaretleri tekrar `a` ve
`b` haline getirir. Toplam 8 durum kullandim. `A` ve `B'` sembolleri hangi
karakterin daha once kopyalandigini kaybetmeden tutmak icin yeterli oldu. Bos
girdi icin sonuc `#` olarak kabul edildi, cunku `w#w` formunda iki taraf da bos
kaliyor. Bu makine de her karakter icin sona kadar gittigi icin O(n^2) adim
atar. En dikkat ettigim nokta, kopya bolumundeki karakterleri tekrar isaretlememekti;
bu nedenle `#` siniri makinenin ana kontrol noktasi oldu.

## Student Choice: Binary Divisible by 4

Ogrenci secimi olarak binary sayinin 4'e bolunebilirligini test eden makineyi
yaptim. Binary sayilarda son iki bit `00` ise sayi 4'e bolunur. Bu nedenle makine
once girdinin sonuna kadar gider, son biti kontrol eder, sonra bir onceki biti
kontrol eder. Son bit `1` ise ret, son bit `0` ve onceki bit de `0` ise kabul
edilir. Tek karakterlik `0` girdisini de 0 sayisi olarak kabul ettim. Makine 5
durumdan olusuyor ve serit alfabesinde ek isaretleyici gerekmiyor. Karmasiklik
O(n), cunku sadece sona kadar tek bir tarama yapiliyor ve en fazla iki basamak
geri bakiliyor. Bu tasarimda en kolay hata bos girdiyi kabul etmek olurdu; bos
girdiyi sayi olarak kabul etmedigim icin onu acikca ret durumuna bagladim.
