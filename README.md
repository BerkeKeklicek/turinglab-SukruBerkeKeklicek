# TuringLab

Hazirlayan: Sukru Berke Keklicek  
Ogrenci No: 233311038

Bu repo Hesaplama Kurami final odevi icin hazirladigim TuringLab projesini
icerir. Projede Python ile tek seritli Turing makinelerini YAML dosyalarindan
calistiran temel bir motor bulunur. Ek olarak cok seritli Turing makinesi motoru
ve basit bir calisma gorsellestirici de eklenmistir.

## Kurulum

```powershell
python -m pip install -r requirements.txt
```

## Ornek Kullanim

Tek seritli makine calistirma:

```powershell
python -m turinglab machines/binary_increment.yaml 1011 --verbose
```

Cok seritli makine calistirma:

```powershell
python -m turinglab machines/binary_reverse_3tape.yaml 10010
```

Testleri calistirma:

```powershell
python -m pytest
```

Gorsellestirme kareleri uretme:

```powershell
python -m turinglab.visualizer machines/binary_increment.yaml 1011 --output-dir docs/images --max-frames 8 --prefix binary_increment --gif docs/images/binary_increment.gif
```

## Klasorler

- `turinglab/`: Turing makinesi motorlari ve yardimci moduller
- `machines/`: YAML makine tanimlari
- `tests/`: pytest testleri
- `docs/`: tasarim notlari ve gorsellestirme ciktilari
