"""
Nombre del programa: Gato.py
Descripción: Este script ejecuta un clasico juego de gato.

Autores:
    -Equipo Mac Trio
    -Acosta Avila Diego Ernersto
    -Diaz Pompa Jesus Eduardo
    -Ruiz Alejandro Ignacio Alberto

Fecha de creación: 09 de septiembre de 2026
"""
__authors__ = ["Acosta Avila Diego Ernesto", "Diaz Pompa Jesus Eduardo", "Ruiz Alejandro Ignacio Alberto"]
__credits__ = ["Acosta Avila Diego Ernesto", "Diaz Pompa Jesus Eduardo", "Ruiz Alejandro Ignacio Alberto"]
__license__ = "GPL"
__version__ = "1.0.0"

import math
import random
import sys
import pygame

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
pygame.init()
pygame.font.init()

# Dimensiones de la pantalla
ANCHO_PANEL = 600
ALTO_SUPERIOR = 135
ALTO_TABLERO = 600
ALTO_INFERIOR = 80
ANCHO_PANTALLA = ANCHO_PANEL
ALTO_PANTALLA = ALTO_SUPERIOR + ALTO_TABLERO + ALTO_INFERIOR

FILAS, COLUMNAS = 3, 3
TAMANO_CELDA = ANCHO_PANEL // COLUMNAS

# Estilos visuales
ANCHO_LINEA = 10
GROSOR_CIRCULO = 12
RADIO_CIRCULO = TAMANO_CELDA // 3
ANCHO_X = 18
ESPACIO_X = TAMANO_CELDA // 4
ANCHO_LINEA_VICTORIA = 12

# Paleta de Colores
COLOR_FONDO_PANEL = (38, 50, 56)      # Gris azulado oscuro
COLOR_FONDO_TABLERO = (55, 71, 79)    # Gris azulado medio
COLOR_LINEA = (78, 104, 116)          # Líneas de la cuadrícula
COLOR_CIRCULO = (255, 202, 40)        # Amarillo/Dorado cálido
COLOR_X = (239, 83, 80)               # Rojo suave
COLOR_GANADOR = (102, 187, 106)       # Verde esmeralda
COLOR_TEXTO = (236, 239, 241)         # Blanco
COLOR_TURNO = (255, 213, 79)          # Amarillo claro para el turno
COLOR_BOTON = (41, 182, 246)          # Azul celeste
COLOR_BOTON_HOVER = (129, 212, 250)   # Azul claro
COLOR_BOTON_MONEDA = (255, 179, 0)     # Dorado
COLOR_BLOQUEO = (0, 0, 0, 150)        # Transparencia para bloquear el tablero

# Titulo de la ventana
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Juego del Gato - IA (Mac Trio)")

# Fuentes
fuente_pequena = pygame.font.SysFont("Arial", 15, bold=True)
fuente_mediana = pygame.font.SysFont("Arial", 19, bold=True)
fuente_anuncio = pygame.font.SysFont("Arial", 28, bold=True)

# Variables de Estado del Juego
tablero = [[0 for _ in range(COLUMNAS)] for _ in range(FILAS)]
juego_terminado = False
linea_ganadora = None

# Configuración de Fichas y Turnos:
ficha_humano = 1
ficha_ia = 2
turno_actual = 1

# Variables para Animación de Moneda
lanzando_moneda = False
tiempo_inicio_moneda = 0
duracion_animacion = 1500  # 1.5 segundos
mensaje_anuncio = ""

# Marcador y Ajustes
puntos_humano = 0
puntos_ia = 0
empates = 0
modo_dificultad = "Medio"


# --- FUNCIONES DE DIBUJO Y UI ---

def dibujar_interfaz():
    pantalla.fill(COLOR_FONDO_TABLERO)
    mouse_pos = pygame.mouse.get_pos()
    
    # Panel Superior
    pygame.draw.rect(pantalla, COLOR_FONDO_PANEL, (0, 0, ANCHO_PANTALLA, ALTO_SUPERIOR))
    
    # Marcador
    txt_marcador = fuente_mediana.render(f"Jugador: {puntos_humano}  |  IA: {puntos_ia}  |  Empates: {empates}", True, COLOR_TEXTO)
    rect_marcador = txt_marcador.get_rect(center=(ANCHO_PANTALLA // 2, 20))
    pantalla.blit(txt_marcador, rect_marcador)

    # Botón de Tirar Moneda
    rect_btn_moneda = pygame.Rect(20, 45, 260, 38)
    color_moneda = COLOR_BOTON_HOVER if rect_btn_moneda.collidepoint(mouse_pos) and not lanzando_moneda else COLOR_BOTON_MONEDA
    pygame.draw.rect(pantalla, color_moneda, rect_btn_moneda, border_radius=8)
    
    txt_moneda = fuente_pequena.render("Lanzar Moneda", True, COLOR_FONDO_PANEL)
    rect_txt_moneda = txt_moneda.get_rect(center=rect_btn_moneda.center)
    pantalla.blit(txt_moneda, rect_txt_moneda)

    # Botón de Dificultad
    rect_btn_dif = pygame.Rect(300, 45, 280, 38)
    color_dif = COLOR_BOTON_HOVER if rect_btn_dif.collidepoint(mouse_pos) and not lanzando_moneda else COLOR_BOTON
    pygame.draw.rect(pantalla, color_dif, rect_btn_dif, border_radius=8)

    txt_dif = fuente_pequena.render(f"Dificultad: {modo_dificultad}", True, COLOR_FONDO_PANEL)
    rect_txt_dif = txt_dif.get_rect(center=rect_btn_dif.center)
    pantalla.blit(txt_dif, rect_txt_dif)

    # --- TEXTO DE TURNO (Debajo de los botones) ---
    if lanzando_moneda:
        str_turno = "Lanzando moneda..."
    elif juego_terminado:
        str_turno = "Juego Terminado - Presiona Reiniciar (R)"
    elif turno_actual == ficha_humano:
        str_turno = "Turno: Humano"
    else:
        str_turno = "Turno: IA (Pensando...)"

    txt_turno = fuente_mediana.render(str_turno, True, COLOR_TURNO)
    rect_turno = txt_turno.get_rect(center=(ANCHO_PANTALLA // 2, 108))
    pantalla.blit(txt_turno, rect_turno)

    # Cuadrícula del Tablero
    for i in range(1, FILAS):
        pygame.draw.line(pantalla, COLOR_LINEA, (0, ALTO_SUPERIOR + i * TAMANO_CELDA), (ANCHO_PANEL, ALTO_SUPERIOR + i * TAMANO_CELDA), ANCHO_LINEA)
        pygame.draw.line(pantalla, COLOR_LINEA, (i * TAMANO_CELDA, ALTO_SUPERIOR), (i * TAMANO_CELDA, ALTO_SUPERIOR + ALTO_TABLERO), ANCHO_LINEA)

    # Panel Inferior
    pygame.draw.rect(pantalla, COLOR_FONDO_PANEL, (0, ALTO_SUPERIOR + ALTO_TABLERO, ANCHO_PANTALLA, ALTO_INFERIOR))
    
    rect_btn_reinicio = pygame.Rect(ANCHO_PANTALLA // 2 - 100, ALTO_SUPERIOR + ALTO_TABLERO + 15, 200, 50)
    color_reiniciar = COLOR_BOTON_HOVER if rect_btn_reinicio.collidepoint(mouse_pos) and not lanzando_moneda else COLOR_BOTON
    pygame.draw.rect(pantalla, color_reiniciar, rect_btn_reinicio, border_radius=12)

    txt_reiniciar = fuente_mediana.render("Reiniciar", True, COLOR_FONDO_PANEL)
    rect_txt_btn = txt_reiniciar.get_rect(center=rect_btn_reinicio.center)
    pantalla.blit(txt_reiniciar, rect_txt_btn)


def dibujar_figuras():
    for f in range(FILAS):
        for c in range(COLUMNAS):
            if tablero[f][c] == 1:
                cx = c * TAMANO_CELDA + TAMANO_CELDA // 2
                cy = ALTO_SUPERIOR + f * TAMANO_CELDA + TAMANO_CELDA // 2
                pygame.draw.circle(pantalla, COLOR_CIRCULO, (cx, cy), RADIO_CIRCULO, GROSOR_CIRCULO)
                
            elif tablero[f][c] == 2:
                ix1 = c * TAMANO_CELDA + ESPACIO_X
                iy1 = ALTO_SUPERIOR + f * TAMANO_CELDA + ESPACIO_X
                fx1 = (c + 1) * TAMANO_CELDA - ESPACIO_X
                fy1 = ALTO_SUPERIOR + (f + 1) * TAMANO_CELDA - ESPACIO_X
                pygame.draw.line(pantalla, COLOR_X, (ix1, iy1), (fx1, fy1), ANCHO_X)

                ix2 = c * TAMANO_CELDA + ESPACIO_X
                iy2 = ALTO_SUPERIOR + (f + 1) * TAMANO_CELDA - ESPACIO_X
                fx2 = (c + 1) * TAMANO_CELDA - ESPACIO_X
                fy2 = ALTO_SUPERIOR + f * TAMANO_CELDA + ESPACIO_X
                pygame.draw.line(pantalla, COLOR_X, (ix2, iy2), (fx2, fy2), ANCHO_X)


def dibujar_linea_ganadora():
    if linea_ganadora is not None:
        inicio, fin = linea_ganadora
        pygame.draw.line(pantalla, COLOR_GANADOR, inicio, fin, ANCHO_LINEA_VICTORIA)


def dibujar_overlay_moneda():
    if lanzando_moneda:
        overlay = pygame.Surface((ANCHO_PANEL, ALTO_TABLERO), pygame.SRCALPHA)
        overlay.fill(COLOR_BLOQUEO)
        pantalla.blit(overlay, (0, ALTO_SUPERIOR))

        txt_anuncio = fuente_anuncio.render(mensaje_anuncio, True, COLOR_TEXTO)
        rect_anuncio = txt_anuncio.get_rect(center=(ANCHO_PANEL // 2, ALTO_SUPERIOR + ALTO_TABLERO // 2))
        pantalla.blit(txt_anuncio, rect_anuncio)


# --- LÓGICA DE JUEGO & DIFICULTAD ---

def marcar_casilla(fila, col, jugador):
    tablero[fila][col] = jugador


def casilla_disponible(fila, col):
    return tablero[fila][col] == 0


def tablero_lleno(tab=tablero):
    for f in range(FILAS):
        for c in range(COLUMNAS):
            if tab[f][c] == 0:
                return False
    return True


def verificar_victoria(jugador):
    global linea_ganadora

    for f in range(FILAS):
        if tablero[f][0] == jugador and tablero[f][1] == jugador and tablero[f][2] == jugador:
            py = ALTO_SUPERIOR + f * TAMANO_CELDA + TAMANO_CELDA // 2
            linea_ganadora = ((20, py), (ANCHO_PANEL - 20, py))
            return True

    for c in range(COLUMNAS):
        if tablero[0][c] == jugador and tablero[1][c] == jugador and tablero[2][c] == jugador:
            px = c * TAMANO_CELDA + TAMANO_CELDA // 2
            linea_ganadora = ((px, ALTO_SUPERIOR + 20), (px, ALTO_SUPERIOR + ALTO_TABLERO - 20))
            return True

    if tablero[0][0] == jugador and tablero[1][1] == jugador and tablero[2][2] == jugador:
        linea_ganadora = ((20, ALTO_SUPERIOR + 20), (ANCHO_PANEL - 20, ALTO_SUPERIOR + ALTO_TABLERO - 20))
        return True

    if tablero[2][0] == jugador and tablero[1][1] == jugador and tablero[0][2] == jugador:
        linea_ganadora = ((20, ALTO_SUPERIOR + ALTO_TABLERO - 20), (ANCHO_PANEL - 20, ALTO_SUPERIOR + 20))
        return True

    return False


def evaluar_tablero(tab):
    for f in range(3):
        if tab[f][0] == tab[f][1] == tab[f][2] and tab[f][0] != 0:
            return 10 if tab[f][0] == ficha_ia else -10
    for c in range(3):
        if tab[0][c] == tab[1][c] == tab[2][c] and tab[0][c] != 0:
            return 10 if tab[0][c] == ficha_ia else -10
    if tab[0][0] == tab[1][1] == tab[2][2] and tab[0][0] != 0:
        return 10 if tab[0][0] == ficha_ia else -10
    if tab[2][0] == tab[1][1] == tab[0][2] and tab[2][0] != 0:
        return 10 if tab[2][0] == ficha_ia else -10
    return 0


def obtener_casillas_vacias(tab):
    return [(f, c) for f in range(3) for c in range(3) if tab[f][c] == 0]


def minimax(tab, es_maximizando):
    puntuacion = evaluar_tablero(tab)

    if puntuacion == 10 or puntuacion == -10:
        return puntuacion

    casillas_libres = obtener_casillas_vacias(tab)
    if not casillas_libres:
        return 0

    if es_maximizando:
        mejor_valor = -math.inf
        for f, c in casillas_libres:
            tab[f][c] = ficha_ia
            valor = minimax(tab, False)
            tab[f][c] = 0
            mejor_valor = max(mejor_valor, valor)
        return mejor_valor
    else:
        mejor_valor = math.inf
        for f, c in casillas_libres:
            tab[f][c] = ficha_humano
            valor = minimax(tab, True)
            tab[f][c] = 0
            mejor_valor = min(mejor_valor, valor)
        return mejor_valor


def buscar_mejor_movimiento(tab):
    mejor_valor = -math.inf
    mejor_movimiento = None

    for f, c in obtener_casillas_vacias(tab):
        tab[f][c] = ficha_ia
        valor_movimiento = minimax(tab, False)
        tab[f][c] = 0

        if valor_movimiento > mejor_valor:
            mejor_valor = valor_movimiento
            mejor_movimiento = (f, c)

    return mejor_movimiento


def obtener_movimiento_ia():
    vacias = obtener_casillas_vacias(tablero)
    if not vacias:
        return None

    if modo_dificultad == "Fácil":
        return random.choice(vacias)
    elif modo_dificultad == "Medio":
        if random.random() < 0.5:
            return buscar_mejor_movimiento(tablero)
        else:
            return random.choice(vacias)
    else:  # Imposible
        return buscar_mejor_movimiento(tablero)


def iniciar_lanzamiento_moneda():
    global lanzando_moneda, tiempo_inicio_moneda, mensaje_anuncio
    reiniciar_juego()
    lanzando_moneda = True
    tiempo_inicio_moneda = pygame.time.get_ticks()
    mensaje_anuncio = "Lanzando moneda..."


def procesar_resultado_moneda():
    global ficha_humano, ficha_ia, turno_actual, lanzando_moneda
    
    if random.choice([True, False]):
        ficha_humano = 1  # Círculo (O)
        ficha_ia = 2      # Cruz (X)
    else:
        ficha_humano = 2  # Cruz (X)
        ficha_ia = 1      # Círculo (O)

    turno_actual = 1  # Arranca la ficha 1 (O)
    lanzando_moneda = False


def cambiar_dificultad():
    global modo_dificultad
    if modo_dificultad == "Fácil":
        modo_dificultad = "Medio"
    elif modo_dificultad == "Medio":
        modo_dificultad = "Imposible"
    else:
        modo_dificultad = "Fácil"


def reiniciar_juego():
    global juego_terminado, turno_actual, linea_ganadora
    for f in range(FILAS):
        for c in range(COLUMNAS):
            tablero[f][c] = 0
    turno_actual = 1
    juego_terminado = False
    linea_ganadora = None


# Lanzar la moneda al arrancar
iniciar_lanzamiento_moneda()

# --- BUCLE PRINCIPAL ---
mientras_ejecutando = True

while mientras_ejecutando:
    if lanzando_moneda:
        tiempo_transcurrido = pygame.time.get_ticks() - tiempo_inicio_moneda
        if tiempo_transcurrido >= duracion_animacion:
            procesar_resultado_moneda()

    dibujar_interfaz()
    dibujar_figuras()
    dibujar_linea_ganadora()
    dibujar_overlay_moneda()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            mientras_ejecutando = False
            pygame.quit()
            sys.exit()

        if not lanzando_moneda:
            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos_x, pos_y = evento.pos
                rect_btn_reinicio = pygame.Rect(ANCHO_PANTALLA // 2 - 100, ALTO_SUPERIOR + ALTO_TABLERO + 15, 200, 50)
                rect_btn_dif = pygame.Rect(300, 45, 280, 38)
                rect_btn_moneda = pygame.Rect(20, 45, 260, 38)

                # Clic en Tirar Moneda
                if rect_btn_moneda.collidepoint((pos_x, pos_y)):
                    iniciar_lanzamiento_moneda()

                # Clic en Cambiar Dificultad
                elif rect_btn_dif.collidepoint((pos_x, pos_y)):
                    cambiar_dificultad()

                # Clic en Reiniciar
                elif rect_btn_reinicio.collidepoint((pos_x, pos_y)):
                    reiniciar_juego()

                # Clic en el Tablero (Turno del Humano)
                elif ALTO_SUPERIOR <= pos_y < ALTO_SUPERIOR + ALTO_TABLERO and not juego_terminado and turno_actual == ficha_humano:
                    fila_clic = (pos_y - ALTO_SUPERIOR) // TAMANO_CELDA
                    columna_clic = pos_x // TAMANO_CELDA

                    if casilla_disponible(fila_clic, columna_clic):
                        marcar_casilla(fila_clic, columna_clic, ficha_humano)

                        if verificar_victoria(ficha_humano):
                            puntos_humano += 1
                            juego_terminado = True
                        elif tablero_lleno():
                            empates += 1
                            juego_terminado = True
                        else:
                            turno_actual = ficha_ia  # Pasa el turno a la IA

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    reiniciar_juego()
                elif evento.key == pygame.K_d:
                    cambiar_dificultad()
                elif evento.key == pygame.K_m:
                    iniciar_lanzamiento_moneda()

    # --- TURNO DE LA IA ---
    if not lanzando_moneda and turno_actual == ficha_ia and not juego_terminado:
        # 1. Redibujamos la pantalla completa con la jugada del humano y el texto "Turno: IA (Pensando...)"
        dibujar_interfaz()
        dibujar_figuras()
        dibujar_linea_ganadora()
        pygame.display.update()

        # 2. Aplicamos la pausa de 700 ms para simular el pensamiento
        pygame.time.delay(700)
        
        # 3. La IA calcula y efectúa su jugada
        movimiento_ia = obtener_movimiento_ia()
        if movimiento_ia:
            f, c = movimiento_ia
            marcar_casilla(f, c, ficha_ia)

            if verificar_victoria(ficha_ia):
                puntos_ia += 1
                juego_terminado = True
            elif tablero_lleno():
                empates += 1
                juego_terminado = True
            else:
                turno_actual = ficha_humano

    pygame.display.update()