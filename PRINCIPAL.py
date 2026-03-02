import pygame
from personaje import Personaje
from personaje import NPC
from personaje import ObjetoEstatico
from personaje import Camara




# 1. INICIALIZAR Pygame (Obligatorio)
pygame.init()

print(pygame.font.get_fonts())

pygame.mixer.init()



pygame.mixer.music.load("asets/music/A1.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)

beep_dialogo = pygame.mixer.Sound("asets/music/E1.mp3")
beep_dialogo.set_volume(0.3) # Que no suene muy fuerte


#color de la ventana( por ahora ese color)
Scala_Personaje=1.3
Scala_NPC= 1.3








# Configuración de la ventana
ventana = pygame.display.set_mode((800, 600))
# Le ponemos nombre a la ventana
pygame.display.set_caption("FIEE QUEST")


assets = {
    "casa": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/casa01.png"),
        (300, 350)
    ),
    "arbol1": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/arbol1.png"),
        (128, 248)
    ),
    "arbol2": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/arbol1.png"),
        (128, 248)
    ),
    "arbol3": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/arbol1.png"),
        (128, 248)
    ),
    "arbol4": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/arbol1.png"),
        (128, 248)
    ),
    "arbol5": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/arbol1.png"),
        (128, 248)
    ),
    "arbol6": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/arbol1.png"),
        (128, 248)
    ),
    "arbol7": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/arbol1.png"),
        (128, 248)
    ),
    "arbol8": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/arbol1.png"),
        (128, 248)
    ),
    "arbol9": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/arbol1.png"),
        (128, 248)
    ),
    "arbol10": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/arbol1.png"),
        (128, 248)
    ),
    "arbol11": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/arbol1.png"),
        (128, 248)
    ),
    "arbol12": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/arbol1.png"),
        (128, 248)
    ),
    "arbol13": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/arbol1.png"),
        (128, 248)
    ),
    "arbol14": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/arbol1.png"),
        (128, 248)
    ),
    "arbol15": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/arbol1.png"),
        (128, 248)
    ),
    "mesa":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/mesa1.png"),
        (108, 78)
    ),
    "silla1":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/silla01.png"),
        (141, 39)
    ),
    "silla2":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/silla01.png"),
        (141, 39)
    ),
    "mesa1":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/mesa1.png"),
        (108, 78)
    ),
    "silla3":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/silla01.png"),
        (141, 39)
    ),
    "silla4":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/silla01.png"),
        (141, 39)
    ),
    "pastoc1":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/pasto_de_captura_2.png"),
        (96, 96)
    ),
    "pastoc2":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/pasto_de_captura_2.png"),
        (96, 96)
    ),
    "pastoc3":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/pasto_de_captura.png"),
        (96, 192)
    ),
    "pastoc4":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/pasto_de_captura.png"),
        (96, 192)
    ),
    "carro1":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/carro1.png"),
        (177, 390)
    ),
    "aula1":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/aula_oficial.png"),
        (442, 442)
    ),
    "aula2":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/aula_oficial.png"),
        (442, 442)
    ),
    "aula3":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/aula_oficial.png"),
        (442, 442)
    ),
    "aula4":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/aula_oficial.png"),
        (442, 442)
    ),
    "aula5":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/aula_oficial.png"),
        (442, 442)
    ),
    "aula6":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/aula_oficial.png"),
        (442, 442)
    ),
    "L4":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/lab2.png"),
        (852, 996)
    ),
    "letrero1":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/letrero1.png"),
        (96, 72)
    ),
    "L2":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/CENTRAL.png"),
        (374, 372)
    ),
    "CENTROAULA":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/centro_aula.png"),
        (654, 346)
    ),
    "edificio1":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/edificio1.png"),
        (886.5, 379.5)
    ),
    "edificio2":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/edificio1.png"),
        (886.5, 379.5)
    ),
    "edificiogrande":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/edificiogrande.png"),
        (206, 406)
    ),
    "carro2":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/carro2.png"),
        (262, 177)
    ),
    "carro3":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/carro2.png"),
        (262, 177)
    ),
    "carro4":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/carro3.png"),
        (114, 147)
    ),
    "carroblanco":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/carro_blanco.png"),
        (168,120)
    ),
    "carroverde":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/carro_verde.png"),
        (168, 120)
    ),
    "carroazul":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/carro_azul.png"),
        (168, 120)
    ),
    "escalera1":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/escalera_oficial.png"),
        (56, 152)
    ),
    "escalera2":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/escalera_oficial1.png"),
        (64, 178)
    ),
    "camion":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/camion.png"),
        (192, 160)
    ),
    "tractor":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/tractor.png"),
        (154, 132)
    ),
    "leo":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/leo.png"),
        (195, 261)
    ),
    "estadio":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/batalla1.png"),
        (224, 96)
    ),
    "faro1":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/faro1.png"),
        (54, 141)
    ),
    "faro2":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/faro2.png"),
        (96, 141)
    ),
    "decoracion1":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/decoracion1.png"),
        (45, 45)
    ),
    "decoracion2":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/decoracion2.png"),
        (180, 87)
    ),
    "decoracion3":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/decoracion3.png"),
        (31, 86)
    ),
    "decoracion4":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/decoracion4.png"),
        (95, 133)
    ),
    "basura1":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/basura1.png"),
        (45, 72)
    ),
    "basura2":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/basura2.png"),
        (45, 72)
    ),
    "basura3":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/basura3.png"),
        (45, 72)
    ),
    "pastoalto1":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/pastoalto1.png"),
        (63, 34)
    ),
    "pastoalto2":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/pastoalto2.png"),
        (32, 50)
    ),
    "centropokemon":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/centropokemon.png"),
        (261, 273)
    ),
    "edificiosinpuerta":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/edificiosinpuerta.png"),
        (354, 354)
    ),
    "labo2":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/labo1.png"),
        (478.5, 457.5)
    ),
    "edificiogrande2":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/edificiogrande2.png"),
        (260, 560)
    ),
    "estadistica2":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/estadistica1.png"),
        (570,621)
    ),
    "fiee":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/teleco.png"),
        (560,540)
    ),
    "veredasuper":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/verderasuper.png"),
        (95,114)
    ),
    "veredafinal": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/veredafinal.png"),
        (95,114)
    ),
    "pastoamarillo": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/pastoamarillo.png"),
        (193.5,48)
    ),
    "pastoverdeclaro": pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/pastoverdeclaro.png"),
        (192,48)
    ),
    "arbolgrande":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/arbolgrande.png"),
        (320,504)
    ),
    "floresazules":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/floresazules.png"),
        (144,32)
    ),
    "floresrosadas":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/flores.png"),
        (144,32)
    ),
    "floresamarillas":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/floresamarillas.png"),
        (144,32)
    ),
    "estatua":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/estatuapok.png"),
        (45,96)
    ),
    "pastosalto":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/pastosalto.png"),
        (96,87)
    ),
    "barro":pygame.transform.scale(
        pygame.image.load("asets/imagenes/character/Tiles/barro.png"),
        (108,82)
    ),













}

img_pasto = pygame.image.load("asets/imagenes/character/Tiles/pasto1.png")
img_vereda = pygame.image.load("asets/imagenes/character/Tiles/vereda.png").convert_alpha()
img_pista1= pygame.image.load("asets/imagenes/character/Tiles/pista_1.png").convert_alpha()
img_pista2= pygame.image.load("asets/imagenes/character/Tiles/pista_2.png").convert_alpha()

# 2. Creamos una "Superficie" del tamaño de toda la ventana
# Esto es como un lienzo en blanco gigante


fondo_completo = pygame.Surface((4000, 4000))

# 3. "Alfombramos" el lienzo una sola vez
for x in range(0, 4000, 32):
    for y in range(0, 4000, 32):
        # 1. Dibujamos SIEMPRE el pasto base primero
        fondo_completo.blit(img_pasto, (x, y))



inicio_x = 3000
inicio_y = 1200
largo_vereda = 3300 # Hasta dónde llega hacia abajo

# Dibujamos la vereda repitiendo el bloque de 39px de alto
for y in range(inicio_y, largo_vereda, 30):
    # Si quieres que la vereda sea más ancha que 20px,
    # podemos dibujarla 3 veces de lado (20 + 20 + 20 = 60px)
    fondo_completo.blit(img_vereda, (inicio_x, y))
    fondo_completo.blit(img_vereda, (inicio_x + 20, y))
    fondo_completo.blit(img_vereda, (inicio_x + 40, y))


inicio_x4 = 495
inicio_y4 = 1200
largo_vereda4 = 3500 # Hasta dónde llega hacia abajo

# Dibujamos la vereda repitiendo el bloque de 39px de alto
for y in range(inicio_y4, largo_vereda4, 30):
    # Si quieres que la vereda sea más ancha que 20px,
    # podemos dibujarla 3 veces de lado (20 + 20 + 20 = 60px)
    fondo_completo.blit(img_vereda, (inicio_x4, y))
    fondo_completo.blit(img_vereda, (inicio_x4 + 20, y))
    fondo_completo.blit(img_vereda, (inicio_x4 + 40, y))

inicio_x5 = 2400
inicio_y5 = 0
largo_vereda5 = 1200  # Hasta dónde llega hacia abajo

# Dibujamos la vereda repitiendo el bloque de 39px de alto
for y in range(inicio_y5, largo_vereda5, 30):
    # Si quieres que la vereda sea más ancha que 20px,
    # podemos dibujarla 3 veces de lado (20 + 20 + 20 = 60px)
    fondo_completo.blit(img_vereda, (inicio_x5, y))
    fondo_completo.blit(img_vereda, (inicio_x5 + 20, y))
    fondo_completo.blit(img_vereda, (inicio_x5 + 40, y))

inicio_x6 = 1500
inicio_y6 = 0
largo_vereda6 = 1250 # Hasta dónde llega hacia abajo

# Dibujamos la vereda repitiendo el bloque de 39px de alto
for y in range(inicio_y6, largo_vereda6, 30):
    # Si quieres que la vereda sea más ancha que 20px,
    # podemos dibujarla 3 veces de lado (20 + 20 + 20 = 60px)
    fondo_completo.blit(img_vereda, (inicio_x6, y))
    fondo_completo.blit(img_vereda, (inicio_x6 + 20, y))
    fondo_completo.blit(img_vereda, (inicio_x6 + 40, y))

inicio_x1 = 3350
inicio_y1 = 0
largo_vereda1 = 3300

for y in range(inicio_y1, largo_vereda1, 30):
    # Si quieres que la vereda sea más ancha que 20px,
    # podemos dibujarla 3 veces de lado (20 + 20 + 20 = 60px)
    fondo_completo.blit(img_vereda, (inicio_x1, y))
    fondo_completo.blit(img_vereda, (inicio_x1+ 20, y))
    fondo_completo.blit(img_vereda, (inicio_x1 + 40, y))


# 1. Rotamos la imagen original
img_vereda_h = pygame.transform.rotate(img_vereda, 90)

# 2. Ahora el ancho es 39 y el alto es 20
for x in range(0, 3000, 30): # El -1 es para evitar grietas
    # Dibujamos 3 filas para que la vereda tenga 60px de alto (20 * 3)
    fondo_completo.blit(img_vereda_h, (x, 1200))
    fondo_completo.blit(img_vereda_h, (x, 1220))
    fondo_completo.blit(img_vereda_h, (x, 1240))

for x in range(0, 3650, 30):  # El -1 es para evitar grietas
    # Dibujamos 3 filas para que la vereda tenga 60px de alto (20 * 3)
    fondo_completo.blit(img_vereda_h, (x, 1200))
    fondo_completo.blit(img_vereda_h, (x, 1220))
    fondo_completo.blit(img_vereda_h, (x, 1240))

for x in range(0, 4000, 30):  # El -1 es para evitar grietas
    # Dibujamos 3 filas para que la vereda tenga 60px de alto (20 * 3)
    fondo_completo.blit(img_vereda_h, (x, 3200))
    fondo_completo.blit(img_vereda_h, (x, 3220))


inicio_x2 = 3428
inicio_y2 = 0
largo_pista1 = 3300 # Hasta dónde llega hacia abajo

# Dibujamos la vereda repitiendo el bloque de 39px de alto
for y in range(inicio_y2, largo_pista1, 30):
    # Si quieres que la vereda sea más ancha que 20px,
    # podemos dibujarla 3 veces de lado (20 + 20 + 20 = 60px)
    fondo_completo.blit(img_pista1, (inicio_x2 + 200, y))
    fondo_completo.blit(img_pista1, (inicio_x2 + 180, y))
    fondo_completo.blit(img_pista1, (inicio_x2 + 160, y))
    fondo_completo.blit(img_pista1, (inicio_x2 + 140, y))
    fondo_completo.blit(img_pista1, (inicio_x2 + 120, y))
    fondo_completo.blit(img_pista1, (inicio_x2 + 100, y))
    fondo_completo.blit(img_pista1, (inicio_x2 + 80, y))
    fondo_completo.blit(img_pista1, (inicio_x2 + 60, y))
    fondo_completo.blit(img_pista1, (inicio_x2 + 40, y))
    fondo_completo.blit(img_pista1, (inicio_x2 + 20, y))
    fondo_completo.blit(img_pista1, (inicio_x2, y))

inicio_x3 = 3600
inicio_y3 = 0
largo_pista2 = 3300 # Hasta dónde llega hacia abajo

# Dibujamos la vereda repitiendo el bloque de 39px de alto
for y in range(inicio_y3, largo_pista2, 30):
    # Si quieres que la vereda sea más ancha que 20px,
    # podemos dibujarla 3 veces de lado (20 + 20 + 20 = 60px)
    fondo_completo.blit(img_pista2, (inicio_x3, y))
    fondo_completo.blit(img_pista2, (inicio_x3 + 20, y))
    fondo_completo.blit(img_pista2, (inicio_x3 + 40, y))
    fondo_completo.blit(img_pista2, (inicio_x3 + 60, y))

img_pista1_h = pygame.transform.rotate(img_pista1, 90)



for x in range(0, 4000, 30): # El -1 es para evitar grietas
    # Dibujamos 3 filas para que la vereda tenga 60px de alto (20 * 3)
    fondo_completo.blit(img_pista1_h, (x, 3240))
    fondo_completo.blit(img_pista1_h, (x, 3260))
    fondo_completo.blit(img_pista1_h, (x, 3280))

for x in range(0, 4000, 30):  # El -1 es para evitar grietas
    # Dibujamos 3 filas para que la vereda tenga 60px de alto (20 * 3)
    fondo_completo.blit(img_pista1_h, (x, 3300))
    fondo_completo.blit(img_pista1_h, (x, 3320))
    fondo_completo.blit(img_pista1_h, (x, 3340))



camara =Camara(800,600,4000,4000)

# llama a la imagen del personaje
#player_image =pygame.image.load("asets/imagenes/character/p1/xd.png")
#Escala al personaje
#player_image =pygame.transform.scale(player_image,(player_image.get_width()*Scala_Personaje,player_image.get_height()*Scala_Personaje))

animaciones =[]
direcciones = ["abajo","arriba","izquierda","derecha"]

for dir in direcciones:
    lista_temporal = []
    for i in range (1,4):
        img = pygame.image.load(f"asets/imagenes/character/p1/{dir}_{i}.png")

        img = pygame.transform.scale(img,(img.get_width()*Scala_Personaje,img.get_height()*Scala_Personaje))
        lista_temporal.append(img)
    animaciones.append(lista_temporal)

jugador =Personaje(1000,1200,animaciones)


# Escalamos las 4 imágenes
anim_npc1 = [
    pygame.transform.scale(n_abajo, (n_abajo.get_width()*Scala_NPC, n_abajo.get_height()*Scala_NPC)),
    pygame.transform.scale(n_arriba, (n_arriba.get_width()*Scala_NPC, n_arriba.get_height()*Scala_NPC)),
    pygame.transform.scale(n_izq, (n_izq.get_width()*Scala_NPC, n_izq.get_height()*Scala_NPC)),
    pygame.transform.scale(n_der, (n_der.get_width()*Scala_NPC, n_der.get_height()*Scala_NPC))
]
npc1 = NPC(2000, 1200, anim_npc1, ["¡Nuestras miradas se han cruzado!", "¡Combate Pokémon!"], beep_dialogo)



# Creamos al NPC pasando la lista





# Crear la lista de objetos del entorno

datos_mapa = [
    ("casa",100, 3680, (95, 3830,250,80)),
    ("casa", 850, 3680, (795, 3830,250,80)),
    ("arbol1", 1200, 1200, (1230, 1350,60,50)),
    ("mesa", 1015, 1350, (1000,1350,120,60)),
    ("silla1", 1000 , 1300, (0,0,0,0)),
    ("silla2", 1000,1450, (0,0,0,0)),

    ("mesa1",1615,1350,(1600,1350,120,60)),
    ("silla3", 1600 ,1300, (0,0,0,0)),
    ("silla4", 1600,1450, (0,0,0,0)),

    ("mesa", 2815, 1350, (2800,1350,120,60)),
    ("silla1", 2800 , 1300, (0,0,0,0)),
    ("silla2", 2800,1450, (0,0,0,0)),

    ("mesa", 3115, 1350, (3100,1350,120,60)),
    ("silla1", 3100 , 1300, (0,0,0,0)),
    ("silla2", 3100,1450, (0,0,0,0)),

    ("mesa", 3115, 2150, (3100,2150,120,60)),
    ("silla1", 3100 , 2100, (0,0,0,0)),
    ("silla2", 3100,2250, (0,0,0,0)),

    ("mesa", 2815, 2150, (2800,2150,120,60)),
    ("silla1", 2800 , 2100, (0,0,0,0)),
    ("silla2", 2800,2250, (0,0,0,0)),





    ("arbol2", 1250, 1500, (1280,1650,60,50)),
    ("arbol3", 1800, 1700, (1830,1850,60,50)),
    ("arbol4", 2100, 1600, (2130,1750,60,50)),
    ("arbol5", 2300,1200, (2330,1250,60,50)),
    ("arbol6", 2500, 1400, (2530,1550,60,50)),
    ("arbol7", 2600, 2000, (2630,2150,60,50)),
    ("arbol8", 2300, 2100, (2330,2250,60,50)),
    ("arbol9", 2700, 2300, (2730,2450,60,50)),
    ("arbol10", 2100, 2400, (2130,2550,60,50)),
    ("arbol11", 1400, 2400, (1430,2550,60,50)),
    ("arbol12", 1200, 2600, (1230,2750,60,50)),
    ("arbol13", 1300, 2100, (1330,2250,60,50)),
    ("arbol14", 1400, 1900, (1430,2050,60,50)),
    ("arbol15", 1800, 1200, (1830,1350,60,50)),
    ("arbol1", 3160, 1800, (3190, 1950,60,50)),
    ("arbol1", 3150, 1400, (3180, 1550,60,50)),
    ("arbol1", 3200, 2200, (3230, 2350,60,50)),
    ("arbol1", 3220, 2400, (3250, 2550,60,50)),
    ("arbol1", 3150, 2800, (3180, 2950,60,50)),
    ("arbol1", 2800, 3600, (2830, 3750,60,50)),
    ("arbol1", 2600, 3400, (2630, 3550,60,50)),
    ("arbol1", 2100, 3800, (2130, 3950,60,50)),


    ("pastoc2",2100,3400,(0,0,0,0)),
    ("pastoc2",2200,3400,(120,300,190,120)),
    ("pastoc2",2300,3400,(0,0,0,0)),
    ("pastoc2",2400,3400,(0,0,0,0)),
    ("pastoc3",1600,2000,(0,0,0,0)),
    ("pastoc4",2000,2000,(0,0,0,0)),

    ("pastoc1",2300,3880,(0,0,0,0)),
    ("pastoc1",2400,3880,(0,0,0,0)),
    ("pastoc1",2500,3880,(0,0,0,0)),
    ("pastoc1",2600,3880,(0,0,0,0)),

    ("pastoc1",2900,3880,(0,0,0,0)),
    ("pastoc1",3000,3880,(0,0,0,0)),

    ("pastoc1",2200,2100,(0,0,0,0)),
    ("pastoc1",2500,2300,(0,0,0,0)),
    ("pastoc1",2500,2400,(0,0,0,0)),
    ("pastoc1",2500,2400,(0,0,0,0)),
    ("pastoc1",2500,2500,(0,0,0,0)),
    ("pastoc1",2500,2600,(0,0,0,0)),
    ("pastoc1",2500,2700,(0,0,0,0)),
    ("pastoc1",2600,2300,(0,0,0,0)),
    ("pastoc1",2600,2400,(0,0,0,0)),
    ("pastoc1",2600,2500,(0,0,0,0)),
    ("pastoc1",2600,2600,(0,0,0,0)),

    ("pastoc1",1600,2600,(0,0,0,0)),
    ("pastoc1",1600,2700,(0,0,0,0)),
    ("pastoc1",1700,2300,(0,0,0,0)),
    ("pastoc1",1700,2400,(0,0,0,0)),
    ("pastoc1",1700,2500,(0,0,0,0)),
    ("pastoc1",1700,2600,(0,0,0,0)),

    ("pastoc1",1300,3000,(200,0,740,200)),
    ("pastoc1",1400,3000,(315,160,70,100)),
    ("pastoc1",1500,3000,(530,190,60,150)),
    ("pastoc1",1600,3000,(690,190,70,150)),
    ("pastoc1",1700,3000,(890,190,70,70)),
    ("pastoc1",1800,3000,(0,0,0,0)),
    ("pastoc1",1900,3000,(0,0,0,0)),
    ("pastoc1",2000,3000,(0,0,0,0)),
    ("pastoc1",2100,3000,(0,0,0,0)),
    ("pastoc1",2200,3000,(0,0,0,0)),
    ("pastoc1",2300,3000,(0,0,0,0)),
    ("pastoc1",2400,3000,(0,0,0,0)),

    ("pastoc1",2800,3000,(0,0,0,0)),

    ("pastoc1",1700,2200,(0,0,0,0)),
    ("pastoc1",1800,2200,(0,0,0,0)),
    ("pastoc1",1900,2300,(0,0,0,0)),

    ("pastoc1",2300,1700,(1350,900,120,230)),
    ("pastoc1",2300,1800,(1260,920,100,40)),
    ("pastoc1",2300,1900,(1050,920,100,40)),
    ("pastoc1",2300,2000,(1330,200,150,120)),
    ("pastoc1",2400,2000,(0,0,0,0)),
    ("pastoc1",2500,2000,(0,0,0,0)),
    ("pastoc1",2500,1900,(0,0,0,0)),
    ("pastoc1",2500,1800,(0,0,0,0)),
    ("pastoc1",2500,1700,(0,0,0,0)),

    ("pastoc1",3800,0,(0,0,0,0)),
    ("pastoc1",3800,100,(0,0,0,0)),
    ("pastoc1",3800,200,(0,0,0,0)),
    ("pastoc1",3800,300,(0,0,0,0)),
    ("pastoc1",3800,400,(0,0,0,0)),

    ("pastoc1", 1600, 0, (0, 0, 0, 0)),
    ("pastoc1", 1600, 100, (0, 0, 0, 0)),
    ("pastoc1", 1600, 200, (0, 0, 0, 0)),
    ("pastoc1", 1600, 300, (0, 0, 0, 0)),
    ("pastoc1", 1600, 400, (0, 0, 0, 0)),

    ("pastoc1", 1700, 100, (2490, 800, 180, 170)),
    ("pastoc1", 1800, 200, (3130, 800, 210, 170)),
    ("pastoc1", 1900, 300, (0, 0, 0, 0)),
    ("pastoc1", 2000, 300, (0, 0, 0, 0)),
    ("pastoc1", 2000, 200, (1700, 970, 20, 100)),
    ("pastoc1", 2000, 100, (1800, 970, 20, 100)),
    ("pastoc1", 2000, 400, (0, 0, 0, 0)),
    ("pastoc1", 2000, 0, (2150, 500, 200, 350)),


    ("pastoc1", 3910, 1000, (0, 0, 0, 0)),
    ("pastoc1", 3910, 1100, (0, 0, 0, 0)),
    ("pastoc1", 3910, 1200, (0, 0, 0, 0)),
    ("pastoc1", 3910, 1300, (0, 0, 0, 0)),
    ("pastoc1", 3910, 1400, (0, 0, 0, 0)),
    ("pastoc1", 3910, 1500, (0, 0, 0, 0)),
    ("pastoc1", 3910, 1600, (0, 0, 0, 0)),
    ("pastoc1", 3910, 1700, (0, 0, 0, 0)),
    ("pastoc1", 3910, 1800, (0, 0, 0, 0)),
    ("pastoc1", 3910, 1900, (0, 0, 0, 0)),
    ("pastoc1", 3910, 2000, (0, 0, 0, 0)),

    ("pastoverdeclaro", 3910, 2300, (0, 0, 0, 0)),
    ("pastoverdeclaro", 3910, 2360, (0, 0, 0, 0)),
    ("pastoverdeclaro", 3910, 2420, (0, 0, 0, 0)),
    ("pastoverdeclaro", 3910, 2480, (0, 0, 0, 0)),
    ("pastoverdeclaro", 3910, 2540, (0, 0, 0, 0)),
    ("pastoverdeclaro", 3910, 2600, (0, 0, 0, 0)),



    ("carro1",3500,200,(3480,200,180,340)),
    ("carro1",3400,2800,(3380,2800,180,340)),

    ("aula1",630,1500,(630,1500,430,390)),
    ("aula2",0,1300,(0,1300,430,390)),
    ("aula3",630,2100,(630,2100,430,390)),
    ("aula4",0,1900,(0,1900,430,390)),
    ("aula5",630,2700,(630,2700,430,390)),
    ("aula6",0,2500,(0,2500,430,390)),



    ("L4",2490,10,(2490,10,850,780)),
    ("letrero1",3000,1000,(3000,1010,100,20)),
    ("L2",1600,750,(1600,810,330,150)),
    ("CENTROAULA",320,20,(0,0,0,0)),
    ("carro3",915,3300,(910,3300,270,110)),


    ("carroblanco",1250,3150,(1250,3190,170,30)),
    ("carroazul",2200,3250,(2200,3290,170,30)),
    ("carroverde",2800,3150,(2800,3190,170,30)),

    ("tractor",50,3170,(50,3190,155,90)),
    ("edificio1",5,3300,(5,3330,880,300)),
    ("edificio2",1200,3300,(1200,3330,880,300)),
    ("edificiogrande",3700,1000,(3700,1000,200,400)),
    ("edificiogrande",3700,1400,(3700,1400,200,400)),
    ("edificiogrande",3700,1800,(3700,1800,200,400)),
    ("edificiogrande",3700,2200,(3700,2200,200,400)),
    ("edificiogrande2",3700,2600,(3690,2830,250,270)),
    ("carro2",550,3600,(545,3600,270,110)),
    ("escalera1",440,1440,(0,0,0,0)),
    ("escalera1",440,2050,(0,0,0,0)),
    ("escalera1",440,2650,(0,0,0,0)),
    ("escalera2",570,2250,(0,0,0,0)),
    ("escalera2",570,2800,(0,0,0,0)),
    ("escalera2",570,1650,(0,0,0,0)),
    ("camion",3850,3170,(3850,3170,180,120)),
    ("leo",3800,3300,(3800,3300,200,150)),
    ("estadio",3500,3500,(0,0,0,0)),
    ("estadio",3500,3700,(0,0,0,0)),
    ("estadio",3500,3900,(0,0,0,0)),
    ("estadio",3200,3500,(0,0,0,0)),
    ("estadio",3200,3700,(0,0,0,0)),
    ("estadio",3200,3900,(0,0,0,0)),

    ("faro1",1600,1050,(1610,1150,40,5)),
    ("faro1",580,1200,(590,1300,40,5)),
    ("faro1",2200,1250,(2210,1350,40,5)),
    ("faro1",1100,3000,(1110,3100,40,5)),
    ("faro1",3700,3050,(3710,3150,40,5)),

    ("faro2",3100,3050,(3110,3150,40,5)),
    ("faro2",3250,1050,(3260,1150,40,5)),
    ("faro2",2450,1050,(2460,1150,40,5)),
    ("decoracion2",650,2500,(630,2500,200,50)),
    ("decoracion2",2200,1100,(2190,1100,200,50)),
    ("decoracion2",650,1930,(630,1930,200,50)),
    ("decoracion2",650,3100,(630,3100,200,50)),

    ("decoracion3",3200,1650,(3190,1650,30,65)),
    ("decoracion3",3200,2700,(3190,2700,30,65)),
    ("decoracion3",2900,3000,(2890,3000,30,65)),
    ("decoracion3",2900,2400,(2890,2400,30,65)),

    ("decoracion4",1200,3680,(1190,3680,110,80)),
    ("decoracion4",1400,3880,(1390,3880,110,80)),
    ("decoracion4",1600,3680,(1590,3680,110,80)),
    ("decoracion4",1800,3880,(1790,3880,110,80)),
    ("decoracion4",2000,3680,(1990,3680,110,80)),




    ("basura1",2900,2000,(2900,2000,40,20)),
    ("basura2",2900,1910,(2900,1910,40,20)),
    ("basura3",700,1250,(700,1250,40,20)),
    ("basura1",3750,3350,(3750,3350,40,20)),
    ("basura2",2000,3100,(2000,3100,40,20)),
    ("basura3",2100,3100,(2100,3100,40,20)),

    ("pastoalto2",2100,3400,(2100,3400,25,50)),
    ("pastoalto2",2100,3450,(2100,3450,25,50)),
    ("pastoalto2",2100,3500,(2100,3500,25,50)),
    ("pastoalto2",2100,3550,(2100,3550,25,50)),
    ("pastoalto2",2100,3600,(2100,3600,25,50)),
    ("pastoalto2",2100,3650,(2100,3650,25,50)),
    ("pastoalto2",2100,3700,(2100,3700,25,50)),
    ("pastoalto2",2100,3750,(2100,3750,25,50)),
    ("pastoalto2",2100,3800,(2100,3800,25,50)),
    ("pastoalto2",2100,3850,(2100,3850,25,30)),


    ("pastoalto2",3100,3400,(3090,3400,35,50)),
    ("pastoalto2",3100,3450,(3090,3450,35,50)),
    ("pastoalto2",3100,3500,(3090,3500,35,50)),
    ("pastoalto2",3100,3550,(3090,3550,35,50)),
    ("pastoalto2",3100,3600,(3090,3600,35,50)),
    ("pastoalto2",3100,3650,(3090,3650,35,50)),
    ("pastoalto2",3100,3700,(3090,3700,35,50)),
    ("pastoalto2",3100,3750,(3090,3750,35,50)),
    ("pastoalto2",3100,3800,(3090,3800,35,50)),
    ("pastoalto2",3100,3850,(3090,3850,35,50)),
    ("pastoalto2",3100,3900,(3090,3900,35,50)),
    ("pastoalto2",3100,3950,(3090,3950,35,50)),

    ("pastoalto1",3050,3990,(3050,3990,40,20)),
    ("pastoalto1",2980,3990,(2980,3990,40,20)),
    ("pastoalto1",2910,3990,(2910,3990,40,20)),
    ("pastoalto1",2840,3990,(2840,3990,40,20)),
    ("pastoalto1",2750,3990,(2750,3990,40,20)),
    ("pastoalto1",2680,3990,(2680,3990,40,20)),
    ("pastoalto1",2610,3990,(2610,3990,40,20)),
    ("pastoalto1",2540,3990,(2540,3990,40,20)),
    ("pastoalto1",2450,3990,(2450,3990,40,20)),
    ("pastoalto1",2380,3990,(2380,3990,40,20)),
    ("pastoalto1",2310,3990,(2310,3990,40,20)),
    ("pastoalto1",2240,3990,(2240,3990,40,20)),
    ("pastoalto1",2170,3990,(2170,3990,40,20)),

    ("centropokemon",3700,600,(3700,620,230,150)),
    ("edificiosinpuerta",2040,820,(2040,850,300,220)),
    ("labo2",1920,470,(1930,480,250,250)),

    ("estadistica2",900,550,(900,550,580,390)),
    ("fiee",950,-200,(950,0,540,270)),
    ("fiee",-240,-100,(0,0,330,350)),
    ("veredasuper",600,210,(0,0,0,0)),
    ("veredasuper",600,300,(0,0,0,0)),
    ("veredasuper",600,400,(0,0,0,0)),
    ("veredasuper",600,500,(0,0,0,0)),
    ("veredasuper",600,600,(0,0,0,0)),
    ("veredasuper",600,700,(0,0,0,0)),
    ("veredasuper",600,800,(0,0,0,0)),
    ("veredasuper",600,900,(0,0,0,0)),
    ("veredasuper",600,1000,(0,0,0,0)),
    ("veredafinal",600,1090,(0,0,0,0)),

    ("pastoverdeclaro",180,480,(0,0,0,0)),
    ("pastoverdeclaro",375,480,(0,0,0,0)),
    ("pastoverdeclaro",180,520,(0,0,0,0)),
    ("pastoverdeclaro",375,520,(0,0,0,0)),
    ("pastoverdeclaro",180,560,(0,0,0,0)),
    ("pastoverdeclaro",375,560,(0,0,0,0)),
    ("pastoverdeclaro",180,600,(0,0,0,0)),
    ("pastoverdeclaro",375,600,(0,0,0,0)),
    ("pastoverdeclaro",180,640,(0,0,0,0)),
    ("pastoverdeclaro",375,640,(0,0,0,0)),
    ("pastoverdeclaro",180,680,(0,0,0,0)),
    ("pastoverdeclaro",375,680,(0,0,0,0)),
    ("pastoverdeclaro", 180, 720, (0, 0, 0, 0)),
    ("pastoverdeclaro", 375, 720, (0, 0, 0, 0)),
    ("pastoverdeclaro", 180, 760, (0, 0, 0, 0)),
    ("pastoverdeclaro", 375, 760, (0, 0, 0, 0)),
    ("pastoverdeclaro", 180, 800, (0, 0, 0, 0)),

    ("pastoverdeclaro", 180, 960, (0, 0, 0, 0)),
    ("pastoverdeclaro", 375, 960, (0, 0, 0, 0)),
    ("pastoverdeclaro", 180, 1000, (0, 0, 0, 0)),
    ("pastoverdeclaro", 375, 1000, (0, 0, 0, 0)),
    ("pastoverdeclaro", 180, 1040, (0, 0, 0, 0)),


    ("pastoverdeclaro", 900, 500, (0, 0, 0, 0)),
    ("pastoverdeclaro", 1095, 500, (0, 0, 0, 0)),

    ("pastoverdeclaro", 1250, 400, (0, 0, 0, 0)),
    ("pastoverdeclaro", 1250, 440, (0, 0, 0, 0)),
    ("pastoverdeclaro", 1100, 1040, (0, 0, 0, 0)),




    ("arbolgrande",150,500,(280,850,40,40)),
    ("arbolgrande",870,50,(1000,400,40,40)),
    ("arbolgrande",2280,3350,(2410,3700,40,40)),

    ("pastoamarillo",1100,2100,(0,0,0,0)),
    ("pastoamarillo",1100,2160,(0,0,0,0)),
    ("pastoamarillo",1100,2220,(0,0,0,0)),
    ("pastoamarillo",1100,2280,(0,0,0,0)),
    ("pastoamarillo",1100,2340,(0,0,0,0)),
    ("pastoamarillo",1100,2400,(0,0,0,0)),
    ("pastoamarillo",1100,2460,(0,0,0,0)),


    ("pastoamarillo",1070,1500,(0,0,0,0)),
    ("pastoamarillo",1070,1560,(0,0,0,0)),
    ("pastoamarillo",1070,1620,(0,0,0,0)),
    ("pastoamarillo",1070,1680,(0,0,0,0)),
    ("pastoamarillo",1070,1740,(0,0,0,0)),

    ("pastoamarillo",900,3150,(0,0,0,0)),
    ("pastoamarillo",1100,2880,(0,0,0,0)),
    ("pastoamarillo",1100,2940,(0,0,0,0)),

    ("pastoamarillo",500,3780,(0,0,0,0)),
    ("pastoamarillo",500,3880,(0,0,0,0)),
    ("pastoamarillo",500,3940,(0,0,0,0)),

    ("floresrosadas",2900,3370,(0,0,0,0)),
    ("floresazules",460,1170,(0,0,0,0)),
    ("floresazules",690,1170,(0,0,0,0)),
    ("floresamarillas",2530,1170,(0,0,0,0)),
    ("floresamarillas",3130,1170,(0,0,0,0)),
    ("estatua",540,300,(0,0,0,0)),
    ("estatua",710,300,(0,0,0,0)),
    ("pastosalto",3800,3600,(3830,3650,0,0)),
    ("pastosalto",3800,3670,(3830,3720,0,0)),
    ("pastosalto",3800,3740,(3830,3790,0,0)),
    ("pastosalto",3890,3600,(3910,3650,0,0)),
    ("pastosalto",3890,3670,(3910,3720,0,0)),
    ("pastosalto",3890,3740,(3910,3790,0,0)),

    ("barro",3850,3900,(0,0,0,0)),
























]

lista_entorno = []
for tipo,x,y,offset in datos_mapa:
    obj= ObjetoEstatico(x, y, assets[tipo],offset)
    lista_entorno.append(obj)



#llamamos a la clase de personaje
#jugador =Personaje(50,50,player_image)







#definir variables para el movimiento del jugador
mover_arriba = False
mover_abajo = False
mover_izquierda = False
mover_derecha= False



# Esto controla la velocidad del juego
reloj = pygame.time.Clock()



fuente = pygame.font.Font("asets/FuenteDeTexto/pixel.ttf", 24)


def dibujar_dialogo(texto, ventana):
    # Dibujar una caja de texto en la parte inferior
    pygame.draw.rect(ventana, (0, 0, 0), (50, 450, 700, 100))  # Fondo negro
    pygame.draw.rect(ventana, (255, 255, 255), (50, 450, 700, 100), 3)  # Borde blanco

    img_texto = fuente.render(texto, True, (255, 255, 255))
    ventana.blit(img_texto, (70, 470))




# 1. Crear una superficie del tamaño total del mapa
foto_nivel = pygame.Surface((4000, 4000)) # Ajusta al tamaño de tu mapa

# 2. Dibujar el suelo
foto_nivel.blit(fondo_completo, (0, 0))

# 3. Dibujar los objetos (Casas, árboles, etc.)
# Usamos un offset de (0,0) porque queremos la imagen completa, no la vista de la cámara
for obj in lista_entorno:
    # Dibujamos la imagen del objeto en su posición absoluta
    foto_nivel.blit(obj.image, obj.rect_dibujo.topleft)

# 4. Guardar el resultado final
pygame.image.save(foto_nivel, "mapa_con_objetos.png")








# BUCLE PRINCIPAL

game_over = False
while not game_over:
    camara.seguir(jugador)
    ventana.blit(fondo_completo, (0-camara.offset.x, 0 - camara.offset.y))

    lista_obstaculos = [npc1] + lista_entorno

    #calcular el movimiento del jugador
    delta_x=0
    delta_y=0
    if mover_derecha == True:
        delta_x=5
    if mover_izquierda == True:
        delta_x=-5
    if mover_arriba == True:
        delta_y=-5
    if mover_abajo == True:
        delta_y=5
    #mover al personaje
    jugador.movimiento(delta_x,delta_y,lista_obstaculos)
    # --- Dentro del bucle principal ---
    npc1.actualizar_direccion(jugador.forma)  # El NPC detecta dónde está el jugador

    elementos_escena = lista_entorno + [npc1, jugador]



    # 2. Ordenamos la lista: el que tenga la base (bottom) más alta en la pantalla
    # se dibuja primero, y el que esté más cerca del borde inferior se dibuja al final.
    elementos_escena.sort(key=lambda obj: obj.forma.bottom)


    # 4. Dibujamos todo en el orden correcto
    for elemento in elementos_escena:
        elemento.dibujar(ventana,camara.offset)

    #for objeto in lista_entorno:
        #objeto.dibujar(ventana)

    if delta_x !=0 or delta_y != 0:
        jugador.update_animacion()

    #jugador.dibujar(ventana)
    #npc1.dibujar(ventana)

    area_interaccion = npc1.forma.inflate(40, 40)
    cerca_del_npc = jugador.forma.colliderect(area_interaccion)


    if npc1.hablando:
        dibujar_dialogo(npc1.dialogo[npc1.frase_actual], ventana)
    elif cerca_del_npc:
        # Solo mostrar el aviso de "Presiona E" si no está hablando ya
        aviso = fuente.render("", True, (255, 255, 0))
        ventana.blit(aviso, (npc1.forma.x - 20, npc1.forma.y - 40))

    # A. Manejo de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True  # Es mejor cambiar la variable para una salida limpia

        if event.type ==pygame.KEYDOWN:
            if event.key == pygame.K_e:
                area_interaccion = npc1.forma.inflate(40, 40)
                if cerca_del_npc:
                    npc1.interactuar()  # Esto cambia la frase o cierra el diálogo
            if event.key == pygame.K_a:
                mover_izquierda =True

            if event.key == pygame.K_d:
                mover_derecha = True

            if event.key == pygame.K_s:
                mover_abajo = True

            if event.key == pygame.K_w:
                mover_arriba = True

        #para cuando se suelta la tecla
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                    mover_izquierda = False

            if event.key == pygame.K_d:
                    mover_derecha = False

            if event.key == pygame.K_s:
                    mover_abajo = False

            if event.key == pygame.K_w:
                    mover_arriba = False








    # C. ACTUALIZAR la pantalla (Esto es lo que te faltaba)
    pygame.display.update()

    # D. Control de frames (60 cuadros por segundo)
    reloj.tick(60)

# Salida limpia del programa
pygame.quit()


