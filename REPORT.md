# TuringLab Mini Rapor

Hazirlayan: Sukru Berke Keklicek  
Ogrenci No: 233311038

## 1. Giris

TuringLab, Hesaplama Kurami dersi icin hazirlanan ve Turing makinelerini
calistirmayi amaclayan bir Python projesidir. Projenin ana hedefi, derste
formel olarak tanimlanan tek seritli deterministik Turing makinesini calisan bir
yazilim modeli haline getirmektir. Bu nedenle proje sadece bir simulator degil,
ayni zamanda durum, serit, kafa konumu, gecis fonksiyonu ve kabul/ret
davranislarini kod uzerinde gormemi saglayan bir calisma oldu.

Projede makineler Python kodu icine sabitlenmedi. Bunun yerine her makine YAML
dosyasi olarak tanimlandi. Bu sayede motor ile makine tasarimi birbirinden
ayrildi. `turinglab/tm_engine.py` dosyasi genel calistirma mantigini tasirken,
`machines/` klasoru farkli problemler icin yazilmis Turing makinelerini tutar.
Testler de `tests/` klasorunde ayrildi. Boylece yeni bir makine eklerken motoru
degistirmeden sadece yeni bir YAML dosyasi ve ona ait testler yazmak yeterli
oluyor.

Zorunlu kisimda tek seritli motor, dort farkli Turing makinesi ve test dosyalari
hazirlandi. Ek puan icin de cok seritli Turing makinesi motorunun ilk calisan
surumu eklendi. Bu bonus kisimda 3 seritli bir makine ile binary girdinin tersini
ucuncu seride yazan bir ornek tasarlandi.

## 2. Mimari

Ana tek seritli motor `SingleTapeTM` sinifidir. Bu sinif YAML dosyasini okur,
alanlari dogrular ve gecisleri `(state, read_symbol)` anahtari ile sozlukte
tutar. Calisma sirasinda mevcut durum, serit uzerindeki sembol ve gecis tablosu
birlikte degerlendirilir. Gecerli gecis bulunursa sembol yazilir, kafa hareket
eder ve yeni duruma gecilir. Makine kabul durumuna gelirse `accept`, ret
durumuna gelirse `reject`, gecis bulunamazsa `no_transition`, adim siniri
asilirsa `timeout` nedeni ile durur.

Serit icin `Tape` sinifi yazildi. Seridi Python string olarak tutmak yerine
`dict[int, str]` ile sparse olarak tuttum. Bos semboller sozlukte saklanmiyor;
okuma sirasinda hucre yoksa blank sembol donuyor. Bu tercih iki konuda isimi
kolaylastirdi. Birincisi, serit saga dogru kendiliginden buyuyebiliyor. Ikincisi,
kafa sola gittiginde Python listelerindeki negatif indeks problemi yasanmiyor.
Bu projede negatif konumlar da seridin normal hucreleri gibi ele alindi.

`RunResult` sinifi calisma sonucunu tasir. Sonucun kabul edilip edilmedigi,
durma nedeni, final serit, adim sayisi ve history bilgisi bu nesnede bulunur.
History icinde baslangic konfigurasyonu da vardir. Bu nedenle bir makine `n`
adimda durduysa history uzunlugu `n + 1` olur. Bu tercih testlerde ve verbose
modda adimlari incelemeyi kolaylastirdi.

YAML okuma kisminda eksik alan, bilinmeyen sembol, hatali durum adi ve tekrarli
gecis gibi durumlar `ValueError` ile yakalandi. Bu kontrolleri eklemek basta
fazladan is gibi gorundu ama makine dosyalari buyudukce hatayi erken bulmayi
sagladi. Ozellikle `binary_compare.yaml` gibi cok durumlu makinelerde yanlis
duruma gecmek veya sembol adini eksik yazmak kolay oluyor.

Bonus A icin `turinglab/multi_tape.py` dosyasinda `MultiTapeTM` sinifi yazildi.
Bu sinif genel olarak tek seritli motora benziyor ama gecis anahtari
`(state, read_symbols)` seklindedir. `read`, `write` ve `move` alanlari YAML
icinde liste olarak verilir ve bu listelerin uzunlugu `num_tapes` degeri ile
uyumlu olmak zorundadir. Calisma sonucunda `final_tapes` listesi doner. Boylece
her seridin son hali ayri ayri incelenebilir.

## 3. Tasarlanan Turing Makineleri

Ilk tasarlanan makine `unary_to_binary.yaml` dosyasidir. Bu makine unary girisi
binary gosterime cevirir. Yontem olarak unary kisimdaki her `1` isaretlenir ve
sag tarafta tutulan binary sayac bir artirilir. Sayac ilk basta ters sirada
tutuldu, cunku en dusuk anlamli bitten artirma yapmak tek seritte daha kolay
oldu. Tum unary semboller bitince sayac sagdan sola okunarak normal binary sira
ile sol tarafa yazildi. Bu makine tek seritte cok gidip geldigi icin adim sayisi
buyuk olabilir ama tasarim olarak takip etmesi kolaydir.

Ikinci makine `binary_compare.yaml` dosyasidir. Girdi bicimi `x#y` seklindedir
ve makine ilk sayi ikinci sayidan buyukse kabul eder. Once iki sayinin uzunlugu
karsilastirilir. Uzunluklar farkliysa daha uzun olan sayi daha buyuk kabul
edilir. Uzunluklar esitse gecici isaretler geri acilir ve sayilar soldan saga
karsilastirilir. Bu makine projenin en ugrastiran zorunlu makinesi oldu, cunku
tek seritte hem sol hem sag tarafin ayni anda takip edilmesi cok fazla ileri geri
hareket gerektiriyor.

Ucuncu makine `string_copy.yaml` dosyasidir. Bu makine `w` girdisini `w#w`
bicimine getirir. Soldaki karakterler sirayla `A` ve `B'` sembolleri ile
isaretlenir, sonra seridin sonuna ayni karakter eklenir. Butun karakterler
kopyalandiktan sonra isaretler tekrar orijinal `a` ve `b` sembollerine cevrilir.
Bos girdi icin sonuc `#` olarak kabul edildi.

Dorduncu makine ogrenci secimi olarak yazilan `student_choice.yaml` dosyasidir.
Bu makine binary bir sayinin 4'e bolunebilirligini test eder. Binary sayilarda
son iki bit `00` ise sayi 4'e bolunur. Bu nedenle makine sadece girdinin sonuna
kadar gider ve son iki biti kontrol eder. Diger zorunlu makinelere gore daha
kisa ve daha verimli bir tasarimdir.

Bonus A kapsaminda `binary_reverse_3tape.yaml` dosyasi eklendi. Bu 3 seritli
makine binary girdiyi ikinci seride ayni sirayla kopyalar, sonra ikinci seridi
sagdan sola okuyarak ucuncu seride ters sirada yazar. Ornegin `10010` girdisi
icin ucuncu seritte `01001` elde edilir. Bu ornek cok seritli makinelerde ara
serit kullanmanin tek seritli tasarima gore nasil daha rahat oldugunu gostermek
icin secildi.

## 4. Kavramsal Tartisma: Halting Problemi

TuringLab icinde halting problemini genel olarak cozmek mumkun degildir. Bunun
sebebi halting probleminin sadece bu projeye ait teknik bir eksiklik olmamasi,
hesaplama kuraminda karar verilemez oldugu bilinen temel problemlerden biri
olmasidir. Halting problemi kisaca su soruyu sorar: Verilen herhangi bir Turing
makinesi ve herhangi bir girdi icin, bu makine sonunda duracak mi yoksa sonsuza
kadar calismaya devam mi edecek?

TuringLab bir makineyi adim adim calistirabilir. Eger makine kabul veya ret
durumuna ulasirsa durdugunu gorebiliriz. Eger gecis bulunamazsa yine durma
nedenini raporlayabiliriz. Fakat makine uzun sure calisiyorsa bunun iki farkli
anlami olabilir: makine biraz daha calisirsa duracak olabilir veya gercekten
sonsuz donguye girmis olabilir. Disaridan bakarak bu ayrimi her makine icin
kesin olarak yapmak mumkun degildir.

Projede `max_steps` parametresi bu nedenle pratik bir guvenlik siniri olarak
kullanildi. Bu sinir asilinca sonuc `timeout` olarak doner. Ancak `timeout`,
"bu makine hic durmaz" anlamina gelmez. Sadece verilen adim siniri icinde
durmadigini soyler. Daha buyuk bir sinir verilseydi makine belki kabul veya ret
durumuna ulasabilirdi. Bu ayrim onemlidir, cunku bir simulator yazmak ile tum
makinelerin davranisini karar veren genel bir algoritma yazmak ayni sey degildir.

TuringLab teorik olarak evrensel Turing makinesine benzer bir yonde
genisletilebilir. Bir makine tanimi ve girdisi kodlanip baska bir makinenin
girdisi haline getirilebilir. Fakat bu da halting problemini cozmez; sadece bir
makinenin baska bir makineyi simule etmesini saglar. Sonuc olarak TuringLab,
halting problemini deneysel olarak gormek ve ornekler uzerinden anlamak icin
yararlidir, ama problemi genel durumda cozemez.

## 5. Sinirlar ve Ileri Calisma

Projenin su anki halinde tek seritli deterministik Turing makineleri calisiyor.
YAML dogrulama, history tutma, verbose cikti ve pytest testleri mevcut. Bununla
birlikte proje hala gelistirilebilir. Ornegin hata mesajlari daha kullanici dostu
hale getirilebilir, komut satiri arayuzu daha ayrintili secenekler alabilir ve
makine calisma adimlari gorsel olarak sunulabilir.

Bonus A ile cok seritli motor eklendi ama bu kisim tek seritli motor kadar cok
ornek makine icermiyor. Ileri calismada daha anlamli bir 3 seritli binary toplama
makinesi yazilabilir. Ayrica non-deterministic Turing makinesi icin BFS tabanli
bir motor eklemek de projeyi genisletir. Gorsellestirici tarafinda her adimin
PNG veya GIF olarak uretilmesi, ozellikle verbose metin ciktisini takip etmekte
zorlanan biri icin faydali olurdu.

Bir baska sinir da performanstir. Bu proje egitim amacli oldugu icin oncelik
okunabilirlik ve dogru davranis oldu. Tek seritli makinelerde cok fazla ileri
geri tarama yapildigindan adim sayilari hizli buyuyor. Gercek kullanimda bunu
iyilestirmek icin daha fazla yardimci serit veya daha farkli kodlama stratejileri
kullanilabilir.

## 6. Kaynakca

- TuringLab Ogrenci El Kitabi.
- Hesaplama Kurami ders notlari.
- Python resmi dokumantasyonu: `dataclasses`, `pathlib`, `argparse`.
- PyYAML dokumantasyonu.
