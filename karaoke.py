import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
import re
import requests
import yt_dlp
import sys
import tkinter as tk
from tkinter import font as tkFont
import textwrap
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

TEMP_MP3 = "cancion_descargada.mp3"
TEMP_LRC = "cancion_descargada.lrc"
TOLERANCIA = 5.0
W_ANCHO = 350
W_ALTO = 350
C_START = "#4a148c"
C_END = "#1a237e"
FONT_FAM = "Segoe UI"
F_SIZE_ACT = 22
F_SIZE_INA = 16

def descargar_contenido(busqueda):
    print(f"\nBuscando '{busqueda}'...")
    vid_url, vid_dur, vid_title = None, None, None
    lrc_final = None
    try:
        ydl_opts = {'format':'bestaudio/best','default_search':'ytsearch5','quiet':True,'no_warnings':True,'noplaylist':True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            res = ydl.extract_info(busqueda, download=False)
            vids = res.get('entries', [])
            if not vids: return False, False
        for v in vids:
            if v and v.get('duration'):
                vid_url, vid_dur, vid_title = v.get('url'), v.get('duration'), v.get('title')
                break
        if not vid_dur: return False, False
        print(f"Ref: '{vid_title}' ({vid_dur:.2f}s)")
        
        s = requests.Session()
        ret = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        s.mount("https://", HTTPAdapter(max_retries=ret))
        res = s.get(f"https://lrclib.net/api/search?q={busqueda}", timeout=30)
        res.raise_for_status()
        for l in res.json():
            if not l.get('duration') or not l.get('syncedLyrics'): continue
            if abs(l['duration'] - vid_dur) <= TOLERANCIA:
                lrc_final = l['syncedLyrics']
                break
        if not lrc_final: return False, False

        if os.path.exists(TEMP_MP3): os.remove(TEMP_MP3)
        dl_opts = {'format':'bestaudio/best','postprocessors':[{'key':'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':'192'}],'outtmpl':'cancion_descargada','no_warnings':True,'noplaylist':True}
        with yt_dlp.YoutubeDL(dl_opts) as ydl: ydl.download([vid_url])
        if not os.path.exists(TEMP_MP3): raise Exception("MP3 no generado")
        with open(TEMP_LRC, 'w', encoding='utf-8') as f: f.write(lrc_final)
        return True, True
    except Exception as e:
        print(f"Error: {e}")
        return False, False

def parse_lrc(fp):
    lyr = []
    reg = re.compile(r'\[(\d{2}):(\d{2})\.?(\d{2,3})?\](.*)')
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            for l in f:
                m = reg.match(l)
                if not m: continue
                mn, sg = int(m.group(1)), int(m.group(2))
                fr = int(m.group(3)) if m.group(3) else 0
                if m.group(3) and len(m.group(3)) == 2: fr *= 10
                tx = m.group(4).strip()
                if tx: lyr.append(((mn*60000)+(sg*1000)+fr, tx))
    except: return None
    lyr.sort()
    return lyr

def gen_bg(w, h):
    if not PIL_AVAILABLE: return None
    base = Image.new('RGB', (w, h), C_START)
    cs, ce = tuple(int(C_START.lstrip('#')[i:i+2], 16) for i in (0,2,4)), tuple(int(C_END.lstrip('#')[i:i+2], 16) for i in (0,2,4))
    draw = ImageDraw.Draw(base)
    for y in range(h):
        r = int(cs[0] + (ce[0] - cs[0]) * (y/h))
        g = int(cs[1] + (ce[1] - cs[1]) * (y/h))
        b = int(cs[2] + (ce[2] - cs[2]) * (y/h))
        draw.line([(0, y), (w, y)], fill=(r,g,b))
    glow = Image.new('RGBA', (w, h), (0,0,0,0))
    ImageDraw.Draw(glow).ellipse((-w//2, -h//2, w, h), fill=(255,255,255,40))
    base.paste(glow.filter(ImageFilter.GaussianBlur(50)), (0,0), glow)
    noise = Image.effect_noise((w, h), 15).convert('L')
    n_rgba = Image.new('RGBA', (w, h))
    n_rgba.putdata([(0,0,0,int(p*0.05)) for p in noise.getdata()])
    base.paste(n_rgba, (0,0), n_rgba)
    return base

def blend_col(hex_bg, op):
    bg = tuple(int(hex_bg.lstrip('#')[i:i+2], 16) for i in (0,2,4))
    return f"#{int(255*op + bg[0]*(1-op)):02x}{int(255*op + bg[1]*(1-op)):02x}{int(255*op + bg[2]*(1-op)):02x}"

def run_gui(mp3, lrc):
    data = parse_lrc(lrc)
    if not data: return
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(mp3)
    except: return

    root = tk.Tk()
    root.title("Spotify2025")
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{W_ANCHO}x{W_ALTO}+{(sw-W_ANCHO)//2}+{(sh-W_ALTO)//2}")
    root.overrideredirect(True)
    root.wm_attributes("-topmost", 1)

    bg_tk = None
    if PIL_AVAILABLE:
        bg_tk = ImageTk.PhotoImage(gen_bg(W_ANCHO, W_ALTO))
    
    cv = tk.Canvas(root, highlightthickness=0, bg="#321b85")
    cv.pack(fill="both", expand=True)
    if bg_tk: cv.create_image(0, 0, image=bg_tk, anchor="nw")

    def move(e): root.geometry(f"+{root.winfo_x()+(e.x-root.x)}+{root.winfo_y()+(e.y-root.y)}")
    cv.bind("<Button-1>", lambda e: setattr(root, 'x', e.x) or setattr(root, 'y', e.y))
    cv.bind("<B1-Motion>", move)

    f_act = tkFont.Font(family=FONT_FAM, size=F_SIZE_ACT, weight="bold")
    f_ina = tkFont.Font(family=FONT_FAM, size=F_SIZE_INA, weight="bold")
    c_act, c_ina = "#FFFFFF", blend_col("#321b85", 0.4)
    
    # Pre-cálculo de layout para optimización masiva
    w_act = textwrap.TextWrapper(width=int((W_ANCHO-40)/f_act.measure("a")))
    w_ina = textwrap.TextWrapper(width=int((W_ANCHO-40)/f_ina.measure("a")))
    
    cache = []
    for _, tx in data:
        t_a = w_act.fill(tx) if tx else ""
        t_i = w_ina.fill(tx) if tx else ""
        h_a = (f_act.metrics('linespace') * len(t_a.split('\n'))) + 30
        h_i = (f_ina.metrics('linespace') * len(t_i.split('\n'))) + 15
        cache.append({'ta':t_a, 'ti':t_i, 'ha':h_a, 'hi':h_i})

    idx, pan, cy = 0, W_ALTO/2, W_ALTO/2
    
    def loop():
        nonlocal idx, pan
        pos = pygame.mixer.music.get_pos()
        if pos == -1 and not pygame.mixer.music.get_busy():
            root.destroy()
            return
        
        while idx < len(data) and pos >= data[idx][0]: idx += 1
        cur = idx - 1
        
        cv.delete("l")
        y, tgt = 0, 0 if cur < 0 else 0
        
        for i, item in enumerate(cache):
            act = (i == cur)
            h = item['ha'] if act else item['hi']
            if act: tgt = cy - (y + h/2)
            
            # Solo dibujar si será visible (aprox)
            fy = y + pan
            if -50 < fy + h and fy < W_ALTO + 50:
                cv.create_text(W_ANCHO/2, fy + h/2, text=item['ta'] if act else item['ti'], 
                             fill=c_act if act else c_ina, font=f_act if act else f_ina, 
                             anchor="center", justify="center", width=W_ANCHO-30, tags="l")
            y += h
            
        pan += (tgt - pan) * 0.15
        root.after(33, loop)

    cv.create_text(W_ANCHO-20, 20, text="✕", fill=c_ina, font=(FONT_FAM, 10), tags="x")
    cv.tag_bind("x", "<Button-1>", lambda e: root.destroy() or pygame.mixer.music.stop())
    
    pygame.mixer.music.play()
    loop()
    root.mainloop()

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Canción: ")
    if q:
        m, l = descargar_contenido(q)
        if m and l: run_gui(TEMP_MP3, TEMP_LRC)