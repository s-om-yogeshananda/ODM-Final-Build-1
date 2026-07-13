import sys
import os
import threading
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
from plyer import notification
import yt_dlp

class HackerThemeLabel(MDLabel):
    """কাস্টম নিয়ন গ্রিন হ্যাকার লেবেল"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_text_color = "Custom"
        self.text_color = (0, 1, 0.4, 1)  # Neon Green
        self.font_style = "Button"

class ODM_Mobile_UI(MDBoxLayout):
    def __init__(self, shared_url="", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.md_bg_color = (0.05, 0.05, 0.08, 1) # Dark Cyberpunk Background
        self.shared_url = shared_url
        
        # ১. প্রিমিয়াম নিয়ন টাইটেল বার
        title_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), padding=dp(10), md_bg_color=(0.08, 0.08, 0.12, 1))
        title_box.add_widget(HackerThemeLabel(text="ODM (OM's Download Manager)", font_style="H6", bold=True, halign="left"))
        self.add_widget(title_box)
        
        # ২. বটম নেভিগেশন (ট্যাব সিস্টেম)
        self.nav = MDBottomNavigation(panel_color=(0.08, 0.08, 0.12, 1), text_color_active=(0, 1, 0.4, 1))
        
        # ট্যাব ১: ডাউনলোডার ও ইন-অ্যাপ সার্চ
        self.tab_download = MDBottomNavigationItem(name='download_tab', text='Search & DL', icon='xml')
        self.setup_download_tab()
        self.nav.add_widget(self.tab_download)
        
        # ট্যাব ২: ডাউনলোডেড ফাইলস (ক্যাটাগরি লিস্ট)
        self.tab_files = MDBottomNavigationItem(name='files_tab', text='Library', icon='folder-download')
        self.setup_files_tab()
        self.nav.add_widget(self.tab_files)
        
        self.add_widget(self.nav)
        
        if self.shared_url:
            self.search_input.text = self.shared_url

    def setup_download_tab(self):
        box = MDBoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        
        # সাইবারপাংক সার্চ বার
        self.search_input = MDTextField(
            hint_text="Search or Paste Social Media Link...",
            line_color_focus=(0, 1, 0.4, 1),
            text_color_focus=(1, 1, 1, 1),
            current_hint_text_color=(0, 1, 0.4, 0.7),
            size_hint_x=1
        )
        box.add_widget(self.search_input)
        
        # কোয়ালিটি সিলেক্টর লেবেল
        box.add_widget(HackerThemeLabel(text="⚡ SELECT QUALITY & FORMAT:", font_style="Caption"))
        
        # প্রিমিয়াম হ্যাকার বাটনস (ক্লিক করলেই ডাউনলোড শুরু হবে)
        btn_box = MDBoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        btn_box.bind(minimum_height=btn_box.setter('height'))
        
        qualities = [
            ("Video - 4K Ultra HD (MP4)", "video"),
            ("Video - 1080p Full HD (MP4)", "video"),
            ("Video - 720p HD (MP4)", "video"),
            ("Audio - High Quality (MP3)", "audio")
        ]
        
        for q_text, q_type in qualities:
            btn = MDRaisedButton(
                text=q_text,
                md_bg_color=(0.1, 0.1, 0.15, 1),
                text_color=(0, 1, 0.4, 1),
                line_color=(0, 1, 0.4, 1),
                line_width=1,
                size_hint_x=1,
                padding=dp(12)
            )
            btn.bind(on_release=lambda x, text=q_text: self.start_download(text))
            btn_box.add_widget(btn)
            
        box.add_widget(btn_box)
        
        # লাইভ স্পিড ও প্রোগ্রেস এরিয়া
        self.status_lbl = HackerThemeLabel(text="SYSTEM STATUS: IDLE", halign="center")
        box.add_widget(self.status_lbl)
        
        self.progress_bar = MDProgressBar(value=0, color=(0, 1, 0.4, 1), size_hint_y=None, height=dp(6))
        box.add_widget(self.progress_bar)
        
        self.tab_download.add_widget(box)

    def setup_files_tab(self):
        # ভিডিও ও অডিও আলাদা করার ক্যাটাগরি ভিউ
        box = MDBoxLayout(orientation='vertical', padding=dp(10))
        
        box.add_widget(HackerThemeLabel(text="📂 DOWNLOADED MEDIA CATEGORIES", font_style="Subtitle1", bold=True))
        
        scroll = MDScrollView()
        self.file_list = MDList()
        
        # ডামি রিয়েল-টাইম ক্যাটাগরি বাটন (ফোনের ফোল্ডার রিড করবে)
        self.refresh_library()
        
        scroll.add_widget(self.file_list)
        box.add_widget(scroll)
        self.tab_files.add_widget(box)

    def refresh_library(self):
        self.file_list.clear_widgets()
        save_path = "/storage/emulated/0/Download"
        
        # ভিডিও ক্যাটাগরি হেডার
        self.file_list.add_widget(HackerThemeLabel(text="[ VIDEOS (MP4) ]", font_style="Caption", bold=True))
        if os.path.exists(save_path):
            for f in os.listdir(save_path):
                if f.endswith(".mp4"):
                    item = OneLineIconListItem(text=f[:40], text_color=(1,1,1,1))
                    item.add_widget(IconLeftWidget(icon="video", icon_color=(0, 1, 0.4, 1)))
                    self.file_list.add_widget(item)
                    
        # অডিও ক্যাটাগরি হেডার
        self.file_list.add_widget(HackerThemeLabel(text="\n[ AUDIOS (MP3) ]", font_style="Caption", bold=True))
        if os.path.exists(save_path):
            for f in os.listdir(save_path):
                if f.endswith(".mp3"):
                    item = OneLineIconListItem(text=f[:40], text_color=(1,1,1,1))
                    item.add_widget(IconLeftWidget(icon="music", icon_color=(0, 1, 0.4, 1)))
                    self.file_list.add_widget(item)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            speed = d.get('speed', 0)
            
            speed_mbps = (speed * 8) / (1024 * 1024) if speed else 0
            percent = int(downloaded / total * 100) if total else 0
            
            self.progress_bar.value = percent
            self.status_lbl.text = f"DOWNLOADING... SPEED: {speed_mbps:.2f} Mbps | {percent}%"

    def start_download(self, quality_text):
        url = self.search_input.text.strip()
        if not url:
            self.status_lbl.text = "ERROR: NO URL DETECTED!"
            return
            
        try:
            notification.notify(title="ODM Cyber Core", message="High-Speed Download Injection Started...", timeout=2)
        except: pass
        
        threading.Thread(target=self.download_process, args=(url, quality_text)).start()

    def download_process(self, url, quality_text):
        save_path = "/storage/emulated/0/Download"
        try:
            if "MP3" in quality_text:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}],
                    'nocheckcertificate': True,
                }
            else:
                height = "2160" if "4K" in quality_text else ("1080" if "1080p" in quality_text else "720")
                ydl_opts = {
                    'format': f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best',
                    'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                    'merge_output_format': 'mp4',
                    'nocheckcertificate': True,
                }
                
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            self.status_lbl.text = "SUCCESS: MAIN FRAME DOWNLOADED!"
            try:
                notification.notify(title="ODM Success", message="File compiled and saved to Library.", timeout=3)
            except: pass
            self.refresh_library()
            
        except Exception as e:
            self.status_lbl.text = f"BREAK: {str(e)[:30]}"

class ODMApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        shared_url = sys.argv[1] if len(sys.argv) > 1 else ""
        return ODM_Mobile_UI(shared_url=shared_url)

if __name__ == '__main__':
    ODMApp().run()