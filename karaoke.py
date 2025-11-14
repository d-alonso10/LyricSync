import os
# ¡NUEVO! Esto debe ir ANTES de importar pygame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

import pygame
import re
import time
import colorama
from colorama import Fore, Style
import requests  # Para descargar LRC
import yt_dlp      # Para descargar MP3
import sys

# --- Configuración de Pantalla ---
LINEAS_ANTES = 2
LINEAS_DESPUES = 4

# --- Nombres de archivo temporales ---
TEMP_MP3 = "cancion_descargada.mp3"
TEMP_LRC = "cancion_descargada.lrc"

# --- Configuración de Validación ---
TOLERANCIA_SEGUNDOS = 5.0 

# ###################################################################
# FUNCIONES DE DESCARGA (LÓGICA INVERTIDA + TERMINAL LIMPIA)
# ###################################################################

def descargar_cancion_y_letra(busqueda):
    """
    Intenta descargar el MP3 y LRC.
    LÓGICA: YouTube es la fuente de referencia.
    1. Busca el video en YouTube y obtiene su duración.
    2. Busca en LRC Lib una letra que coincida con esa duración.
    """
    print(f"\nBuscando '{busqueda}'...")
    lrc_listo = False
    mp3_listo = False
    
    video_ref_url = None
    video_ref_duration = None
    video_ref_title = None
    
    lrc_data_final = None

    try:
        # --- 1. Buscar en YouTube PRIMERO ---
        print("Buscando video de referencia en YouTube...")
        
        # Opciones para SÓLO BUSCAR (eliminamos 'extract_flat')
        ydl_search_opts = {
            'format': 'bestaudio/best',
            'default_search': 'ytsearch5', # Buscar los 5 primeros
            'quiet': True,
            'no_warnings': True, # ¡NUEVO! Oculta warnings de búsqueda
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_search_opts) as ydl:
            search_result = ydl.extract_info(busqueda, download=False)
            videos = search_result.get('entries', [])

            if not videos:
                print("❌ Error: No se encontró ningún video en YouTube.")
                return False, False
        
        # --- 2. Encontrar un video de referencia VÁLIDO ---
        # Usaremos el primer video que tenga duración
        for video in videos:
            if video and video.get('duration'):
                video_ref_url = video.get('url')
                video_ref_duration = video.get('duration')
                video_ref_title = video.get('title', 'Video sin título')
                break # Encontramos nuestro video de referencia
        
        if not video_ref_duration:
            print("❌ Error: YouTube no devolvió videos con datos de duración.")
            return False, False
            
        print(f"ℹ️ Video de referencia: '{video_ref_title}'")
        print(f"ℹ️ Duración de referencia: {video_ref_duration:.2f} segundos.")

        # --- 3. Buscar en LRC Lib una letra que COINCIDA ---
        print("Buscando en lrclib.net una letra con duración similar...")
        response = requests.get(f"https://lrclib.net/api/search?q={busqueda}", timeout=10)
        response.raise_for_status()
        lrc_results = response.json()
        
        if not lrc_results:
            print("❌ Error: No se encontraron letras en lrclib.net.")
            return False, False

        # --- Comprobación simplificada (sin 'print' sucios) ---
        for lrc_entry in lrc_results:
            lrc_duration = lrc_entry.get('duration')

            if not lrc_duration or not lrc_entry.get('syncedLyrics'):
                continue

            diferencia = abs(lrc_duration - video_ref_duration)
            
            if diferencia <= TOLERANCIA_SEGUNDOS:
                lrc_data_final = lrc_entry['syncedLyrics']
                print(f"  ✅ ¡Letra sincronizada encontrada!\n") # Mensaje limpio
                break 
        # --- Fin de la comprobación simplificada ---

        # --- 4. Validar y Descargar ---
        
        if not lrc_data_final:
            print("❌ Error: Se encontró un video, pero ninguna letra coincidió con su duración.")
            return False, False

        # Si llegamos aquí, tenemos AMBAS cosas. Procedemos a descargar.
        
        # Descargar MP3
        # ¡NUEVO! Imprime el TÍTULO, no la URL
        print(f"Descargando MP3 de: '{video_ref_title}' (puede tardar)...")
        
        ydl_download_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'cancion_descargada',
            # 'quiet': True, <-- Se quita para ver la barra de progreso
            'no_warnings': True, # ¡NUEVO! Oculta warnings de descarga
            'noplaylist': True,
        }

        if os.path.exists(TEMP_MP3):
            os.remove(TEMP_MP3)
            
        with yt_dlp.YoutubeDL(ydl_download_opts) as ydl:
            ydl.download([video_ref_url]) 

        if not os.path.exists(TEMP_MP3):
             raise Exception("yt-dlp no generó el archivo MP3.")

        print(f"\n✅ MP3 guardado como {TEMP_MP3}")
        mp3_listo = True
        
        # Guardar LRC
        print(f"✅ LRC guardado como {TEMP_LRC}")
        with open(TEMP_LRC, 'w', encoding='utf-8') as f:
            f.write(lrc_data_final)
        lrc_listo = True

    except Exception as e:
        print(f"❌ Error inesperado durante la descarga: {e}")
        
    return mp3_listo, lrc_listo

# ###################################################################
# FUNCIONES DEL KARAOKE (SIN CAMBIOS)
# ###################################################################

def parse_lrc(filepath):
    lyrics = []
    lrc_regex = re.compile(r'\[(\d{2}):(\d{2})\.?(\d{2,3})?\](.*)')
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                match = lrc_regex.match(line)
                if not match: continue
                minutos, segundos = int(match.group(1)), int(match.group(2))
                frac_seg = 0
                if match.group(3):
                    frac_seg = int(match.group(3))
                    if len(match.group(3)) == 2: frac_seg *= 10
                texto = match.group(4).strip()
                tiempo_ms = (minutos * 60 * 1000) + (segundos * 1000) + frac_seg
                lyrics.append((tiempo_ms, texto))
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de letra {filepath}")
        return None
    lyrics.sort()
    return lyrics

def play_karaoke(mp3_file, lrc_file):
    colorama.init(autoreset=True)
    letras_con_tiempo = parse_lrc(lrc_file)
    if not letras_con_tiempo:
        print("No se pudieron cargar las letras.")
        return

    if not os.path.exists(mp3_file):
        print(f"Error: No se encontró el archivo de audio {mp3_file}")
        return
        
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_file)
    except pygame.error as e:
        print(f"\n❌ Error de Pygame al cargar el MP3: {e}")
        print("El archivo de audio puede estar corrupto o en un formato no compatible.")
        return
    
    print(f"\n🎤 Preparando Karaoke... Presiona Enter para comenzar")
    try:
        input() 
    except EOFError:
        pass 

    pygame.mixer.music.play()
    indice_letra_actual = 0
    indice_letra_mostrada = -1
    
    try:
        while pygame.mixer.music.get_busy() or indice_letra_actual < len(letras_con_tiempo):
            tiempo_actual_ms = pygame.mixer.music.get_pos()
            if tiempo_actual_ms == -1: break
                
            if indice_letra_actual < len(letras_con_tiempo):
                (tiempo_siguiente_letra, _) = letras_con_tiempo[indice_letra_actual]
                
                if tiempo_actual_ms >= tiempo_siguiente_letra:
                    if indice_letra_mostrada != indice_letra_actual:
                        os.system('cls' if os.name == 'nt' else 'clear') 
                        start_index = max(0, indice_letra_actual - LINEAS_ANTES)
                        end_index = min(len(letras_con_tiempo), indice_letra_actual + LINEAS_DESPUES + 1)
                        print("\n\n")
                        for i in range(start_index, end_index):
                            (_, texto_linea) = letras_con_tiempo[i]
                            if i == indice_letra_actual:
                                print(f"  {Style.BRIGHT}{Fore.WHITE}▶ {texto_linea}{Style.RESET_ALL}")
                            elif i > indice_letra_actual:
                                print(f"  {Style.DIM}{Fore.WHITE}  {texto_linea}{Style.RESET_ALL}")
                            else:
                                print(f"  {Style.DIM}{Fore.LIGHTBLACK_EX}  {texto_linea}{Style.RESET_ALL}")
                        print("\n\n")
                        indice_letra_mostrada = indice_letra_actual
                    indice_letra_actual += 1
            time.sleep(0.05) 
    except KeyboardInterrupt:
        print("\n¡Karaoke detenido!")
    finally:
        pygame.mixer.music.stop()
        print("Fin de la canción.")

# ###################################################################
# BLOQUE PRINCIPAL (SIN CAMBIOS)
# ###################################################################

if __name__ == "__main__":
    if len(sys.argv) > 1:
        termino_busqueda = " ".join(sys.argv[1:])
    else:
        termino_busqueda = input("¿Qué canción quieres cantar? (artista y nombre): ")
    
    if termino_busqueda:
        mp3_ok, lrc_ok = descargar_cancion_y_letra(termino_busqueda)
        
        if mp3_ok and lrc_ok:
            play_karaoke(TEMP_MP3, TEMP_LRC)
        else:
            print("\nNo se pudo iniciar el karaoke.")
    else:
        print("No se ingresó búsqueda.")