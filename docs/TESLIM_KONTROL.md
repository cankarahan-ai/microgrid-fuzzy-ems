# Nihai teslim kontrolü — 10 Kasım 2026

> Hazırlanmış olması **Classroom'a teslim edildiği** anlamına gelmez. Bu dosya gerçek yükleme sonrası işaretlenmelidir.

| Classroom alanı | Dosya / işlem | Durum |
|---|---|---|
| 1 — Teknik rapor | `report/Teknik_Rapor_Microgrid_Fuzzy_EMS.pdf` | TASLAK HAZIR; öğrenci no/son okuma bekliyor |
| 2 — Sunum | `presentation/Microgrid_Fuzzy_EMS_Sunum.pptx` veya `.pdf` | TASLAK HAZIR; sunum provası bekliyor |
| 3 — Kaynak kod & deney ZIP | `EMS_10Kas_Classroom_Kaynak_Kod_Deney.zip` | OLUŞTURULDU / HENÜZ CLASSROOM'A YÜKLENMEDİ |
| 4 — GitHub repository URL | https://github.com/cankarahan-ai/microgrid-fuzzy-ems | Mevcut; yeni kod/deney/rapor commit'leri bekleniyor |
| 5 — Final teslim kontrolü | Diğer dört teslimin kontrolünü yapıp yönergeye göre onayla | YAPILMADI |

## Dosyalar son kez denetlenirken

- [ ] Gerçek makale Fig. 3 & Fig. S6 nümerik tutarsızlığını doğru ve dikkatli sun.
- [ ] Teknik rapordaki bibliyografya DOI'lerini kontrol et.
- [ ] Modelin sentetik veri ve varsayımsal batarya üzerinden çalıştığı net yazılsın.
- [ ] README ile PDF/PPTX metrikleri aynı kod çalışmasından gelsin.
- [ ] `python -m unittest discover -s tests -v` → 10 test.
- [ ] `python -m experiments.run_experiments` → 126 simülasyon.
- [ ] GitHub'da `.gitignore` ve bağımlılık dosyası görünür olsun.
- [ ] AI kullanım bildirimi raporda olsun.
- [ ] Classroom tarihlerini ve teslim butonunun durumunu giriş yaparak doğrula.
- [ ] Sunumda canlı demo ve 15–20 dk hazırlık yap.

Bu projede Simulink kullanmak zorunlu değildir: ders yönergesi Python ve Colab seçeneklerini içerir. Ama birebir referans deneyinin tekrarı zorunlu bir beklenti olduğundan, Fig. S6 sayısal uyuşmazlığı açık bir eksik/limitasyon olarak belgelenmiş ve sunumda saklanmamıştır.
