"""Generate editable PowerPoint from independently run experiment files."""
from pathlib import Path
import json
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'results/tables/summary.json').read_text(encoding='utf-8'))
M=DATA['modes'];N=DATA['noise_experiment'];ABL=DATA['guard_width_ablation']
prs=Presentation();prs.slide_width=Inches(13.33);prs.slide_height=Inches(7.5)
NAVY=RGBColor(20,50,76);TEAL=RGBColor(14,117,108);INK=RGBColor(43,56,71)
GRAY=RGBColor(98,112,126);LIGHT=RGBColor(236,245,244);WHITE=RGBColor(255,255,255)

def shape(s,x,y,w,h,fill=LIGHT):
    o=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    o.fill.solid();o.fill.fore_color.rgb=fill;o.line.fill.background()
    return o

def txt(s,t,x,y,w,h,font=19,bold=False,color=INK,center=False):
    tbox=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    tf=tbox.text_frame;tf.clear();tf.word_wrap=True
    p=tf.paragraphs[0];p.text=str(t);p.font.name='Aptos';p.font.size=Pt(font);p.font.bold=bold;p.font.color.rgb=color
    p.alignment=PP_ALIGN.CENTER if center else PP_ALIGN.LEFT
    return tbox

def slide(title,kicker=''):
    s=prs.slides.add_slide(prs.slide_layouts[6]);shape(s,0,0,13.33,.10,TEAL)
    txt(s,kicker.upper(),.68,.39,11,.26,10,True,TEAL)
    txt(s,title,.66,.82,12,.72,29,True,NAVY)
    shape(s,.66,7.03,12,.02,RGBColor(220,231,235))
    txt(s,'MICROGRID FUZZY EMS  |  DÖNEM PROJESİ',.68,7.11,7,.2,8,color=GRAY)
    txt(s,str(len(prs.slides)),12.08,7.10,.3,.25,8,color=GRAY,center=True)
    return s

def bullets(s,items,y=1.8,fontsize=20,spacing=.90):
    for i,t in enumerate(items):
        shape(s,.84,y+i*spacing+.16,.12,.12,TEAL)
        txt(s,t,1.12,y+i*spacing,11.5,.74,fontsize)

def picture(s,path,x,y,w,h):
    s.shapes.add_picture(str(ROOT/'results/figures'/path),Inches(x),Inches(y),width=Inches(w),height=Inches(h))

def mini(s,label,value,x,y,w=3.7,foot=None):
    shape(s,x,y,w,1.75,LIGHT)
    txt(s,label,x+.19,y+.15,w-.38,.36,13,True,GRAY)
    txt(s,str(value),x+.19,y+.53,w-.38,.69,30,True,NAVY)
    if foot:txt(s,foot,x+.19,y+1.27,w-.38,.32,11,color=GRAY)

s=slide('Mikroşebekelerde Mamdani Bulanık Enerji Yönetimi','Bulanık Mantık proje sunumu')
txt(s,'Şekil 3 yeniden gerçekleştirmesi ve SOC sınırlarında yönlü yumuşak kontrol',.82,1.92,11.7,.84,22)
shape(s,.81,3.3,11.75,1.39)
txt(s,'2 giriş  ×  3 dilsel küme  →  9 IF–THEN kuralı  →  1 çıktı',1.03,3.77,11.24,.57,24,True,NAVY,True)
txt(s,'Can KARAHAN  |  1306210004  |  İÜC Bilgisayar Mühendisliği  |  Kasım 2026',.85,6.18,11.5,.4,16,color=GRAY)

s=slide('Problem: üretim ve tüketim sürekli değişiyor','Giriş')
bullets(s,['PV üretimi güneşe bağlıdır, yük talebi gün boyunca değişir.','Şebeke, batarya ve PV arasında anlık güç dengesi kurulmalıdır.','Bataryanın SOC sınırlarını gözetmeyen kararlar istenmeyen akışlar yaratabilir.','Bulanık mantık, uzman bilgisini anlaşılır kurallarla sayısallaştırır.'],fontsize=20,spacing=1.03)

s=slide('Literatür ve referans çalışma','İlgili çalışmalar')
bullets(s,['Zadeh (1965): bulanık kümelerde üyelik derecesi.','Mamdani & Assilian (1975): dilsel kurallarla kontrol.','Arcos-Avilés vd. (2018): şebeke bağlantılı mikroşebekede FLC ve SOC.','Rodriguez vd. (2023): izolasyonlu MG için bulanık EMS ve optimizasyon.','Nur-E-Alam vd. (2025): PV + batarya + şebekede FLC / PI karşılaştırması.'],fontsize=18,spacing=.9)

s=slide('2025 makalesi neyi yapıyor?','Referans makale')
bullets(s,['50 kW PV, 500 Ah batarya, şebeke ve yük üzerinde Simulink çalışması.','PV üretimi için MPPT, enerji yönetimi için Mamdani FIS.','PI denetleyiciyle harmonik bozulma (THD) karşılaştırması.','FLC için SOC koruması, PI için bazı THD üstünlükleri raporlanıyor.','Bu proje: güç elektroniğini değil FIS alt sistemini yeniden yapıyor.'],fontsize=18,spacing=.87)

s=slide('Kontrol sistemi: iki giriş, bir çıktı','Mimari')
labels=['PV üretimi\nPpv','Yük talebi\nPload','Normalize\ngüç dengesi','Mamdani\n9 kural','Batarya\nc/d komutu']
for i,label in enumerate(labels):
    x=.76+i*2.54;shape(s,x,2.8,2.3,1.17);txt(s,label,x+.12,3.05,2.07,.75,17,True,NAVY,True)
    if i<4:txt(s,'→',x+2.30,3.16,.25,.36,18,True,TEAL)
txt(s,'SOC (%) ikinci girdidir. Çıktı: negatif = şarj, pozitif = deşarj, sıfır = bekle.',1.08,5.08,11.6,.9,21)

s=slide('Üyelik fonksiyonları: düşük / orta / yüksek','Fuzzification')
picture(s,'membership_functions.png',.78,1.8,11.83,3.92)
txt(s,'Fig. 3’teki üçgensel kümelerin Python ile bağımsız çizimi.',1.00,6.06,11.2,.42,15,color=GRAY)

s=slide('3×3 = 9 IF–THEN kuralı','Rule base')
rows=[['Güç / SOC','Düşük','Orta','Yüksek'],['PV > Load','Şarj','Şarj','Bekle'],['PV < Load','Bekle','Deşarj','Deşarj'],['PV = Load','Bekle','Bekle','Bekle']]
for i,row in enumerate(rows):
    for j,label in enumerate(row):
        x=.78+j*3.12;y=2.0+i*.88
        shape(s,x,y,2.92,.71,TEAL if i==0 else LIGHT)
        txt(s,label,x+.08,y+.18,2.78,.37,16,True,WHITE if i==0 else NAVY,True)
txt(s,'Örnek: IF PV fazlası AND SOC düşük THEN şarj.',1.01,6.0,11.4,.4,19,True)

s=slide('Makale içinde kritik bir ayrım var','Bilimsel değerlendirme')
bullets(s,['Fig. 3(d): düşük SOC + PV fazlası ⇒ şarj; yüksek SOC + yük fazlası ⇒ deşarj.','Makale metni: SOC <%20 veya >%80 iken şarj/deşarj yok.','Fig. S6 sayısal örneği, Fig. 3 kural tabanımızdan aynı çıkmıyor.','Bu nedenle hem Fig. 3 FIS’i hem metinsel sınır yorumunu ayrı inceliyoruz.'],fontsize=19,spacing=1.10)
txt(s,'Fark gizlenmedi: gerçek .fis dosyası olmadan birebir sayısal tekrar iddia etmiyoruz.',1.0,6.26,11.2,.5,17,True,TEAL)

s=slide('Python’da yeniden gerçekleştirme','FIS hesaplama')
bullets(s,['1. Normalize denge ve SOC üyeliklerini hesapla.','2. Her kural için etkinlik = min(üyelik1, üyelik2).','3. Kural çıktısını min ile kes, bütün çıktıları max ile birleştir.','4. Centroid durulaştırma ile sürekli bir kontrol komutu üret.','5. Kaynak işaret yönünü ve enerji dengesini otomatik test et.'],fontsize=19,spacing=.94)

s=slide('Özgün katkı: yön-duyarlı yumuşak sınır','Proposed extension')
shape(s,.89,1.9,11.54,3.1)
txt(s,'Deşarj (u > 0):    g = clip((SOC − 20)/w, 0, 1)',1.3,2.25,10.8,.55,23,True,NAVY)
txt(s,'Şarj (u < 0):        g = clip((80 − SOC)/w, 0, 1)',1.3,3.13,10.8,.55,23,True,NAVY)
txt(s,'Yeni komut: u_yeni = g × u_FIS      (ana deney: w = 10)',1.3,4.1,10.8,.55,20,True,TEAL)
txt(s,'Riskli yöndeki işlem kapalı; SOC’yi güvenli banda döndüren yön açık.',1.03,5.50,11.2,.7,19)

s=slide('Üç politikayı neden karşılaştırıyoruz?','Fair comparison')
bullets(s,['Fig. 3 FIS: yayınlanmış dokuz kuralın doğrudan çıktısı.','Makale metni: band dışında akımı kapatan katı kural yorumu.','Önerilen: aynı FIS çıktısına yalnızca yumuşak yönlü güvenlik katmanı.','Tüm yöntemler aynı PV/yük profilleriyle ve aynı batarya modeliyle test edildi.'],fontsize=20,spacing=1.04)

s=slide('Tekrar üretilebilir deney kurulumu','Deney tasarımı')
mini(s,'Sentetik PV/yük profili','6 tohum',.86,1.94)
mini(s,'Başlangıç SOC','7 değer',4.85,1.94)
mini(s,'Toplam karşılaştırma','126 koşu',8.85,1.94)
bullets(s,['24 saat × 15 dakika = 96 adım / koşu.','50 kWh ve 8 kW batarya: proje varsayımları.','Ek olarak ölçüm gürültüsü ve 4 geçiş genişliği denenmiştir.'],y=4.2,fontsize=19,spacing=.78)

s=slide('Ölçülen gerçek Python sonuçları','Results')
mini(s,'Fig3 FIS riskli yön',M['fig3_fis']['unsafe_direction_steps_total'],.83,1.82)
mini(s,'Katı kesme riskli yön',M['text_cutoff']['unsafe_direction_steps_total'],4.82,1.82)
mini(s,'Önerilen riskli yön',M['proposed']['unsafe_direction_steps_total'],8.81,1.82)
txt(s,'SOC bandı dışında kalan toplam adım:',1.04,4.12,10.7,.35,19,color=GRAY)
txt(s,f"{M['fig3_fis']['outside_band_steps_total']}   /   {M['text_cutoff']['outside_band_steps_total']}   /   {M['proposed']['outside_band_steps_total']}",1.0,4.52,11.0,.71,27,True,NAVY)
txt(s,'Sırasıyla Fig3 / katı kesme / önerilen. Bant dışı başlangıçlar dahildir.',1.02,5.53,11.15,.54,17,color=GRAY)

s=slide('Kontrol yüzeyleri','Görsel sonuçlar')
picture(s,'controller_surface_comparison.png',.46,1.68,12.5,4.72)
txt(s,'Çizgiler: SOC %20 ve %80. Aynı FIS, üç farklı son-işlem yorumu.',.88,6.47,11.2,.4,14,color=GRAY)

s=slide('Ölçüm gürültüsünde komut değişimleri','Robustness')
picture(s,'noise_robustness.png',1.4,1.7,10.5,3.46)
for i,t in enumerate(['401 eşlenik ölçüm / koşul; SOC ölçüm gürültüsü σ=1,5 puan.',
                       'Yumuşak katmanda ani komut sıçramaları katı kesmeye göre daha küçük.',
                       'Ancak düşük komut değişimi tek başına fiziksel performans garantisi değildir.']):
    txt(s,t,1.02,5.23+i*.46,11.4,.41,15 if i<2 else 14,color=INK)

s=slide('Geçiş genişliği ve enerji ödünleşimi','Ablation')
rows=[['w (SOC puanı)','Ort. şebeke ithalatı kWh','Ort. batarya throughput kWh']]+[[str(z['guard_width_soc_points']),str(z['mean_grid_import_kwh']),str(z['mean_battery_throughput_kwh'])] for z in ABL]
for i,row in enumerate(rows):
    for j,val in enumerate(row):
        x=[1.0,4.4,8.6][j];w=[3.05,3.83,3.73][j];y=2.0+i*.76
        shape(s,x,y,w,.61,TEAL if i==0 else LIGHT)
        txt(s,val,x+.06,y+.14,w-.12,.33,15 if i==0 else 18,i==0,WHITE if i==0 else NAVY,True)
txt(s,'Daha geniş geçiş → batarya daha temkinli kullanılır, şebeke ithalatı artabilir.',1.1,6.18,11.2,.60,17,True,TEAL)

s=slide('Bir günlük örnek zaman serisi','Trajectory')
picture(s,'daily_trajectory.png',1.73,1.63,9.88,4.92)
txt(s,'Sentetik profil: tohum 42; başlangıç SOC %25.',1.1,6.58,11.2,.33,13,color=GRAY)

s=slide('Sınırlılıklar ve çıkarım','Discussion')
bullets(s,['Tam Simulink, MPPT, PI denetleyici ve THD analizi uygulanmadı.','Enerji profilleri sentetik; 20 kW normalizasyon ve 50 kWh kapasite varsayım.','Fig. S6 ile Fig. 3 kural tabanı arasında nümerik uyumsuzluk bulunuyor.','Yönlü güvenlik filtresi fiziki BMS doğrulamasının yerini alamaz.','Kazanç: kontrollü senaryoda yönlü toparlanma; bedel: batarya/şebeke ödünleşimi.'],fontsize=18,spacing=.84)

s=slide('Canlı demo, sonuç ve kaynakça','Savunma')
bullets(s,['python -m unittest discover -s tests -v   → 10/10 test',
           'python demo.py --pv 15 --load 23 --soc 18   → üç komut ve kurallar',
           'python -m experiments.run_experiments   → tablolar/grafikler',
           'Referans: doi:10.1038/s41598-024-82360-4',
           'Kaynaklar: Zadeh (1965), Mamdani (1975), Arcos (2018), Rodriguez (2023), El Zerk (2023).'],fontsize=16,spacing=.80)
txt(s,'AI açıklaması: ChatGPT taslak kod, testler, deney, metin ve görsel hazırlığında kullanıldı.',1.02,6.32,11.2,.51,14,True,TEAL)

if __name__=='__main__':
    out=ROOT/'presentation'/'Microgrid_Fuzzy_EMS_Sunum.pptx'
    prs.save(str(out))
    print(out, 'slides:',len(prs.slides))
