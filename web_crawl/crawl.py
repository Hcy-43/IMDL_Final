from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import requests
import argparse

def crawl_pinterest_images_v2(keyword, save_folder='images', num_scrolls=10, max_download=50):
    save_folder = os.path.join('data', save_folder)
    os.makedirs(save_folder, exist_ok=True)

    driver = webdriver.Chrome()
    url = f'https://www.pinterest.com/search/pins/?q={keyword}'
    driver.get(url)
    time.sleep(5)

    image_urls = set()

    for scroll in range(num_scrolls):
        print(f"📜 第 {scroll+1} 次滾動...")
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        img_elements = driver.find_elements(By.TAG_NAME, "img")
        for img in img_elements:
            srcset = img.get_attribute('srcset')
            if srcset:
                biggest_img = srcset.split(',')[-1].strip().split(' ')[0]
                image_urls.add(biggest_img)
                

        if len(image_urls) >= max_download:
            print("✅ 抓到足夠的圖片了，停止滾動。")
            break

    driver.quit()

    print(f"🎯 總共抓到 {len(image_urls)} 張圖片，開始下載...")

    for i, url in enumerate(list(image_urls)[:max_download]):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                file_path = os.path.join(save_folder, f'image_{i+1}.jpg')
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ 已存檔：{file_path}")
            else:
                print(f"❌ 下載失敗（HTTP {response.status_code}）：{url}")
        except Exception as e:
            print(f"⚠️ 發生錯誤：{e}，網址：{url}")

    print("🎉 爬圖完成！")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pinterest 圖片爬蟲")
    parser.add_argument('--keyword', type=str, required=True, help="搜尋關鍵字，例如 'cats' 或 'ちいかわ うさぎ'")
    parser.add_argument('--save_folder', type=str, default='images', help="儲存圖片的資料夾名稱")
    parser.add_argument('--num_scrolls', type=int, default=10, help="滾動頁面的次數（越多越能抓到更多圖片）")
    parser.add_argument('--max_download', type=int, default=50, help="最多下載幾張圖片")

    args = parser.parse_args()

    crawl_pinterest_images_v2(
        keyword=args.keyword,
        save_folder=args.save_folder,
        num_scrolls=args.num_scrolls,
        max_download=args.max_download
    )
