# TuringLab

Hazirlayan: Sukru Berke Keklicek  
Ogrenci No: 233311038

Bu repo, Hesaplama Kurami final projesi icin yazilan tek-seritli Turing makinesi
simulatorunu ve ornek makine tanimlarini icerir.

## Kurulum

```powershell
python -m pip install -r requirements.txt
```

## Kullanim

```powershell
python -m turinglab machines/binary_increment.yaml 1011 --verbose
```

Python API:

```python
from turinglab import RunResult, SingleTapeTM

tm = SingleTapeTM.from_yaml("machines/binary_increment.yaml")
result: RunResult = tm.run("1011", max_steps=1000, verbose=False)

assert result.accepted is True
assert result.final_tape.strip("B") == "1100"
```

## Test

```powershell
python -m pytest
```

## Tasarim Notu

Serit `dict[int, str]` ile sparse olarak tutulur. Bu nedenle kafa sola gittiginde
Python negatif indeks problemi olusmaz; negatif hucreler de normal serit hucresi
gibi kullanilir. README'de belirtilmesi istenen sol tasma karari budur.

Demo videosu: Henuz eklenmedi.
