# Microgrid Energy Management with Mamdani Fuzzy Logic

**Bulanık Mantık Dönem Projesi**  
**Can KARAHAN — 1306210004**  
**İstanbul Üniversitesi-Cerrahpaşa, Bilgisayar Mühendisliği**

## Proje Hakkında

Bu projede, güneş enerjisi (PV), tüketim yükü ve bataryadan oluşan bir mikroşebekede enerji yönetimini bulanık mantıkla ele aldım. Çıkış noktası olarak Nur-E-Alam ve arkadaşlarının 2025 yılında yayımladığı mikroşebeke enerji yönetimi çalışmasını kullandım. Makalede sunulan iki girişli, dokuz kurallı Mamdani bulanık çıkarım sistemini Python ile yeniden kurdum. Ardından batarya doluluk sınırlarında şarj ve deşarj komutlarını yönlerine göre kademeli sınırlayan alternatif bir kontrol yaklaşımını aynı deney koşullarında karşılaştırdım.

Bu çalışma, makaledeki **bulanık kontrolcü alt sisteminin yeniden gerçekleştirilmesi** üzerine kuruludur. Özgün MATLAB/Simulink mikroşebeke modelinin, MPPT ve dönüştürücü devrelerinin ya da saha verilerinin birebir kopyası değildir.

## Referans Makale

Nur-E-Alam ve diğerleri, **“Optimization of energy management in Malaysian microgrids using fuzzy logic-based EMS scheduling controller,”** *Scientific Reports*, cilt 15, makale 995, 2025.  
DOI: https://doi.org/10.1038/s41598-024-82360-4

## Kullanılan Yöntem

Bulanık kontrolcünün girişleri:

- **Güç dengesi:** PV üretimi ile yük tüketimi arasındaki farkın normalize edilmiş hâli. Negatif değer üretim fazlasını, pozitif değer tüketim fazlasını gösterir.
- **SOC (State of Charge):** Bataryanın %0–100 arasındaki doluluk oranı.

Çıkış, **şarj / bekleme / deşarj** davranışını temsil eden `[-1, 1]` aralığında normalize bir komuttur. Negatif değer şarjı, pozitif değer deşarjı ifade eder.

Her giriş için üç dilsel küme kullanılır. Dolayısıyla kontrolcünün **3 × 3 = 9 adet IF–THEN kuralı** vardır:

| Güç dengesi / SOC | Düşük | Orta | Yüksek |
|---|---|---|---|
| PV üretimi fazla | Şarj | Şarj | Bekle |
| Tüketim fazla | Bekle | Deşarj | Deşarj |
| Üretim ve tüketim dengede | Bekle | Bekle | Bekle |

Sistem, **Mamdani bulanık çıkarımı** kullanır. Kural öncüllerinde `min`, kural çıktılarının birleştirilmesinde `max`, durulaştırmada ise **ağırlık merkezi (centroid)** yöntemi uygulanır. Üyelik fonksiyonları üçgenseldir.

Makaledeki Şekil 3 ile metindeki SOC sınırı açıklamaları ve ek sonuçların bazı sayısal örnekleri tam olarak aynı davranışı göstermediğinden bunları tek bir referans model olarak varsaymadım; karşılaştırmada ayrı kontrol politikaları şeklinde tanımladım.

## Geliştirdiğim Yaklaşım

Referans çalışmada batarya doluluk sınırlarının gözetilmesi zaten ele alınmaktadır. Bu projede denediğim farklılık, **yöne duyarlı ve kademeli bir kontrol filtresidir**:

- SOC düşükken bataryanın daha fazla **deşarj olmasını** engellerken, uygun koşullarda **şarj olmasına** izin verir.
- SOC yüksekken bataryanın daha fazla **şarj olmasını** engellerken, uygun koşullarda **deşarj olmasına** izin verir.
- Sınır bölgelerine yaklaşırken kontrol komutunu bir anda kesmek yerine kademeli azaltır.

Kontrol çıktısı `u`, SOC yüzdesi `s`, geçiş genişliği `w` olmak üzere:

- `u > 0` (deşarj): `g = clip((s - 20) / w, 0, 1)`
- `u < 0` (şarj): `g = clip((80 - s) / w, 0, 1)`
- **Yeni çıktı:** `u_new = u × g`

Ana deneyde `w = 10` kullanıldı. Ayrıca `w = 5, 10, 15, 20` için duyarlılık karşılaştırması yapıldı. Bu filtre, batarya üreticisinin gerçek BMS denetiminin yerini almaz.

## Deney Düzeni

Python simülasyonunda üç kontrol seçeneği karşılaştırıldı:

1. **`fig3_fis`:** Şekil 3'teki dokuz kuralı kullanan Mamdani FIS.
2. **`text_cutoff`:** Makale metnindeki SOC sınırı açıklamasının basitleştirilmiş, katı kesme yorumu.
3. **`proposed`:** Yöne duyarlı, kademeli sınırlandırma yaklaşımı.

Deneylerde 6 farklı sentetik günlük üretim/tüketim profili ve 7 başlangıç SOC değeri kullanıldı. Böylece kontrol yöntemi başına **42 senaryo**, toplam **126 simülasyon koşusu** gerçekleştirildi. Her senaryo 15 dakikalık adımlarla bir günü kapsar.

Örnek sistemde 50 kWh batarya kapasitesi, 8 kW güç limiti ve %95 şarj/deşarj verimi varsayıldı. Bu değerler **deney için belirlenmiş model varsayımlarıdır**; makaleden alınmış ölçüm veya saha parametreleri olarak sunulmamaktadır.

### Özet Sonuçlar

| Ölçüt | Şekil 3 FIS | Katı kesme yorumu | Geliştirilen yöntem |
|---|---:|---:|---:|
| Riskli yönde işlem yapılan zaman adımı | 983 | 0 | 0 |
| SOC güvenli bandı dışında geçirilen zaman adımı | 1555 | 2808 | 856 |
| Ortalama şebekeden enerji alımı (kWh/gün) | 159,57 | 167,69 | 161,11 |
| Ortalama batarya enerji çevrimi (kWh/gün) | 18,81 | 7,35 | 16,85 |

Bu değerler **sentetik veriyle çalıştırılan Python deneylerinin** sonuçlarıdır; referans makalenin deney tablosu değildir. Riskli yönlü işlemin sıfıra inmesi, kullanılan filtrenin tanımından kaynaklanır. Güvenli bant dışındaki adımların sayımına başlangıçta zaten bant dışında olan senaryolar da dahildir. Şebeke kullanımı ve batarya çevrimi açısından farklı kontrol politikalarının ödünleşimleri bulunmaktadır.

Deney çıktıları `results/tables/` ve `results/figures/` altında bulunmaktadır. Ayrıca SOC ölçüm gürültüsü ve geçiş genişliği deneyleri de bu klasörlerde yer alır.

## Dosya Yapısı

```text
microgrid-fuzzy-ems/
├── README.md
├── requirements.txt
├── demo.py
├── src/
│   ├── fuzzy_ems.py
│   └── simulator.py
├── tests/
│   └── test_controller.py
├── experiments/
│   ├── run_experiments.py
│   └── Microgrid_Fuzzy_EMS_Colab.ipynb
├── data/
│   └── README.md
└── results/
    ├── tables/
    └── figures/
```

`src/` kontrolcü ve simülasyon kodlarını, `tests/` otomatik testleri, `experiments/` çalıştırılabilir deneyleri, `results/` ise tablolara ve grafiklere dönüştürülmüş çıktıları içerir. Kaynak dosyalardaki Python paket dosyaları (`__init__.py`) gösterimde sadeleştirilmiştir.

## Kurulum ve Çalıştırma

Python **3.10+** ve `requirements.txt` dosyasındaki kütüphaneler gereklidir. Repo kök dizininde:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python demo.py --pv 15 --load 23 --soc 18
python -m experiments.run_experiments
```

Demo örneğinde PV üretimi **15 kW**, yük talebi **23 kW** ve batarya SOC değeri **%18** olarak verilir. Çıktıda bulanık üyelik dereceleri, etkin kurallar ve kontrol seçeneklerinin kararları görüntülenebilir.

Google Colab üzerinden çalıştırmak için `experiments/Microgrid_Fuzzy_EMS_Colab.ipynb` dosyası açılabilir. Deneyler yeniden çalıştırıldığında sonuç CSV dosyaları ve grafikler üretilir.

## Sınırlılıklar

- Model, makalenin **tam Simulink güç elektroniği sistemini** değil bulanık kontrolcü alt sistemini temsil eder.
- Günlük PV/yük profilleri gerçek ölçüm değil, **sentetik verilerdir**.
- Bazı üyelik fonksiyonu parametreleri ve güç normalizasyonu, Şekil 3'ün yeniden gerçekleştirilmesi için belirlenmiş yaklaşımlardır; özgün `.fis` dosyası mevcut değildir.
- Makaledeki Şekil 3, açıklama metni ve bazı sayısal örnekler arasında gözlenen farklılıklar nedeniyle makaledeki bütün sayısal sonuçlar birebir yeniden üretilememiştir.
- Batarya modeli sadeleştirilmiştir; gerçek BMS, sıcaklık, yaşlanma, dönüştürücü ve şebeke koşullarını kapsamaz.
- Elde edilen sonuçlar uygulamanın bu sentetik senaryolardaki davranışını gösterir; gerçek bir mikroşebekede üstün performans veya güvenlik garantisi vermez.

## Kaynaklar

1. Nur-E-Alam ve diğerleri, “Optimization of energy management in Malaysian microgrids using fuzzy logic-based EMS scheduling controller,” *Scientific Reports*, 2025. https://doi.org/10.1038/s41598-024-82360-4
2. L. A. Zadeh, “Fuzzy Sets,” *Information and Control*, 1965. https://doi.org/10.1016/S0019-9958(65)90241-X
3. E. H. Mamdani ve S. Assilian, “An Experiment in Linguistic Synthesis with a Fuzzy Logic Controller,” *International Journal of Man-Machine Studies*, 1975. https://doi.org/10.1016/S0020-7373(75)80002-2
4. D. Arcos-Avilés ve diğerleri, enerji yönetimi ve bulanık kontrol üzerine çalışma, *IEEE Transactions on Smart Grid*. https://doi.org/10.1109/TSG.2016.2555245
5. A. El Zerk ve M. Ouassaid, “Real-Time Fuzzy Logic Based Energy Management System for Microgrid Using Hardware in the Loop,” *Energies*, 2023. https://doi.org/10.3390/en16052244
