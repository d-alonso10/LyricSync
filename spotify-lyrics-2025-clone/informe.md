# Informe Técnico de Funcionalidad y Validaciones: VocaSync (v2.0)

Este documento detalla la arquitectura optimizada, el flujo de datos paralelo y el algoritmo de "Smart Matching" implementado para garantizar la máxima sincronización y velocidad.

## 1. Arquitectura de Alto Rendimiento

El backend (`backend/server.py`) ha evolucionado de un modelo secuencial a un modelo **concurrente**, reduciendo drásticamente los tiempos de espera.

### Endpoint Principal: `GET /search`

El proceso utiliza `concurrent.futures.ThreadPoolExecutor` para lanzar múltiples hilos de ejecución simultáneos:

1.  **Hilo A (YouTube):** Busca los **Top 5** videos candidatos (no solo el primero).
2.  **Hilo B (LRCLIB):** Busca todas las letras candidatas disponibles.

Ambos procesos ocurren al mismo tiempo. El sistema no espera a que termine uno para empezar el otro.

---

## 2. Nuevo Algoritmo: "Smart Matching" (Cruce Inteligente)

Anteriormente, el sistema fallaba si el primer video de YouTube era una versión extendida (ej. "Thriller" de Michael Jackson, 13 min) y la letra era la versión de radio (4 min).

**Solución Implementada:**
El sistema ahora realiza un cruce matricial (MxN) entre los Videos encontrados y las Letras encontradas.

**Lógica de Selección:**
1.  Recuperamos:
    *   `Videos = [V1, V2, V3, V4, V5]`
    *   `Letras = [L1, L2, L3...]`
2.  Iteramos sobre cada par posible `(Video, Letra)`.
3.  Calculamos la diferencia de duración: `diff = abs(Duration_Video - Duration_Letra)`.
4.  **Validación de Tolerancia:**
    *   Solo se aceptan pares donde `diff <= 5.0` segundos.
5.  **Selección del Mejor Candidato:**
    *   De todos los pares válidos, se elige aquel con la **menor diferencia de tiempo** y mayor relevancia en YouTube.

### Ejemplo Real: "Thriller"
*   **Video 1 (Oficial):** 13:42 min. -> Letra (5:58) -> Diff: 7m (DESCARTADO)
*   **Video 2 (Audio):** 5:59 min. -> Letra (5:58) -> Diff: 1s (**ACEPTADO - MATCH PERFECTO**)
*   *Resultado:* Se descarga el Video 2, ignorando el Video 1 aunque sea más popular.

---

## 3. Optimizaciones de Descarga y Conversión

Para mejorar la velocidad de respuesta final (Time-to-Music):

1.  **Paralelismo:** Como se mencionó, la búsqueda ya no es secuencial.
2.  **Calidad de Audio Balanceada:**
    *   Se ajustó la conversión de FFmpeg a **128kbps** mp3.
    *   *Razón:* Es el estándar de calidad de streaming ("Calidad Alta" en Spotify web). Subir a 192kbps o 320kbps incrementa el tiempo de descarga y cpu en un 40% sin beneficio perceptible para Karaoke.
3.  **Supresión de Logs:** Se eliminaron salidas de consola innecesarias en `yt-dlp` para reducir overhead de I/O.
4.  **Caché Persistente:** Se sigue validando si el archivo existe en disco antes de intentar descargarlo.

## 4. Validaciones de Integridad y Errores

| Validación | Descripción | Acción si falla |
| :--- | :--- | :--- |
| **Query Vacía** | Verifica que el usuario envió texto. | Error 400 |
| **Video Results** | Verifica que YouTube devuelva al menos 1 video. | Error 404 |
| **Lyrics Results** | Verifica que LRCLIB devuelva resultados con `syncedLyrics`. | Error 404 |
| **Match Duration** | Algoritmo Smart Matching (descrito arriba). | Error 404 (con mensaje de diff mínima) |
| **API Resilience** | Reintentos automáticos (x3) si LRCLIB falla (5xx). | Log de error y continua |

## 5. Archivos Clave Actualizados

*   `backend/server.py`: Implementa `concurrent.futures` y la lógica de bucles anidados para el Smart Matching.
*   `informe.md`: Este documento.
