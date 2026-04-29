import csv
import os

db_path = r'D:\AntiGravity\舒酸與三高守護者\food_logic\data\food_database.csv'

# 各類食物資料庫清單
vegetables = [
    ["地瓜葉", "GREEN", "GREEN", "GREEN", "GREEN", "高纖低卡，有助穩定血糖與血壓。"],
    ["高麗菜", "GREEN", "GREEN", "GREEN", "GREEN", "百搭且安全的十字花科蔬菜。"],
    ["菠菜", "GREEN", "GREEN", "GREEN", "GREEN", "高營養價值，但若有結石體質需注意草酸。"],
    ["空心菜", "GREEN", "GREEN", "GREEN", "GREEN", "高鉀有助降血壓。"],
    ["青江菜", "GREEN", "GREEN", "GREEN", "GREEN", "富含鈣質，對長輩骨骼有益。"],
    ["小白菜", "GREEN", "GREEN", "GREEN", "GREEN", "熱量極低，適合三高族群。"],
    ["芥藍菜", "GREEN", "GREEN", "GREEN", "GREEN", "十字花科，營養豐富。"],
    ["大陸妹", "GREEN", "GREEN", "GREEN", "GREEN", "口感脆甜，百無禁忌。"],
    ["萵苣", "GREEN", "GREEN", "GREEN", "GREEN", "生菜沙拉常見，適合三高。"],
    ["韭菜", "GREEN", "GREEN", "GREEN", "GREEN", "富含膳食纖維，但氣味強烈。"],
    ["芹菜", "GREEN", "GREEN", "GREEN", "GREEN", "降血壓好幫手。"],
    ["香菜", "GREEN", "GREEN", "GREEN", "GREEN", "提味用，對三高無害。"],
    ["九層塔", "GREEN", "GREEN", "GREEN", "GREEN", "香辛料，適量食用安全。"],
    ["南瓜", "GREEN", "GREEN", "YELLOW", "GREEN", "屬於澱粉類，糖尿病患者需替換主食份量。"],
    ["馬鈴薯", "GREEN", "GREEN", "YELLOW", "GREEN", "屬於澱粉，容易使血糖升高，建議煮熟放涼抗性澱粉化。"],
    ["地瓜", "GREEN", "GREEN", "YELLOW", "GREEN", "膳食纖維高，但糖尿病需注意份量。"],
    ["芋頭", "GREEN", "GREEN", "YELLOW", "GREEN", "澱粉類，適量食用。"],
    ["蘿蔔", "GREEN", "GREEN", "GREEN", "GREEN", "水分多熱量低，適合三高。"],
    ["紅蘿蔔", "GREEN", "GREEN", "GREEN", "GREEN", "富含β胡蘿蔔素。"],
    ["洋蔥", "GREEN", "GREEN", "GREEN", "GREEN", "抗氧化，對心血管有益。"],
    ["冬瓜", "GREEN", "GREEN", "GREEN", "GREEN", "利尿消水腫，高血壓好朋友。"],
    ["苦瓜", "GREEN", "GREEN", "GREEN", "GREEN", "有助於穩定血糖。"],
    ["絲瓜", "GREEN", "GREEN", "GREEN", "GREEN", "水分豐富，適合長輩。"],
    ["大黃瓜", "GREEN", "GREEN", "GREEN", "GREEN", "清熱解暑，適合涼拌。"],
    ["小黃瓜", "GREEN", "GREEN", "GREEN", "GREEN", "低卡高纖，三高友善。"],
    ["茄子", "GREEN", "GREEN", "GREEN", "GREEN", "富含花青素，對血管友善。"],
    ["番茄", "GREEN", "GREEN", "GREEN", "GREEN", "茄紅素對攝護腺與心血管好。"],
    ["青椒", "GREEN", "GREEN", "GREEN", "GREEN", "維生素C豐富。"],
    ["甜椒", "GREEN", "GREEN", "GREEN", "GREEN", "抗氧化能力強。"],
    ["四季豆", "YELLOW", "GREEN", "GREEN", "GREEN", "豆莢類普林偏中，痛風者宜適量。"],
    ["豌豆", "YELLOW", "GREEN", "GREEN", "GREEN", "普林中等，非急性期可吃。"],
    ["毛豆", "YELLOW", "GREEN", "GREEN", "GREEN", "植物蛋白豐富，痛風適量。"],
    ["蘆筍", "RED", "GREEN", "GREEN", "GREEN", "蔬菜中極少數普林偏高的食材，痛風患者需注意。"],
    ["竹筍", "GREEN", "GREEN", "GREEN", "GREEN", "高纖低卡，但草酸較高。"],
    ["玉米", "GREEN", "GREEN", "YELLOW", "GREEN", "屬於澱粉類，糖尿病需控量。"],
    ["玉米筍", "GREEN", "GREEN", "GREEN", "GREEN", "屬於蔬菜，低糖高纖。"],
    ["秋葵", "GREEN", "GREEN", "GREEN", "GREEN", "黏液對腸胃有益，適合三高。"],
    ["花椰菜", "GREEN", "GREEN", "GREEN", "GREEN", "十字花科之王，超級食物。"],
    ["青花菜", "GREEN", "GREEN", "GREEN", "GREEN", "抗癌抗發炎，營養極高。"],
    ["生鮮香菇", "YELLOW", "GREEN", "GREEN", "GREEN", "生鮮菇類普林未被濃縮，非痛風急性期可適量。"],
    ["金針菇", "YELLOW", "GREEN", "GREEN", "GREEN", "普林中等，促進腸胃蠕動。"],
    ["杏鮑菇", "YELLOW", "GREEN", "GREEN", "GREEN", "高蛋白低脂肪，痛風適量。"],
    ["黑木耳", "GREEN", "GREEN", "GREEN", "GREEN", "血管的清道夫，三高絕佳。"],
    ["乾香菇", "RED", "GREEN", "GREEN", "GREEN", "乾貨類普林濃縮度極高，痛風絕對禁忌。"]
]

fruits = [
    ["芭樂", "GREEN", "GREEN", "GREEN", "GREEN", "富含維生素 C 與纖維，有助排尿酸且糖分低。"],
    ["木瓜", "GREEN", "GREEN", "YELLOW", "GREEN", "對痛風與代謝好，但水果糖分高，糖尿病需控量。"],
    ["蘋果", "GREEN", "GREEN", "GREEN", "GREEN", "富含果膠與維生素，對三高與痛風皆友善。"],
    ["西瓜", "GREEN", "GREEN", "RED", "GREEN", "GI 值極高，糖尿病患者容易血糖狂飆。"],
    ["芒果", "GREEN", "GREEN", "RED", "GREEN", "糖分極高，糖尿病絕對需控量。"],
    ["荔枝", "GREEN", "GREEN", "RED", "GREEN", "糖分極高，不宜多吃。"],
    ["龍眼", "GREEN", "GREEN", "RED", "GREEN", "極高糖分，長輩淺嚐即止。"],
    ["香蕉", "GREEN", "GREEN", "YELLOW", "GREEN", "富含鉀有助血壓，但糖分不低，糖尿病宜一次半根。"],
    ["奇異果", "GREEN", "GREEN", "GREEN", "GREEN", "維生素與纖維豐富，適合所有族群。"],
    ["小番茄", "GREEN", "GREEN", "GREEN", "GREEN", "低糖高纖，非常適合取代一般水果。"],
    ["葡萄", "GREEN", "GREEN", "YELLOW", "GREEN", "糖分稍高，建議連皮少量吃。"],
    ["鳳梨", "GREEN", "GREEN", "YELLOW", "GREEN", "有助消化，但鳳梨酵素與高糖分需注意。"],
    ["火龍果", "GREEN", "GREEN", "GREEN", "GREEN", "果膠豐富，有助排便。"],
    ["柳丁", "GREEN", "GREEN", "YELLOW", "GREEN", "維生素C多，但榨汁會讓糖分飆高。"],
    ["橘子", "GREEN", "GREEN", "YELLOW", "GREEN", "富含鉀，糖尿病需控制在一顆。"],
    ["柚子", "GREEN", "YELLOW", "YELLOW", "GREEN", "會與多種血壓/血脂藥物產生交互作用，需特別注意！"],
    ["檸檬", "GREEN", "GREEN", "GREEN", "GREEN", "維生素C極高，適合泡水喝。"],
    ["草莓", "GREEN", "GREEN", "GREEN", "GREEN", "低糖高維生素C。"],
    ["櫻桃", "GREEN", "GREEN", "GREEN", "GREEN", "對痛風有輕微幫助，糖分中等。"],
    ["百香果", "GREEN", "GREEN", "GREEN", "GREEN", "高纖低糖，抗氧化極佳。"],
    ["水蜜桃", "GREEN", "GREEN", "YELLOW", "GREEN", "糖分偏高，柔軟好入口。"],
    ["哈密瓜", "GREEN", "GREEN", "RED", "GREEN", "甜度極高，糖尿病需嚴格限制。"],
    ["水梨", "GREEN", "GREEN", "YELLOW", "GREEN", "水分多，糖分中等。"],
    ["蓮霧", "GREEN", "GREEN", "GREEN", "GREEN", "水分多糖分低，適合長輩。"],
    ["釋迦", "GREEN", "GREEN", "RED", "GREEN", "水果中的糖分炸彈，糖尿病大忌。"]
]

meats = [
    ["雞胸肉", "YELLOW", "GREEN", "GREEN", "GREEN", "優質低脂蛋白質，普林中等。"],
    ["帶皮雞腿", "YELLOW", "GREEN", "GREEN", "YELLOW", "脂肪含量較高，高血脂患者宜去皮食用。"],
    ["去皮雞腿", "YELLOW", "GREEN", "GREEN", "GREEN", "去皮後脂肪減少，是不錯的蛋白質來源。"],
    ["雞翅", "YELLOW", "GREEN", "GREEN", "RED", "幾乎都是皮與脂肪，高血脂應避免。"],
    ["豬瘦肉", "YELLOW", "GREEN", "GREEN", "GREEN", "富含維生素B群，適合三高族群。"],
    ["豬五花", "YELLOW", "RED", "GREEN", "RED", "飽和脂肪極高，強烈不建議高血壓與高血脂食用。"],
    ["松阪豬", "YELLOW", "GREEN", "GREEN", "YELLOW", "油花豐富，飽和脂肪略高，需控制份量。"],
    ["控肉", "YELLOW", "RED", "YELLOW", "RED", "高飽和脂肪與高鈉，對心血管負擔極重。"],
    ["豬腳", "YELLOW", "RED", "YELLOW", "RED", "膠原蛋白多但也伴隨大量脂肪與滷汁的鈉。"],
    ["豬肝", "RED", "GREEN", "GREEN", "YELLOW", "內臟類普林與膽固醇極高，絕對禁忌。"],
    ["豬大腸", "RED", "RED", "GREEN", "RED", "高脂肪、高膽固醇、高普林，痛風與高血脂大忌。"],
    ["牛腱", "YELLOW", "GREEN", "GREEN", "GREEN", "低脂肪紅肉，適合三高，但痛風患者不宜過量。"],
    ["牛五花", "YELLOW", "RED", "GREEN", "RED", "脂肪含量極高，不適合高血脂與高血壓。"],
    ["牛排", "YELLOW", "GREEN", "GREEN", "YELLOW", "視部位而定，通常含有不少飽和脂肪。"],
    ["羊肉", "YELLOW", "GREEN", "GREEN", "YELLOW", "溫補食材，但常以羊肉爐(高油高普林)形式出現。"],
    ["鴨肉", "YELLOW", "GREEN", "GREEN", "YELLOW", "脂肪較高，痛風患者適量。"],
    ["鵝肉", "YELLOW", "GREEN", "GREEN", "YELLOW", "與鴨肉類似，普林偏中高。"]
]

seafoods = [
    ["虱目魚肚", "RED", "GREEN", "GREEN", "YELLOW", "普林值偏高；雖富含魚油，但熱量與飽和脂肪需控制。"],
    ["白帶魚", "RED", "GREEN", "GREEN", "GREEN", "普林極高，痛風患者應避免。"],
    ["透抽", "YELLOW", "GREEN", "GREEN", "YELLOW", "膽固醇偏高，高血脂患者需注意份量。"],
    ["花枝", "YELLOW", "GREEN", "GREEN", "YELLOW", "與透抽類似，需注意膽固醇。"],
    ["魷魚", "YELLOW", "GREEN", "GREEN", "YELLOW", "膽固醇高，但含有牛磺酸。"],
    ["鮭魚", "YELLOW", "GREEN", "GREEN", "GREEN", "富含 Omega-3，有助心血管，但普林中等。"],
    ["鱈魚", "YELLOW", "GREEN", "GREEN", "GREEN", "肉質軟嫩，好消化。"],
    ["吳郭魚", "YELLOW", "GREEN", "GREEN", "GREEN", "優質蛋白質，但要注意養殖與烹調方式。"],
    ["秋刀魚", "RED", "GREEN", "GREEN", "YELLOW", "普林偏高，魚油雖好但整體熱量不可忽視。"],
    ["鯖魚", "RED", "GREEN", "GREEN", "YELLOW", "健康魚油多，但也是高普林魚類。"],
    ["鱸魚", "YELLOW", "GREEN", "GREEN", "GREEN", "術後復原好物，適合長輩。"],
    ["蛤蜊", "RED", "GREEN", "GREEN", "GREEN", "帶殼海鮮普林偏高，煮湯尤甚。"],
    ["牡蠣", "RED", "GREEN", "GREEN", "YELLOW", "高普林，且含有膽固醇。"],
    ["蚵仔", "RED", "GREEN", "GREEN", "YELLOW", "同牡蠣，夜市小吃常見。"],
    ["白灼蝦", "RED", "GREEN", "GREEN", "YELLOW", "海鮮類普林偏高，高血脂需注意膽固醇。"],
    ["草蝦", "RED", "GREEN", "GREEN", "YELLOW", "蝦類普林高。"],
    ["螃蟹", "RED", "GREEN", "GREEN", "RED", "蟹膏含有極高膽固醇與普林。"],
    ["干貝", "RED", "GREEN", "GREEN", "GREEN", "海鮮類高普林。"],
    ["小魚乾", "RED", "GREEN", "GREEN", "GREEN", "普林極度濃縮的乾貨，痛風大忌。"],
    ["柴魚片", "RED", "GREEN", "GREEN", "GREEN", "熬湯好物，但普林非常高。"]
]

carbs = [
    ["白米飯", "GREEN", "GREEN", "YELLOW", "GREEN", "精緻澱粉易使血糖快速升高，需控量（限半碗）。"],
    ["糙米飯", "GREEN", "GREEN", "GREEN", "GREEN", "高纖、低 GI，比白米更適合三高族群。"],
    ["五穀飯", "YELLOW", "GREEN", "GREEN", "GREEN", "營養豐富，但部分穀物含普林，痛風急性期少吃。"],
    ["白麵條", "GREEN", "GREEN", "YELLOW", "GREEN", "精緻澱粉，易升血糖。"],
    ["冬粉", "GREEN", "GREEN", "YELLOW", "GREEN", "綠豆澱粉，本身熱量不低，且極易吸附湯汁油脂。"],
    ["米粉", "GREEN", "GREEN", "YELLOW", "GREEN", "與白飯相似，若為炒米粉則油脂與鈉都會超標。"],
    ["燕麥", "GREEN", "GREEN", "GREEN", "GREEN", "有助降膽固醇，但仍是澱粉，需替換主食。"],
    ["吐司", "GREEN", "YELLOW", "RED", "YELLOW", "精緻澱粉且含奶油與糖，糖尿病應避免。"],
    ["全麥麵包", "GREEN", "GREEN", "YELLOW", "GREEN", "比白吐司好，但市售多半仍有不少油脂。"],
    ["饅頭", "GREEN", "GREEN", "YELLOW", "GREEN", "純澱粉，影響血糖。"],
    ["水餃", "YELLOW", "YELLOW", "YELLOW", "YELLOW", "外皮澱粉厚，內餡肥肉多且含鹽，隱形地雷。"],
    ["鍋貼", "YELLOW", "RED", "YELLOW", "RED", "與水餃相同，且經過大量油脂煎烤。"]
]

others = [
    ["雞蛋", "GREEN", "GREEN", "GREEN", "YELLOW", "每天一顆很安全，高血脂者不用刻意完全不吃。"],
    ["豆腐", "GREEN", "GREEN", "GREEN", "GREEN", "優質植物蛋白，痛風患者適量吃很安全。"],
    ["無糖豆漿", "GREEN", "GREEN", "GREEN", "GREEN", "優質植物蛋白，有助於降低心血管負擔。"],
    ["豆干", "YELLOW", "GREEN", "GREEN", "GREEN", "普林稍高於豆腐，但仍是好食材。"],
    ["牛奶", "GREEN", "GREEN", "GREEN", "YELLOW", "有助降尿酸！但全脂牛奶對高血脂需注意，建議低脂。"],
    ["無糖優格", "GREEN", "GREEN", "GREEN", "GREEN", "腸道益生菌，對健康全面有益。"],
    ["滷肉飯", "YELLOW", "RED", "RED", "RED", "精緻澱粉加上高油、高鹽的滷汁，極易使三高惡化。"],
    ["鹹水雞", "YELLOW", "RED", "GREEN", "YELLOW", "調味過鹹（鈉含量高），但蛋白質本體與蔬菜類對血糖友善。"],
    ["菜脯蛋", "GREEN", "RED", "GREEN", "YELLOW", "醃漬菜脯鹽分極高，油煎蛋含油量多，高血壓/高血脂不宜。"],
    ["火鍋湯底", "RED", "RED", "RED", "RED", "久煮湯底融出大量普林、高鈉且高熱量，絕對禁忌。"],
    ["蚵仔煎", "RED", "RED", "RED", "RED", "勾芡醬汁高糖、高鹽，蚵仔普林高且重油煎炸。"],
    ["臭豆腐", "YELLOW", "RED", "GREEN", "RED", "油炸物飽和脂肪多，泡菜與沾醬鈉含量爆表。"],
    ["烤香腸", "YELLOW", "RED", "RED", "RED", "高飽和脂肪、高鈉，且加工肉品不利於尿酸代謝。"],
    ["珍珠奶茶", "RED", "RED", "RED", "RED", "高果糖漿快速生成尿酸，引發血糖血脂失控。"],
    ["蚵仔麵線", "RED", "RED", "RED", "RED", "勾芡(高糖)、大腸/蚵仔(高普林)、重鹹(高鈉)，慢性病天敵。"],
    ["肉圓", "YELLOW", "RED", "RED", "RED", "外皮精緻澱粉且油炸，醬汁高鹽高糖。"],
    ["碗粿", "GREEN", "RED", "YELLOW", "YELLOW", "純米漿製作對痛風安全，但配料與淋醬鈉含量高。"],
    ["大腸包小腸", "YELLOW", "RED", "RED", "RED", "糯米難消化，香腸屬加工肉高鈉高脂。"],
    ["胡椒餅", "YELLOW", "RED", "YELLOW", "RED", "外皮多油，內餡肥肉多且重口味。"],
    ["白糖粿", "GREEN", "YELLOW", "RED", "RED", "糯米油炸再裹糖粉，糖尿病與高血脂大忌。"],
    ["肉鬆", "YELLOW", "RED", "YELLOW", "RED", "高鈉、高油、高糖加工品，極不推薦。"],
    ["貢丸", "YELLOW", "RED", "YELLOW", "RED", "加工肉品，隱含大量肥肉與鹽分。"],
    ["魚餃", "YELLOW", "RED", "YELLOW", "RED", "火鍋料皆屬高油高鹽加工品。"],
    ["泡麵", "YELLOW", "RED", "RED", "RED", "麵體油炸，調味包高鈉高油，無營養價值。"],
    ["皮蛋", "GREEN", "RED", "GREEN", "GREEN", "鈉含量偏高，高血壓需注意。"],
    ["鹹蛋", "GREEN", "RED", "GREEN", "YELLOW", "極度高鈉，高血壓與腎臟負擔大。"],
    ["豆乳雞", "YELLOW", "RED", "RED", "RED", "醃漬加炸，重口味極地雷。"],
    ["鹹酥雞", "YELLOW", "RED", "RED", "RED", "高溫油炸，反式脂肪與熱量破表。"],
    ["蔥油餅", "GREEN", "RED", "YELLOW", "RED", "餅皮吸附大量油脂，重鹹。"],
    ["水煎包", "YELLOW", "RED", "YELLOW", "RED", "底部重油煎，內餡多半較肥。"]
]

all_foods = vegetables + fruits + meats + seafoods + carbs + others

# 去重複並寫入 CSV
unique_foods = {}
for row in all_foods:
    unique_foods[row[0]] = row

with open(db_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['name', 'gout', 'hypertension', 'diabetes', 'hyperlipidemia', 'reason'])
    writer.writerows(list(unique_foods.values()))

print(f"✅ Success: Generated {len(unique_foods)} distinct food items.")
