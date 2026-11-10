"""Generate the Turkish technical report strictly from reproducible experiment results.
Run: python report/build_report.py (after python -m experiments.run_experiments).
"""
from pathlib import Path
import csv, json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

R=Path(__file__).resolve().parents[1]
DATA=json.loads((R/'results/tables/summary.json').read_text(encoding='utf-8'))
M=DATA['modes']; NOISE=DATA['noise_experiment']; ABL=DATA['guard_width_ablation']
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONTB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('DV',FONT));pdfmetrics.registerFont(TTFont('DVB',FONTB))
NAVY=colors.HexColor('#19334c');TEAL=colors.HexColor('#12716c');GRAY=colors.HexColor('#536273')
ST={
 'title': ParagraphStyle('rt_title',fontName='DVB',fontSize=20,leading=28,textColor=NAVY,spaceAfter=15),
 'sub': ParagraphStyle('rt_sub',fontName='DV',fontSize=11,leading=16,textColor=GRAY,spaceAfter=12),
 'head': ParagraphStyle('rt_head',fontName='DVB',fontSize=14,leading=20,textColor=NAVY,spaceAfter=8,spaceBefore=10),
 'p': ParagraphStyle('rt_p',fontName='DV',fontSize=10.4,leading=17,spaceAfter=11),
 'small': ParagraphStyle('rt_sm',fontName='DV',fontSize=9.1,leading=13.4,spaceAfter=7),
 'fine': ParagraphStyle('rt_fine',fontName='DV',fontSize=8.4,leading=12.4,spaceAfter=7,textColor=GRAY),
 'table': ParagraphStyle('rt_tab',fontName='DV',fontSize=8.4,leading=12),
}
S=[]
def P(text,style='p'):return Paragraph(text,ST[style])
def add(*nodes):S.extend(nodes)
def H(t):return P(t,'head')
def pg():add(PageBreak())
def tbl(rows,widths=None):
    t=Table([[P(str(x),'table') for x in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([
       ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6f4f2')),
       ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f8fa')]),
       ('GRID',(0,0),(-1,-1),.35,colors.HexColor('#d8e2e6')),
       ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
       ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
       ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    return t

def fig(filename,width=470):
    im=Image(str(R/'results/figures'/filename))
    factor=im.imageHeight/im.imageWidth
    im.drawWidth=width;im.drawHeight=width*factor
    return im

# Page 1 — cover and abstract
add(Spacer(1,42),P('İSTANBUL ÜNİVERSİTESİ-CERRAHPAŞA  |  BİLGİSAYAR MÜHENDİSLİĞİ','sub'),
    P('BULANIK MANTIK<br/>DÖNEM PROJESİ','title'),
    P('Mikroşebekelerde Mamdani Bulanık Enerji Yönetimi: Figure 3 Yeniden Gerçekleştirmesi ve SOC Sınırında Yönlü Yumuşak Kontrol','sub'),
    Spacer(1,20),
    tbl([['Öğrenci','Can KARAHAN — Öğrenci No: 1306210004'],
         ['Referans çalışma','Nur-E-Alam vd. (2025), Scientific Reports 15, 995'],
         ['Ortam','Python / NumPy / Matplotlib / unittest'],
         ['Hazırlanan sürüm','10 Kasım 2026 — Akademik kontrol taslağı'],
         ['Bağlantı','github.com/cankarahan-ai/microgrid-fuzzy-ems']], [135,347]),
    Spacer(1,24),H('Özet'),
    P('Bu proje, PV üretimi, yük ve batarya doluluk oranını kullanan iki girişli, dokuz kurallı Mamdani bulanık denetleyicisini bağımsız Python uygulamasıyla yeniden kurmaktadır. Referans makalenin Şekil 3(d) kural tabanı temel alınmış; min–max çıkarımı ve centroid durulaştırma hesaplanmıştır. Makalenin metnindeki SOC sınırlarında akımı kesme ifadesi ile Şekil 3 kuralları ayrı yorumlar olarak modellenmiştir.'),
    P('Özgün katkı, aynı Mamdani çıktısına uygulanan yön-duyarlı, kademeli SOC kısıtıdır: düşük SOC’de bataryanın toparlayıcı yönde şarj edilmesine ve yüksek SOC’de toparlayıcı yönde deşarj edilmesine izin verilirken, ters yöndeki komutlar engellenir. Karşılaştırma altı rastgele tohum ve yedi başlangıç SOC değerinin eşlenmesinden oluşan 42 sentetik günlük senaryoda üç politika için 126 simülasyonla yapılmıştır.'),
    P('<b>Bilimsel kapsam uyarısı:</b> Bu sonuçlar makaledeki gerçek Nilai, Malezya verileri veya MATLAB/Simulink güç elektroniği modelinin birebir tekrarından elde edilmemiştir. Makaledeki Fig. S6 sayısal örnekleriyle bulunan fark açıkça raporlanmaktadır.','fine'))
pg()
# Page 2
add(H('1. Introduction — Problem ve motivasyon'),
    P('Güneş enerjisi dalgalandığı için Ppv (fotovoltaik üretim) ve Pload (yük talebi) her zaman eşit değildir. Enerji yönetim sistemi (EMS), fazlayı bataryaya yönlendirebilir veya eksikliği batarya/şebekeden karşılayabilir. Batarya SOC değeri aşırı şarj ile derin deşarj arasında korunmalıdır. Bulanık mantık, mühendislik sezgilerini yorumlanabilir IF–THEN kurallarıyla ifade etmeyi sağlar.'),
    P('İncelenen makalede 50 kW PV sistem, 500 Ah batarya ve elektrik şebekesi MATLAB/Simulink ile ele alınmıştır [1]. FLC ve PI kontrol yaklaşımları karşılaştırılmış; FLC için SOC yönetimi, PI için bazı harmonik performansı kazanımları bildirilmiştir. Makalenin MPPT verimliliği ve THD sonuçları bu projenin deney sonuçları değildir.'),
    H('2. Related Work — Güncel ve temel literatür'),
    P('Zadeh [2] bulanık küme üyeliğini [0,1] aralığında tanımlamış, Mamdani ve Assilian [3] dilsel uzman kurallarının kontrolcüye aktarılabileceğini göstermiştir. Arcos-Avilés ve ark. [4], şebekeye bağlı konut mikroşebekelerinde SOC’yi güvenli tutmayı ve şebeke akışındaki dalgalanmaları azaltmayı amaçlayan bir FLC incelemiştir. Rodriguez, Arcos-Aviles ve Martinez [5], izole mikroşebekelerde bulanık EMS ve meta-sezgisel optimizasyonu değerlendirmiştir. El Zerk ve Ouassaid [6], donanım-döngüde doğrulama ile gerçek zamanlı enerji yönetimini incelemiştir.'),
    H('Literatüre göre proje konumu'),
    tbl([['Çalışma','Kapsam','Bu proje açısından önemli nokta'],
         ['Nur-E-Alam vd. [1]','PV-batarya-şebeke / FLC + PI','Şekil 3 FIS ve SOC davranışı'],
         ['Arcos-Avilés vd. [4]','Konut MG / 25 kurallı FLC','SOC ve şebeke değişkenliği'],
         ['Rodriguez vd. [5]','İzole MG / optimizasyon','Parametre ayarlama ve yöntem karşılaştırma'],
         ['El Zerk vd. [6]','Gerçek zamanlı HIL','Basit simülasyonun fiziksel doğrulama sınırı']], [122,158,202]),
    P('<b>Araştırma sorusu:</b> Orijinal Fig. 3 kural tabanının ürettiği komut ile makale metnindeki katı sınır politikası arasındaki gerilim, yumuşak yön-duyarlı bir kısıtla hangi ölçütlerde daha iyi yönetilebilir?','small'))
pg()
# Page 3
add(H('3. Theoretical Background — Kuramsal altyapı'),
    P('<b>Üyelik fonksiyonu:</b> µA(x) değeri x’in A dilsel kümesine üyeliğini belirtir. 0 tam dışarıda, 1 tam üye; ara değerler kısmi üyedir. Bu değer olasılık değildir. Bir SOC değeri düşük ve orta kümelerine birlikte üye olabilir; bu üyeliklerin toplamının 1 olması şart değildir.'),
    P('<b>Üçgensel küme:</b> a&lt;b&lt;c için µ(x)=max(0,min((x−a)/(b−a),(c−x)/(c−b))). Uçtaki üçgenler evren dışında başlayan ayakları sayesinde [0,100] üzerinde omuz kümesi gibi görünür. Üyelik fonksiyonları gerçek dünyaya ait değerleri dilsel terimlere bağlar.'),
    P('<b>Mamdani çıkarım akışı:</b> Sayısal giriş → <i>fuzzification</i> → IF–THEN kurallarının değerlendirilmesi → min ile sonuç kümesinin kesilmesi → max ile kümelerin birleştirilmesi → <i>defuzzification</i> ile kesin karar. Kural ağırlıkları eşit (1) kabul edilmiştir.'),
    P('<b>Örnek:</b> normalize güç dengesi +0,4 ve SOC %18 için “balanced” üyeliği 0,6, “deficit” 0,4, “low SOC” 0,64, “medium SOC” 0,36 olur. “IF deficit AND medium THEN discharge” kuralının etkinliği min(0,4,0,36)=0,36’dır. Diğer kurallarla birleştirilen çıktı centroid ile sayısallaştırılır.'),
    P('<b>Centroid:</b> u = ∫[−1,1] y µagg(y) dy / ∫[−1,1] µagg(y) dy. Sayısal hesapta 1001 örnek nokta ve trapez integrasyon kullanılmıştır. Buradaki çıktı bulanık kümelerden gelir; Sugeno’nun sabit çıktı ağırlıklı ortalaması kullanılmamıştır.'),
    P('<b>FIS ile kontrol sistemi ayrımı:</b> FIS üçgenler ve kurallarla işareti belirleyen karar motorudur. Bataryanın fiziksel akımı, güç, verim, SOC dinamiği ve şebeke dengelemesi ise ayrı enerji modeliyle ilişkilidir. Bizim model, makalenin güç elektroniği ve harmonik dinamiğini içermez.'),
    H('Üçgensel üyelik fonksiyonlarımız'),
    fig('membership_functions.png',470),
    P('Şekil A. Referans makale Şekil 3’ten bağımsız Python çizimi; makalenin görüntüsü kopyalanmamıştır.','fine'))
pg()
# Page 4
add(H('4. Original Method — Referans yöntemin analizi'),
    P('Makalenin Şekil 3’ü iki girdi (balance, SOC) ve bir çıktı (c/d) tanımlar. Balance evreni [−1,+1], SOC [0,100] ve c/d [−1,+1] olarak çizilmiştir. Balance kümeleri PV&gt;Load, PV=Load, PV&lt;Load; SOC kümeleri düşük, orta, yüksek; çıktılar charging, no_change ve discharging’dir. Negatif c/d bataryanın şarjını, pozitif c/d deşarjını temsil eder [1].'),
    tbl([['Güç durumu / SOC','Düşük','Orta','Yüksek'],
         ['PV üretim fazlası','Şarj','Şarj','Bekle'],
         ['Yük talep fazlası','Bekle','Deşarj','Deşarj'],
         ['PV = Yük','Bekle','Bekle','Bekle']], [188,98,98,98]),
    P('Bu tablo, referans makalenin Şekil 3(d)’de gösterdiği dokuz IF–THEN kuralının transkripsiyonudur. Üç giriş kümesi × üç SOC kümesi = dokuz birleşim; kural başına AND=min, çıktı kesme=min, birleştirme=max ve centroid seçilmiştir.'),
    H('Makaledeki kritik belirsizlik'),
    P('Makalenin yazılı açıklamaları SOC&lt;20 veya SOC&gt;80 durumunda bataryanın şarj/deşarj etmediğini bildirir [1, EMS akış ve FLC sonuç bölümleri]. Buna karşılık Şekil 3(d)’de düşük SOC + PV fazlası “şarj”, yüksek SOC + yük fazlası “deşarj” kuralına sahiptir. Bu güvenli yöndeki toparlanmayı engellemeyen farklı bir yorumdur. Dolayısıyla dokuz kuralın sayısal çıktısı ile metindeki tüm akımı kapatma savı matematiksel olarak özdeş değildir.'),
    P('İki referans yorumu bu nedenle ayrı tutulmuştur: (A) Şekil 3 FIS’in çıplak çıktısı; (B) makaledeki yazılı emniyet davranışının yalın katı kesme yaklaşımı. B yaklaşımının yazılı kısımdan türetilmiş <b>yorum</b> olduğu, yayınlanmış orijinal MATLAB koduyla doğrulanmadığı açıkça belirtilir.'),
    H('Kaynak değerlerine ilişkin kontrol'),
    P('Makale, Fig. S6 için balance=−1 ve SOC=0, 100 durumlarında sırasıyla yaklaşık +0,00494 ve −0,00494 komutlardan söz eder [1]. Şekil 3 kural tabanının Python çıktısı aynı girişlerde −0,666668 ve 0,000000’dır. Sayısal uyuşmazlık, kaynakta açıklanmayan veya çelişen ayrıntıların varlığına işaret eder; <b>Fig. S6 nicel olarak yeniden üretildi</b> iddiasında bulunulmaz.'))
pg()
# Page 5
add(H('5. Reproduction Methodology — Yeniden gerçekleştirme'),
    P('Orijinal Simulink/MPPT güç katının tamamının yeniden oluşturulması yerine ders yönergesindeki minimum yeniden gerçekleştirme yaklaşımına uygun biçimde FIS alt sistemine odaklanılmıştır. Kod sıfırdan Python/NumPy ile yazılmış, MATLAB’dan FIS dosyası veya yayımlanmamış özgün kod kullanılmamıştır.'),
    P('<b>1. Tanım evrenleri:</b> balance∈[−1,1], SOC∈[0,100], c/d∈[−1,1]. <b>2. Üçgen parametreleri:</b> balance ve çıktı için (−2,−1,0),(−1,0,1),(0,1,2); SOC için (−50,0,50),(0,50,100),(50,100,150). <b>3. Kurallar:</b> Şekil 3(d)’den dokuz satır. <b>4. Çıkarım:</b> Mamdani min/max. <b>5. Durulaştırma:</b> centroid.'),
    P('<b>Ek varsayım:</b> Makale balance girdisini normalize [-1,1] gösterir fakat fiziksel Pload−Ppv farkının tam kW ölçeğini burada kullanacağımız biçimde sayısallaştırmaz. Bu projede balance=clip((Pload−Ppv)/20 kW,−1,1) alınmıştır. 20 kW ölçek makalede doğrulanmış parametre değildir.'),
    H('Fig. 3 tutarlılık ve kontrol örnekleri'),
    tbl([['Balance','SOC','FIS komutu','Katı kesme','Önerilen'],
         ['−1 (PV fazla)','0%','−0,66667','0','−0,66667'],
         ['0 (denge)','50%','0,00000','0','0'],
         ['+1 (yük fazla)','100%','+0,66667','0','+0,66667'],
         ['+0,4 (yük fazla)','18%','+0,06302','0','0']], [123,52,93,102,112]),
    P('Son satır demo.py --pv 15 --load 23 --soc 18 komutuna karşılık gelir. Kaynakla karşılaştırılabilir her sayısal giriş ayrıca experiments/run_experiments.py ile results/tables/paper_anchor_checks.csv içinde bulunur.'),
    H('Doğrulama'),
    P('tests/test_controller.py testleri; dokuz kuralın eşleşmesini, üçgen parametrelerini, kural yönlerini, sınır politikası ile Fig. 3 farkını, yeni kısıtın yönlü güvenliğini, sınır dışı/NaN girişlerinin reddini ve günlük enerji bilançosu Ppv + Pbatt + Pgrid = Pload tutarlılığını doğrular. Tüm testler Python unittest ile otomatik çalıştırılır.'),
    P('<b>Tekrarlanabilir komutlar:</b> python -m pip install -r requirements.txt ; python -m unittest discover -s tests -v ; python demo.py --pv 15 --load 23 --soc 18 ; python -m experiments.run_experiments.','small'))
pg()
# Page 6
add(H('6. Proposed Extension — Yönlü yumuşak SOC zarfı'),
    P('Makalenin kendisi SOC sınırlarında batarya güvenliğini amaçlamaktadır. Bu projede yenilik “SOC güvenliğini ilk defa sağlamak” değil, <b>aynı dokuz kurala dokunmadan, çıktı katmanında yön-duyarlı ve yumuşak bir geçiş tanımlamak</b>tır. Böylece katı kesme nedeniyle alt/üst bant dışında kalan bataryanın toparlanma yönündeki enerji alışverişi korunur.'),
    P('<b>Deşarj (u&gt;0):</b> g = clip((SOC−20)/w,0,1). <b>Şarj (u&lt;0):</b> g = clip((80−SOC)/w,0,1). <b>Geliştirilmiş komut:</b> u_new = g × u_FIS. Bu deneylerin ana sürümünde w=10 SOC-yüzde-puanıdır; w∈{5,10,15,20} ile ayrıca ablation yapılmıştır.'),
    tbl([['SOC / komut yönü','Katı politika','Önerilen yaklaşım'],
         ['SOC %10, PV fazlası (şarj)','Komut 0','Şarj (toparlanma) açık'],
         ['SOC %10, yük fazlası (deşarj)','Komut 0','Deşarj engelli'],
         ['SOC %90, yük fazlası (deşarj)','Komut 0','Deşarj (toparlanma) açık'],
         ['SOC %90, PV fazlası (şarj)','Komut 0','Şarj engelli']], [160,133,189]),
    P('Yeni yaklaşım, fiziksel batarya sağlığı hakkında denenmiş ticari garanti vermez. Lityum iyon bataryaların güvenli şarj/deşarj sınırları gerçek hücre gerilimi, sıcaklık, üretici kuralları ve Battery Management System (BMS) kısıtlarına da bağlıdır. Buradaki SOC yüzdeleri makale kontrol hedefini takip eden basitleştirilmiş deney parametreleridir.'),
    H('Araştırma hipotezleri'),
    P('H1: Hem katı politika hem yönlü zarf tanımlı riskli yönlü komutları sıfıra indirebilir. H2: Yönlü zarf, bandın dışından bataryanın toparlanmasına izin verdiğinden katı politikanın aksine band dışında geçirilen adımları azaltabilir. H3: Geçiş genişliğinin artışı batarya enerji çevrimini azaltırken şebeke kullanımını artırabilir. H4: Ölçüm gürültüsünde yumuşak zarf, katı kapat/aç politikası karşısında daha küçük ardışık komut sıçramaları üretebilir.'),
    P('Bu hipotezler gerçek saha verisinde değil kontrollü sayısal simülasyonda değerlendirilir.','fine'))
pg()
# Page 7
add(H('7. Experimental Setup — Deney kurulumu'),
    P('Aynı PV/yük girişleri, aynı başlangıç SOC ve aynı plant varsayımları tüm yöntemlere verilmiştir. Deterministik 24 saatlik profiller src/simulator.py ile üretilmiştir; tohumlar 2, 7, 14, 42, 101, 2026; SOC başlangıçları %10, %19, %25, %50, %75, %81, %90. Her eşlenik durumda Fig. 3 FIS, metin-kesme ve önerilen yöntem çalıştırılmıştır: 6×7=42 eşlenik durum ve 42×3=126 günlük koşu.'),
    tbl([['Parametre','Değer','Kaynağı / açıklama'],
         ['Örnekleme','15 dakika, 96 adım/gün','Proje varsayımı'],
         ['Batarya kapasitesi','50 kWh','Proje varsayımı; 500 Ah ile aynı değildir'],
         ['Batarya güç üst sınırı','8 kW','Proje varsayımı'],
         ['Şarj ve deşarj verimi','%95 / %95','Proje varsayımı'],
         ['Güç farkı normalizasyonu','20 kW','Proje varsayımı'],
         ['Geçiş genişliği','10 SOC puanı','Önerilen katkı parametresi'],
         ['FIS çözünürlüğü','1001 nokta','Sayısal centroid yaklaşımı']], [145,145,192]),
    P('<b>Çıktılar:</b> Güvenli yönde olmayan işlem sayısı (SOC≤20 iken deşarj veya SOC≥80 iken şarj), SOC bandı dışındaki adım sayısı, şebekeden çekilen/şebekeye verilen kWh ve batarya enerji çevrimi. Riskli yön sayacı eklenen güvenlik filtresi tarafından tasarımsal olarak sıfırlanabileceği için <i>bağımsız performans doğrulaması yerine</i> koşul kontrol testi olarak ele alınmalıdır.'),
    H('İkinci deney: ölçüm gürültüsü ve ablation'),
    P('Ölçüm gürültüsü deneyinde true SOC=%20,%22,%78,%80 çevresinde σ=1,5 SOC puan Gauss ölçüm gürültüsü eklenmiş; her moda aynı 401 rastgele ölçüm uygulanmıştır. Ardışık denetleyici komutlarının mutlak değişiminin ortalaması raporlanır. Ayrı deneyde geçiş genişliği w=5,10,15,20 için aynı 42 senaryo çalıştırılır.'),
    P('<b>Temel sınır:</b> Bu simülatör şebeke akımı THD, inverter harmonikleri, MPPT, hücre BMS veya elektromanyetik geçici rejimleri hesaplamaz. Referans çalışmanın PI/FLC karşılaştırmasındaki fiziksel göstergeler karşılaştırma tablosuna taşınmamıştır.','fine'))
pg()
# Page 8
add(H('8. Results — Eşlenik deneyler'),
    tbl([['Ölçüt','Figure 3 FIS','Metin kesme','Önerilen'],
         ['Riskli yön toplamı',str(M['fig3_fis']['unsafe_direction_steps_total']),str(M['text_cutoff']['unsafe_direction_steps_total']),str(M['proposed']['unsafe_direction_steps_total'])],
         ['Bant dışı adım',str(M['fig3_fis']['outside_band_steps_total']),str(M['text_cutoff']['outside_band_steps_total']),str(M['proposed']['outside_band_steps_total'])],
         ['Ort. şebeke ithalatı, kWh',str(M['fig3_fis']['mean_grid_import_kwh']),str(M['text_cutoff']['mean_grid_import_kwh']),str(M['proposed']['mean_grid_import_kwh'])],
         ['Ort. şebeke ihracatı, kWh',str(M['fig3_fis']['mean_grid_export_kwh']),str(M['text_cutoff']['mean_grid_export_kwh']),str(M['proposed']['mean_grid_export_kwh'])],
         ['Ort. batarya throughput, kWh',str(M['fig3_fis']['mean_battery_throughput_kwh']),str(M['text_cutoff']['mean_battery_throughput_kwh']),str(M['proposed']['mean_battery_throughput_kwh'])]], [182,101,98,101]),
    P('42 eşlenik girdi profilinin her birinde üç yöntem farklı SOC evrimi üretmiştir. Katı kesme politikası tehlikeli yönde komutu engellese de başlangıçta SOC bandı dışında kalan bataryayı şarj/deşarj ettirmediğinden toparlanmayı sınırlamaktadır. Önerilen zarf aynı tanımlı riskli yön ölçütünü sıfır tutarken toparlayıcı yöndeki enerji alışverişini korur.'),
    H('Kontrol yüzeyi karşılaştırması'),
    fig('controller_surface_comparison.png',480),
    P('Şekil B. Aynı Mamdani tabanı üzerine uygulanan üç yorumun çıktı yüzeyleri. Kesikli çizgiler SOC %20 ve %80 sınırlarını gösterir.','fine'),
    P('<b>Not:</b> 983 sayısı makalenin kendi kontrolcüsünün raporlanmış ihlal sayısı değildir; bizim Şekil 3 FIS uyarlamasının <i>bu simülatörle</i> ölçülen “riskli yön” sayısıdır. Geliştirilmiş yöntemin başarısı makaleye karşı değil, açık tanımlı yöntem varyantlarına karşı sunulmalıdır.','small'))
pg()
# Page 9
add(H('9. Results — Gürültü, parametre ve örnek zaman serisi'),
    P('SOC sınırında rastgele ölçüm oynaklığı katı kesme yaklaşımında komutu sıfır/aktif arasında değiştirebilir. Aşağıda veriyle kaydedilmiş ortalama ardışık komut değişimi yer alır; küçük değer daha az komut sıçraması demektir. Ancak daha küçük genlik, kontrol yeteneğinin her zaman daha iyi olduğu anlamına gelmez.'),
    tbl([['Gerçek SOC / denge','Fig3 FIS','Katı kesme','Önerilen'],
         ['%20 / yük fazlası']+[f"{next(x for x in NOISE if x['true_soc']==20 and x['normalized_balance']==1 and x['mode']==m)['mean_abs_step_change']:.6f}" for m in ('fig3_fis','text_cutoff','proposed')],
         ['%80 / PV fazlası']+[f"{next(x for x in NOISE if x['true_soc']==80 and x['normalized_balance']==-1 and x['mode']==m)['mean_abs_step_change']:.6f}" for m in ('fig3_fis','text_cutoff','proposed')]], [182,101,98,101]),
    fig('noise_robustness.png',420),
    H('Ablation: koruma genişliğinin etkisi'),
    tbl([['Geçiş genişliği','Bant dışı adım','Ort. ithalat kWh','Ort. çevrim kWh']]+[
        [str(x['guard_width_soc_points']),str(x['outside_band_steps_total']),str(x['mean_grid_import_kwh']),str(x['mean_battery_throughput_kwh'])] for x in ABL], [120,120,123,119]),
    P('Geçiş genişliği yükseldikçe bataryadan geçiş yapan toplam enerji azalmakta ve şebeke ithalatı artmaktadır. Bu eğilim kontrolcünün beklenen ödünleşimidir: daha temkinli batarya kullanımı daha fazla şebeke gücü gerektirebilir.','small'))
pg()
# Page 10
add(H('10. Discussion — Değerlendirme'),
    P('Bu çalışmanın ana sonucu üç farklı iddiayı birbirinden ayırmasıdır: <b>(i)</b> Makalenin Şekil 3’te gösterdiği dokuz Mamdani kuralını sayısal olarak işletmek, <b>(ii)</b> makalenin metinsel SOC sınır politikasını idealize edilmiş katı kesme olarak uygulamak ve <b>(iii)</b> özgün yönlü/yumuşak geçiş tanımlamak. İkinci yöntem kural tablosunun birebir tekrarı değil, metinden türetilmiş bir alternatif yorumdur.'),
    P('Önerilen yaklaşımda bant dışında geçirilen adım sayısının düşmesi, başlangıç SOC değerleri %10 veya %90 olduğunda toparlayıcı akışların devam edebilmesinden kaynaklanır. Katı kesme politikası bu durumlarda sistemi bandın dışında kilitleyebilir. Karşılaştırmanın bu sonucu simülatörün batarya kullanımına ilişkin basit varsayımlarına bağlıdır. Gerçek BMS politikaları farklı kararlar verebilir.'),
    P('Şekil 3’ün çakışan üyelik fonksiyonları çok sayıda kuralın eşzamanlı etkinleşmesine yol açar; centroid komutu temiz bir “şarj/şarj etme” anahtarından farklı olarak düşük genlikli kontrol üretebilir. Örneğin Fig. 3 FIS ve yazılı Fig. S6 değerleri uyuşmazlığı, yayımlanmış modelin çıkarım ve uç durum davranışını tek başına makale görsellerinden kesin eşlemek için yeterli veri bulunmadığını göstermektedir.'),
    H('11. Limitations — Sınırlılıklar'),
    P('1) Orijinal Simulink enerji/güç elektroniği sistemi, MPPT ve PI/THD karşılaştırması yoktur. 2) 24 saatlik gerçek Nilai saha verileri yerine sentetik profil kullanılmıştır. 3) Bataryanın sıcaklığı, hücre gerilimi, aging, BMS güvenliği ve elektrik tarifeleri hesaplanmaz. 4) Kodun güç ölçeği ve 50 kWh–8 kW batarya parametreleri varsayımdır. 5) Şekil 3 üzerinden çıkarılan üyelik üçgenlerinin sayısal doğruluğu, orijinal FIS dosyası olmadığından sınırlıdır. 6) Kaynak metni ile kural editöründeki SOC sınırı davranışı tutarsız görünmektedir.'),
    P('7) Güvenli yönün mutlak fiziksel uygunluğu için üretici BMS kuralları gereklidir. 8) Ölçüm gürültüsü sentetiktir ve yalnızca çıkış kararlılığı için ön test niteliğindedir. 9) Bu sonuçlar sahaya genellenemez, kontrol tasarımının kontrollü örnekleridir.'),
    H('Şeffaflık ve tekrar üretilebilirlik'),
    P('Deney üretecinin rastgele tohumları, bütün kontrol parametreleri, CSV/JSON sonuçları ve görsel üretim komutu depoya dahil edilmiştir. Deneyler gerçek kod tarafından çalıştırılmıştır; sayılar rapor metnine elle tahminle yazılmamıştır.','small'))
pg()
# Page 11
add(H('12. Conclusion — Sonuç ve ileri çalışma'),
    P('Bu dönem projesinde iki giriş, bir çıktı, üçer üçgen üyelik fonksiyonu ve dokuz kuraldan oluşan Mamdani EMS alt sistemi yeniden gerçekleştirilmiştir. Referans yayın ile elde edilen uyumsuz nümerik durumlar gizlenmeden belgelenmiş; kaynak metninden türetilen katı SOC sınır politikası ve yeni yönlü yumuşak güvenlik zarfı karşılaştırılmıştır.'),
    P(f"42 eşlenik senaryonun her birinde üç yöntem çalıştırıldığında önerilen yaklaşımda riskli yönlü adım sayısı {M['proposed']['unsafe_direction_steps_total']} ve SOC bandı dışında geçirilen toplam adım {M['proposed']['outside_band_steps_total']} olmuştur. Katı kesme yorumunda ikinci metrik {M['text_cutoff']['outside_band_steps_total']} seviyesindedir. Buna karşılık önerilen kontrolcü daha yüksek batarya çevrimi ile çalışır; enerji kaynağı tercihine ilişkin kesin üstünlük iddiasında bulunulmaz."),
    P('Gelecekte yazarların orijinal .fis dosyası ve ölçülmüş PV/yük verileri elde edilerek gerçek model parametreleri, SOC geçişleri ve THD/PI performansı ayrı ayrı doğrulanmalıdır. Bu çalışmanın amacı doğrulanmış fiziksel optimizasyon sonucu değil, açıklanabilir bulanık mantık alt sisteminin yeniden gerçekleştirilmesi ve kontrollü bir mühendislik uzantısının değerlendirilmesidir.'),
    H('Generative AI Usage Disclosure'),
    P('ChatGPT; bilimsel kaynakların aranması/özetlenmesi, Python kodu ve test taslakları, hata ayıklama, sentetik deneylerin tasarlanması/çalıştırılması, grafiklerin üretilmesi, teknik raporun ve slaytların ilk metinlerinin hazırlanmasında yardımcı araç olarak kullanılmıştır. Gerçek deney sonuçları Python scriptiyle üretilmiştir. Öğrenci bütün kodu, bilimsel iddiaları ve canlı gösterimi teslim öncesinde inceleyip doğrulamalıdır.'),
    H('References — IEEE formatı'),
    P('[1] M. Nur-E-Alam et al., “Optimization of energy management in Malaysian microgrids using fuzzy logic-based EMS scheduling controller,” <i>Scientific Reports</i>, vol. 15, art. 995, 2025. doi: 10.1038/s41598-024-82360-4.','small'),
    P('[2] L. A. Zadeh, “Fuzzy sets,” <i>Information and Control</i>, vol. 8, no. 3, pp. 338–353, 1965. doi: 10.1016/S0019-9958(65)90241-X.','small'),
    P('[3] E. H. Mamdani and S. Assilian, “An experiment in linguistic synthesis with a fuzzy logic controller,” <i>International Journal of Man-Machine Studies</i>, vol. 7, no. 1, pp. 1–13, 1975. doi: 10.1016/S0020-7373(75)80002-2.','small'),
    P('[4] D. Arcos-Avilés, J. Pascual, L. Marroyo, P. Sanchis, and F. Guinjoan, “Fuzzy logic-based energy management system design for residential grid-connected microgrids,” <i>IEEE Trans. Smart Grid</i>, vol. 9, no. 2, pp. 530–543, 2018. doi: 10.1109/TSG.2016.2555245.','small'),
    P('[5] M. Rodriguez, D. Arcos-Aviles, and W. Martinez, “Fuzzy logic-based energy management for isolated microgrid using meta-heuristic optimization algorithms,” <i>Applied Energy</i>, vol. 335, art. 120771, 2023. doi: 10.1016/j.apenergy.2023.120771.','small'),
    P('[6] A. El Zerk and M. Ouassaid, “Real-Time Fuzzy Logic Based Energy Management System for Microgrid Using Hardware in the Loop,” <i>Energies</i>, vol. 16, no. 5, art. 2244, 2023. doi: 10.3390/en16052244.','small'))


def decorate(c,doc):
    c.saveState()
    w,h=A4;c.setStrokeColor(colors.HexColor('#d6e4e6'))
    c.line(42,42,w-42,42);c.setFont('DV',8);c.setFillColor(GRAY)
    c.drawString(43,28,'Bulanık Mantık • Microgrid Fuzzy EMS • 10 Kasım 2026')
    c.drawRightString(w-43,28,f'Sayfa {doc.page}')
    c.restoreState()

if __name__=='__main__':
    out=R/'report'/'Teknik_Rapor_Microgrid_Fuzzy_EMS.pdf'
    pdf=SimpleDocTemplate(str(out),pagesize=A4,leftMargin=45,rightMargin=45,topMargin=45,bottomMargin=53,
                          title='Mamdani Microgrid Fuzzy EMS — Teknik Rapor',author='Bulanık Mantık Dönem Projesi')
    pdf.build(S,onFirstPage=decorate,onLaterPages=decorate)
    print('Report:',out)
