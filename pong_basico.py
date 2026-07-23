import pygame
import sys
import random
import asyncio

#Inicializar Pygame
pygame.init()

# Configuracion de la pantalla
ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Pong con IA o 2 jugadores")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (20, 20, 20)
AZUL = (50, 150, 255)
ROJO = (255, 80, 80)
ESTELA_COLOR = (255, 255, 0)

fuente = pygame.font.Font(None, 60)
reloj = pygame.time.Clock()

# Sonido
try:
    rebote_sonido = pygame.mixer.Sound("bounce.ogg")
    pygame.mixer.music.load("background.ogg")
    pygame.mixer.music.play(-1)
except Exception:
    pass

# Paletas
ANCHO_PALETA, ALTO_PALETA = 10, 100
velocidad_paleta = 7

pelota_rastro = []
MAX_RASTRO = 15

# Pelota
TAMANO_PELOTA = 30

# Fincion para mostrar texto centrado
def mostrar_texto(texto, tamaño=60, y_offset=0):
    fuente_local = pygame.font.Font(None, tamaño)
    render = fuente_local.render(texto, True, BLANCO)
    rect = render.get_rect(center=(ANCHO // 2, ALTO // 2+ y_offset))
    pantalla.blit(render, rect)

# Pantalla de inicio
async def pantalla_inicio():
    seleccion = 0
    opciones = ["1. Jugador vs Jugador", "2. Jugador vs IA"]

    while True:
        pantalla.fill(NEGRO)
        mostrar_texto("Selecciona el modo de juego", 50, -100)
        for i, opcion in enumerate(opciones):
            color = AZUL if i == seleccion else BLANCO
            texto = fuente.render(opcion, True, color)
            pantalla.blit(texto, (ANCHO // 2 - texto.get_width() // 2, ALTO // 2+ i * 50))
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    seleccion = (seleccion - 1) % len(opciones)
                elif evento.key == pygame.K_DOWN:
                    seleccion = (seleccion + 1) % len(opciones)
                elif evento.key == pygame.K_RETURN:
                    return seleccion

        await asyncio.sleep(0)

# Pantalla ganador
async def pantalla_ganador(ganador):
    pantalla.fill(NEGRO)
    mostrar_texto(f"¡{ganador} gana!", 60, -40)
    mostrar_texto("Presiona cualquier tecla para jugar otra vez", 40, 40)
    pygame.display.flip()
    await esperar_tecla()

# Esperar una tecla
async def esperar_tecla():
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                return
        await asyncio.sleep(0)
                       
# Juego principal
async def main():
    while True:
        modo = await pantalla_inicio()
        contra_ia = (modo == 1)

        paleta_izquierda = pygame.Rect(50, ALTO // 2- ALTO_PALETA // 2, ANCHO_PALETA, ALTO_PALETA)
        paleta_derecha = pygame.Rect(ANCHO - 60, ALTO // 2- ALTO_PALETA // 2, ANCHO_PALETA, ALTO_PALETA)
        pelota = pygame.Rect(ANCHO // 2 - 15, ALTO // 2-15, TAMANO_PELOTA, TAMANO_PELOTA)
        velocidad_pelota = [random.choice([-5, 5]), random.choice([-5, 5])]
        puntos_izquierda = 0
        puntos_derecha = 0

        
        jugando = True
        while jugando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Movimiento de paletas
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_w] and paleta_izquierda.top > 0:
                paleta_izquierda.y -= velocidad_paleta
            if teclas[pygame.K_s] and paleta_izquierda.bottom < ALTO:
                paleta_izquierda.y += velocidad_paleta

            #Movimiento jugador 2 (IA o gentepersona)
            if contra_ia:
                # IA sigue la pelota con lentitud
                if paleta_derecha.centery < pelota.centery and paleta_derecha.bottom < ALTO:
                    paleta_derecha.y += velocidad_paleta - 2
                elif paleta_derecha.centery > pelota.centery and paleta_derecha.top > 0:
                    paleta_derecha.y -= velocidad_paleta - 2
            else:
                if teclas[pygame.K_UP] and paleta_derecha.top > 0:
                    paleta_derecha.y -= velocidad_paleta
                if teclas[pygame.K_DOWN] and paleta_derecha.bottom < ALTO:
                    paleta_derecha.y += velocidad_paleta

            # Mover pelota
            pelota.x += velocidad_pelota[0]
            pelota.y += velocidad_pelota[1]

            # Rastro
            pelota_rastro.append(pelota.center)
            if len(pelota_rastro) > MAX_RASTRO:
                pelota_rastro.pop(0)

            # Colisiones con bordes
            if pelota.top <= 0 or pelota.bottom >= ALTO:
                velocidad_pelota[1] *= -1

            # Colision con paleta
            if pelota.colliderect(paleta_izquierda) or pelota.colliderect(paleta_derecha):
                velocidad_pelota[0] *= -1.1
                velocidad_pelota[1] *= 1.05
                try:
                    rebote_sonido.play()
                except Exception:
                    pass

            # Puntos para derecha
            if pelota.left <= 0:
                puntos_derecha += 1
                pelota.center = (ANCHO // 2, ALTO // 2)
                velocidad_pelota = [random.choice([-5, 5]), random.choice([-5, 5])]

            # Puntos para izquierda
            if pelota.right >= ANCHO:
                puntos_izquierda += 1
                pelota.center = (ANCHO // 2, ALTO // 2)
                velocidad_pelota = [random.choice([-5, 5]), random.choice([-5, 5])]

            # Verificar ganador
            if puntos_izquierda == 5:
                await pantalla_ganador("Jugador 1")
                jugando = False
            elif puntos_derecha == 5:
                await pantalla_ganador("Jugador 2")
                jugando = False

            pantalla.fill(NEGRO)

            # DIbujar estela
            for i, pos in enumerate(pelota_rastro):
                r = TAMANO_PELOTA // 2
                intensidad = max(0, 255 - i * 20)
                color = (ESTELA_COLOR[0], intensidad, intensidad)
                pygame.draw.circle(pantalla, color, pos, r)

            # Dibujar elementos
            pygame.draw.rect(pantalla, AZUL, paleta_izquierda)
            pygame.draw.rect(pantalla, ROJO, paleta_derecha)
            pygame.draw.ellipse(pantalla, BLANCO, pelota)
            pygame.draw.aaline(pantalla, BLANCO, (ANCHO // 2, 0), (ANCHO // 2, ALTO))

            # Puntuacion
            txt_izq = fuente.render(str(puntos_izquierda), True, BLANCO)
            txt_der = fuente.render(str(puntos_derecha), True, BLANCO)
            pantalla.blit(txt_izq, (ANCHO // 4,20))
            pantalla.blit(txt_der, (ANCHO * 3 // 4, 20))

            pygame.display.flip()
            reloj.tick(60)
            await asyncio.sleep(0)

# Ejecutar juego
asyncio.run(main())