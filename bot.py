from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import os

# Setup untuk Termux
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless')  # Opsional: jika tidak perlu GUI
options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')

# Untuk Termux, biasanya menggunakan Chrome di Android
driver = webdriver.Chrome(options=options)

try:
    # Membuka WhatsApp Web
    driver.get('https://web.whatsapp.com/')
    
    print("Silakan scan QR code dan masuk ke group...")
    input("Press Enter setelah berhasil login...")

    # Tunggu sampai elemen WhatsApp load
    wait = WebDriverWait(driver, 60)
    
    # Menunggu hingga chat container terbuka
    chat_container = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "_2A8P4"))
    )

    # Konfirmasi ban akan aktif secara default
    ban_confirmation = True

    # Loop utama untuk memantau pesan
    while True:
        try:
            # Mendapatkan pesan terakhir
            messages = driver.find_elements(By.CLASS_NAME, '_21S-L')
            if not messages:
                time.sleep(2)
                continue
                
            last_message = messages[-1]
            
            # Mendapatkan teks pesan
            message_elements = last_message.find_elements(By.CLASS_NAME, '_11JPr')
            if not message_elements:
                time.sleep(2)
                continue
                
            message_span = message_elements[0]
            message = message_span.text.strip().lower()

            # Input pesan
            message_input = driver.find_element(By.CLASS_NAME, '_3Uu1_')
            
            # Tombol kirim
            send_button = driver.find_element(By.CLASS_NAME, '_3HQNh')

            # Command: /help
            if message == "/help":
                help_text = """*Daftar Perintah:*
1- /rules - Lihat aturan group
2- /ban @nama - Ban anggota group
3- /ban confirmation - Aktif/nonaktif konfirmasi ban
4- /status - Cek status bot"""

                message_input.send_keys(help_text)
                send_button.click()
                time.sleep(1)

            # Command: /rules  
            elif message == "/rules":
                rules_text = """*ATURAN GROUP:*
• Dilarang spam
• Dilarang konten pornografi
• Dilarang berbagi link tanpa izin
• Hormati semua anggota
• Admin berhak mengambil tindakan"""

                message_input.send_keys(rules_text)
                send_button.click()
                time.sleep(1)

            # Command: /ban
            elif message.startswith("/ban") and message != "/ban confirmation":
                if " @" in message:
                    target_user = message.split(" @")[1].strip()
                    
                    if ban_confirmation:
                        # Minta konfirmasi
                        confirm_msg = f"Konfirmasi ban untuk @{target_user}? (Y/N)"
                        message_input.send_keys(confirm_msg)
                        send_button.click()
                        time.sleep(1)
                        
                        # Tunggu jawaban
                        time.sleep(10)  # Tunggu 10 detik untuk konfirmasi
                        
                        # Cek pesan terakhir untuk konfirmasi
                        latest_messages = driver.find_elements(By.CLASS_NAME, '_21S-L')
                        if latest_messages:
                            latest_msg = latest_messages[-1].find_elements(By.CLASS_NAME, '_11JPr')
                            if latest_msg:
                                response = latest_msg[0].text.strip().lower()
                                
                                if response == 'y':
                                    self.remove_user(driver, target_user)
                                else:
                                    message_input.send_keys("Ban dibatalkan")
                                    send_button.click()
                        else:
                            message_input.send_keys("Waktu konfirmasi habis")
                            send_button.click()
                    else:
                        self.remove_user(driver, target_user)

            # Command: /ban confirmation
            elif message == "/ban confirmation":
                # Cek apakah pengirim adalah admin
                if self.is_admin(driver, last_message):
                    ban_confirmation = not ban_confirmation
                    status = "diaktifkan" if ban_confirmation else "dinonaktifkan"
                    message_input.send_keys(f"Konfirmasi ban {status}")
                    send_button.click()
                else:
                    message_input.send_keys("Hanya admin yang bisa menggunakan perintah ini")
                    send_button.click()

            # Command: /status
            elif message == "/status":
                status_text = f"*Status Bot:*\n• Konfirmasi ban: {'Aktif' if ban_confirmation else 'Nonaktif'}\n• Bot berjalan normal"
                message_input.send_keys(status_text)
                send_button.click()
                time.sleep(1)

            # Command tidak dikenali
            elif message.startswith("/"):
                message_input.send_keys("Perintah tidak dikenali. Ketik /help untuk bantuan")
                send_button.click()

            time.sleep(2)  # Tunggu 2 detik sebelum cek pesan berikutnya

        except Exception as e:
            print(f"Error: {str(e)}")
            time.sleep(5)

except KeyboardInterrupt:
    print("\nBot dihentikan oleh user")
except Exception as e:
    print(f"Error utama: {str(e)}")
finally:
    driver.quit()

def remove_user(self, driver, username):
    """Fungsi untuk menghapus user dari group"""
    try:
        # Buka info group
        group_header = driver.find_element(By.CLASS_NAME, '_2vDPL')
        group_header.click()
        time.sleep(2)
        
        # Cari anggota
        search_box = driver.find_element(By.CLASS_NAME, '_3UX5Z')
        search_box.send_keys(username)
        time.sleep(2)
        
        # Klik anggota yang ditemukan
        members = driver.find_elements(By.CLASS_NAME, '_2EXPL')
        for member in members:
            if username.lower() in member.text.lower():
                # Hover dan hapus
                actions = ActionChains(driver)
                actions.move_to_element(member).perform()
                time.sleep(1)
                
                # Klik menu options
                menu_btn = member.find_element(By.CLASS_NAME, '_3e4VU')
                menu_btn.click()
                time.sleep(1)
                
                # Klik remove
                remove_btn = driver.find_element(By.XPATH, "//div[text()='Remove']")
                remove_btn.click()
                time.sleep(1)
                
                # Konfirmasi
                confirm_btn = driver.find_element(By.CLASS_NAME, '_3y5oW')
                confirm_btn.click()
                
                # Kirim pesan konfirmasi
                message_input = driver.find_element(By.CLASS_NAME, '_3Uu1_')
                message_input.send_keys(f"@{username} telah dihapus dari group")
                send_button = driver.find_element(By.CLASS_NAME, '_3HQNh')
                send_button.click()
                
                break
                
        # Kembali ke chat
        back_btn = driver.find_element(By.CLASS_NAME, '_1aTxu')
        back_btn.click()
        
    except Exception as e:
        print(f"Error remove user: {str(e)}")
        # Kembali ke chat jika error
        try:
            back_btn = driver.find_element(By.CLASS_NAME, '_1aTxu')
            back_btn.click()
        except:
            pass

def is_admin(self, driver, message_element):
    """Cek apakah pengirim adalah admin"""
    try:
        # Cek struktur elemen untuk menentukan apakah pengirim adalah admin
        parent = message_element.find_element(By.XPATH, "./..")
        classes = parent.get_attribute("class")
        return "message-out" in classes
    except:
        return False
