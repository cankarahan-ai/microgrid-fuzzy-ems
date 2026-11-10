# Bulanık Mantık Projesi — Sunum ve Canlı Savunma

**Sunum:** Yaklaşık 15–20 dakika + 5 dakika soru/cevap (ders yönergesine göre).  
**Repo:** https://github.com/cankarahan-ai/microgrid-fuzzy-ems  
**Makale:** https://doi.org/10.1038/s41598-024-82360-4

## Canlı demo sırası (Windows terminal veya Google Colab)

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python demo.py --pv 15 --load 23 --soc 18
python demo.py --pv 23 --load 12 --soc 90
python -m experiments.run_experiments
```

**Örnek 1:** PV=15, load=23, SOC=18. Balance = (23−15)/20 = +0.4. FIS ≈ +0.06302: SOC düşükken az bir deşarj eğilimi; hard-cutoff=0 ve proposed=0. Bu sayı bir fiziksel amper ölçümü değil, normalize karar çıktısıdır.

**Örnek 2:** PV=23, load=12, SOC=90. Fazla PV, yüksek SOC. Makale kural tabanı “bekle”ye yaklaşır; yönlü güvenlik filtresi yüksek SOC'de şarjı engeller.

**Örnek 3:** `python demo.py --pv 27 --load 10 --soc 10`. PV fazlası + düşük SOC → şarj edebilir (negatif işaret). Katı kesme yorumunda bu toparlanma engellenir.

## Hoca ne sorarsa?

**Neden 3×3=9 kural?** İki girişte üçer dilsel küme var: balance (surplus/balanced/deficit) ve SOC (low/mid/high). Her kombinasyona bir çıkış atandı.

**Mamdani nasıl işliyor?** Kesin girişler bulanıklaştırılır; AND=min, implication=min, aggregation=max; centroid durulaştırma tek çıktı üretir.

**Mamdani ile Sugeno farkı?** Mamdani kural sonuçları bulanık çıktı kümeleri; Sugeno’da sonuçlar sabit veya fonksiyon olabilir. Biz Mamdani kullandık.

**Üyelikler niçin toplam 1 değil?** Farklı bulanık kümelere kısmi üyelikler ayrı ayrı tanımlanır; toplamın 1 olması şart değildir.

**Orijinal makaleyi tamamen yeniden mi yaptın?** Hayır. Şekil 3 FIS'i bağımsız uyguladık, Simulink MPPT/PI/THD fiziksel sistemi yeniden yapmadık.

**Makaledeki FIS ile neden tüm sayılar eşleşmiyor?** Şekil 3'ün dokuz kuralı ile yazılı SOC sınır davranışı ve S6 nümerikleri tam tutarlı görünmüyor. Orijinal .fis/Simulink dosyası olmadan Fig S6 birebir kopyalanamaz. Bu sınırlılığı sonuçlarda açıkladık.

**Özgün katkın ne?** Referanstaki SOC korumasını ilk kez keşfetmek değil: aynı FIS çıktısına yön-duyarlı ve *kademeli* sınırlandırma ekleyerek güvenli banda dönüşe izin vermek. Katı kesmeden farkı şarj/ deşarj yönünü ayırmak ve geçişi yumuşatmak.

**983→0 gerçek makale başarısı mı?** Hayır. Bu sayı salt Fig 3 FIS'in sentetik plant ve bizim tanımlı riskli-yön metriğine göre çıktısıdır. Makale veri setinden gelmez, üstelik proposed için riskli komutun sıfır olması filtrenin tasarım özelliğidir.

**Karşılaştırma adil mi?** Evet: üç modda PV/yük profili, batarya varsayımları ve başlangıç SOC eşleniktir. Yalnızca son-kontrol politikası farklıdır.

**Yöntemin dezavantajı?** Batarya kullanım miktarı ve şebeke bağımlılığında ödünleşim; gerçek BMS/saha üzerinde güvenlik garantisi yok.

**AI kullandın mı?** Evet, ChatGPT kod/deney/rapor taslaklarına destek verdi. Deneyler Python ile çalıştırıldı; ayrıntılar rapordaki açıklamada.

## Sunumdan önce bizzat doğrula

- [ ] README ve raporu anlayarak oku; terimleri açıklayabil.
- [ ] Üç komutu yerel bilgisayarda veya Colab'da çalıştır.
- [ ] Aşağıdaki son commit'in GitHub'da göründüğünü kontrol et.
- [ ] Şekil 3 görselindeki dokuz kuralın sırayla hangi output'a gittiğini anlat.
- [ ] PowerPoint'teki şekillerin ve metinlerin taştığı bir sayfa olmadığını gözden geçir.
- [ ] Öğrenci numaranı PDF/PPTX üstünde doğru gir.
