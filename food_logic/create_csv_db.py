import csv
import os

# 定義目標路徑
db_path = r'D:\AntiGravity\舒酸與三高守護者\food_logic\data\food_database.csv'
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# 準備擴充資料庫
foods = [
    # 格式: 名稱, 痛風(gout), 高血壓(hyper), 糖尿病(diab), 高血脂(lipid), 說明
    # 原始 20 種
    ["芭樂", "GREEN", "GREEN", "GREEN", "GREEN", "富含維生素 C 與纖維，有助排尿酸且糖分低。"],
    ["滷肉飯", "YELLOW", "RED", "RED", "RED", "精緻澱粉加上高油、高鹽的滷汁，極易使三高惡化。"],
    ["虱目魚肚", "RED", "GREEN", "GREEN", "YELLOW", "普林值偏高；雖富含魚油，但熱量與飽和脂肪需控制。"],
    ["地瓜葉", "GREEN", "GREEN", "GREEN", "GREEN", "高纖低卡，有助穩定血糖與血壓。"],
    ["鹹水雞", "YELLOW", "RED", "GREEN", "YELLOW", "調味過鹹（鈉含量高），但蛋白質本體與蔬菜類對血糖友善。"],
    ["木瓜", "GREEN", "GREEN", "YELLOW", "GREEN", "對痛風與代謝好，但水果糖分高，糖尿病需控量。"],
    ["菜脯蛋", "GREEN", "RED", "GREEN", "YELLOW", "醃漬菜脯鹽分極高，油煎蛋含油量多，高血壓/高血脂不宜。"],
    ["火鍋湯底", "RED", "RED", "RED", "RED", "久煮湯底融出大量普林、高鈉且高熱量，絕對禁忌。"],
    ["控肉", "YELLOW", "RED", "YELLOW", "RED", "高飽和脂肪與高鈉，對心血管負擔極重。"],
    ["糙米飯", "GREEN", "GREEN", "GREEN", "GREEN", "高纖、低 GI，比白米更適合三高族群。"],
    ["蚵仔煎", "RED", "RED", "RED", "RED", "勾芡醬汁高糖、高鹽，蚵仔普林高且重油煎炸。"],
    ["臭豆腐", "YELLOW", "RED", "GREEN", "RED", "油炸物飽和脂肪多，泡菜與沾醬鈉含量爆表。"],
    ["無糖豆漿", "GREEN", "GREEN", "GREEN", "GREEN", "優質植物蛋白，有助於降低心血管負擔，對痛風適量安全。"],
    ["豬肝", "RED", "GREEN", "GREEN", "YELLOW", "內臟類普林極高，絕對禁忌。"],
    ["乾香菇", "RED", "GREEN", "GREEN", "GREEN", "乾貨類普林濃縮度極高，痛風急性期禁吃。"],
    ["生鮮香菇", "YELLOW", "GREEN", "GREEN", "GREEN", "生鮮菇類水分多、普林未被濃縮，非痛風急性期可適量食用。"],
    ["珍珠奶茶", "RED", "RED", "RED", "RED", "高果糖漿快速生成尿酸，引發血糖血脂失控。"],
    ["白灼蝦", "RED", "GREEN", "GREEN", "YELLOW", "海鮮類普林偏高，高血脂需注意膽固醇。"],
    ["烤香腸", "YELLOW", "RED", "RED", "RED", "高飽和脂肪、高鈉，且加工肉品不利於尿酸代謝。"],
    ["白米飯", "GREEN", "GREEN", "YELLOW", "GREEN", "精緻澱粉易使血糖快速升高，需控量（限半碗）。"],
    ["蘋果", "GREEN", "GREEN", "GREEN", "GREEN", "富含果膠與維生素，對三高與痛風皆友善。"],
    
    # 擴充 - 肉品類
    ["雞胸肉", "YELLOW", "GREEN", "GREEN", "GREEN", "優質低脂蛋白質，普林中等。"],
    ["帶皮雞腿", "YELLOW", "GREEN", "GREEN", "YELLOW", "脂肪含量較高，高血脂患者宜去皮食用。"],
    ["松阪豬", "YELLOW", "GREEN", "GREEN", "YELLOW", "油花豐富，飽和脂肪略高，需控制份量。"],
    ["牛腱", "YELLOW", "GREEN", "GREEN", "GREEN", "低脂肪紅肉，適合三高，但痛風患者不宜過量。"],
    ["牛五花", "YELLOW", "RED", "GREEN", "RED", "脂肪含量極高，不適合高血脂與高血壓。"],
    ["肉鬆", "YELLOW", "RED", "YELLOW", "RED", "高鈉、高油、高糖加工品，極不推薦。"],
    
    # 擴充 - 海鮮類
    ["白帶魚", "RED", "GREEN", "GREEN", "GREEN", "普林極高，痛風患者應避免。"],
    ["透抽", "YELLOW", "GREEN", "GREEN", "YELLOW", "膽固醇偏高，高血脂患者需注意份量。"],
    ["鮭魚", "YELLOW", "GREEN", "GREEN", "GREEN", "富含 Omega-3，有助心血管，但普林中等。"],
    ["蛤蜊", "RED", "GREEN", "GREEN", "GREEN", "帶殼海鮮普林偏高，煮湯尤甚。"],
    ["秋刀魚", "RED", "GREEN", "GREEN", "YELLOW", "普林偏高，魚油雖好但整體熱量不可忽視。"],
    
    # 擴充 - 水果類
    ["西瓜", "GREEN", "GREEN", "RED", "GREEN", "GI 值極高，糖尿病患者容易血糖狂飆。"],
    ["芒果", "GREEN", "GREEN", "RED", "GREEN", "糖分極高，糖尿病絕對需控量。"],
    ["荔枝", "GREEN", "GREEN", "RED", "GREEN", "糖分極高，不宜多吃。"],
    ["香蕉", "GREEN", "GREEN", "YELLOW", "GREEN", "富含鉀有助血壓，但糖分不低，糖尿病宜一次半根。"],
    ["奇異果", "GREEN", "GREEN", "GREEN", "GREEN", "維生素與纖維豐富，適合所有族群。"],
    ["小番茄", "GREEN", "GREEN", "GREEN", "GREEN", "低糖高纖，非常適合取代一般水果。"],
    
    # 擴充 - 蔬菜與根莖類
    ["高麗菜", "GREEN", "GREEN", "GREEN", "GREEN", "百搭且安全的十字花科蔬菜。"],
    ["菠菜", "GREEN", "GREEN", "GREEN", "GREEN", "高營養價值，但若有結石體質需注意草酸。"],
    ["南瓜", "GREEN", "GREEN", "YELLOW", "GREEN", "屬於澱粉類，糖尿病患者需替換主食份量。"],
    ["馬鈴薯", "GREEN", "GREEN", "YELLOW", "GREEN", "屬於澱粉，容易使血糖升高，建議煮熟放涼抗性澱粉化。"],
    ["空心菜", "GREEN", "GREEN", "GREEN", "GREEN", "高鉀有助降血壓。"],
    ["蘆筍", "RED", "GREEN", "GREEN", "GREEN", "蔬菜中極少數普林偏高的食材，痛風患者需注意。"],
    
    # 擴充 - 夜市與傳統小吃
    ["蚵仔麵線", "RED", "RED", "RED", "RED", "勾芡(高糖)、大腸/蚵仔(高普林)、重鹹(高鈉)，慢性病天敵。"],
    ["肉圓", "YELLOW", "RED", "RED", "RED", "外皮精緻澱粉且油炸，醬汁高鹽高糖。"],
    ["碗粿", "GREEN", "RED", "YELLOW", "YELLOW", "純米漿製作對痛風安全，但配料與淋醬鈉含量高。"],
    ["大腸包小腸", "YELLOW", "RED", "RED", "RED", "糯米難消化，香腸屬加工肉高鈉高脂。"],
    ["胡椒餅", "YELLOW", "RED", "YELLOW", "RED", "外皮多油，內餡肥肉多且重口味。"],
    ["白糖粿", "GREEN", "YELLOW", "RED", "RED", "糯米油炸再裹糖粉，糖尿病與高血脂大忌。"]
]

# 寫入 CSV
with open(db_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['name', 'gout', 'hypertension', 'diabetes', 'hyperlipidemia', 'reason'])
    writer.writerows(foods)

print(f"✅ 成功建立 {len(foods)} 筆資料至 CSV 檔案。")
