import math
import sys
from pathlib import Path
import json
import cv2

# Esto obliga al juego a mirar en su propia carpeta antes de buscar en internet
if not str(Path.cwd()) in sys.path:
    sys.path.append(str(Path.cwd()))

import pygame
from personaje import Personaje, NPC, ObjetoEstatico, Camara,Pokemon
from LOGICA_BATALLA import SistemaBatalla
import random
import asyncio


class Juego:
    def __init__(self):
        # 1. Configuración de Ventana y Sistemas
        pygame.init()
        pygame.mixer.init()
        self.ancho, self.alto = 800, 600
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("UNIMON- El Camino del Ingeniero")
        self.reloj = pygame.time.Clock()
        self.offset_interior = pygame.Vector2(0, 0)

        self.oak_dialogos = []  # Empezamos con una lista vacía para que "exista"
        self.oak_indice = 0
        self.estado_juego = "MENU_INICIO"  # O el estado que tengas por defecto
        self.base_oak = None
        self.sprite_oak = None
        self.musica_batalla_entrenador = "asets/music/A3.mp3"


        #Fuente de texto del juego
        try:
            self.fuente = pygame.font.Font("asets/FuenteDeTexto/pokemon.otf", 40)
        except Exception as e:
            print(f"Error cargando fuente: {e}")
            self.fuente = pygame.font.SysFont("Arial", 40)


        # 2. CARGA DE AUDIOS (IMPORTANTE: Definir antes que los NPCs)
        self.musica_ambiente = "asets/music/A1.mp3"
        self.musica_batalla = "asets/music/A2.mp3"
        self.musica_batalla_salvaje = "asets/music/A2.mp3"

        self.sonido_curacion = pygame.mixer.Sound("asets/music/curacion.mp3")
        self.sonido_curacion.set_volume(0.8)

        try:
            # Cargamos el sonido del diálogo (el .ogg que convertiste)
            self.beep_dialogo = pygame.mixer.Sound("asets/music/E1.ogg")
            self.beep_dialogo.set_volume(0.3)

            # Cargamos la música pero NO le damos play aquí (evita error en web)
            pygame.mixer.music.load(self.musica_ambiente)
            pygame.mixer.music.set_volume(1)
        except Exception as e:
            print(f"Advertencia de audio: {e}")
            # Creamos un objeto vacío para que el código no falle en la línea 200
            self.beep_dialogo = None



        # 3. Carga de Sprites y Assets
        self.assets = self._cargar_diccionario_assets()

        try:
            img_joy = pygame.image.load("asets/imagenes/CENTROPOKEMON/enfermera.png").convert_alpha()
            # La escalamos de una vez (ajusta el 3.8 para que coincida con el tamaño del mapa)
            self.joy_sprite = pygame.transform.scale(img_joy,
                                                     (int(img_joy.get_width() * 3.8), int(img_joy.get_height() * 3.8)))
        except Exception as e:
            print(f"No se encontró la imagen de fondo: {e}")


        #cuando creas a Joy:
        self.joy_dialogo = [
            "¡Hola! Bienvenido al Centro Pokémon.",
            "Tus Pokémon parecen cansados...",
            "Déjame curarlos por ti.",
            "......",
            "¡Listo! Tus Pokémon están en plena forma."
        ]
        self.joy_indice_dialogo = -1  # -1 significa que no está hablando




        #TIENDA
        self.items_tienda = [
            {"nombre": "Pokebola", "precio": 200},
            {"nombre": "Pocion", "precio": 300},
            {"nombre": "Antidoto", "precio": 100},
            {"nombre": "Salir", "precio": 0}
        ]
        self.tienda_seleccionada = 0  # Para saber qué ítem tiene la flechita
        self.mostrar_menu_tienda = False

        self.menu_tienda_abierto = False
        self.fase_tienda = "PRINCIPAL"  # Puede ser "PRINCIPAL" o "COMPRAR"
        self.tienda_seleccionada = 0

        # Opciones de los dos menús
        self.opciones_principal = ["Comprar", "Vender", "Salir"]
        self.opciones_compra = ["Pokebola", "Pocion", "Atras"]





        # 4. Construcción del Mundo
        self.fondo_completo = self._crear_mapa_base()
        self._dibujar_veredas_y_pistas()
        self.camara = Camara(800, 600, 4000, 4000)




        # ---------------------------------------------------------
        # 5. CREACIÓN DE ENTIDADES
        # ---------------------------------------------------------
        self.jugador = self._crear_jugador()

        self.mapa_actual = "EXTERIOR"  # Esto quita el error que te sale

        # --- COLISIONES INVISIBLES DEL CENTRO POKÉMON ---
        self.muros_interiores = []  # Se llenará al entrar al centro

        # --- SENSORES DE PUERTA DEL CENTRO POKEMON ---
        self.rect_puerta_cp = pygame.Rect(3800, 750, 60, 40)
        self.npcs_exterior = []  # NPCs que van en el mapa exterior
        self.npcs_interior_estadistica = []  # NPCs que van en estadística
        self.lista_npcs = self.npcs_exterior


        # Cargar los NPCs en sus listas correspondientes
        self._cargar_todos_los_npcs()

        # Inicializar lista_npcs con los del exterior
        self.lista_npcs = self.npcs_exterior  # <--- ESTA ES LA ÚNICA ASIGNACIÓ

        self.lista_entorno = self._cargar_objetos_estaticos()

        # IMPORTANTE: Asegúrate de que _crear_pokemons_salvajes NO use .mp3 en Sound()
        self.lista_pokemon = self._crear_pokemons_salvajes()

        # 6. Estados de Control y Zonas
        self.mover_arriba = self.mover_abajo = False
        self.mover_izquierda = self.mover_derecha = False


        #ZONAS DEL MAPA
        self.zonas = [
            {"nombre": "ESTADISTICA", "rect": pygame.Rect(1200, 900, 600, 400)},
            {"nombre": "LAB. DE L4", "rect": pygame.Rect(1600, 800, 600, 400)},
            {"nombre": "LAB. DE L3", "rect": pygame.Rect(2780, 350, 800, 600)},
            {"nombre": "JAULA FIEE", "rect": pygame.Rect(3300, 3600, 500, 500)},
            {"nombre": "TIENDA LEO", "rect": pygame.Rect(3800, 3500, 400, 300)},
            {"nombre": "MESITAS FIEE", "rect": pygame.Rect(2600, 1500, 500, 500)},
            {"nombre": "NUEVOS LAB L1", "rect": pygame.Rect(1500, 3200, 400, 300)},
            {"nombre": "AULAS", "rect": pygame.Rect(400, 2000, 400, 300)}
        ]
        self.zona_actual = ""
        self.timer_cartel = 0
        self.alpha_cartel = 0
        self.estado_juego = "EXPLORACION"
        self.instancia_batalla = None
        self.transicion_batalla = False
        self.alpha_transicion = 0
        self.pokemon_pendiente = None



        #MENU
        self.menu_pausa_abierto = False
        self.opcion_menu_seleccionada = 0
        self.opciones_menu = ["Pokemon", "Bolsa", "Carnet", "Guardar", "Salir"]

        #MENU INICIO
        self.estado_juego = "MENU_INICIO"  # El juego arranca aquí
        self.opcion_inicio_seleccionada = 0
        self.opciones_inicio = ["Nueva Partida", "Continuar"]
        try:
            self.imagen_fondo_titulo = pygame.image.load("asets/imagenes/INICIO/fondo_inicio.png").convert()
            self.imagen_fondo_titulo = pygame.transform.scale(self.imagen_fondo_titulo, (800, 600))
        except:
            print("No se encontró la imagen de fondo, usando color sólido.")
            self.imagen_fondo_titulo = None



        #INTRODUCCION
        self.video_path = "asets/video/tu_introduccion.mp4"
        self.cap = cv2.VideoCapture(self.video_path)
        self.video_terminado = False
        try:
            self.sonido_intro = pygame.mixer.Sound("asets/music/intro_audio.mp3")
            self.sonido_intro.set_volume(0.5)
        except Exception as e:
            self.sonido_intro = None
            print(f"No se pudo cargar el audio de la intro: {e}")
        self.audio_intro_reproducido = False
        self.ruta_musica_menu = "asets/music/musica_menu.mp3"
        self.musica_menu_sonando = False
        self.video_terminado = False
        self.estado_juego = "INTRO"

        # 1. Cargar la imagen del título
        self.imagen_titulo_juego = None  # Valor por defecto
        try:
            ruta_test = "asets/imagenes/INICIO/titulo_juego.png"
            print(f"Intentando cargar desde: {ruta_test}")

            # Cargamos
            img_raw = pygame.image.load(ruta_test).convert_alpha()

            # Medidas
            self.orig_width = img_raw.get_width()
            self.orig_height = img_raw.get_height()
            self.base_width = 500
            self.base_height = int((self.orig_height / self.orig_width) * self.base_width)

            # Guardamos en la variable definitiva
            self.imagen_titulo_juego = pygame.transform.smoothscale(img_raw, (self.base_width, self.base_height))
            print("¡ÉXITO: Imagen cargada correctamente!")

        except Exception as e:
            print(f"ERROR CRÍTICO: No se pudo cargar el título. Motivo: {e}")

        # VARIABLES DE ANIMACIÓN
        self.titulo_x = 400
        self.titulo_y = 150
        self.escala_titulo = 1.0
        self.destino_x = 400
        self.angulo_respiracion = 0
        self.opciones_x = -300

        self.transicion_batalla = False
        self.alpha_transicion = 0


        #INTRO RECTOR
        # --- EN EL __init__ ---
        try:
            # 1. El fondo del laboratorio
            img_lab = pygame.image.load("asets/imagenes/INICIO_RECTOR/fondo_lab.png").convert()
            self.imagen_fondo_oak= pygame.transform.scale(img_lab, (800, 600))

            # 2. La base donde se para Oak
            img_base = pygame.image.load("asets/imagenes/INICIO_RECTOR/base_oak.png").convert_alpha()
            self.base_oak = pygame.transform.scale(img_base,
                                                   (int(img_base.get_width() * 4), int(img_base.get_height() * 4)))

            # 3. El Profesor Oak
            img_oak = pygame.image.load("asets/imagenes/INICIO_RECTOR/oak_sprite.png").convert_alpha()
            self.sprite_oak = pygame.transform.scale(img_oak,
                                                     (int(img_oak.get_width() * 4), int(img_oak.get_height() * 4)))

            # --- DIÁLOGOS DE OAK ---
            self.oak_dialogos = [
                "¡Hola! ¡Perdona por la espera!",
                "¡Bienvenido al mundo de POKÉMON!",
                "Me llamo OAK. ¡Pero la gente me llama PROFESOR POKÉMON!",
                "Este mundo está habitado por unas criaturas llamadas POKÉMON.",
                "¿Estás listo para comenzar tu propia aventura?"
            ]


        except Exception as e:
            print(f"Error cargando recursos de Oak: {e}")

        try:
            self.imagen_cuadro_dialogo = pygame.image.load(
                "asets/imagenes/INICIO_RECTOR/cuadro_dialogo.png").convert_alpha()
            # Escalar si es necesario (ajusta el tamaño según prefieras)
            self.imagen_cuadro_dialogo = pygame.transform.scale(self.imagen_cuadro_dialogo, (575, 105))
        except Exception as e:
            print(f"Error cargando cuadro de diálogo: {e}")
            self.imagen_cuadro_dialogo = None

        self.img_pokebola = pygame.image.load("asets/imagenes/INICIO_RECTOR/pokebola.png").convert_alpha()
        self.img_pokemon_intro = pygame.image.load("asets/imagenes/INICIO_RECTOR/bulbasaur_intro.png").convert_alpha()

        # Escalamos si es necesario (ajusta el tamaño a tu gusto)
        self.img_pokebola = pygame.transform.scale(self.img_pokebola, (45, 45))
        self.img_pokemon_intro = pygame.transform.scale(self.img_pokemon_intro, (110, 110))




        try:
            self.sonido_pokebola = pygame.mixer.Sound("asets/music/pokebola.mp3")  # Ajusta la ruta
            self.sonido_pokebola.set_volume(0.2)

            self.sonido_pokemon = pygame.mixer.Sound("asets/music/rugido_pokemon.mp3")  # Ajusta la ruta
            self.sonido_pokemon.set_volume(1.5)

            # Variable para controlar qué sonidos ya se reprodujeron
            self.sonidos_intro_reproducidos = {
                "pokebola": False,
                "pokemon": False
            }

        except Exception as e:
            print(f"Error cargando sonidos de la intro: {e}")
            self.sonido_pokebola = None
            self.sonido_pokemon = None

        self.mostrando_mensaje_mision = False
        self.titulo_mision = ""
        self.descripcion_mision = ""
        self.tiempo_inicio_mensaje = 0
        self.duracion_mensaje = 5000  # 5 segundos

        self.rect_puerta_estadistica = pygame.Rect(1188, 943, 24, 44)
        self.game_over = False



        self.npcs_exterior = []  # NPCs que van en el mapa exterior
        self.npcs_interior_estadistica = []  # NPCs que van en estadística

        # Cargar los NPCs en sus listas correspondientes
        self._cargar_todos_los_npcs()




        self.pokemon_mostrado = None  # Pokémon que se está mostrando actualmente
        self.mostrar_pokemon = False  # Controlar si se muestra o no

        try:
            self.img_charmander = pygame.image.load(
                "asets/imagenes/POKEMON_EN_BATALLA/charmander_1.png").convert_alpha()
            self.img_charmander = pygame.transform.scale(self.img_charmander, (150, 150))
            print(f"✅ Charmander cargado: {self.img_charmander.get_size()}")
        except Exception as e:
            print(f"❌ Error Charmander: {e}")
            self.img_charmander = None

        try:
            self.img_squirtle = pygame.image.load("asets/imagenes/POKEMON_EN_BATALLA/squirtle_1.png").convert_alpha()
            self.img_squirtle = pygame.transform.scale(self.img_squirtle, (150, 150))
            print(f"✅ Squirtle cargado: {self.img_squirtle.get_size()}")
        except Exception as e:
            print(f"❌ Error Squirtle: {e}")
            self.img_squirtle = None

        try:
            self.img_bulbasaur = pygame.image.load("asets/imagenes/POKEMON_EN_BATALLA/bulbasaur_1.png").convert_alpha()
            self.img_bulbasaur = pygame.transform.scale(self.img_bulbasaur, (150, 150))
            print(f"✅ Bulbasaur cargado: {self.img_bulbasaur.get_size()}")
        except Exception as e:
            print(f"❌ Error Bulbasaur: {e}")
            self.img_bulbasaur = None

        # Después de cargar las imágenes, agrega:
        self.descripciones_pokemon = {
            "charmander": {
                "nombre": "Charmander",
                "tipo": "Fuego",
                "descripcion1": "Le encantan las cosas calientes. Dicen",
                "descripcion2": "cuando llueve,el vapor sale de",
                "descripcion3": "la punta de su cola.",
                "habilidad": "Mar Llamas",
                "altura": "0.6 m",
                "peso": "8.5 kg"
            },
            "squirtle": {
                "nombre": "Squirtle",
                "tipo": "Agua",
                "descripcion1": "Cuando retrae su largo cuello en el ",
                "descripcion2": "caparazón,dispara agua a una presión",
                "descripcion3": "increíble.",
                "habilidad": "Torrente",
                "altura": "0.5 m",
                "peso": "9.0 kg"
            },
            "bulbasaur": {
                "nombre": "Bulbasaur",
                "tipo": "Planta/Veneno",
                "descripcion1": "Este Pokémon nace con una semilla en ",
                "descripcion2": "el lomo, que crece según va",
                "descripcion3":"evolucionando.",
                "habilidad": "Espesura",
                "altura": "0.7 m",
                "peso": "6.9 kg"
            }
        }

        self.mostrando_tarjeta_pokemon = False
        self.pokemon_en_tarjeta = None
        self.opcion_starter_seleccionada = 0  # 0 = Sí, 1 = No
        self.starter_ya_elegido = False

        self.tiene_pokemon = False

        self.mostrando_mensaje_mision = False
        self.titulo_mision = ""
        self.descripcion_mision = ""
        self.tiempo_inicio_mensaje = 0
        self.duracion_mensaje = 5000  # 5 segundos

        try:
            self.imagen_cartel_zona = pygame.image.load("asets/imagenes/INTERFAZ/cartel_zona.png").convert_alpha()
            # Escalar si es necesario (ajusta el tamaño según tu imagen)
            self.imagen_cartel_zona = pygame.transform.scale(self.imagen_cartel_zona, (300, 80))
            print("✅ Imagen de cartel de zona cargada")
        except Exception as e:
            print(f"⚠️ No se pudo cargar imagen de cartel: {e}")
            self.imagen_cartel_zona = None


    def _crear_pokemons_salvajes(self):
        """Crea los Pokémon que actúan como NPCs decorativos en el mapa."""

        # 1. Cargamos solo las animaciones de caminar (las 4 direcciones)
        anim_onix = self._cargar_animaciones_pokemon("onix")
        anim_pikachu = self._cargar_animaciones_pokemon("pikachu")
        anim_bulbasaur = self._cargar_animaciones_pokemon("bulbasaur")
        anim_magnamite = self._cargar_animaciones_pokemon("magnamite")
        anim_charmander = self._cargar_animaciones_pokemon("charmander")
        anim_squirtle = self._cargar_animaciones_pokemon("squirtle")


        # 2. Definimos las zonas de movimiento
        z_central = pygame.Rect(100, 100, 550, 800)
        z_estadio = pygame.Rect(900, 300, 500, 800)
        z_parque1 = pygame.Rect(1400, 1800, 500, 800)
        z_parque2 = pygame.Rect(1900, 1800, 500, 900)

        # 3. Añadimos los Pokémon (Sin sonidos, son solo visuales)
        # Nota: He quitado el argumento de sonido de la clase Pokemon para estos NPCs
        lista_temporal = [
            Pokemon("onix", 500, 600, anim_onix, None, z_central),
            Pokemon("pikachu", 1100, 400, anim_pikachu, None, z_estadio),
            Pokemon("bulbasaur", 1200, 450, anim_bulbasaur, None, z_estadio, escala_personalizada=1.5),
            Pokemon("charmander", 1450, 1860, anim_charmander, None, z_parque1, escala_personalizada=1.5),
            Pokemon("magnamite", 1980, 1830, anim_magnamite, None, z_parque2, escala_personalizada=1.5),
            Pokemon("charmander", 1950, 1890, anim_charmander, None, z_parque2, escala_personalizada=1.5),
            Pokemon("squirtle", 2000, 1850, anim_squirtle, None, z_parque2, escala_personalizada=1.5),
            Pokemon("magnamite", 500, 700, anim_magnamite, None, z_central, escala_personalizada=1.5),
            Pokemon("bulbasaur", 480, 350, anim_bulbasaur, None, z_central, escala_personalizada=1.5),

        ]

        return lista_temporal


    def _definir_pool_salvajes(self):
        # Esta lista no se dibuja, solo guarda la "receta" para crear al pokemon
        return [
            {"nombre": "onix", "nivel": 5  },
            {"nombre": "pikachu", "nivel": 5},
            {"nombre": "magnamite", "nivel": 5},
            {"nombre": "pidgey", "nivel": 5},
            {"nombre": "horsea", "nivel": 5},
            {"nombre": "Rhyhorn", "nivel": 4},
            {"nombre": "tangela", "nivel": 4},
            {"nombre": "hitmonlee", "nivel": 5},
            {"nombre": "hitmonchan", "nivel": 5},
            {"nombre": "caterpie", "nivel": 5},



        ]

    def _preparar_pokemon_pool(self, nombre, nivel):
        try:
            # Cargar imágenes para el enemigo (vista frontal)
            frames_enemigo = []
            for i in range(1, 3):
                ruta = f"asets/imagenes/POKEMON_EN_BATALLA/{nombre}_{i}.png"
                img = pygame.image.load(ruta).convert_alpha()
                frames_enemigo.append(img)

            # 🎵 Cargar sonido del Pokémon
            try:
                sonido = pygame.mixer.Sound(f"asets/music/{nombre}_song.mp3")
                print(f"   ✅ Sonido cargado para {nombre}")
            except Exception as e:
                print(f"   ⚠️ No hay sonido para {nombre}: {e}")
                sonido = None

            # Cargar imagen de jugador (si existe)
            frames_jugador = []
            try:
                ruta_player = f"asets/imagenes/POKEMON_EN_BATALLA/{nombre}_player.png"
                img_player = pygame.image.load(ruta_player).convert_alpha()
                frames_jugador = [img_player, img_player]
                print(f"   ✅ Imagen de jugador cargada para {nombre}")
            except:
                # Si no existe, crear desde enemigo
                img_volteada = pygame.transform.flip(frames_enemigo[0], True, False)
                frames_jugador = [img_volteada, img_volteada]
                print(f"   ⚠️ Usando imagen volteada para {nombre}")

            # Escalado personalizado
            escala = 1.0
            nombre_clean = nombre.lower().strip()
            if nombre_clean == "pikachu":  # 🟢 AÑADIR PIKACHU AQUÍ
                escala = 1.9  # Un poco más grande que el estándar
                print(f"   ⚡ Pikachu escala ajustada a {escala}")






            # Escalar imágenes enemigo
            frames_enemigo_escalados = []
            for img in frames_enemigo:
                ancho = int(img.get_width() * escala)
                alto = int(img.get_height() * escala)
                frames_enemigo_escalados.append(pygame.transform.scale(img, (ancho, alto)))

            # Escalar imágenes jugador
            frames_jugador_escalados = []
            for img in frames_jugador:
                ancho = int(img.get_width() * escala)
                alto = int(img.get_height() * escala)
                frames_jugador_escalados.append(pygame.transform.scale(img, (ancho, alto)))

            # Animaciones para batalla
            anim_batalla = {
                "abajo": frames_enemigo_escalados,
                "arriba": frames_enemigo_escalados,
                "izquierda": frames_enemigo_escalados,
                "derecha": frames_enemigo_escalados
            }

            # Crear Pokémon (CON SONIDO)
            pokemon = Pokemon(nombre, 0, 0, anim_batalla, sonido, None, escala, nivel)
            pokemon.nombre = nombre
            pokemon.nivel = nivel

            # 🟢 OBTENER STATS DEL POKÉMON
            stats = self.obtener_stats_pokemon(nombre)

            # Asignar tipos
            pokemon.tipo = stats["tipo"]
            pokemon.tipo2 = stats.get("tipo2")

            # Calcular stats según nivel
            pokemon.tipo = stats["tipo"]
            pokemon.tipo2 = stats.get("tipo2")
            pokemon.hp_max = stats["hp"] + (nivel * 2)  # +10 para nivel 5
            pokemon.hp_actual = pokemon.hp_max
            pokemon.ataque = stats["ataque"] + (nivel // 2)  # +2 para nivel 5
            pokemon.defensa = stats["defensa"] + (nivel // 2)
            pokemon.ataque_especial = stats["ataque_especial"] + (nivel // 2)
            pokemon.defensa_especial = stats["defensa_especial"] + (nivel // 2)
            pokemon.velocidad = stats["velocidad"] + (nivel // 2)



            # Inicializar modificadores de stats
            pokemon.modificador_ataque = 0
            pokemon.modificador_defensa = 0
            pokemon.modificador_ataque_especial = 0
            pokemon.modificador_defensa_especial = 0
            pokemon.modificador_velocidad = 0
            pokemon.modificador_evasion = 0
            pokemon.modificador_precision = 0

            # Asignar ataques según el nombre
            pokemon.ataques = self.obtener_ataques_por_pokemon(nombre)
            print(f"🔴 _preparar_pokemon_pool - {nombre} recibe ataques: {pokemon.ataques}")

            # Guardar frames
            pokemon.frames_batalla_enemigo = frames_enemigo_escalados
            pokemon.frames_batalla_jugador = frames_jugador_escalados

            print(
                f"✅ {nombre} Nv.{nivel} creado - Tipo: {pokemon.tipo} - HP: {pokemon.hp_max} - Stats: ATK:{pokemon.ataque} DEF:{pokemon.defensa} VEL:{pokemon.velocidad}")
            return pokemon

        except Exception as e:
            print(f"❌ Error cargando Pokémon {nombre}: {e}")
            return None



    def obtener_stats_pokemon(self, nombre):
        """Devuelve los stats base de cada Pokémon"""
        nombre = nombre.lower().strip()

        stats = {
            "bulbasaur": {"tipo": "planta", "tipo2": "veneno", "hp": 45, "ataque": 49, "defensa": 49,
                          "ataque_especial": 65, "defensa_especial": 65, "velocidad": 45},
            "charmander": {"tipo": "fuego", "hp": 39, "ataque": 52, "defensa": 43,
                           "ataque_especial": 60, "defensa_especial": 50, "velocidad": 65},
            "squirtle": {"tipo": "agua", "hp": 44, "ataque": 48, "defensa": 65,
                         "ataque_especial": 50, "defensa_especial": 64, "velocidad": 43},
            "pikachu": {"tipo": "electrico", "hp": 35, "ataque": 55, "defensa": 40,
                        "ataque_especial": 50, "defensa_especial": 50, "velocidad": 90},
            "onix": {"tipo": "roca", "tipo2": "tierra", "hp": 35, "ataque": 45, "defensa": 160,
                     "ataque_especial": 30, "defensa_especial": 45, "velocidad": 70},
            "magnamite": {"tipo": "electrico", "tipo2": "acero", "hp": 25, "ataque": 35, "defensa": 70,
                          "ataque_especial": 95, "defensa_especial": 55, "velocidad": 45},
            "hitmonlee": {"tipo": "lucha", "hp": 50, "ataque": 120, "defensa": 53,
                          "ataque_especial": 35, "defensa_especial": 110, "velocidad": 87},
            "hitmonchan": {"tipo": "lucha", "hp": 50, "ataque": 105, "defensa": 79,
                           "ataque_especial": 35, "defensa_especial": 110, "velocidad": 76},
            "pidgey": {"tipo": "normal", "tipo2": "volador", "hp": 40, "ataque": 45, "defensa": 40,
                       "ataque_especial": 35, "defensa_especial": 35, "velocidad": 56},
            "horsea": {"tipo": "agua", "hp": 30, "ataque": 40, "defensa": 70,
                       "ataque_especial": 70, "defensa_especial": 25, "velocidad": 60},
            "rhyhorn": {"tipo": "tierra", "tipo2": "roca", "hp": 80, "ataque": 85, "defensa": 95,
                        "ataque_especial": 30, "defensa_especial": 30, "velocidad": 25},
            "tangela": {"tipo": "planta", "hp": 65, "ataque": 55, "defensa": 115,
                        "ataque_especial": 100, "defensa_especial": 40, "velocidad": 60},
            "caterpie": {"tipo":"insecto", "hp": 65, "ataque": 55, "defensa": 115,
                        "ataque_especial": 100, "defensa_especial": 40, "velocidad": 60},
        }

        # Si el Pokémon no está en la lista, usar Bulbasaur como predeterminado
        if nombre not in stats:
            print(f"⚠️ No hay stats para {nombre}, usando Bulbasaur como predeterminado")
            return stats["bulbasaur"]

        return stats[nombre]






    def _crear_jugador(self):
        animaciones = []
        escala = 1.3
        direcciones = ["abajo", "arriba", "izquierda", "derecha"]

        for dir in direcciones:
            lista_temporal = []
            for i in range(1, 4):
                img = pygame.image.load(f"asets/imagenes/character/p1/{dir}_{i}.png")
                ancho = int(img.get_width() * escala)
                alto = int(img.get_height() * escala)
                img = pygame.transform.scale(img, (ancho, alto))
                lista_temporal.append(img)
            animaciones.append(lista_temporal)

        # Crear personaje SIN stats de Pokémon
        personaje = Personaje(638, 223, animaciones, nombre="Entrenador")

        # 🟢 Inicializar sin Pokémon
        personaje.tiene_pokemon = False
        personaje.hp_max = 0
        personaje.hp_actual = 0
        personaje.nivel = 0
        personaje.ataques = []
        personaje.equipo = []
        personaje.pokemon_activo = 0
        personaje.frames_batalla = None

        print("✅ Personaje creado sin Pokémon (debe elegir starter)")
        return personaje

    def _cargar_animaciones_npc(self, nombre_npc, escala=1.3):
        """Carga las animaciones de un NPC con la escala especificada"""
        animaciones = []
        direcciones = ["n1_abajo", "n1_arriba", "n1_izquierda", "n1_derecha"]

        for direccion in direcciones:
            lista_frames = []
            ruta = f"asets/imagenes/npcs/{nombre_npc}/{direccion}.png"

            try:
                img = pygame.image.load(ruta).convert_alpha()

                # Aplicar escala
                nuevo_ancho = int(img.get_width() * escala)
                nuevo_alto = int(img.get_height() * escala)
                img_escalada = pygame.transform.scale(img, (nuevo_ancho, nuevo_alto))

                lista_frames.append(img_escalada)

            except Exception as e:
                print(f"Error cargando: {ruta} - {e}")
                # Crear superficie de respaldo
                surf = pygame.Surface((64, 96))
                surf.fill((255, 0, 255))
                lista_frames.append(surf)

            animaciones.append(lista_frames)

        return animaciones

    def _cargar_todos_los_npcs(self):
        """Carga todos los NPCs y los separa por mapa"""

        pokemon_rival1 = self._preparar_pokemon_pool("charmander", 13)
        pokemon_rival2 = self._preparar_pokemon_pool("pikachu", 8)
        pokemon_rival3 = self._preparar_pokemon_pool("onix", 15)
        pokemon_rival4 = self._preparar_pokemon_pool("horsea", 28)
        pokemon_rival5 = self._preparar_pokemon_pool("magnamite", 7)
        pokemon_rival6 = self._preparar_pokemon_pool("pidgey", 12)
        pokemon_rival7 = self._preparar_pokemon_pool("hitmonlee", 24)
        pokemon_rival8 = self._preparar_pokemon_pool("hitmonchan", 26)
        pokemon_rival9 = self._preparar_pokemon_pool("squirtle", 30)
        pokemon_rival10 = self._preparar_pokemon_pool("tangela", 34)
        pokemon_rival11 = self._preparar_pokemon_pool("bulbasaur", 35)






        # 1. Cargar animaciones
        anim_alumno1 = self._cargar_animaciones_npc("NPC1", escala=1.3)
        anim_vigilante1 = self._cargar_animaciones_npc("NPC2", escala=1.3)
        anim_vigilante2 = self._cargar_animaciones_npc("NPC3", escala=1.3)
        anim_oak = self._cargar_animaciones_npc("OAK", escala=1.3)  # Oak más grande
        anim_estudiante1 = self._cargar_animaciones_npc("ESTUDIANTE1", escala=1.3)
        anim_estudiante2 = self._cargar_animaciones_npc("ESTUDIANTE2", escala=1.3)
        anim_estudiante3 = self._cargar_animaciones_npc("ESTUDIANTE3", escala=1.3)
        anim_estudiante4=  self._cargar_animaciones_npc("ESTUDIANTE4", escala=1.3)
        anim_estudiante5 = self._cargar_animaciones_npc("ESTUDIANTE5", escala=1.3)

        anim_estudiante6 = self._cargar_animaciones_npc("ESTUDIANTE6", escala=1.3)
        anim_estudiante7 = self._cargar_animaciones_npc("ESTUDIANTE7", escala=1.3)
        anim_estudiante8 = self._cargar_animaciones_npc("ESTUDIANTE8", escala=1.3)
        anim_estudiante9 = self._cargar_animaciones_npc("ESTUDIANTE9", escala=1.3)
        anim_estudiante10 = self._cargar_animaciones_npc("ESTUDIANTE10", escala=1.3)
        anim_estudiante11 = self._cargar_animaciones_npc("ESTUDIANTE11", escala=1.3)
        anim_estudiante12 = self._cargar_animaciones_npc("ESTUDIANTE12", escala=1.3)
        anim_hugito= self._cargar_animaciones_npc("ESPECIAL1", escala=1.3)
        anim_lider1=  self._cargar_animaciones_npc("LIDER1", escala=1.3)
        anim_lider2 = self._cargar_animaciones_npc("LIDER2", escala=1.3)
        anim_lider3 =  self._cargar_animaciones_npc("LIDER3", escala=1.3)



        anim_profesor1 = self._cargar_animaciones_npc("PROFESOR1", escala=1.3)

        anim_pokebolas= self._cargar_animaciones_npc("POKEBOLAS", escala=1.4)  # Oak más grande



        # 2. Diálogo de Oak
        dialogo_oak = [
            "¡Bienvenido al edificio de Estadística!",
            "Soy el Profesor Oak, director de la FIEE.",
            "Para comenzar tu aventura",
            "necesitarás un compañero Pokémon.",
            "Elige uno de estos 3 para empezar:",
            "Bulbasaur, Squirtle o Charmander."
        ]

        # 3. Diálogos para otros NPCs
        dialogo_profesor = [
            "La FIEE es la mejor facultad.",
            "Estudia mucho y serás un gran ingeniero."
        ]

        dialogo_estudiante1 = [
            "¿Ya atrapaste todos los Pokémon?",
            "Yo estoy buscando un Pikachu."
        ]

        dialogo_estudiante2 = [
            "Tralalero tralala",
            "Orcalero orcala",
            "Capto hipopotamo ",
            "Cocofanto Elefanto",
            "Bonbardilo Cocodrilo",
            ":>....."

        ]

        dialogo_estudiante3= [
            "Mi Unimon esta envenenado",
            "He venido a la tienda ",
            "a comprar antidotos ",
        ]

        dialogo_estudiante4 = [
            "Es mi primera vez en la FIEE",
            "Un gusto conocerte",
        ]
        dialogo_estudiante5 = [
            "No encuentro mi salon......",
            "¿Sabes donde esta el salon 105?",
        ]
        dialogo_vigilante1 = [
            "prohibido el ingreso........",
            "...................",
            "ahh, porque tengo que tratar ",
            "con estos cachimbos",
        ]
        dialogo_vigilante2 = [
            "hacia el sur estas los salones",
            "No te pierdas",

        ]
        dialogo_profesor1 = [
            "¿Eres de L4?",
        ]
        dialogo_hugito = [
            "Que tal cachimbo,cuídate de química 2",
            "cachimbo es broma, debes tener en cuenta",
            "la ventaja de tipos para lograr tu egreso"
        ]
        dialogo_estudiante6 = [
            "estoy esperando que habran el salon",
            "dicen que el profe del salon 205 ",
            "usa pokemon tipo tierra"
        ]

        dialogo_lider1 = [
            "hola este es el salon 201",
            "soy el profesor del curso de redes",
            "usa pokemon tipo electrico",
            "preparate!"
        ]

        dialogo_lider2 = [
            "hola este es el salon 202",
            "soy el profesor del curso de redes",
            "usa pokemon tipo volador",
            "preparate!"
        ]

        dialogo_lider3 = [
            "hola este es el salon 203",
            "soy el profesor del curso de POO",
            "usa pokemon tipo fuego",
            "preparate!"
        ]
        dialogo_lider4 = [
            "hola este es el salon 204",
            "soy el profesor del curso de F1 y F3",
            "usa pokemon tipo lucha",
            "preparate!"
        ]
        dialogo_lider5 = [
            "hola este es el salon 205",
            "soy el profesor del curso de SO",
            "usa pokemon tipo agua",
            "preparate!"
        ]
        dialogo_lider6 = [
            "hola este es el salon 206",
            "soy el profesor del curso de diferencial",
            "usa pokemon tipo planta",
            "preparate!"
        ]



        # ==========================================
        # NPCs del EXTERIOR (¡AQUÍ AGREGA TODOS LOS QUE QUIERAS!)
        # ==========================================
        self.npcs_exterior = [
            # NPCs existentes
            NPC(2000, 1200, anim_alumno1, ["¡Hola!"], self.beep_dialogo),
            NPC(100, 1200, anim_vigilante1, dialogo_vigilante2, self.beep_dialogo),
            NPC(3180, 3400, anim_vigilante1, ["¡Hola!"], self.beep_dialogo),
            NPC(3700, 300, anim_vigilante1, ["¡Hola!"], self.beep_dialogo),
            NPC(400, 3600, anim_vigilante1, ["¡Hola!"], self.beep_dialogo),
            NPC(1300, 2600, anim_vigilante2, ["¡Hola!"], self.beep_dialogo),
            NPC(1230, 300, anim_vigilante2, ["no puedes entrar aca ,solo egresados"], self.beep_dialogo),
            NPC(20, 400, anim_vigilante2, dialogo_vigilante1, self.beep_dialogo),
            NPC(2500, 2000, anim_vigilante2, ["cuidado con los Pokémon salvajes!"], self.beep_dialogo),
            NPC(2500, 2400, anim_estudiante1, dialogo_estudiante1, self.beep_dialogo),
            NPC(2500, 2700, anim_estudiante2, dialogo_estudiante2, self.beep_dialogo),
            NPC(3800, 3900, anim_estudiante3, dialogo_estudiante3, self.beep_dialogo),
            NPC(400,400,anim_estudiante4,dialogo_estudiante4,self.beep_dialogo),
            NPC(984, 400, anim_estudiante5, dialogo_estudiante5, self.beep_dialogo),
            NPC(1000, 600, anim_profesor1, dialogo_profesor1, self.beep_dialogo),

            NPC(3000, 1293, anim_estudiante6, dialogo_profesor1, self.beep_dialogo),
            NPC(370, 1100, anim_estudiante7, dialogo_profesor1, self.beep_dialogo),
            NPC(360, 1800, anim_estudiante10, dialogo_estudiante6, self.beep_dialogo),
            NPC(470, 2200, anim_estudiante8, dialogo_profesor1, self.beep_dialogo),
            NPC(2800, 100, anim_estudiante8, dialogo_profesor1, self.beep_dialogo),
            NPC(3150, 3600, anim_estudiante9, dialogo_profesor1, self.beep_dialogo),
            NPC(2060, 2600, anim_estudiante10, dialogo_profesor1, self.beep_dialogo),
            NPC(1480, 2400, anim_estudiante12, dialogo_profesor1, self.beep_dialogo),
            NPC(2640, 2800, anim_estudiante10, dialogo_profesor1, self.beep_dialogo),
            NPC(2860, 2900, anim_estudiante1, dialogo_profesor1, self.beep_dialogo),
            NPC(3404, 3300, anim_estudiante7, dialogo_profesor1, self.beep_dialogo),
            NPC(470, 3200, anim_estudiante11, dialogo_profesor1, self.beep_dialogo),
            NPC(470, 2700, anim_estudiante9, dialogo_profesor1, self.beep_dialogo),
            NPC(490, 2900, anim_estudiante12, dialogo_profesor1, self.beep_dialogo),
            NPC(560, 3100, anim_estudiante4, dialogo_profesor1, self.beep_dialogo),
            NPC(800, 2800, anim_estudiante2, dialogo_profesor1, self.beep_dialogo),
            NPC(2300, 2200, anim_estudiante7, dialogo_profesor1, self.beep_dialogo),
            NPC(780, 2900, anim_estudiante9, dialogo_profesor1, self.beep_dialogo),
            NPC(1472, 1273, anim_estudiante6, dialogo_profesor1, self.beep_dialogo),

            NPC(890, 1950, anim_hugito, dialogo_hugito, self.beep_dialogo),
            NPC(2032, 758, anim_vigilante2, dialogo_vigilante1, self.beep_dialogo),
            NPC(2044, 40, anim_estudiante10, dialogo_vigilante1, self.beep_dialogo),
            NPC(1973, 320, anim_estudiante1, dialogo_vigilante1, self.beep_dialogo),
            NPC(2627, 985, anim_estudiante8, dialogo_vigilante1, self.beep_dialogo),
            NPC(3087, 890, anim_estudiante12, dialogo_vigilante1, self.beep_dialogo),
            NPC(3362, 820, anim_estudiante4, dialogo_vigilante1, self.beep_dialogo),
            NPC(2627, 985, anim_estudiante7, dialogo_vigilante1, self.beep_dialogo),
            NPC(3901, 2180, anim_estudiante9, dialogo_vigilante1, self.beep_dialogo),

            NPC(3936, 2628, anim_estudiante11, dialogo_vigilante1, self.beep_dialogo),
            NPC(3676, 3698, anim_estudiante8, dialogo_vigilante1, self.beep_dialogo),
            NPC(3501, 3703, anim_estudiante12, dialogo_vigilante1, self.beep_dialogo),
            NPC(3201, 3881, anim_estudiante4, dialogo_vigilante1, self.beep_dialogo),
            NPC(2836, 3876, anim_estudiante7, dialogo_vigilante1, self.beep_dialogo),
            NPC(2491, 3706, anim_estudiante9, dialogo_vigilante1, self.beep_dialogo),
            NPC(2256, 3886, anim_estudiante11, dialogo_vigilante1, self.beep_dialogo),

            NPC(2852, 2093, anim_estudiante8, dialogo_vigilante1, self.beep_dialogo),
            NPC(3152, 2103, anim_estudiante12, dialogo_vigilante1, self.beep_dialogo),
            NPC(2767, 2143, anim_estudiante4, dialogo_vigilante1, self.beep_dialogo),
            NPC(3117, 1533, anim_estudiante7, dialogo_vigilante1, self.beep_dialogo),
            NPC(3182, 1298, anim_estudiante9, dialogo_vigilante1, self.beep_dialogo),
            NPC(1682, 1298, anim_estudiante11, dialogo_vigilante1, self.beep_dialogo),

        ]
        self.npcs_exterior.append(
            NPC(
                2800, 1500,
                anim_vigilante1,
                ["¡Hola! Soy estudiante de L4!", "¿Quieres combatir?", "¡Prepárate!"],
                self.beep_dialogo,
                equipo=[pokemon_rival1, pokemon_rival2],
                nombre_entrenador="Entrenador Juan",
                es_rival= True  # ← ¡IMPORTANTÍSIMO!

            ),
        )

        self.npcs_exterior.append(
            NPC(
                1000, 1200,
                anim_profesor1,
                dialogo_profesor1,
                self.beep_dialogo,
                equipo=[pokemon_rival1, pokemon_rival2],
                nombre_entrenador="Profesor Merchan",
                es_rival=True  # ← ¡IMPORTANTÍSIMO!
            )

        )

        self.npcs_exterior.append(
            NPC(
                3910, 180,
                anim_estudiante7,
                dialogo_profesor1,
                self.beep_dialogo,
                equipo=[pokemon_rival3, pokemon_rival4],
                nombre_entrenador="Estudiante Sebastian",
                es_rival=True  # ← ¡IMPORTANTÍSIMO!
            )

        )
        self.npcs_exterior.append(
            NPC(
                3910, 3980,
                anim_estudiante4,
                dialogo_estudiante6,
                self.beep_dialogo,
                equipo=[pokemon_rival3, pokemon_rival4],
                nombre_entrenador="Estudiante Bruno",
                es_rival=True  # ← ¡IMPORTANTÍSIMO!
            )

        )
        self.npcs_exterior.append(
            NPC(
                3800, 3580,
                anim_estudiante8,
                dialogo_profesor1,
                self.beep_dialogo,
                equipo=[pokemon_rival2, pokemon_rival4],
                nombre_entrenador="Estudiante Luis",
                es_rival=True  # ← ¡IMPORTANTÍSIMO!
            )

        )
        self.npcs_exterior.append(
            NPC(
                3910, 3700,
                anim_estudiante10,
                dialogo_profesor1,
                self.beep_dialogo,
                equipo=[pokemon_rival1, pokemon_rival4],
                nombre_entrenador="Estudiante Paul",
                es_rival=True  # ← ¡IMPORTANTÍSIMO!
            )

        )
        self.npcs_exterior.append(
            NPC(
                3600, 3500,
                anim_estudiante1,
                dialogo_profesor1,
                self.beep_dialogo,
                equipo=[pokemon_rival3, pokemon_rival1],
                nombre_entrenador="Estudiante Carlos",
                es_rival=True  # ← ¡IMPORTANTÍSIMO!
            )

        )
        self.npcs_exterior.append(
            NPC(
                3400, 3900,
                anim_estudiante3,
                dialogo_profesor1,
                self.beep_dialogo,
                equipo=[pokemon_rival3, pokemon_rival4],
                nombre_entrenador="Estudiante Sebastian",
                es_rival=True  # ← ¡IMPORTANTÍSIMO!
            )

        )
        self.npcs_exterior.append(
            NPC(
                3910, 180,
                anim_estudiante7,
                dialogo_profesor1,
                self.beep_dialogo,
                equipo=[pokemon_rival4, pokemon_rival4],
                nombre_entrenador="Estudiante Diego",
                es_rival=True  # ← ¡IMPORTANTÍSIMO!
            )

        )
        self.npcs_exterior.append(
            NPC(
                3910, 180,
                anim_estudiante5,
                dialogo_profesor1,
                self.beep_dialogo,
                equipo=[pokemon_rival1, pokemon_rival4],
                nombre_entrenador="Estudiante Pedro",
                es_rival=True  # ← ¡IMPORTANTÍSIMO!
            )

        )






        self.npcs_exterior.append(
            NPC(
                442, 1480,
                anim_lider1,
                dialogo_lider1,
                self.beep_dialogo,
                equipo=[pokemon_rival5, pokemon_rival2],
                nombre_entrenador="Profesor Quillas",
                es_rival=True

            ),
        )
        self.npcs_exterior.append(
            NPC(
                577, 1688,
                anim_lider2,
                dialogo_lider2,
                self.beep_dialogo,
                equipo=[pokemon_rival6, pokemon_rival6],
                nombre_entrenador="Profesor Janampa",
                es_rival=True

            ),
        )
        self.npcs_exterior.append(
            NPC(
                442, 2078,
                anim_lider3,
                dialogo_lider3,
                self.beep_dialogo,
                equipo=[pokemon_rival1, pokemon_rival3],
                nombre_entrenador="Profesor Yury",
                es_rival=True

            ),
        )
        self.npcs_exterior.append(
            NPC(
                582, 2283,
                anim_lider1,
                dialogo_lider4,
                self.beep_dialogo,
                equipo=[pokemon_rival7, pokemon_rival8],
                nombre_entrenador="Profesor Chirinos",
                es_rival=True  # ← ¡IMPORTANTÍSIMO!

            ),
        )
        self.npcs_exterior.append(
            NPC(
                572, 2833,
                anim_lider2,
                dialogo_lider5,
                self.beep_dialogo,
                equipo=[pokemon_rival4, pokemon_rival9],
                nombre_entrenador="profesor Wattson",
                es_rival=True  # ← ¡IMPORTANTÍSIMO!

            ),
        )
        self.npcs_exterior.append(
            NPC(
                580, 3000,
                anim_lider3,
                dialogo_lider6,
                self.beep_dialogo,
                equipo=[pokemon_rival10, pokemon_rival11],
                nombre_entrenador="profesor Chavez",
                es_rival=True,
                es_lider_final=True



            ),
        )







        # ==========================================
        # NPCs del INTERIOR DE ESTADÍSTICA (SOLO OAK)
        # ==========================================
        self.npcs_interior_estadistica = [
            NPC(350, 250, anim_oak, dialogo_oak, self.beep_dialogo),  # Solo Oak
            NPC(500, 200, anim_pokebolas,["....."], self.beep_dialogo, tipo_pokemon="charmander"),
            NPC(570, 200, anim_pokebolas, ["....."], self.beep_dialogo, tipo_pokemon="squirtle"),
            NPC(640, 200, anim_pokebolas, ["....."], self.beep_dialogo, tipo_pokemon="bulbasaur"),
            NPC(300, 50, anim_pokebolas, ["no dice que pokemon es"], self.beep_dialogo),
        ]

        self.npcs_exterior[1].forma.width = 10  # Ancho de colisión
        self.npcs_exterior[1].forma.height = 40


        self.npcs_interior_estadistica[2].forma.width = 10
        self.npcs_interior_estadistica[2].forma.height =40
        self.npcs_interior_estadistica[3].forma.width = 10
        self.npcs_interior_estadistica[3].forma.height = 40



        # ==========================================
        # (OPCIONAL) NPCs para OTROS INTERIORES
        # ==========================================
        # self.npcs_centro_pokemon = [
        #     NPC(200, 300, anim_enfermera, ["Bienvenido al Centro"], self.beep_dialogo),
        # ]

        # self.npcs_tienda = [
        #     NPC(400, 350, anim_vendedor, ["¿Qué desea comprar?"], self.beep_dialogo),
        # ]

        # 5. Por defecto, usar NPCs del exterior
        self.lista_npcs = self.npcs_exterior

        print(f"✅ NPCs cargados:")
        print(f"   - Exterior: {len(self.npcs_exterior)} NPCs")
        print(f"   - Estadística: {len(self.npcs_interior_estadistica)} NPCs")


    def _cargar_diccionario_assets(self):
        # Aquí va tu diccionario gigante de 'assets' que ya tienes configurado
        # He puesto los principales para mantener el ejemplo claro
        return {
            "kakuna": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/arriba_1.png"),
                (39, 51)
            ),
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
            "mesa": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/mesa1.png"),
                (108, 78)
            ),
            "silla1": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/silla01.png"),
                (141, 39)
            ),
            "silla2": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/silla01.png"),
                (141, 39)
            ),
            "mesa1": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/mesa1.png"),
                (108, 78)
            ),
            "silla3": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/silla01.png"),
                (141, 39)
            ),
            "silla4": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/silla01.png"),
                (141, 39)
            ),
            "pastoc1": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/pasto_de_captura_2.png"),
                (96, 96)
            ),
            "pastoc2": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/pasto_de_captura_2.png"),
                (96, 96)
            ),
            "pastoc3": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/pasto_de_captura.png"),
                (96, 192)
            ),
            "pastoc4": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/pasto_de_captura.png"),
                (96, 192)
            ),
            "carro1": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/carro1.png"),
                (177, 390)
            ),
            "aula1": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/aula_oficial.png"),
                (442, 442)
            ),
            "aula2": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/aula_oficial.png"),
                (442, 442)
            ),
            "aula3": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/aula_oficial.png"),
                (442, 442)
            ),
            "aula4": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/aula_oficial.png"),
                (442, 442)
            ),
            "aula5": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/aula_oficial.png"),
                (442, 442)
            ),
            "aula6": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/aula_oficial.png"),
                (442, 442)
            ),
            "L4": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/lab2.png"),
                (852, 996)
            ),
            "letrero1": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/letrero1.png"),
                (96, 72)
            ),
            "L2": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/CENTRAL.png"),
                (374, 372)
            ),
            "CENTROAULA": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/centro_aula.png"),
                (654, 346)
            ),
            "edificio1": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/edificio1.png"),
                (886.5, 379.5)
            ),
            "edificio2": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/edificio1.png"),
                (886.5, 379.5)
            ),
            "edificiogrande": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/edificiogrande.png"),
                (206, 406)
            ),
            "carro2": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/carro2.png"),
                (262, 177)
            ),
            "carro3": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/carro2.png"),
                (262, 177)
            ),
            "carro4": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/carro3.png"),
                (114, 147)
            ),
            "carroblanco": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/carro_blanco.png"),
                (168, 120)
            ),
            "carroverde": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/carro_verde.png"),
                (168, 120)
            ),
            "carroazul": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/carro_azul.png"),
                (168, 120)
            ),
            "escalera1": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/escalera_oficial.png"),
                (56, 152)
            ),
            "escalera2": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/escalera_oficial1.png"),
                (64, 178)
            ),
            "camion": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/camion.png"),
                (192, 160)
            ),
            "tractor": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/tractor.png"),
                (154, 132)
            ),
            "leo": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/leo.png"),
                (195, 261)
            ),
            "estadio": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/batalla1.png"),
                (224, 96)
            ),
            "faro1": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/faro1.png"),
                (54, 141)
            ),
            "faro2": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/faro2.png"),
                (96, 141)
            ),
            "decoracion1": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/decoracion1.png"),
                (45, 45)
            ),
            "decoracion2": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/decoracion2.png"),
                (180, 87)
            ),
            "decoracion3": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/decoracion3.png"),
                (31, 86)
            ),
            "decoracion4": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/decoracion4.png"),
                (95, 133)
            ),
            "basura1": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/basura1.png"),
                (45, 72)
            ),
            "basura2": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/basura2.png"),
                (45, 72)
            ),
            "basura3": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/basura3.png"),
                (45, 72)
            ),
            "pastoalto1": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/pastoalto1.png"),
                (63, 34)
            ),
            "pastoalto2": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/pastoalto2.png"),
                (32, 50)
            ),
            "centropokemon": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/centropokemon.png"),
                (261, 273)
            ),
            "edificiosinpuerta": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/edificiosinpuerta.png"),
                (354, 354)
            ),
            "labo2": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/labo1.png"),
                (478.5, 457.5)
            ),
            "edificiogrande2": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/edificiogrande2.png"),
                (260, 560)
            ),
            "estadistica2": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/estadistica1.png"),
                (570, 621)
            ),
            "fiee": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/teleco.png"),
                (560, 540)
            ),
            "veredasuper": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/verderasuper.png"),
                (95, 114)
            ),
            "veredafinal": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/veredafinal.png"),
                (95, 114)
            ),
            "pastoamarillo": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/pastoamarillo.png"),
                (193.5, 48)
            ),
            "pastoverdeclaro": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/pastoverdeclaro.png"),
                (192, 48)
            ),
            "arbolgrande": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/arbolgrande.png"),
                (320, 504)
            ),
            "floresazules": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/floresazules.png"),
                (144, 32)
            ),
            "floresrosadas": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/flores.png"),
                (144, 32)
            ),
            "floresamarillas": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/floresamarillas.png"),
                (144, 32)
            ),
            "estatua": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/estatuapok.png"),
                (45, 96)
            ),
            "pastosalto": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/pastosalto.png"),
                (96, 87)
            ),
            "barro": pygame.transform.scale(
                pygame.image.load("asets/imagenes/character/Tiles/barro.png"),
                (108, 82)
            ),


        }


    def _crear_mapa_base(self):
        # Cargamos una sola vez
        img_pasto = pygame.image.load(
            "asets/imagenes/character/Tiles/pasto1.png").convert()  # .convert() es clave para velocidad
        superficie = pygame.Surface((4000, 4000))

        # Llenamos el mapa
        for x in range(0, 4000, 32):
            for y in range(0, 4000, 32):
                superficie.blit(img_pasto, (x, y))

        return superficie  # Esta superficie ya tiene todo el pasto

    def _dibujar_veredas_y_pistas(self):

        img_pasto = pygame.image.load("asets/imagenes/character/Tiles/pasto1.png")
        img_vereda = pygame.image.load("asets/imagenes/character/Tiles/vereda.png").convert_alpha()
        img_pista1 = pygame.image.load("asets/imagenes/character/Tiles/pista_1.png").convert_alpha()
        img_pista2 = pygame.image.load("asets/imagenes/character/Tiles/pista_2.png").convert_alpha()

        # 2. Creamos una "Superficie" del tamaño de toda la ventana
        # Esto es como un lienzo en blanco gigante

        fondo_completo = pygame.Surface((4000, 4000))

        # 3. "Alfombramos" el lienzo una sola vez
        for x in range(0, 4000, 32):
            for y in range(0, 4000, 32):
                # 1. Dibujamos SIEMPRE el pasto base primero
                self.fondo_completo.blit(img_pasto, (x, y))

        inicio_x = 3000
        inicio_y = 1200
        largo_vereda = 3300  # Hasta dónde llega hacia abajo

        # Dibujamos la vereda repitiendo el bloque de 39px de alto
        for y in range(inicio_y, largo_vereda, 30):
            # Si quieres que la vereda sea más ancha que 20px,
            # podemos dibujarla 3 veces de lado (20 + 20 + 20 = 60px)
            self.fondo_completo.blit(img_vereda, (inicio_x, y))
            self.fondo_completo.blit(img_vereda, (inicio_x + 20, y))
            self.fondo_completo.blit(img_vereda, (inicio_x + 40, y))

        inicio_x4 = 495
        inicio_y4 = 1200
        largo_vereda4 = 3500  # Hasta dónde llega hacia abajo

        # Dibujamos la vereda repitiendo el bloque de 39px de alto
        for y in range(inicio_y4, largo_vereda4, 30):
            # Si quieres que la vereda sea más ancha que 20px,
            # podemos dibujarla 3 veces de lado (20 + 20 + 20 = 60px)
            self.fondo_completo.blit(img_vereda, (inicio_x4, y))
            self.fondo_completo.blit(img_vereda, (inicio_x4 + 20, y))
            self.fondo_completo.blit(img_vereda, (inicio_x4 + 40, y))

        inicio_x5 = 2400
        inicio_y5 = 0
        largo_vereda5 = 1200  # Hasta dónde llega hacia abajo

        # Dibujamos la vereda repitiendo el bloque de 39px de alto
        for y in range(inicio_y5, largo_vereda5, 30):
            # Si quieres que la vereda sea más ancha que 20px,
            # podemos dibujarla 3 veces de lado (20 + 20 + 20 = 60px)
            self.fondo_completo.blit(img_vereda, (inicio_x5, y))
            self.fondo_completo.blit(img_vereda, (inicio_x5 + 20, y))
            self.fondo_completo.blit(img_vereda, (inicio_x5 + 40, y))

        inicio_x6 = 1500
        inicio_y6 = 0
        largo_vereda6 = 1250  # Hasta dónde llega hacia abajo

        # Dibujamos la vereda repitiendo el bloque de 39px de alto
        for y in range(inicio_y6, largo_vereda6, 30):
            # Si quieres que la vereda sea más ancha que 20px,
            # podemos dibujarla 3 veces de lado (20 + 20 + 20 = 60px)
            self.fondo_completo.blit(img_vereda, (inicio_x6, y))
            self.fondo_completo.blit(img_vereda, (inicio_x6 + 20, y))
            self.fondo_completo.blit(img_vereda, (inicio_x6 + 40, y))

        inicio_x1 = 3350
        inicio_y1 = 0
        largo_vereda1 = 3300

        for y in range(inicio_y1, largo_vereda1, 30):
            # Si quieres que la vereda sea más ancha que 20px,
            # podemos dibujarla 3 veces de lado (20 + 20 + 20 = 60px)
            self.fondo_completo.blit(img_vereda, (inicio_x1, y))
            self.fondo_completo.blit(img_vereda, (inicio_x1 + 20, y))
            self.fondo_completo.blit(img_vereda, (inicio_x1 + 40, y))

        # 1. Rotamos la imagen original
        img_vereda_h = pygame.transform.rotate(img_vereda, 90)

        # 2. Ahora el ancho es 39 y el alto es 20
        for x in range(0, 3000, 30):  # El -1 es para evitar grietas
            # Dibujamos 3 filas para que la vereda tenga 60px de alto (20 * 3)
            self.fondo_completo.blit(img_vereda_h, (x, 1200))
            self.fondo_completo.blit(img_vereda_h, (x, 1220))
            self.fondo_completo.blit(img_vereda_h, (x, 1240))

        for x in range(0, 3650, 30):  # El -1 es para evitar grietas
            # Dibujamos 3 filas para que la vereda tenga 60px de alto (20 * 3)
            self.fondo_completo.blit(img_vereda_h, (x, 1200))
            self.fondo_completo.blit(img_vereda_h, (x, 1220))
            self.fondo_completo.blit(img_vereda_h, (x, 1240))

        for x in range(0, 4000, 30):  # El -1 es para evitar grietas
            # Dibujamos 3 filas para que la vereda tenga 60px de alto (20 * 3)
            self.fondo_completo.blit(img_vereda_h, (x, 3200))
            self.fondo_completo.blit(img_vereda_h, (x, 3220))

        inicio_x2 = 3428
        inicio_y2 = 0
        largo_pista1 = 3300  # Hasta dónde llega hacia abajo

        # Dibujamos la vereda repitiendo el bloque de 39px de alto
        for y in range(inicio_y2, largo_pista1, 30):
            # Si quieres que la vereda sea más ancha que 20px,
            # podemos dibujarla 3 veces de lado (20 + 20 + 20 = 60px)
            self.fondo_completo.blit(img_pista1, (inicio_x2 + 200, y))
            self.fondo_completo.blit(img_pista1, (inicio_x2 + 180, y))
            self.fondo_completo.blit(img_pista1, (inicio_x2 + 160, y))
            self.fondo_completo.blit(img_pista1, (inicio_x2 + 140, y))
            self.fondo_completo.blit(img_pista1, (inicio_x2 + 120, y))
            self.fondo_completo.blit(img_pista1, (inicio_x2 + 100, y))
            self.fondo_completo.blit(img_pista1, (inicio_x2 + 80, y))
            self.fondo_completo.blit(img_pista1, (inicio_x2 + 60, y))
            self.fondo_completo.blit(img_pista1, (inicio_x2 + 40, y))
            self.fondo_completo.blit(img_pista1, (inicio_x2 + 20, y))
            self.fondo_completo.blit(img_pista1, (inicio_x2, y))

        inicio_x3 = 3600
        inicio_y3 = 0
        largo_pista2 = 3300  # Hasta dónde llega hacia abajo

        # Dibujamos la vereda repitiendo el bloque de 39px de alto
        for y in range(inicio_y3, largo_pista2, 30):
            # Si quieres que la vereda sea más ancha que 20px,
            # podemos dibujarla 3 veces de lado (20 + 20 + 20 = 60px)
            fondo_completo.blit(img_pista2, (inicio_x3, y))
            fondo_completo.blit(img_pista2, (inicio_x3 + 20, y))
            fondo_completo.blit(img_pista2, (inicio_x3 + 40, y))
            fondo_completo.blit(img_pista2, (inicio_x3 + 60, y))

        img_pista1_h = pygame.transform.rotate(img_pista1, 90)

        for x in range(0, 4000, 30):  # El -1 es para evitar grietas
            # Dibujamos 3 filas para que la vereda tenga 60px de alto (20 * 3)
            self.fondo_completo.blit(img_pista1_h, (x, 3240))
            self.fondo_completo.blit(img_pista1_h, (x, 3260))
            self.fondo_completo.blit(img_pista1_h, (x, 3280))

        for x in range(0, 4000, 30):  # El -1 es para evitar grietas
            # Dibujamos 3 filas para que la vereda tenga 60px de alto (20 * 3)
            self.fondo_completo.blit(img_pista1_h, (x, 3300))
            self.fondo_completo.blit(img_pista1_h, (x, 3320))
            self.fondo_completo.blit(img_pista1_h, (x, 3340))

    def _crear_jugador(self):
        animaciones = []
        # Usamos tu escala original
        escala = 1.3
        direcciones = ["abajo", "arriba", "izquierda", "derecha"]

        for dir in direcciones:
            lista_temporal = []
            for i in range(1, 4):
                img = pygame.image.load(f"asets/imagenes/character/p1/{dir}_{i}.png")
                # Aplicamos la escala correctamente al ancho y alto original
                ancho = int(img.get_width() * escala)
                alto = int(img.get_height() * escala)
                img = pygame.transform.scale(img, (ancho, alto))
                lista_temporal.append(img)
            animaciones.append(lista_temporal)

        # Retornamos al jugador en su posición inicial (1000, 1200)
        return Personaje(634, 220, animaciones)


    def _cargar_objetos_estaticos(self):
        self.rect_puerta_tienda = pygame.Rect(3860, 3430, 60, 40)
        # Tu lista 'datos_mapa' gigante
        datos_mapa = [
            ("casa", 100, 3680, (95, 3830, 250, 80)),
            ("casa", 850, 3680, (795, 3830, 250, 80)),
            ("arbol1", 1200, 1200, (1230, 1350, 60, 50)),
            ("mesa", 1015, 1350, (1000, 1350, 120, 60)),
            ("silla1", 1000, 1300, (0, 0, 0, 0)),
            ("silla2", 1000, 1450, (0, 0, 0, 0)),

            ("mesa1", 1615, 1350, (1600, 1350, 120, 60)),
            ("silla3", 1600, 1300, (0, 0, 0, 0)),
            ("silla4", 1600, 1450, (0, 0, 0, 0)),

            ("mesa", 2815, 1350, (2800, 1350, 120, 60)),
            ("silla1", 2800, 1300, (0, 0, 0, 0)),
            ("silla2", 2800, 1450, (0, 0, 0, 0)),

            ("mesa", 3115, 1350, (3100, 1350, 120, 60)),
            ("silla1", 3100, 1300, (0, 0, 0, 0)),
            ("silla2", 3100, 1450, (0, 0, 0, 0)),

            ("mesa", 3115, 2150, (3100, 2150, 120, 60)),
            ("silla1", 3100, 2100, (0, 0, 0, 0)),
            ("silla2", 3100, 2250, (0, 0, 0, 0)),

            ("mesa", 2815, 2150, (2800, 2150, 120, 60)),
            ("silla1", 2800, 2100, (0, 0, 0, 0)),
            ("silla2", 2800, 2250, (0, 0, 0, 0)),



            ("arbol2", 1250, 1500, (1280, 1650, 60, 50)),
            ("arbol3", 1800, 1700, (1830, 1850, 60, 50)),
            ("arbol4", 2100, 1600, (2130, 1750, 60, 50)),
            ("arbol5", 2300, 1200, (2330, 1350, 60, 50)),
            ("arbol6", 2500, 1400, (2530, 1550, 60, 50)),
            ("arbol7", 2600, 2000, (2630, 2150, 60, 50)),
            ("arbol8", 2300, 2100, (2330, 2250, 60, 50)),
            ("arbol9", 2700, 2300, (2730, 2450, 60, 50)),
            ("arbol10", 2100, 2400, (2130, 2550, 60, 50)),
            ("arbol11", 1400, 2400, (1430, 2550, 60, 50)),
            ("arbol12", 1200, 2600, (1230, 2750, 60, 50)),
            ("arbol13", 1300, 2100, (1330, 2250, 60, 50)),
            ("arbol14", 1400, 1900, (1430, 2050, 60, 50)),
            ("arbol15", 1800, 1200, (1830, 1350, 60, 50)),
            ("arbol1", 3160, 1800, (3190, 1950, 60, 50)),
            ("arbol1", 3150, 1400, (3180, 1550, 60, 50)),
            ("arbol1", 3200, 2200, (3230, 2350, 60, 50)),
            ("arbol1", 3220, 2400, (3250, 2550, 60, 50)),
            ("arbol1", 3150, 2800, (3180, 2950, 60, 50)),
            ("arbol1", 2800, 3600, (2830, 3750, 60, 50)),
            ("arbol1", 2600, 3400, (2630, 3550, 60, 50)),
            ("arbol1", 2100, 3800, (2130, 3950, 60, 50)),

            ("pastoc2", 2500, 3400, (0, 0, 0, 0)),
            ("pastoc2", 2200, 3400, (120, 300, 190, 120)),
            ("pastoc2", 2300, 3400, (0, 0, 0, 0)),
            ("pastoc2", 2400, 3400, (0, 0, 0, 0)),
            ("pastoc3", 1600, 2000, (0, 0, 0, 0)),
            ("pastoc4", 2000, 2000, (0, 0, 0, 0)),

            ("pastoc1", 2300, 3880, (0, 0, 0, 0)),
            ("pastoc1", 2400, 3880, (0, 0, 0, 0)),
            ("pastoc1", 2500, 3880, (0, 0, 0, 0)),
            ("pastoc1", 2600, 3880, (0, 0, 0, 0)),

            ("pastoc1", 2900, 3880, (0, 0, 0, 0)),
            ("pastoc1", 3000, 3880, (0, 0, 0, 0)),

            ("pastoc1", 2200, 2100, (0, 0, 0, 0)),
            ("pastoc1", 2500, 2300, (0, 0, 0, 0)),
            ("pastoc1", 2500, 2400, (0, 0, 0, 0)),
            ("pastoc1", 2500, 2400, (0, 0, 0, 0)),
            ("pastoc1", 2500, 2500, (0, 0, 0, 0)),
            ("pastoc1", 2500, 2600, (0, 0, 0, 0)),
            ("pastoc1", 2500, 2700, (0, 0, 0, 0)),
            ("pastoc1", 2600, 2300, (0, 0, 0, 0)),
            ("pastoc1", 2600, 2400, (0, 0, 0, 0)),
            ("pastoc1", 2600, 2500, (0, 0, 0, 0)),
            ("pastoc1", 2600, 2600, (0, 0, 0, 0)),

            ("pastoc1", 1600, 2600, (0, 0, 0, 0)),
            ("pastoc1", 1600, 2700, (0, 0, 0, 0)),
            ("pastoc1", 1700, 2300, (0, 0, 0, 0)),
            ("pastoc1", 1700, 2400, (0, 0, 0, 0)),
            ("pastoc1", 1700, 2500, (0, 0, 0, 0)),
            ("pastoc1", 1700, 2600, (0, 0, 0, 0)),

            ("pastoc1", 1300, 3000, (200, 0, 740, 200)),
            ("pastoc1", 1400, 3000, (315, 160, 70, 100)),
            ("pastoc1", 1500, 3000, (530, 190, 60, 150)),
            ("pastoc1", 1600, 3000, (690, 190, 70, 150)),
            ("pastoc1", 1700, 3000, (890, 190, 70, 70)),
            ("pastoc1", 1800, 3000, (0, 0, 0, 0)),
            ("pastoc1", 1900, 3000, (0, 0, 0, 0)),
            ("pastoc1", 2000, 3000, (0, 0, 0, 0)),
            ("pastoc1", 2100, 3000, (0, 0, 0, 0)),
            ("pastoc1", 2200, 3000, (0, 0, 0, 0)),
            ("pastoc1", 2300, 3000, (0, 0, 0, 0)),
            ("pastoc1", 2400, 3000, (0, 0, 0, 0)),

            ("pastoc1", 2800, 3000, (0, 0, 0, 0)),

            ("pastoc1", 1700, 2200, (0, 0, 0, 0)),
            ("pastoc1", 1800, 2200, (0, 0, 0, 0)),
            ("pastoc1", 1900, 2300, (0, 0, 0, 0)),

            ("pastoc1", 2300, 1700, (1350, 900, 120, 230)),
            ("pastoc1", 2300, 1800, (1260, 920, 100, 40)),
            ("pastoc1", 2300, 1900, (1050, 920, 100, 40)),
            ("pastoc1", 2300, 2000, (1330, 200, 150, 120)),
            ("pastoc1", 2400, 2000, (0, 0, 0, 0)),
            ("pastoc1", 2500, 2000, (0, 0, 0, 0)),
            ("pastoc1", 2500, 1900, (0, 0, 0, 0)),
            ("pastoc1", 2500, 1800, (0, 0, 0, 0)),
            ("pastoc1", 2500, 1700, (0, 0, 0, 0)),

            ("pastoc1", 3800, 0, (0, 0, 0, 0)),
            ("pastoc1", 3800, 100, (0, 0, 0, 0)),
            ("pastoc1", 3800, 200, (0, 0, 0, 0)),
            ("pastoc1", 3800, 300, (0, 0, 0, 0)),
            ("pastoc1", 3800, 400, (0, 0, 0, 0)),

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

            ("carro1", 3500, 200, (3480, 200, 180, 340)),
            ("carro1", 3400, 2800, (3380, 2800, 180, 340)),

            ("aula1", 630, 1500, (630, 1500, 430, 390)),
            ("aula2", 0, 1300, (0, 1300, 430, 390)),
            ("aula3", 630, 2100, (630, 2100, 430, 390)),
            ("aula4", 0, 1900, (0, 1900, 430, 390)),
            ("aula5", 630, 2700, (630, 2700, 430, 390)),
            ("aula6", 0, 2500, (0, 2500, 430, 390)),

            ("L4", 2490, 10, (2490, 10, 850, 780)),
            ("letrero1", 3000, 1000, (3000, 1010, 100, 20)),
            ("L2", 1600, 750, (1600, 810, 330, 150)),
            ("CENTROAULA", 320, 20, (0, 0, 0, 0)),
            ("carro3", 915, 3300, (910, 3300, 270, 110)),

            ("carroblanco", 1250, 3150, (1250, 3190, 170, 30)),
            ("carroazul", 2200, 3250, (2200, 3290, 170, 30)),
            ("carroverde", 2800, 3150, (2800, 3190, 170, 30)),

            ("tractor", 50, 3170, (50, 3190, 155, 90)),
            ("edificio1", 5, 3300, (5, 3330, 880, 300)),
            ("edificio2", 1200, 3300, (1200, 3330, 880, 300)),
            ("edificiogrande", 3700, 1000, (3700, 1000, 200, 400)),
            ("edificiogrande", 3700, 1400, (3700, 1400, 200, 400)),
            ("edificiogrande", 3700, 1800, (3700, 1800, 200, 400)),
            ("edificiogrande", 3700, 2200, (3700, 2200, 200, 400)),
            ("edificiogrande2", 3700, 2600, (3690, 2830, 250, 270)),
            ("carro2", 550, 3600, (545, 3600, 270, 110)),
            ("escalera1", 440, 1440, (0, 0, 0, 0)),
            ("escalera1", 440, 2050, (0, 0, 0, 0)),
            ("escalera1", 440, 2650, (0, 0, 0, 0)),
            ("escalera2", 570, 2250, (0, 0, 0, 0)),
            ("escalera2", 570, 2800, (0, 0, 0, 0)),
            ("escalera2", 570, 1650, (0, 0, 0, 0)),
            ("camion", 3850, 3170, (3850, 3170, 180, 120)),
            ("leo", 3800, 3300, (3800, 3300, 200, 150)),
            ("estadio", 3500, 3500, (0, 0, 0, 0)),
            ("estadio", 3500, 3700, (0, 0, 0, 0)),
            ("estadio", 3500, 3900, (0, 0, 0, 0)),
            ("estadio", 3200, 3500, (0, 0, 0, 0)),
            ("estadio", 3200, 3700, (0, 0, 0, 0)),
            ("estadio", 3200, 3900, (0, 0, 0, 0)),

            ("faro1", 1600, 1050, (1610, 1150, 40, 5)),
            ("faro1", 580, 1200, (590, 1300, 40, 5)),
            ("faro1", 2200, 1250, (2210, 1350, 40, 5)),
            ("faro1", 1100, 3000, (1110, 3100, 40, 5)),
            ("faro1", 3700, 3050, (3710, 3150, 40, 5)),

            ("faro2", 3100, 3050, (3110, 3150, 40, 5)),
            ("faro2", 3250, 1050, (3260, 1150, 40, 5)),
            ("faro2", 2450, 1050, (2460, 1150, 40, 5)),
            ("decoracion2", 650, 2500, (630, 2500, 200, 50)),
            ("decoracion2", 2200, 1100, (2190, 1100, 200, 50)),
            ("decoracion2", 650, 1930, (630, 1930, 200, 50)),
            ("decoracion2", 650, 3100, (630, 3100, 200, 50)),

            ("decoracion3", 3200, 1650, (3190, 1650, 30, 65)),
            ("decoracion3", 3200, 2700, (3190, 2700, 30, 65)),
            ("decoracion3", 2900, 3000, (2890, 3000, 30, 65)),
            ("decoracion3", 2900, 2400, (2890, 2400, 30, 65)),

            ("decoracion4", 1200, 3680, (1190, 3680, 110, 80)),
            ("decoracion4", 1400, 3880, (1390, 3880, 110, 80)),
            ("decoracion4", 1600, 3680, (1590, 3680, 110, 80)),
            ("decoracion4", 1800, 3880, (1790, 3880, 110, 80)),
            ("decoracion4", 2000, 3680, (1990, 3680, 110, 80)),

            ("basura1", 2900, 2000, (2900, 2000, 40, 20)),
            ("basura2", 2900, 1910, (2900, 1910, 40, 20)),
            ("basura3", 700, 1250, (700, 1250, 40, 20)),
            ("basura1", 3750, 3350, (3750, 3350, 40, 20)),
            ("basura2", 2000, 3100, (2000, 3100, 40, 20)),
            ("basura3", 2100, 3100, (2100, 3100, 40, 20)),

            ("pastoalto2", 2100, 3400, (2100, 3400, 25, 50)),
            ("pastoalto2", 2100, 3450, (2100, 3450, 25, 50)),
            ("pastoalto2", 2100, 3500, (2100, 3500, 25, 50)),
            ("pastoalto2", 2100, 3550, (2100, 3550, 25, 50)),
            ("pastoalto2", 2100, 3600, (2100, 3600, 25, 50)),
            ("pastoalto2", 2100, 3650, (2100, 3650, 25, 50)),
            ("pastoalto2", 2100, 3700, (2100, 3700, 25, 50)),
            ("pastoalto2", 2100, 3750, (2100, 3750, 25, 50)),
            ("pastoalto2", 2100, 3800, (2100, 3800, 25, 50)),
            ("pastoalto2", 2100, 3850, (2100, 3850, 25, 30)),

            ("pastoalto2", 3100, 3400, (3090, 3400, 35, 50)),
            ("pastoalto2", 3100, 3450, (3090, 3450, 35, 50)),
            ("pastoalto2", 3100, 3500, (3090, 3500, 35, 50)),
            ("pastoalto2", 3100, 3550, (3090, 3550, 35, 50)),
            ("pastoalto2", 3100, 3600, (3090, 3600, 35, 50)),
            ("pastoalto2", 3100, 3650, (3090, 3650, 35, 50)),
            ("pastoalto2", 3100, 3700, (3090, 3700, 35, 50)),
            ("pastoalto2", 3100, 3750, (3090, 3750, 35, 50)),
            ("pastoalto2", 3100, 3800, (3090, 3800, 35, 50)),
            ("pastoalto2", 3100, 3850, (3090, 3850, 35, 50)),
            ("pastoalto2", 3100, 3900, (3090, 3900, 35, 50)),
            ("pastoalto2", 3100, 3950, (3090, 3950, 35, 50)),

            ("pastoalto1", 3050, 3990, (3050, 3990, 40, 20)),
            ("pastoalto1", 2980, 3990, (2980, 3990, 40, 20)),
            ("pastoalto1", 2910, 3990, (2910, 3990, 40, 20)),
            ("pastoalto1", 2840, 3990, (2840, 3990, 40, 20)),
            ("pastoalto1", 2750, 3990, (2750, 3990, 40, 20)),
            ("pastoalto1", 2680, 3990, (2680, 3990, 40, 20)),
            ("pastoalto1", 2610, 3990, (2610, 3990, 40, 20)),
            ("pastoalto1", 2540, 3990, (2540, 3990, 40, 20)),
            ("pastoalto1", 2450, 3990, (2450, 3990, 40, 20)),
            ("pastoalto1", 2380, 3990, (2380, 3990, 40, 20)),
            ("pastoalto1", 2310, 3990, (2310, 3990, 40, 20)),
            ("pastoalto1", 2240, 3990, (2240, 3990, 40, 20)),
            ("pastoalto1", 2170, 3990, (2170, 3990, 40, 20)),

            ("centropokemon", 3700, 600, (3700, 620, 230, 150)),
            ("edificiosinpuerta", 2040, 820, (2040, 850, 300, 220)),
            ("labo2", 1920, 470, (1930, 480, 250, 250)),

            ("estadistica2", 900, 550, (900, 550, 580, 390)),
            ("fiee", 950, -200, (950, 0, 540, 270)),
            ("fiee", -240, -100, (0, 0, 330, 350)),
            ("veredasuper", 600, 210, (0, 0, 0, 0)),
            ("veredasuper", 600, 300, (0, 0, 0, 0)),
            ("veredasuper", 600, 400, (0, 0, 0, 0)),
            ("veredasuper", 600, 500, (0, 0, 0, 0)),
            ("veredasuper", 600, 600, (0, 0, 0, 0)),
            ("veredasuper", 600, 700, (0, 0, 0, 0)),
            ("veredasuper", 600, 800, (0, 0, 0, 0)),
            ("veredasuper", 600, 900, (0, 0, 0, 0)),
            ("veredasuper", 600, 1000, (0, 0, 0, 0)),
            ("veredafinal", 600, 1090, (0, 0, 0, 0)),

            ("pastoverdeclaro", 180, 480, (0, 0, 0, 0)),
            ("pastoverdeclaro", 375, 480, (0, 0, 0, 0)),
            ("pastoverdeclaro", 180, 520, (0, 0, 0, 0)),
            ("pastoverdeclaro", 375, 520, (0, 0, 0, 0)),
            ("pastoverdeclaro", 180, 560, (0, 0, 0, 0)),
            ("pastoverdeclaro", 375, 560, (0, 0, 0, 0)),
            ("pastoverdeclaro", 180, 600, (0, 0, 0, 0)),
            ("pastoverdeclaro", 375, 600, (0, 0, 0, 0)),
            ("pastoverdeclaro", 180, 640, (0, 0, 0, 0)),
            ("pastoverdeclaro", 375, 640, (0, 0, 0, 0)),
            ("pastoverdeclaro", 180, 680, (0, 0, 0, 0)),
            ("pastoverdeclaro", 375, 680, (0, 0, 0, 0)),
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

            ("arbolgrande", 150, 500, (280, 850, 40, 40)),
            ("arbolgrande", 870, 50, (1000, 400, 40, 40)),
            ("arbolgrande", 2280, 3350, (2410, 3700, 40, 40)),

            ("pastoamarillo", 1100, 2100, (0, 0, 0, 0)),
            ("pastoamarillo", 1100, 2160, (0, 0, 0, 0)),
            ("pastoamarillo", 1100, 2220, (0, 0, 0, 0)),
            ("pastoamarillo", 1100, 2280, (0, 0, 0, 0)),
            ("pastoamarillo", 1100, 2340, (0, 0, 0, 0)),
            ("pastoamarillo", 1100, 2400, (0, 0, 0, 0)),
            ("pastoamarillo", 1100, 2460, (0, 0, 0, 0)),

            ("pastoamarillo", 1070, 1500, (0, 0, 0, 0)),
            ("pastoamarillo", 1070, 1560, (0, 0, 0, 0)),
            ("pastoamarillo", 1070, 1620, (0, 0, 0, 0)),
            ("pastoamarillo", 1070, 1680, (0, 0, 0, 0)),
            ("pastoamarillo", 1070, 1740, (0, 0, 0, 0)),

            ("pastoamarillo", 900, 3150, (0, 0, 0, 0)),
            ("pastoamarillo", 1100, 2880, (0, 0, 0, 0)),
            ("pastoamarillo", 1100, 2940, (0, 0, 0, 0)),

            ("pastoamarillo", 500, 3780, (0, 0, 0, 0)),
            ("pastoamarillo", 500, 3880, (0, 0, 0, 0)),
            ("pastoamarillo", 500, 3940, (0, 0, 0, 0)),

            ("floresrosadas", 2900, 3370, (0, 0, 0, 0)),
            ("floresazules", 460, 1170, (0, 0, 0, 0)),
            ("floresazules", 690, 1170, (0, 0, 0, 0)),
            ("floresamarillas", 2530, 1170, (0, 0, 0, 0)),
            ("floresamarillas", 3130, 1170, (0, 0, 0, 0)),
            ("estatua", 540, 300, (0, 0, 0, 0)),
            ("estatua", 710, 300, (0, 0, 0, 0)),
            ("pastosalto", 3800, 3600, (3830, 3650, 0, 0)),
            ("pastosalto", 3800, 3670, (3830, 3720, 0, 0)),
            ("pastosalto", 3800, 3740, (3830, 3790, 0, 0)),
            ("pastosalto", 3890, 3600, (3910, 3650, 0, 0)),
            ("pastosalto", 3890, 3670, (3910, 3720, 0, 0)),
            ("pastosalto", 3890, 3740, (3910, 3790, 0, 0)),

            ("barro", 3850, 3900, (0, 0, 0, 0)),
            ("kakuna", 1350, 1550, (1300, 1800, 0, 0)),
            ("kakuna", 1250, 1300, (1300, 1800, 0, 0)),
            ("kakuna", 1900, 1850, (1300, 1800, 0, 0)),
            ("kakuna", 2180, 1650, (1300, 1800, 0, 0)),



        ]

        palabras_pasto = ["pastosalto", "pastoamarillo", "pastoverdeclaro", "pastoc1", "pastoc2", "pastoc3"]
        objetos_finales = []

        for tipo, x, y, offset in datos_mapa:
            # IMPORTANTE: Añadimos 'tipo' al final de los argumentos
            nuevo_obj = ObjetoEstatico(x, y, self.assets[tipo], offset, tipo)

            # Verificamos si es zona de combate
            if any(pasto in tipo.lower() for pasto in palabras_pasto):
                nuevo_obj.es_zona_combate = True
            else:
                nuevo_obj.es_zona_combate = False

            objetos_finales.append(nuevo_obj)

        return objetos_finales










    def _cargar_animaciones_pokemon(self, carpeta):
        """Carga las 12 imágenes de un Pokémon (3x4)"""
        animaciones = []
        direcciones = ["abajo", "arriba", "izquierda", "derecha"]
        escala = 1.5  # Para que tengan el mismo tamaño que tu personaje

        for dir in direcciones:
            lista_temporal = []
            for i in range(1, 4):
                # Asume que tus archivos se llaman 'abajo_1.png', 'abajo_2.png', etc.
                ruta = f"asets/imagenes/pokemon/{carpeta}/{dir}_{i}.png"
                img = pygame.image.load(ruta).convert_alpha()
                ancho = int(img.get_width() * escala)
                alto = int(img.get_height() * escala)
                img = pygame.transform.scale(img, (ancho, alto))
                lista_temporal.append(img)
            animaciones.append(lista_temporal)
        return animaciones

    def manejar_eventos(self):
        eventos = pygame.event.get()
        if self.mostrando_tarjeta_pokemon:
            for event in eventos:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.opcion_starter_seleccionada = 0
                        print("👉 Opción: SÍ")
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.opcion_starter_seleccionada = 1
                        print("👉 Opción: NO")
                    elif event.key == pygame.K_e:
                        if self.opcion_starter_seleccionada == 0:
                            self._elegir_starter(self.pokemon_en_tarjeta)
                            self.mostrando_tarjeta_pokemon = False
                        else:
                            self.mostrando_tarjeta_pokemon = False
                            print("❌ Elección cancelada")
            return  # ⚠️ IMPORTANTE: Salir para no procesar otros eventos

        for event in eventos:
            if event.type == pygame.QUIT:
                self.game_over = True
                return

            if event.type == pygame.KEYDOWN:
                # 🆕 En video final, ESPACIO salta al menú
                if self.estado_juego == "VIDEO_FINAL" and event.key == pygame.K_SPACE:
                    if hasattr(self, 'cap_final') and self.cap_final:
                        self.cap_final.release()
                    self.estado_juego = "CREDITOS"
                    self.tiempo_creditos = pygame.time.get_ticks()
                    continue

                # 🆕 En créditos, ESPACIO va al menú
                if self.estado_juego == "CREDITOS" and event.key == pygame.K_SPACE:
                    self.estado_juego = "MENU_INICIO"
                    continue



            if self.estado_juego == "INTRO":
                if event.type == pygame.KEYDOWN:
                    pygame.mixer.stop()
                    self.cap.release()
                    self.estado_juego = "MENU_INICIO"
                continue

            if event.type == pygame.KEYDOWN:
                if self.estado_juego == "MENU_INICIO":
                    if event.key == pygame.K_w:
                        self.opcion_inicio_seleccionada = (self.opcion_inicio_seleccionada - 1) % len(
                            self.opciones_inicio)
                    elif event.key == pygame.K_s:
                        self.opcion_inicio_seleccionada = (self.opcion_inicio_seleccionada + 1) % len(
                            self.opciones_inicio)
                    elif event.key == pygame.K_e:
                        eleccion = self.opciones_inicio[self.opcion_inicio_seleccionada]
                        if eleccion == "Nueva Partida":
                            # Cuando el jugador selecciona "Iniciar Partida" en el menú:
                            self.oak_dialogos = [
                                "¡Hola! ¡Perdona por la espera!",
                                "¡Bienvenido al mundo de UNIMON!",
                                "Soy el Rector,me llamo Arturo Talledo",
                                "¿Estás listo para comenzar?"
                            ]
                            self.oak_indice = 0
                            self.estado_juego = "INTRO_OAK"
                            pygame.mixer.music.stop()


                        elif eleccion == "Continuar":
                            if self._cargar_partida():
                                self.estado_juego = "EXPLORACION"
                                self.camara.seguir(self.jugador)  # Centrar cámara al cargar
                            else:
                                print("No hay partida guardada.")
                    continue  # Importante para no procesar otros menús a la ve

                if self.estado_juego == "INTRO_OAK":
                    if event.key == pygame.K_e or event.key == pygame.K_SPACE:
                        if self.oak_indice == 2:  # Cuando dice "Me llamo OAK..."
                            if self.sonido_pokebola:
                                self.sonido_pokebola.play()
                                # Micro pausa de 50ms (imperceptible para el oído pero separa los sonidos)
                            pygame.time.wait(50)
                            if self.sonido_pokemon:
                                self.sonido_pokemon.play()


                        self.oak_indice += 1
                        if self.oak_indice >= len(self.oak_dialogos):
                            # ACTIVAR MENSAJE DE MISIÓN (ANTES de cambiar el estado)
                            self.activar_mensaje_mision(
                                "MISIÓN 1: ELECCIÓN DEL STARTER",
                                "Ve hacia el edificio de Estadística y habla con el Profesor Oak para elegir tu primer Pokémon."
                            )

                            # Cambiar al estado de exploración
                            self.estado_juego = "EXPLORACION"
                            self.mapa_actual = "EXTERIOR"

                            # Iniciar música
                            try:
                                pygame.mixer.music.load("asets/music/A1.mp3")
                                pygame.mixer.music.play(-1)
                            except:
                                pass

                            print("🎮 ¡A explorar! Misión 1 activada")

                        continue  # <-- Este continue es importante






                # --- CONTROL DE PAUSA (ESCAPE) ---
                if event.key == pygame.K_ESCAPE:
                    if self.estado_juego == "EXPLORACION":
                        self.estado_juego = "MENU_PAUSA"
                        self.opcion_menu_seleccionada = 0
                        # Detenemos al personaje para que no siga caminando solo
                        self.mover_izquierda = self.mover_derecha = self.mover_arriba = self.mover_abajo = False
                    elif self.estado_juego == "MENU_PAUSA":
                        self.estado_juego = "EXPLORACION"
                    continue



                # --- LÓGICA MENÚ DE PAUSA ---
                if self.estado_juego == "MENU_PAUSA":
                    opciones = ["Pokemon", "Bolsa", "Carnet", "Guardar", "Salir"]
                    if event.key == pygame.K_w:
                        self.opcion_menu_seleccionada = (self.opcion_menu_seleccionada - 1) % len(opciones)
                    elif event.key == pygame.K_s:
                        self.opcion_menu_seleccionada = (self.opcion_menu_seleccionada + 1) % len(opciones)
                    elif event.key == pygame.K_e:
                        eleccion = opciones[self.opcion_menu_seleccionada]
                        if eleccion == "Salir":
                            self.estado_juego = "EXPLORACION"
                        elif eleccion == "Guardar":
                            self._guardar_partida()
                        # Aquí puedes añadir: elif eleccion == "Pokemon": (mostrar stats)
                    continue

                # --- LÓGICA MENÚ TIENDA (Solo si está abierto) ---
                if getattr(self, 'menu_tienda_abierto', False):
                    # Definimos las opciones basadas en la fase actual
                    if self.fase_tienda == "PRINCIPAL":
                        opciones_tienda = self.opciones_principal  # ["Comprar", "Vender", "Salir"]
                    else:
                        # Usamos los nombres de tu lista de objetos real
                        opciones_tienda = [item["nombre"] for item in self.items_tienda]

                    if event.key == pygame.K_w:
                        self.tienda_seleccionada = (self.tienda_seleccionada - 1) % len(opciones_tienda)
                    elif event.key == pygame.K_s:
                        self.tienda_seleccionada = (self.tienda_seleccionada + 1) % len(opciones_tienda)
                    elif event.key == pygame.K_e:
                        eleccion = opciones_tienda[self.tienda_seleccionada]

                        if self.fase_tienda == "PRINCIPAL":
                            if eleccion == "Comprar":
                                self.fase_tienda = "COMPRAR"
                                self.tienda_seleccionada = 0
                            elif eleccion == "Salir":
                                self.menu_tienda_abierto = False
                                self.vendedor_indice_dialogo = -1
                                self.fase_tienda = "PRINCIPAL"
                                self.mover_izquierda = self.mover_derecha = self.mover_arriba = self.mover_abajo = False

                        elif self.fase_tienda == "COMPRAR":
                            if eleccion == "Salir":  # El último item de tu lista es "Salir"
                                self.fase_tienda = "PRINCIPAL"
                                self.tienda_seleccionada = 0
                            else:
                                # BUSCAMOS EL OBJETO COMPLETO (con precio) en tu lista original
                                item_completo = self.items_tienda[self.tienda_seleccionada]
                                self._comprar_objeto(item_completo)
                    continue

                # --- LÓGICA EXPLORACIÓN ---
                if self.estado_juego == "EXPLORACION":
                    if event.key == pygame.K_e:
                        interactuo_con_npc = False

                        for npc in self.lista_npcs:
                            # 🟢 Calcular distancia AQUÍ
                            distancia = math.hypot(
                                self.jugador.forma.centerx - npc.forma.centerx,
                                self.jugador.forma.centery - npc.forma.centery
                            )

                            if distancia < 50 and hasattr(npc, 'es_rival') and npc.es_rival:
                                npc.actualizar_direccion(self.jugador.forma)

                                # Verificar si tiene Pokémon
                                if not self.tiene_pokemon:
                                    print("❌ No tienes Pokémon, no puedes combatir")
                                    self.activar_mensaje_mision(
                                        "¡NO TIENES POKÉMON!",
                                        "Ve al edificio de Estadística a elegir tu primer Pokémon."
                                    )
                                    interactuo_con_npc = True
                                    break

                                # 🟢 VERIFICAR ESTADOS DEL ENTRENADOR
                                if npc.derrotado:
                                    # El jugador ya le ganó antes
                                    if not npc.hablando:
                                        npc.dialogo = ["¡Ya me ganaste!", "Eres muy fuerte...", "¡Sigue así!"]
                                        npc.iniciar_dialogo()
                                    else:
                                        # Si ya está hablando, avanzar al siguiente diálogo
                                        npc.iniciar_dialogo()

                                    interactuo_con_npc = True
                                    break

                                elif npc.le_gano_al_jugador:
                                    # El entrenador le ganó al jugador antes (puede revancha)
                                    if not npc.hablando:
                                        npc.dialogo = ["¿Quieres la revancha?", "¡Esta vez te ganaré de nuevo!",
                                                       "¡Prepárate!"]
                                        npc.iniciar_dialogo()
                                    else:
                                        npc.iniciar_dialogo()
                                        if not npc.hablando:
                                            # Quiere revancha
                                            npc.le_gano_al_jugador = False  # Reset para la nueva batalla
                                            self.iniciar_batalla_entrenador(npc)
                                    interactuo_con_npc = True
                                    break

                                else:
                                    # Primera vez que lo enfrenta
                                    if not npc.hablando:
                                        npc.iniciar_dialogo()
                                        print(f"🗣️ {npc.nombre_entrenador}: {npc.dialogo_actual}")
                                    else:
                                        npc.iniciar_dialogo()
                                        if not npc.hablando:
                                            print(f"⚔️ Iniciando batalla contra {npc.nombre_entrenador}")
                                            self.iniciar_batalla_entrenador(npc)
                                    interactuo_con_npc = True
                                    break

                        if self.mapa_actual == "INTERIOR_ESTADISTICA":
                            for npc in self.lista_npcs:
                                distancia = math.hypot(
                                    self.jugador.forma.centerx - npc.forma.centerx,
                                    self.jugador.forma.centery - npc.forma.centery
                                )
                                # En la sección donde detectas la pokebola:
                                if distancia < 50 and hasattr(npc, 'tipo_pokemon') and npc.tipo_pokemon:

                                    # 🆕 Si ya eligió starter, mostrar mensaje diferente
                                    if self.starter_ya_elegido:
                                        print("ℹ️ Ya elegiste starter, no puedes cambiar")
                                        # Opcional: Mostrar un mensaje rápido

                                    else:
                                        # Mostrar tarjeta normalmente
                                        self.mostrando_tarjeta_pokemon = True
                                        self.pokemon_en_tarjeta = npc.tipo_pokemon
                                        self.opcion_starter_seleccionada = 0
                                        print(f"📋 Mostrando tarjeta de {self.pokemon_en_tarjeta}")

                                    interactuo_con_npc = True
                                    break

                        if not interactuo_con_npc:
                            for npc in self.lista_npcs:
                                # 🟢 Excluir pokebolas
                                if hasattr(npc, 'tipo_pokemon') and npc.tipo_pokemon:
                                    continue

                                # 🟢 EXCLUIR ENTRENADORES
                                if hasattr(npc, 'es_rival') and npc.es_rival:
                                    continue

                                distancia = math.hypot(
                                    self.jugador.forma.centerx - npc.forma.centerx,
                                    self.jugador.forma.centery - npc.forma.centery
                                )

                                if distancia < 80:
                                    npc.actualizar_direccion(self.jugador.forma)
                                    npc.iniciar_dialogo()
                                    print(f"🗣️ Hablando con NPC normal")
                                    interactuo_con_npc = True
                                    break

                        pos_previa = self.jugador.forma.copy()
                        # 1. INTERACCIÓN CON ENFERMERA JOY
                        if self.mapa_actual == "CENTRO_POKEMON":
                            if hasattr(self, 'mostrador_rect') and self.jugador.forma.colliderect(self.mostrador_rect):

                                # Avanzar diálogo
                                self.joy_indice_dialogo += 1

                                # Si llegamos al final del diálogo (después de "......")
                                if self.joy_indice_dialogo >= len(self.joy_dialogo):
                                    self.joy_indice_dialogo = -1  # Terminar diálogo

                                    # 🟢 CURAR TODOS LOS POKÉMON
                                    self._curar_todos_pokemon()

                                # Si estamos en el diálogo de curación (índice 3 = "......")
                                elif self.joy_indice_dialogo == 3:
                                    # Aquí podrías reproducir un sonido de curación
                                    if hasattr(self, 'sonido_curacion'):
                                        self.sonido_curacion.play()
                                    print("💚 Curando Pokémon...")

                                interactuo_con_npc = True

                        # 2. INTERACCIÓN CON VENDEDOR
                        if self.mapa_actual == "TIENDA":
                            if hasattr(self, 'mostrador_rect') and self.jugador.forma.colliderect(self.mostrador_rect):

                                # Si la tienda está abierta pero hay un mensaje (como el de "¡Gracias!"),
                                # lo avanzamos para que se limpie, pero dejamos la tienda abierta.
                                if self.menu_tienda_abierto:
                                    if self.vendedor_indice_dialogo != -1:
                                        self.vendedor_indice_dialogo += 1
                                        if self.vendedor_indice_dialogo >= len(self.vendedor_dialogo):
                                            self.vendedor_indice_dialogo = 0  # Mantiene el último mensaje o reinicia
                                    continue

                                    # Si la tienda está cerrada, hacemos el saludo inicial
                                else:
                                    self.vendedor_indice_dialogo += 1
                                    if self.vendedor_indice_dialogo == 1:
                                        self.menu_tienda_abierto = True
                                        self.fase_tienda = "PRINCIPAL"
                                        self.tienda_seleccionada = 0

                    # Control de movimiento
                    if event.key == pygame.K_a: self.mover_izquierda = True
                    if event.key == pygame.K_d: self.mover_derecha = True
                    if event.key == pygame.K_s: self.mover_abajo = True
                    if event.key == pygame.K_w: self.mover_arriba = True

            # Detectar cuando se dejan de pulsar las teclas
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a: self.mover_izquierda = False
                if event.key == pygame.K_d: self.mover_derecha = False
                if event.key == pygame.K_s: self.mover_abajo = False
                if event.key == pygame.K_w: self.mover_arriba = False

            # --- LÓGICA DE BATALLA ---


        if self.estado_juego == "BATALLA" and self.instancia_batalla:
            self.instancia_batalla.manejar_input(eventos)

    def _curar_todos_pokemon(self):
        """Cura a todos los Pokémon del equipo del jugador"""

        print("\n🩺 CENTRO POKÉMON - Iniciando curación...")

        # Verificar si el jugador tiene equipo
        if not hasattr(self.jugador, 'equipo') or len(self.jugador.equipo) == 0:
            print("⚠️ El jugador no tiene Pokémon en su equipo")
            return

        # Curar cada Pokémon en el equipo
        for i, pokemon in enumerate(self.jugador.equipo):
            vida_anterior = pokemon.hp_actual
            pokemon.hp_actual = pokemon.hp_max
            print(
                f"   ✅ {i + 1}. {pokemon.nombre}: {vida_anterior}/{pokemon.hp_max} → {pokemon.hp_actual}/{pokemon.hp_max}")

        # 🟢 IMPORTANTE: Actualizar también el Pokémon activo (el jugador)
        if hasattr(self.jugador, 'pokemon_activo') and len(self.jugador.equipo) > 0:
            pokemon_activo = self.jugador.equipo[self.jugador.pokemon_activo]
            self.jugador.hp_actual = pokemon_activo.hp_actual
            self.jugador.hp_max = pokemon_activo.hp_max
            print(
                f"   🔴 Pokémon activo ({self.jugador.nombre}) actualizado a {self.jugador.hp_actual}/{self.jugador.hp_max}")

        # Mostrar mensaje de confirmación
        total_pokemon = len(self.jugador.equipo)
        print(f"✨ ¡{total_pokemon} Pokémon han sido curados completamente!")

        # Opcional: Activar un mensaje visual
        self.activar_mensaje_mision(
            "¡POKÉMON CURADOS!",
            f"Tus {total_pokemon} Pokémon están en plena forma."
        )



    def actualizar(self):
        # ==========================================
        # --- ESTADO 0: INTRODUCCIÓN (VIDEO) ---
        # ==========================================
        if self.estado_juego == "INTRO":
            ret, frame = self.cap.read()
            if ret:
                # Procesar el frame de OpenCV para Pygame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.transpose(frame)
                self.surface_video = pygame.surfarray.make_surface(frame)
                self.surface_video = pygame.transform.scale(self.surface_video, (self.ancho, self.alto))

                # Control de Audio de la Intro
                if not self.audio_intro_reproducido and self.sonido_intro:
                    self.sonido_intro.play()
                    self.audio_intro_reproducido = True
            else:
                # El video terminó solo
                self.cap.release()
                self.estado_juego = "MENU_INICIO"
                self.titulo_x = 1200  # Asegurar posición inicial para la animación
            return  # Bloquea el resto de la actualización

        # ==========================================
        # --- ESTADO 1: MENÚ DE INICIO ---
        # ==========================================
        if self.estado_juego == "MENU_INICIO":
            # --- LÓGICA DEL TÍTULO (Derecha a Centro) ---
            if self.titulo_x > self.destino_x:
                self.titulo_x -= 15  # Un poco más rápido para que no sea eterno
                if self.titulo_x < self.destino_x:
                    self.titulo_x = self.destino_x

            # Respiración del título
            self.angulo_respiracion += 0.05
            self.escala_titulo = 1.0 + math.sin(self.angulo_respiracion) * 0.05

            # --- NUEVA LÓGICA: OPCIONES (Izquierda a Centro) ---
            # Solo se mueven si self.opciones_x aún no llega a 400
            if hasattr(self, 'opciones_x'):  # Seguridad por si no la definiste en el init
                if self.opciones_x < 400:
                    self.opciones_x += 25  # Velocidad de entrada
                    if self.opciones_x > 400:
                        self.opciones_x = 400

            return

        if self.mapa_actual == "EXTERIOR":
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_p]:  # Presiona P para ver coordenadas
                print(f"Jugador en: ({self.jugador.forma.x}, {self.jugador.forma.y})")
                print(f"Rect jugador: {self.jugador.forma}")
        # ==========================================
        # --- ESTADO: PAUSA ---
        # ==========================================
        if self.estado_juego == "MENU_PAUSA":
            return  # Congela el mundo

        if self.estado_juego == "VIDEO_FINAL":
            self._actualizar_video_final()
            return

        if self.estado_juego == "CREDITOS":
            # No necesita actualización, solo dibujo
            return

        # ==========================================
        # --- ESTADO: EXPLORACIÓN (MUNDO) ---
        # ==========================================
        dx, dy = 0, 0
        velocidad = 5
        if self.mover_arriba:
            dy = -velocidad
        elif self.mover_abajo:
            dy = velocidad
        elif self.mover_izquierda:
            dx = -velocidad
        elif self.mover_derecha:
            dx = velocidad

        for npc in self.lista_npcs:
            npc.actualizar_direccion(self.jugador.forma)

        # Después del último bucle de NPCs, agrega:
        if self.mapa_actual == "INTERIOR_ESTADISTICA":
            # Verificar si algún NPC está hablando
            algun_npc_hablando = False
            for npc in self.lista_npcs:
                if npc.hablando:
                    algun_npc_hablando = True
                    break

            if not algun_npc_hablando:
                self.mostrar_imagen_pokemon = False
                self.pokemon_mostrado = None

            # Si ningún NPC está hablando, ocultar todas las imágenes


        if self.mapa_actual == "CENTRO_POKEMON":
            # 1. Verificamos si el rectángulo del jugador toca la alfombra de salida
            if self.jugador.forma.colliderect(self.rect_salida_cp):
                print("Saliendo del Centro Pokemon...")
                # 2. Llamamos a cambiar_mapa para volver al exterior
                # Ajusta spawn_x y spawn_y a la posición de la puerta en el mundo exterior
                self.cambiar_mapa("exterior", spawn_x=3790, spawn_y=820)



        # Salida de la Tienda
        if self.mapa_actual == "TIENDA":
            if hasattr(self, 'rect_salida_tienda') and self.jugador.forma.colliderect(self.rect_salida_tienda):
                self.cambiar_mapa("exterior", 3850, 3500)
                return

        elif self.mapa_actual == "INTERIOR_ESTADISTICA":
            # Detectar salida
            if hasattr(self, 'rect_salida_estadistica') and self.jugador.forma.colliderect(
                    self.rect_salida_estadistica):
                print("🚪 Saliendo del edificio de Estadística...")
                self.cambiar_mapa("exterior", 1188, 995)  # Aparece frente a la puerta
                self.activar_mensaje_mision(
                    "MISION 2:",
                    "Ve al edificio de Ciberseguridad  hay problemas ahi."
                )
                return

        # Filtrado de Colisiones
        if self.mapa_actual == "EXTERIOR":
            obstaculos_fisicos = [obj for obj in self.lista_entorno if getattr(obj, 'solido', True)]
            obstaculos_que_bloquean = obstaculos_fisicos + self.lista_npcs + self.lista_pokemon
            self.camara.seguir(self.jugador)
        else:
            obstaculos_que_bloquean = self.muros_interiores + self.lista_npcs
            self.camara.offset = pygame.Vector2(0, 0)

        # Ejecución de Movimiento
        self.jugador.movimiento(dx, dy, obstaculos_que_bloquean)

        # Animación y Encuentros Aleatorios
        if dx != 0 or dy != 0:
            self.jugador.update_animacion()

            if self.mapa_actual == "EXTERIOR" and self.tiene_pokemon:
                if getattr(self, 'transicion_batalla', False):
                    return

                for obj in self.lista_entorno:
                    if getattr(obj, 'es_zona_combate', False) and self.jugador.forma.colliderect(obj.forma):
                        if (dx != 0 or dy != 0) and random.randint(1, 1000) < 4:

                            pool = self._definir_pool_salvajes()
                            datos = random.choice(pool)
                            nombre_pkmn = datos["nombre"].lower().strip()

                            # 🟢 FORZAR LA CREACIÓN DE UN POKÉMON NUEVO
                            print(f"\n🔴 Creando NUEVO Pokémon salvaje: {nombre_pkmn}")

                            # Asegurar que no hay referencias anteriores
                            if hasattr(self, 'pokemon_pendiente'):
                                self.pokemon_pendiente = None

                            enemigo_batalla = self._preparar_pokemon_pool(nombre_pkmn, datos["nivel"])

                            if enemigo_batalla:
                                # Verificar que es un objeto nuevo
                                print(f"   ✅ ID del objeto: {id(enemigo_batalla)}")
                                print(f"   ✅ Nombre: {enemigo_batalla.nombre}")
                                print(f"   ✅ HP: {enemigo_batalla.hp_actual}/{enemigo_batalla.hp_max}")

                                self.pokemon_pendiente = enemigo_batalla
                                self.transicion_batalla = True
                                print(f"🎮 ¡Batalla salvaje contra {nombre_pkmn}!")
                                return

        # Detección de Puertas
        if self.mapa_actual == "EXTERIOR":
            if self.jugador.forma.colliderect(self.rect_puerta_cp):
                self.cambiar_mapa("centro_pokemon", 400, 500)
                return

                # Puerta de la Tienda (ya existente)
            if hasattr(self, 'rect_puerta_tienda') and self.jugador.forma.colliderect(self.rect_puerta_tienda):
                self.cambiar_mapa("tienda", 3999, 3999)
                return

                # 🆕 NUEVA: Puerta del Edificio de Estadística
            if hasattr(self, 'rect_puerta_estadistica') and self.jugador.forma.colliderect(
                    self.rect_puerta_estadistica):
                print("🚪 Entrando al edificio de Estadística...")
                self._cargar_interior_estadistica()
                return

        # Actualizar IA de Pokemon y NPCs
        if self.mapa_actual == "EXTERIOR":
            obstaculos_ia = [obj for obj in self.lista_entorno if getattr(obj, 'solido', True)]
            for pkmn in list(self.lista_pokemon):
                pkmn.actualizar_ia(obstaculos_ia + [self.jugador] + self.lista_npcs)

            # Cartel de Zona
            zona_detectada = ""
            for zona in self.zonas:
                if zona["rect"].colliderect(self.jugador.forma):
                    zona_detectada = zona["nombre"]
                    break

            if zona_detectada != "" and zona_detectada != self.zona_actual:
                self.zona_actual = zona_detectada
                self.timer_cartel = pygame.time.get_ticks()
                self.alpha_cartel = 255

        if self.alpha_cartel > 0: self.alpha_cartel -= 2
        for npc in self.lista_npcs:
            npc.actualizar_direccion(self.jugador.forma)

    def _cargar_objetos_centro_pkmn(self):
        self.mapa_actual = "CENTRO_POKEMON"  # Marcamos que estamos dentro
        self.camara.offset = pygame.Vector2(0, 0)  # Cámara fija
        self.lista_entorno.clear()

        # Creamos rectángulos invisibles para las colisiones del interior
        # Estos valores son EJEMPLOS, debes ajustarlos a tu imagen de 800x600
        self.muros_interiores = [
            pygame.Rect(0, 0, 800, 150),  # Pared superior / Mostrador
            pygame.Rect(0, 0, 50, 600),  # Pared izquierda
            pygame.Rect(750, 0, 50, 600),  # Pared derecha
            pygame.Rect(0, 580, 350, 20),  # Pared inferior izq
            pygame.Rect(450, 580, 350, 20),  # Pared inferior der
        ]
        # Dibujamos cada muro en color rojo (semi-transparente o borde)
        for muro in self.muros_interiores:
            pygame.draw.rect(self.ventana, (255, 0, 0), muro, 2)  # El '2' es el grosor del borde

        # El rectángulo de salida (la alfombra)
        self.rect_salida_cp = pygame.Rect(380, 580, 40, 20)
        if hasattr(self, 'rect_salida_cp'):
            pygame.draw.rect(self.ventana, (0, 255, 0), self.rect_salida_cp, 2)

    def _dibujar_menu_tienda(self):
        rect_menu = pygame.Rect(50, 50, 350, 250)
        pygame.draw.rect(self.ventana, (50, 50, 150), rect_menu)
        pygame.draw.rect(self.ventana, (255, 255, 255), rect_menu, 4)

        # ESTO ES LO QUE ARREGLA TU PROBLEMA:
        if self.fase_tienda == "PRINCIPAL":
            opciones = self.opciones_principal  # ["Comprar", "Vender", "Salir"]
        else:
            # Mostramos los objetos de la lista items_tienda
            opciones = [
                f"{item['nombre']} - ${item['precio']}" if item['precio'] > 0 else f"{item['nombre']}"
                for item in self.items_tienda
            ]

        for i, texto in enumerate(opciones):
            color = (255, 255, 255)
            if i == self.tienda_seleccionada:
                # Dibujar flechita
                pygame.draw.polygon(self.ventana, (255, 255, 0),
                                    [(60, 75 + i * 40), (60, 95 + i * 40), (75, 85 + i * 40)])

            img = self.fuente.render(texto, True, color)
            self.ventana.blit(img, (85, 70 + i * 40))

    def _comprar_objeto(self, item):
        """Compra un objeto de la tienda"""

        # Asegurar que el jugador tiene inventario
        if not hasattr(self.jugador, 'inventario'):
            self.jugador.inventario = {
                "pokebola": 0,
                "pocion": 0,
                "antidoto": 0,
                "superpocion": 0
            }

        # Asegurar que el jugador tiene dinero
        if not hasattr(self.jugador, 'dinero'):
            self.jugador.dinero = 3000

        nombre_item = item["nombre"].lower()
        precio = item["precio"]

        print(f"\n🛒 COMPRANDO: {item['nombre']} - ${precio}")
        print(f"💰 Dinero actual: ${self.jugador.dinero}")

        if self.jugador.dinero >= precio:
            # Restar dinero
            self.jugador.dinero -= precio

            # Añadir al inventario
            if nombre_item in self.jugador.inventario:
                self.jugador.inventario[nombre_item] += 1
            else:
                self.jugador.inventario[nombre_item] = 1

            print(f"✅ Comprado! {nombre_item} ahora: {self.jugador.inventario[nombre_item]}")
            print(f"💰 Dinero restante: ${self.jugador.dinero}")

            # Mensaje de éxito
            self.vendedor_dialogo = [f"¡Aquí tienes tu {item['nombre']}!", f"Te quedan ${self.jugador.dinero}"]
            self.vendedor_indice_dialogo = 0

        else:
            print(f"❌ Dinero insuficiente. Necesitas ${precio - self.jugador.dinero} más")
            self.vendedor_dialogo = ["No tienes suficiente dinero...", "Vuelve cuando tengas más"]
            self.vendedor_indice_dialogo = 0

        # Volver al menú principal
        self.fase_tienda = "PRINCIPAL"
        self.tienda_seleccionada = 0
        self.menu_tienda_abierto = True

    def ejecutar_transicion(self, ventana):
        if not self.transicion_batalla:
            return

        superficie_negra = pygame.Surface((800, 600))
        superficie_negra.set_alpha(self.alpha_transicion)
        superficie_negra.fill((0, 0, 0))
        ventana.blit(superficie_negra, (0, 0))

        self.alpha_transicion += 5

        if self.alpha_transicion >= 255:
            # --- SEGURIDAD: Verificar si hay un Pokémon ---
            if self.pokemon_pendiente is None:
                print("¡Error evitado! Se intentó iniciar batalla con None.")
                self.transicion_batalla = False
                self.alpha_transicion = 0
                # Volvemos a poner la música normal por si acaso
                pygame.mixer.music.load(self.musica_ambiente)
                pygame.mixer.music.play(-1)
                return  # Salimos de la función para que no crashee abajo

            # --- NUEVA LÓGICA DE AUDIO ---
            es_entrenador = hasattr(self, 'entrenador_rival') and self.entrenador_rival is not None
            nombre_entrenador = self.entrenador_rival.nombre_entrenador if es_entrenador else "Rival"

            if es_entrenador:
                print(f"🎵 Reproduciendo música de ENTRENADOR para {nombre_entrenador}")
                try:
                    pygame.mixer.music.load(self.musica_batalla_entrenador)
                except:
                    print("⚠️ No se encontró música de entrenador, usando música de batalla normal")
                    pygame.mixer.music.load(self.musica_batalla_salvaje)
            else:
                print("🎵 Reproduciendo música de BATALLA SALVAJE")
                pygame.mixer.music.load(self.musica_batalla_salvaje)

            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.2)

            # --- INICIAR BATALLA ---
            # Ahora estamos seguros de que pokemon_pendiente NO es None
            # 🆕 Verificar si es batalla de entrenador
            # Verificar si es batalla de entrenador
            es_entrenador = hasattr(self, 'entrenador_rival') and self.entrenador_rival is not None
            nombre_entrenador = self.entrenador_rival.nombre_entrenador if es_entrenador else "Rival"

            self.instancia_batalla = SistemaBatalla(
                self.jugador,
                self.pokemon_pendiente,
                self.fuente,
                es_entrenador=es_entrenador,
                entrenador_nombre=nombre_entrenador,
                equipo_entrenador = self.equipo_entrenador if es_entrenador else None
            )
            self.estado_juego = "BATALLA"
            self.pokemon_pendiente.gritar()

            # 🟢 IMPORTANTE: NO LIMPIAR AQUÍ
            # La batalla ya tiene el nombre del entrenador, podemos limpiar después
            # Pero mejor limpiar cuando la batalla termine

            self.transicion_batalla = False
            self.alpha_transicion = 0
    def dibujar(self):
        # 1. LIMPIEZA INICIAL: Fondo negro para evitar rastros de frames anteriores
        self.ventana.fill((0, 0, 0))
        #self._dibujar_colisiones_interiores()
        if self.mapa_actual in ["CENTRO_POKEMON", "TIENDA"]:
            if hasattr(self, 'muros_interiores'):
                for muro in self.muros_interiores:
                    # Color rojo, grosor 3 para que se note mucho
                    pygame.draw.rect(self.ventana, (255, 0, 0), muro, 3)

            # Dibujar la salida en verde
            if self.mapa_actual == "CENTRO_POKEMON" and hasattr(self, 'rect_salida_cp'):
                pygame.draw.rect(self.ventana, (0, 255, 0), self.rect_salida_cp, 3)
            elif self.mapa_actual == "TIENDA" and hasattr(self, 'rect_salida_tienda'):
                pygame.draw.rect(self.ventana, (0, 255, 0), self.rect_salida_tienda, 3)


        # ==========================================
        # --- ESTADO 0: INTRODUCCIÓN (VIDEO) ---
        # ==========================================
        if self.estado_juego == "INTRO":
            # Nota: reproducir_video() ya se encarga del dibujo en el loop ejecutar
            pass

        if self.estado_juego == "VIDEO_FINAL":
            self._dibujar_video_final()
            pygame.display.update()
            return

        if self.estado_juego == "CREDITOS":
            self._dibujar_creditos()
            pygame.display.update()
            return


        elif self.estado_juego == "MENU_INICIO":
            # 1. Fondo
            if self.imagen_fondo_titulo:
                self.ventana.blit(self.imagen_fondo_titulo, (0, 0))
            else:
                self.ventana.fill((30, 30, 50))

            # 2. DIBUJAR TÍTULO CON ANIMACIÓN (La clave está aquí)
            print(f"DEBUG Animación -> X: {self.titulo_x} | Escala: {self.escala_titulo}")
            if self.imagen_titulo_juego:
                # IMPORTANTE: Usamos la escala que cambia en actualizar()
                ancho_animado = int(self.base_width * self.escala_titulo)
                alto_animado = int(self.base_height * self.escala_titulo)

                # Creamos la superficie escalada para ESTE frame específico
                img_animada = pygame.transform.smoothscale(self.imagen_titulo_juego, (ancho_animado, alto_animado))

                # Usamos titulo_x y titulo_y (que también cambian en actualizar)
                rect_tit = img_animada.get_rect(center=(int(self.titulo_x), int(self.titulo_y)))

                self.ventana.blit(img_animada, rect_tit)

            for i, opt in enumerate(self.opciones_inicio):
                color = (255, 255, 0) if i == self.opcion_inicio_seleccionada else (255, 255, 255)

                # Efecto de escala pequeña si está seleccionada (Opcional pero recomendado)
                tamanio = 40 if i == self.opcion_inicio_seleccionada else 35
                fuente_temp = pygame.font.Font(None, tamanio)  # O tu fuente personalizada

                texto_surf = fuente_temp.render(opt, True, color)

                # Usamos self.opciones_x para la entrada animada
                # i * 20 añade un pequeño retraso visual entre botones para que no entren pegados
                rect_opt = texto_surf.get_rect(center=(int(self.opciones_x), 380 + i * 60))

                self.ventana.blit(texto_surf, rect_opt)

        elif self.estado_juego == "INTRO_OAK":
            self._dibujar_intro_oak()





        # ==========================================
        # --- ESTADO 2: BATALLA ---
        # ==========================================





        # ==========================================
        # --- ESTADO 3: EXPLORACIÓN (MUNDO) ---
        # ==========================================
        elif self.estado_juego in ["EXPLORACION", "MENU_PAUSA"]:


            # A. DIBUJO DEL MUNDO SEGÚN MAPA
            if self.mapa_actual == "EXTERIOR":
                self.ventana.blit(self.fondo_completo, (0 - self.camara.offset.x, 0 - self.camara.offset.y))
                offset_dibujo = self.camara.offset

                # Separar suelo de objetos sólidos para efecto de profundidad (Y-sorting)
                suelo = [obj for obj in self.lista_entorno if not getattr(obj, 'solido', True)]
                objetos_con_altura = [obj for obj in self.lista_entorno if getattr(obj, 'solido', True)]

                for pasto in suelo:
                    pasto.dibujar(self.ventana, offset_dibujo)

                # Ordenar elementos por su base (bottom) para que el jugador pase "detrás" de árboles
                elementos_depth = objetos_con_altura + self.lista_npcs + [self.jugador] + self.lista_pokemon
                elementos_depth.sort(key=lambda obj: obj.forma.bottom)

                for el in elementos_depth:
                    el.dibujar(self.ventana, offset_dibujo)

            else:
                # DIBUJO DE INTERIORES
                self.ventana.blit(self.fondo_completo, (self.offset_interior.x, self.offset_interior.y))
                offset_dibujo = pygame.Vector2(0, 0)

                if self.mapa_actual == "CENTRO_POKEMON":
                    if hasattr(self, 'joy_sprite') and self.joy_sprite:
                        self.ventana.blit(self.joy_sprite, self.joy_pos)
                elif self.mapa_actual == "TIENDA":
                    if hasattr(self, 'vendedor_sprite') and self.vendedor_sprite:
                        self.ventana.blit(self.vendedor_sprite, self.vendedor_pos)

                elif self.mapa_actual == "INTERIOR_ESTADISTICA":
                    # 1. Fondo REAL
                    if hasattr(self, 'fondo_completo') and self.fondo_completo:
                        self.ventana.blit(self.fondo_completo, (0, 0))
                    else:
                        self.ventana.fill((0, 0, 255))

                    # 2. Dibujar NPCs (incluyendo las pokebolas)
                    for npc in self.lista_npcs:
                        npc.dibujar(self.ventana, pygame.Vector2(0, 0))

                    # 3. MOSTRAR SOLO EL POKÉMON SELECCIONADO (NO todos)
                    if hasattr(self, 'pokemon_mostrado') and self.pokemon_mostrado:
                        # Buscar la pokebola correspondiente
                        for npc in self.lista_npcs:
                            if hasattr(npc, 'tipo_pokemon') and npc.tipo_pokemon == self.pokemon_mostrado:
                                x = npc.forma.x - 20
                                y = npc.forma.y - 60

                                if self.pokemon_mostrado == "charmander" and self.img_charmander:
                                    self.ventana.blit(self.img_charmander, (x, y))
                                    print(f"🔥 Charmander en ({x}, {y})")
                                elif self.pokemon_mostrado == "squirtle" and self.img_squirtle:
                                    self.ventana.blit(self.img_squirtle, (x, y))
                                    print(f"💧 Squirtle en ({x}, {y})")
                                elif self.pokemon_mostrado == "bulbasaur" and self.img_bulbasaur:
                                    self.ventana.blit(self.img_bulbasaur, (x, y))
                                    print(f"🌱 Bulbasaur en ({x}, {y})")
                                break





                    # 6. Diálogos
                    for npc in self.lista_npcs:
                        if npc.hablando:
                            self._dibujar_cuadro_dialogo(npc.dialogo_actual)
                            break


                # 5. Jugador
                self.jugador.dibujar(self.ventana, pygame.Vector2(0, 0))



            for npc in self.lista_npcs:
                if npc.hablando:
                    self._dibujar_cuadro_dialogo(npc.dialogo_actual)
                    break
            # B. MENÚ DE PAUSA (Se dibuja ENCIMA del mundo)
            if self.estado_juego == "MENU_PAUSA":
                overlay = pygame.Surface((self.ventana.get_width(), self.ventana.get_height()), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.ventana.blit(overlay, (0, 0))

                ancho_p, alto_p = 280, 400
                rect_p = pygame.Rect(self.ventana.get_width() - ancho_p - 30, 30, ancho_p, alto_p)
                pygame.draw.rect(self.ventana, (255, 255, 255), rect_p)
                pygame.draw.rect(self.ventana, (50, 100, 200), rect_p, 6)

                for i, opt in enumerate(self.opciones_menu):
                    pos_y = rect_p.y + 30 + (i * 70)
                    if i == self.opcion_menu_seleccionada:
                        pygame.draw.rect(self.ventana, (230, 230, 230), (rect_p.x + 10, pos_y - 5, ancho_p - 20, 60))
                        flecha = self.fuente.render(">", True, (200, 0, 0))
                        self.ventana.blit(flecha, (rect_p.x + 15, pos_y))
                        color_t = (200, 0, 0)
                    else:
                        color_t = (0, 0, 0)
                    self.ventana.blit(self.fuente.render(opt, True, color_t), (rect_p.x + 55, pos_y))

            if self.estado_juego == "EXPLORACION":
                self._dibujar_cartel_mision()

                # C. INTERFACES DE DIÁLOGO Y TIENDA
            if self.mapa_actual == "CENTRO_POKEMON" and getattr(self, 'joy_indice_dialogo', -1) != -1:
                self._dibujar_cuadro_dialogo(self.joy_dialogo[self.joy_indice_dialogo])
            elif self.mapa_actual == "TIENDA" and getattr(self, 'vendedor_indice_dialogo', -1) != -1:
                if self.vendedor_indice_dialogo >= 0 and self.vendedor_indice_dialogo < len(self.vendedor_dialogo):
                    self._dibujar_cuadro_dialogo(self.vendedor_dialogo[self.vendedor_indice_dialogo])

                    # Si además el menú de la tienda debe estar abierto, lo dibujamos encima
                    if getattr(self, 'menu_tienda_abierto', False):
                        self._dibujar_menu_tienda()

            # Cartel de Zona con imagen (Desvanecimiento)
            if getattr(self, 'alpha_cartel', 0) > 0:
                if self.imagen_cartel_zona:
                    # Usar imagen como fondo
                    imagen_copia = self.imagen_cartel_zona.copy()
                    imagen_copia.set_alpha(self.alpha_cartel)
                    self.ventana.blit(imagen_copia, (20, 20))

                    # Dibujar texto sobre la imagen
                    texto_surface = self.fuente.render(self.zona_actual, True, (255, 255, 255))
                    texto_surface.set_alpha(self.alpha_cartel)

                    # Centrar texto en la imagen (ajusta según el diseño de tu imagen)
                    x_texto = 20 + (self.imagen_cartel_zona.get_width() - texto_surface.get_width()) // 2
                    y_texto = 20 + (self.imagen_cartel_zona.get_height() - texto_surface.get_height()) // 2

                    self.ventana.blit(texto_surface, (x_texto, y_texto))
                else:
                    # Fallback: fondo negro si no hay imagen
                    texto_surface = self.fuente.render(self.zona_actual, True, (255, 255, 255))
                    texto_surface.set_alpha(self.alpha_cartel)
                    s = pygame.Surface((texto_surface.get_width() + 20, 40))
                    s.set_alpha(min(self.alpha_cartel, 180))
                    s.fill((0, 0, 0))
                    self.ventana.blit(s, (20, 20))
                    self.ventana.blit(texto_surface, (30, 25))

                self.alpha_cartel -= 0.4


        if self.mostrando_tarjeta_pokemon and self.pokemon_en_tarjeta:
            self._dibujar_tarjeta_pokemon(self.pokemon_en_tarjeta)
            print("✅ TARJETA DIBUJADA")



        # ==========================================
        # --- CAPA FINAL: TRANSICIONES ---
        # ==========================================
        if getattr(self, 'transicion_batalla', False):
            self.ejecutar_transicion(self.ventana)




        # REFRESCO ÚNICO DE PANTALLA: Mantiene los 60 FPS estables y evita el parpadeo
        pygame.display.update()

    def _dibujar_cuadro_dialogo(self, texto):
        # Si la imagen del cuadro existe, la usamos
        if hasattr(self, 'imagen_cuadro_dialogo') and self.imagen_cuadro_dialogo:
            # Posición del cuadro
            x_cuadro = 100
            y_cuadro = 490

            # 1. PRIMERO: Dibujar la imagen del cuadro
            self.ventana.blit(self.imagen_cuadro_dialogo, (x_cuadro, y_cuadro))

            # 2. DIBUJAR TEXTO DE PRUEBA con color muy brillante
            texto_prueba = self.fuente.render(texto, True, (0, 0, 0))

            # Probar diferentes posiciones
            x_texto = x_cuadro + 50
            y_texto = y_cuadro + 35

            self.ventana.blit(texto_prueba, (x_texto, y_texto))



        else:
            # Fallback...
            pygame.draw.rect(self.ventana, (0, 0, 0), (50, 450, 700, 100))
            pygame.draw.rect(self.ventana, (255, 255, 255), (50, 450, 700, 100), 3)
            img_texto = self.fuente.render(texto, True, (255, 255, 255))
            self.ventana.blit(img_texto, (70, 470))
    def cambiar_mapa(self, nombre_mapa, spawn_x, spawn_y):

        print(f"🗺️ Cambiando a mapa: {nombre_mapa} con spawn ({spawn_x}, {spawn_y})")

        # Detener movimiento
        self.mover_arriba = self.mover_abajo = self.mover_izquierda = self.mover_derecha = False

        # --- MAPA EXTERIOR ---
        if nombre_mapa == "exterior":
            self.mapa_actual = "EXTERIOR"

            # 🟢 IMPORTANTE: Usar la lista de NPCs que ya tenemos guardada
            self.lista_npcs = self.npcs_exterior  # No recrear, solo asignar

            # Reconstruir el entorno (esto es necesario porque los objetos estáticos se modifican)
            self.lista_entorno = self._cargar_objetos_estaticos()
            self.lista_pokemon = self._crear_pokemons_salvajes()

            # Restaurar música
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(self.musica_ambiente)
                pygame.mixer.music.play(-1)
            except:
                pass

            # Posicionar jugador
            self.jugador.forma.x = spawn_x
            self.jugador.forma.y = spawn_y

            # Activar cámara móvil
            self.camara.seguir(self.jugador)

            print(f"✅ Exterior cargado - NPCs: {len(self.lista_npcs)}")
            print(f"   Jugador en ({spawn_x}, {spawn_y})")

        # --- LÓGICA PARA EL CENTRO POKÉMON ---
        if nombre_mapa == "centro_pokemon":
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load("asets/music/centro_pokemon.mp3")
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
            except:
                pass

            self.mapa_actual = "CENTRO_POKEMON"
            self.lista_entorno.clear()
            self.lista_pokemon.clear()

            # Cargar y escalar fondo
            img_original = pygame.image.load("asets/imagenes/CENTROPOKEMON/cp.png").convert()
            ancho_escalado = int(224 * 3.8)
            alto_escalado = int(143 * 3.8)
            self.fondo_completo = pygame.transform.scale(img_original, (ancho_escalado, alto_escalado))

            off_x = (820 - ancho_escalado) // 2
            off_y = 570 - alto_escalado
            self.offset_interior = pygame.Vector2(off_x, off_y)

            # Configurar Enfermera Joy
            self.joy_pos = (self.offset_interior.x + (112 * 3.8), self.offset_interior.y + (26 * 3.8))
            if hasattr(self, 'joy_sprite') and self.joy_sprite:
                self.joy_rect = self.joy_sprite.get_rect(topleft=self.joy_pos)

            self.mostrador_rect = pygame.Rect(self.joy_pos[0] - 20, self.joy_pos[1] + 60, 150, 60)

            # Colisiones del CP
            muros_base = [
                pygame.Rect(off_x, off_y, ancho_escalado, 115),  # Norte
                pygame.Rect(off_x, off_y, 35, alto_escalado),  # Izquierda
                pygame.Rect(off_x + ancho_escalado - 40, off_y, 40, alto_escalado),  # Derecha
                pygame.Rect(off_x, off_y + alto_escalado - 20, 350, 5),  # Inferior izq
                pygame.Rect(off_x + ancho_escalado - 280, off_y + alto_escalado - 20, 350, 5)  # Inferior der
            ]
            self.muros_interiores = muros_base
            self.rect_salida_cp = pygame.Rect(off_x + 300, off_y + alto_escalado - 10, 184, 30)

            # --- POSICIÓN DE ENTRADA AL CENTRO POKEMON ---
            self.jugador.forma.centerx = 400
            self.jugador.forma.bottom = off_y + alto_escalado - 40  # Aparece justo en la alfombra


        # --- LÓGICA PARA LA TIENDA ---
        elif nombre_mapa == "tienda":
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load("asets/music/centro_pokemon.mp3")
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
            except:
                pass




            self.mapa_actual = "TIENDA"
            self.lista_entorno.clear()
            self.lista_pokemon.clear()

            # Cargar fondo Tienda
            img_original = pygame.image.load("asets/imagenes/TIENDA/tienda_leo.png").convert()
            ancho_escalado = int(img_original.get_width() * 4.4)
            alto_escalado = int(img_original.get_height() * 4.4)
            self.fondo_completo = pygame.transform.scale(img_original, (ancho_escalado, alto_escalado))

            off_x = (800 - ancho_escalado) // 2
            off_y = 600 - alto_escalado - 40
            self.offset_interior = pygame.Vector2(off_x, off_y)

            # Vendedor
            img_vendedor_temp = pygame.image.load("asets/imagenes/TIENDA/vendedor.png").convert_alpha()
            escala_vendedor = 3.8
            ancho_v = int(img_vendedor_temp.get_width() * escala_vendedor)
            alto_v = int(img_vendedor_temp.get_height() * escala_vendedor)
            self.vendedor_sprite = pygame.transform.scale(img_vendedor_temp, (ancho_v, alto_v))

            self.vendedor_pos = (off_x + (23 * 3.8), off_y + (52 * 3.8))

            self.vendedor_dialogo = [
                "¡Bienvenido a la Tienda Pokemon!",
                "¿En que puedo ayudarte hoy?",
                "¡Ten un buen dia!"
            ]
            self.vendedor_indice_dialogo = -1

            # Mostrador y colisiones
            mostrador_x = off_x + (0 * 3.8)
            mostrador_y = off_y + (70 * 3.8)
            mostrador_ancho = 55 * 3.8
            mostrador_alto = 10 * 3.8

            self.muros_interiores = [
                pygame.Rect(off_x, off_y, ancho_escalado, 110),
                pygame.Rect(off_x, off_y, 30, alto_escalado),
                pygame.Rect(off_x + ancho_escalado - 30, off_y, 30, alto_escalado),
                pygame.Rect(mostrador_x, mostrador_y, mostrador_ancho, mostrador_alto),
                # Pared inferior con hueco para la puerta
                pygame.Rect(off_x - 90, off_y + alto_escalado - 10, 300, 10),
                pygame.Rect(off_x + 350, off_y + alto_escalado - 10, 400, 10)
            ]

            self.mostrador_rect = pygame.Rect(mostrador_x, mostrador_y + 5, mostrador_ancho, mostrador_alto + 25)

            # Rectángulo de salida
            self.rect_salida_tienda = pygame.Rect(off_x + (ancho_escalado // 2) - 150, off_y + alto_escalado - 15, 100,
                                                  40)

            # --- CORRECCIÓN: POSICIÓN DE ENTRADA A LA TIENDA ---
            self.jugador.forma.centerx = 300
            self.jugador.forma.bottom = off_y + alto_escalado - 20  # Aparece cerca de la puerta

        # --- LÓGICA PARA REGRESAR AL EXTERIOR ---
        elif nombre_mapa == "exterior":

            self.lista_npcs = self.npcs_exterior
            self.mapa_actual = "EXTERIOR"

            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(self.musica_ambiente)
                pygame.mixer.music.play(-1)
            except:
                pass

            # Re-inicializar mundo exterior
            self.fondo_completo = self._crear_mapa_base()
            self._dibujar_veredas_y_pistas()
            self.lista_entorno = self._cargar_objetos_estaticos()
            self.lista_npcs = self.npcs_exterior
            self.lista_pokemon = self._crear_pokemons_salvajes()

            # --- CORRECCIÓN: TELETRANSPORTE PRECISO ---
            self.jugador.forma.x = spawn_x
            self.jugador.forma.y = spawn_y

            # IMPORTANTE: Forzamos a la cámara a centrarse inmediatamente
            self.camara.offset.x = self.jugador.forma.centerx - (self.ventana.get_width() // 2)
            self.camara.offset.y = self.jugador.forma.centery - (self.ventana.get_height() // 2)
            self.camara.seguir(self.jugador)

    def _dibujar_colisiones_interiores(self):
        # Solo dibujamos si estamos en un interior y la lista de muros existe
        if self.mapa_actual in ["CENTRO_POKEMON", "TIENDA"] and hasattr(self, 'muros_interiores'):

            # Dibujamos cada muro de color ROJO
            for muro in self.muros_interiores:
                # pygame.draw.rect(superficie, color, rectangulo, grosor_borde)
                pygame.draw.rect(self.ventana, (255, 0, 0), muro, 2)

            # Dibujamos el rectángulo de SALIDA de color VERDE
            #if hasattr(self, 'rect_salida_cp'):
                #pygame.draw.rect(self.ventana, (0, 255, 0), self.rect_salida_cp, 2)

            # Dibujamos el MOSTRADOR de color AZUL
            #if hasattr(self, 'mostrador_rect'):
                #pygame.draw.rect(self.ventana, (0, 0, 255), self.mostrador_rect, 2)

    def inicializar_escena_centro(self):
        """Carga todas las variables necesarias y CAMBIA EL FONDO al del Centro Pokémon."""
        self.mapa_actual = "CENTRO_POKEMON"

        # --- 1. CAMBIO DE FONDO (Esto es lo que te faltaba) ---
        # Asegúrate de que esta ruta sea la correcta para tu imagen del interior
        try:
            self.fondo_completo = pygame.image.load("asets/imagenes/CENTROPOKEMON/cp.png").convert()
            # Si tu mapa es más pequeño que la pantalla, puedes escalarlo:
            # self.fondo_completo = pygame.transform.scale(self.fondo_completo, (800, 600))
        except Exception as e:
            print(f"Error cargando el fondo del centro: {e}")

        # --- 2. Cámara y Offsets ---
        if not hasattr(self, 'offset_interior'):
            self.offset_interior = pygame.Vector2(0, 0)
        else:
            self.offset_interior.x = 0
            self.offset_interior.y = 0

        # --- 3. Configuración de la Enfermera Joy ---
        self.joy_pos = (370, 160)
        if not hasattr(self, 'joy_sprite'):
            self.joy_sprite = pygame.image.load("asets/imagenes/NPCS/joy.png").convert_alpha()

        # --- 4. Colisión del mostrador ---
        # Importante: el mostrador debe estar en la misma posición relativa que el dibujo de Joy
        self.mostrador_rect = pygame.Rect(350, 200, 100, 50)

        # --- 5. Diálogos ---
        self.joy_dialogo = [
            "¡Hola! Bienvenido al Centro Pokemon.",
            "Tus Pokemon parecen cansados...",
            "Me encargare de curarlos, un segundo.",
            "......",
            "¡Listo! Tus Pokemon estan como nuevos.",
            "¡Vuelve cuando quieras!"
        ]
        self.joy_indice_dialogo = -1

    def dibujar_opciones_menu(self):
        # Definimos las opciones si no existen
        opciones = ["Nueva Partida", "Continuar", "Salir"]

        for i, texto_opcion in enumerate(opciones):
            # Color: Amarillo si está seleccionado, Blanco si no
            color = (255, 255, 0) if i == getattr(self, 'opcion_inicio_seleccionada', 0) else (255, 255, 255)

            # Renderizar el texto
            # Nota: Asegúrate de tener 'self.fuente' definida en tu __init__
            try:
                superficie_texto = self.fuente.render(texto_opcion, True, color)
                # Centramos el texto horizontalmente
                rect_texto = superficie_texto.get_rect(center=(self.ventana.get_width() // 2, 350 + i * 60))
                self.ventana.blit(superficie_texto, rect_texto)
            except AttributeError:
                print("Error: No se encontró 'self.fuente' en el __init__")
                break

    def activar_mensaje_mision(self, titulo, descripcion):
        """Activa el mensaje de misión que se mostrará en exploración"""
        self.mostrar_mensaje_mision = True
        self.titulo_mision = titulo
        self.descripcion_mision = descripcion
        self.tiempo_inicio_mensaje = pygame.time.get_ticks()
        print(f"📋 Misión mostrada: {titulo}")

    def _dibujar_cartel_mision(self):
        """Dibuja un cartel de misión en el centro de la pantalla (solo en exploración)"""
        if not self.mostrando_mensaje_mision:
            return

        # Verificar si ya pasó el tiempo
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.tiempo_inicio_mensaje > self.duracion_mensaje:
            self.mostrar_mensaje_mision = False
            return

        # Crear un fondo semitransparente (más grande y vistoso)
        ancho_cartel = 650
        alto_cartel = 220

        # Fondo negro semitransparente
        fondo = pygame.Surface((ancho_cartel, alto_cartel))
        fondo.set_alpha(220)
        fondo.fill((0, 0, 0))

        # Posición centrada
        x = (self.ancho - ancho_cartel) // 2
        y = (self.alto - alto_cartel) // 2

        # Dibujar fondo
        self.ventana.blit(fondo, (x, y))

        # Borde dorado más grueso
        pygame.draw.rect(self.ventana, (255, 215, 0), (x, y, ancho_cartel, alto_cartel), 5)

        # Título (amarillo brillante)
        try:
            fuente_titulo = pygame.font.Font("asets/FuenteDeTexto/pokemon.otf", 45)
        except:
            fuente_titulo = pygame.font.Font(None, 45)

        titulo_surf = fuente_titulo.render(self.titulo_mision, True, (255, 255, 0))
        titulo_rect = titulo_surf.get_rect(center=(self.ancho // 2, y + 50))
        self.ventana.blit(titulo_surf, titulo_rect)

        # Descripción (blanco)
        try:
            fuente_desc = pygame.font.Font("asets/FuenteDeTexto/pokemon.otf", 25)
        except:
            fuente_desc = pygame.font.Font(None, 25)

        # Dividir descripción en líneas si es muy larga
        palabras = self.descripcion_mision.split(' ')
        lineas = []
        linea_actual = ""

        for palabra in palabras:
            prueba = linea_actual + " " + palabra if linea_actual else palabra
            if fuente_desc.size(prueba)[0] < 600:
                linea_actual = prueba
            else:
                lineas.append(linea_actual)
                linea_actual = palabra

        if linea_actual:
            lineas.append(linea_actual)

        # Dibujar líneas
        y_offset = y + 100
        for linea in lineas:
            linea_surf = fuente_desc.render(linea, True, (255, 255, 255))
            linea_rect = linea_surf.get_rect(center=(self.ancho // 2, y_offset))
            self.ventana.blit(linea_surf, linea_rect)
            y_offset += 35

        # Pequeño icono o decoración (opcional)
        pygame.draw.circle(self.ventana, (255, 215, 0), (x + 30, y + 30), 10)
        pygame.draw.circle(self.ventana, (255, 215, 0), (x + ancho_cartel - 30, y + alto_cartel - 30), 10)

    def _guardar_partida(self):
        """Guarda el estado completo del juego"""
        print("\n💾 GUARDANDO PARTIDA...")

        # 1. Guardar información básica del jugador
        datos = {
            "mapa": self.mapa_actual,
            "posicion": {
                "x": self.jugador.forma.x,
                "y": self.jugador.forma.y
            },
            "dinero": getattr(self.jugador, 'dinero', 3000),
            "inventario": getattr(self.jugador, 'inventario', {
                "pokebola": 0,
                "pocion": 0,
                "antidoto": 0,
                "superpocion": 0
            }),
            "pokemon_activo": getattr(self.jugador, 'pokemon_activo', 0),
            "equipo": [],  # Aquí guardaremos los Pokémon
            "entrenadores_derrotados": []  # Estado de los entrenadores rivales
        }

        # 2. Guardar el equipo de Pokémon
        if hasattr(self.jugador, 'equipo') and self.jugador.equipo:
            for i, pokemon in enumerate(self.jugador.equipo):
                pokemon_data = {
                    "nombre": pokemon.nombre,
                    "nivel": pokemon.nivel,
                    "hp_actual": pokemon.hp_actual,
                    "hp_max": pokemon.hp_max,
                    "ataque": pokemon.ataque,
                    "defensa": pokemon.defensa,
                    "ataque_especial": pokemon.ataque_especial,
                    "defensa_especial": pokemon.defensa_especial,
                    "velocidad": pokemon.velocidad,
                    "tipo": pokemon.tipo,
                    "tipo2": pokemon.tipo2,
                    "ataques": pokemon.ataques.copy() if pokemon.ataques else [],
                    "exp_actual": getattr(pokemon, 'exp_actual', 0),
                    "exp_siguiente_nivel": getattr(pokemon, 'exp_siguiente_nivel', 100)
                }
                datos["equipo"].append(pokemon_data)
                print(
                    f"   ✅ Pokémon {i + 1}: {pokemon.nombre} (Nv.{pokemon.nivel}) - HP: {pokemon.hp_actual}/{pokemon.hp_max}")

        # 3. Guardar estado de entrenadores derrotados
        if hasattr(self, 'npcs_exterior'):
            for npc in self.npcs_exterior:
                if hasattr(npc, 'es_rival') and npc.es_rival and hasattr(npc, 'derrotado') and npc.derrotado:
                    entrenador_data = {
                        "nombre": getattr(npc, 'nombre_entrenador', "Desconocido"),
                        "x": npc.forma.x,
                        "y": npc.forma.y
                    }
                    datos["entrenadores_derrotados"].append(entrenador_data)
                    print(f"   ✅ Entrenador derrotado: {entrenador_data['nombre']}")

        # 4. Guardar a archivo
        try:
            with open("partida_guardada.json", "w", encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            print(f"✅ Partida guardada exitosamente en 'partida_guardada.json'")
            print(f"   📍 Posición: ({datos['posicion']['x']}, {datos['posicion']['y']})")
            print(f"   💰 Dinero: ${datos['dinero']}")
            print(f"   🎒 Inventario: {datos['inventario']}")
            print(f"   🔴 Pokémon en equipo: {len(datos['equipo'])}")

            # Mostrar mensaje en pantalla
            self.activar_mensaje_mision(
                "¡PARTIDA GUARDADA!",
                f"Posición guardada. {len(datos['equipo'])} Pokémon en equipo."
            )

        except Exception as e:
            print(f"❌ Error al guardar partida: {e}")

    def _cargar_partida(self):
        """Carga el estado completo del juego"""
        import os

        print("\n📂 CARGANDO PARTIDA...")

        if not os.path.exists("partida_guardada.json"):
            print("❌ No hay partida guardada")
            return False

        try:
            with open("partida_guardada.json", "r", encoding='utf-8') as f:
                datos = json.load(f)

            print(f"✅ Archivo cargado correctamente")

            # 1. Restaurar dinero e inventario
            self.jugador.dinero = datos.get("dinero", 3000)
            self.jugador.inventario = datos.get("inventario", {
                "pokebola": 0,
                "pocion": 0,
                "antidoto": 0
            })

            print(f"   💰 Dinero: ${self.jugador.dinero}")
            print(f"   🎒 Inventario: {self.jugador.inventario}")

            # 2. Restaurar el equipo de Pokémon
            if "equipo" in datos and datos["equipo"]:
                self.jugador.equipo = []

                for pokemon_data in datos["equipo"]:
                    # Crear el Pokémon con sus stats guardados
                    pokemon = self._reconstruir_pokemon(pokemon_data)
                    if pokemon:
                        self.jugador.equipo.append(pokemon)
                        print(
                            f"   ✅ Pokémon cargado: {pokemon.nombre} (Nv.{pokemon.nivel}) - HP: {pokemon.hp_actual}/{pokemon.hp_max}")

                # Restaurar el índice del Pokémon activo
                self.jugador.pokemon_activo = datos.get("pokemon_activo", 0)

                # Sincronizar el jugador con el Pokémon activo
                if len(self.jugador.equipo) > self.jugador.pokemon_activo:
                    activo = self.jugador.equipo[self.jugador.pokemon_activo]
                    self.jugador.nombre = activo.nombre
                    self.jugador.hp_max = activo.hp_max
                    self.jugador.hp_actual = activo.hp_actual
                    self.jugador.nivel = activo.nivel
                    self.jugador.ataques = activo.ataques.copy()
                    self.jugador.tipo = activo.tipo
                    self.jugador.tipo2 = activo.tipo2
                    print(f"   🔴 Pokémon activo: {activo.nombre}")

            # 3. Restaurar estado de entrenadores derrotados
            if "entrenadores_derrotados" in datos:
                for npc in self.npcs_exterior:
                    if hasattr(npc, 'es_rival') and npc.es_rival:
                        for derrotado in datos["entrenadores_derrotados"]:
                            # Comparar por posición (margen de error de 10 píxeles)
                            if (abs(npc.forma.x - derrotado["x"]) < 10 and
                                    abs(npc.forma.y - derrotado["y"]) < 10):
                                npc.derrotado = True
                                print(
                                    f"   ✅ Entrenador marcado como derrotado: {getattr(npc, 'nombre_entrenador', 'Desconocido')}")

            # 4. Cambiar al mapa guardado
            mapa = datos.get("mapa", "EXTERIOR")
            pos_x = datos["posicion"]["x"]
            pos_y = datos["posicion"]["y"]

            print(f"   📍 Cargando mapa: {mapa} en ({pos_x}, {pos_y})")

            # Cambiar al mapa correspondiente
            if mapa == "EXTERIOR":
                self.cambiar_mapa("exterior", pos_x, pos_y)
            elif mapa == "CENTRO_POKEMON":
                self.cambiar_mapa("centro_pokemon", pos_x, pos_y)
            elif mapa == "TIENDA":
                self.cambiar_mapa("tienda", pos_x, pos_y)
            elif mapa == "INTERIOR_ESTADISTICA":
                self._cargar_interior_estadistica()
                self.jugador.forma.x = pos_x
                self.jugador.forma.y = pos_y

            print("✅ Partida cargada exitosamente")

            # Mostrar mensaje en pantalla
            self.activar_mensaje_mision(
                "¡PARTIDA CARGADA!",
                f"Bienvenido de vuelta. {len(self.jugador.equipo)} Pokémon en equipo."
            )

            return True

        except Exception as e:
            print(f"❌ Error al cargar partida: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _reconstruir_pokemon(self, data):
        """Reconstruye un objeto Pokémon a partir de datos guardados"""

        # Crear un Pokémon base con stats mínimos
        pokemon = Pokemon(
            data["nombre"],
            0, 0,  # Posición temporal
            None,  # Sin animaciones
            None,  # Sin sonido
            None,  # Sin límites
            1.0,  # Escala
            data["nivel"]
        )

        # Restaurar todos los stats
        pokemon.nombre = data["nombre"]
        pokemon.nivel = data["nivel"]
        pokemon.hp_max = data["hp_max"]
        pokemon.hp_actual = data["hp_actual"]
        pokemon.ataque = data["ataque"]
        pokemon.defensa = data["defensa"]
        pokemon.ataque_especial = data["ataque_especial"]
        pokemon.defensa_especial = data["defensa_especial"]
        pokemon.velocidad = data["velocidad"]
        pokemon.tipo = data["tipo"]
        pokemon.tipo2 = data.get("tipo2")
        pokemon.ataques = data["ataques"].copy() if data["ataques"] else ["PLACAJE"]
        pokemon.exp_actual = data.get("exp_actual", 0)
        pokemon.exp_siguiente_nivel = data.get("exp_siguiente_nivel", 100)

        # Restaurar frames de batalla (esto es más complejo)
        # Intentar cargar las imágenes nuevamente
        try:
            # Cargar frames para enemigo
            frames_enemigo = []
            for i in range(1, 3):
                ruta = f"asets/imagenes/POKEMON_EN_BATALLA/{data['nombre'].lower()}_{i}.png"
                img = pygame.image.load(ruta).convert_alpha()
                frames_enemigo.append(img)

            # Escalar
            escala = 1.0
            if data['nombre'].lower() == "onix":
                escala = 2.2
            elif data['nombre'].lower() == "magnamite":
                escala = 0.7

            frames_enemigo_escalados = []
            for img in frames_enemigo:
                ancho = int(img.get_width() * escala)
                alto = int(img.get_height() * escala)
                frames_enemigo_escalados.append(pygame.transform.scale(img, (ancho, alto)))

            pokemon.frames_batalla_enemigo = frames_enemigo_escalados

            # Cargar frames para jugador
            try:
                ruta_player = f"asets/imagenes/POKEMON_EN_BATALLA/{data['nombre'].lower()}_player.png"
                img_player = pygame.image.load(ruta_player).convert_alpha()
                img_player = pygame.transform.scale(img_player, (153, 108))
                pokemon.frames_batalla_jugador = [img_player, img_player]
            except:
                # Si no hay, crear desde enemigo
                if frames_enemigo_escalados:
                    img_volteada = pygame.transform.flip(frames_enemigo_escalados[0], True, False)
                    img_volteada = pygame.transform.scale(img_volteada, (153, 108))
                    pokemon.frames_batalla_jugador = [img_volteada, img_volteada]

        except Exception as e:
            print(f"   ⚠️ No se pudieron cargar frames para {data['nombre']}: {e}")
            # Crear frames por defecto
            surf = pygame.Surface((153, 108))
            surf.fill((200, 100, 200))
            pokemon.frames_batalla_jugador = [surf, surf]
            pokemon.frames_batalla_enemigo = [surf, surf]

        return pokemon



    def reproducir_video(self):
        ret, frame = self.cap.read()

        if ret:
            # Convertir el frame de OpenCV (BGR) a Pygame (RGB)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.transpose(frame)  # Girarlo si aparece de lado

            # Convertir a superficie de Pygame y escalar al tamaño de ventana
            surface = pygame.surfarray.make_surface(frame)
            surface = pygame.transform.scale(surface, (800, 600))

            self.ventana.blit(surface, (0, 0))
        else:
            # Si ret es False, el video terminó
            self.video_terminado = True
            self.cap.release()  # Liberar el archivo

            self.estado_juego = "MENU_INICIO"  # Pasar al menú

    def _dibujar_intro_oak(self):
        # 1. Fondo (Si no existe, pintamos un fondo azul oscuro para que no crashee)
        if self.imagen_fondo_oak:
            self.ventana.blit(self.imagen_fondo_oak, (0, 0))
        else:
            self.ventana.fill((20, 20, 80))

            # 2. Base
        if self.base_oak:
            rect_base = self.base_oak.get_rect(center=(410, 480))
            self.ventana.blit(self.base_oak, rect_base)

        # 3. Profesor Oak
        if self.sprite_oak:
            rect_oak = self.sprite_oak.get_rect(center=(400, 245))
            self.ventana.blit(self.sprite_oak, rect_oak)

        if self.oak_indice == 1:
            # Dibujamos la pokebola cerca de la mano de Oak
            # Ajusta (430, 340) según la posición de tu sprite de Oak
            self.ventana.blit(self.img_pokebola, (290, 220))

        elif self.oak_indice == 2:
            # Dibujamos la pokebola cerca de la mano de Oak
            # Ajusta (430, 340) según la posición de tu sprite de Oak
            self.ventana.blit(self.img_pokebola, (290, 220))


        elif self.oak_indice == 3:
            # Aparece el Pokémon al lado de Oak
            self.ventana.blit(self.img_pokemon_intro, (250, 380))
            self.ventana.blit(self.img_pokebola, (290, 220))



        # 4. Cuadro de Diálogo
        if self.oak_dialogos:
            self._dibujar_cuadro_dialogo(self.oak_dialogos[self.oak_indice])

    def _cargar_interior_estadistica(self):
        """Carga el interior del edificio de Estadística"""
        print("🚪 Cargando interior de estadística...")
        self.mapa_actual = "INTERIOR_ESTADISTICA"




        try:
            # 1. Cargar fondo
            img_fondo = pygame.image.load("asets/imagenes/ESTADISTICA/fondo_estadistica.png").convert()
            self.fondo_completo = pygame.transform.scale(img_fondo, (800, 600))
            print("✅ Fondo cargado")

            # 2. Posición del jugador (cerca de la entrada)
            self.jugador.forma.centerx = 400
            self.jugador.forma.centery = 500
            print(f"✅ Jugador posicionado en ({self.jugador.forma.x}, {self.jugador.forma.y})")

            # 3. Cámara fija
            self.camara.offset = pygame.Vector2(0, 0)

            # 4. Muros (paredes invisibles)
            self.muros_interiores = [
                pygame.Rect(0, 0, 800, 80),  # Pared superior
                pygame.Rect(0, 0, 50, 600),  # Pared izquierda
                pygame.Rect(750, 0, 50, 600),  # Pared derecha
                pygame.Rect(0, 550, 800, 50),  # Pared inferior
                pygame.Rect(300, 200, 200, 50),  # Zona del mostrador/Oak
            ]

            # 5. Salida (alfombra para volver al exterior)
            self.rect_salida_estadistica = pygame.Rect(350, 540, 100, 30)

            # 6. CARGAR NPCs DEL INTERIOR
            self.lista_npcs = self.npcs_interior_estadistica
            print(f"✅ NPCs cargados: {len(self.lista_npcs)}")



            # 8. Variables para el starter
            self.indice_dialogo_starter = 0
            self.mostrando_opciones_starter = False
            self.starter_seleccionado = 0
            self.opciones_starter = ["Bulbasaur", "Squirtle", "Charmander"]
            self.starter_elegido = None

            # 9. VARIABLE PARA CONTROLAR QUÉ POKÉMON SE MUESTRA
            self.pokemon_mostrado = None

            print(f"✅ Interior de Estadística cargado correctamente")


        except Exception as e:
            print(f"❌ Error cargando interior: {e}")
            import traceback
            traceback.print_exc()
            self.cambiar_mapa("exterior", 1160, 690)

    def _dibujar_tarjeta_pokemon(self, pokemon_tipo):
        """Dibuja una tarjeta grande con la imagen, descripción y opciones SÍ/NO"""
        if pokemon_tipo not in self.descripciones_pokemon:
            return

        datos = self.descripciones_pokemon[pokemon_tipo]

        # Fondo de la tarjeta
        ancho_tarjeta = 600
        alto_tarjeta = 400
        x_tarjeta = (self.ancho - ancho_tarjeta) // 2
        y_tarjeta = (self.alto - alto_tarjeta) // 2 - 50

        # Fondo negro semitransparente
        fondo = pygame.Surface((ancho_tarjeta, alto_tarjeta))
        fondo.set_alpha(230)
        fondo.fill((20, 20, 30))
        self.ventana.blit(fondo, (x_tarjeta, y_tarjeta))

        if pokemon_tipo == "charmander":
            color_borde = (255, 165, 0)  # Rojo
        elif pokemon_tipo == "squirtle":
            color_borde = (0, 150, 255)  # Celeste/Azul claro
        elif pokemon_tipo == "bulbasaur":
            color_borde = (0, 255, 0)  # Verde
        else:
            color_borde = (255, 215, 0)  # Dorado por defecto

            # Borde con el color correspondiente
        pygame.draw.rect(self.ventana, color_borde,
                         (x_tarjeta, y_tarjeta, ancho_tarjeta, alto_tarjeta), 4)






        # Título
        titulo = self.fuente.render(f"¿Quieres a {datos['nombre']}?", True, (255, 255, 0))
        self.ventana.blit(titulo, (x_tarjeta + 140, y_tarjeta + 20))

        # Imagen del Pokémon (izquierda) - MÁS GRANDE
        if pokemon_tipo == "charmander" and self.img_charmander:
            img = pygame.transform.scale(self.img_charmander, (150, 150))
            self.ventana.blit(img, (x_tarjeta + 30, y_tarjeta + 80))
        elif pokemon_tipo == "squirtle" and self.img_squirtle:
            img = pygame.transform.scale(self.img_squirtle, (150, 150))
            self.ventana.blit(img, (x_tarjeta + 30, y_tarjeta + 80))
        elif pokemon_tipo == "bulbasaur" and self.img_bulbasaur:
            img = pygame.transform.scale(self.img_bulbasaur, (150, 150))
            self.ventana.blit(img, (x_tarjeta + 30, y_tarjeta + 80))

        # Información del Pokémon (derecha)
        fuente_info = pygame.font.Font(None, 24)
        x_texto = x_tarjeta + 210
        y_texto = y_tarjeta + 90

        # Tipo
        tipo_texto = fuente_info.render(f"Tipo: {datos['tipo']}", True, (255, 255, 255))
        self.ventana.blit(tipo_texto, (x_texto, y_texto))

        # Altura y Peso en una línea
        altura_peso = fuente_info.render(f"Alt: {datos['altura']}  Peso: {datos['peso']}", True, (255, 255, 255))
        self.ventana.blit(altura_peso, (x_texto, y_texto + 30))

        # Habilidad
        habilidad_texto = fuente_info.render(f"Hab: {datos['habilidad']}", True, (255, 255, 255))
        self.ventana.blit(habilidad_texto, (x_texto, y_texto + 60))

        # Descripción1
        descripcion_texto1 = fuente_info.render(datos['descripcion1'], True, (255, 255, 255))
        self.ventana.blit(descripcion_texto1, (x_texto, y_texto + 100))

        descripcion_texto2 = fuente_info.render(datos['descripcion2'], True, (255, 255, 255))
        self.ventana.blit(descripcion_texto2, (x_texto, y_texto + 120))

        descripcion_texto3 = fuente_info.render(datos['descripcion3'], True, (255, 255, 255))
        self.ventana.blit(descripcion_texto3, (x_texto, y_texto + 140))

        # ==========================================
        # 🆕 OPCIONES SÍ/NO
        # ==========================================
        opcion_y = y_tarjeta + alto_tarjeta - 70

        # Colores según selección
        color_si = (255, 255, 0) if self.opcion_starter_seleccionada == 0 else (255, 255, 255)
        color_no = (255, 255, 0) if self.opcion_starter_seleccionada == 1 else (255, 255, 255)

        # Textos
        si_texto = fuente_info.render("SÍ", True, color_si)
        no_texto = fuente_info.render("NO", True, color_no)

        # Posiciones
        self.ventana.blit(si_texto, (x_tarjeta + 200, opcion_y))
        self.ventana.blit(no_texto, (x_tarjeta + 350, opcion_y))

        # Flecha indicadora
        if self.opcion_starter_seleccionada == 0:
            pygame.draw.polygon(self.ventana, (255, 255, 0),
                                [(x_tarjeta + 180, opcion_y + 10),
                                 (x_tarjeta + 190, opcion_y),
                                 (x_tarjeta + 190, opcion_y + 20)])
        else:
            pygame.draw.polygon(self.ventana, (255, 255, 0),
                                [(x_tarjeta + 330, opcion_y + 10),
                                 (x_tarjeta + 340, opcion_y),
                                 (x_tarjeta + 340, opcion_y + 20)])

    def _elegir_starter(self, pokemon_tipo):
        """Configura el Pokémon elegido como starter del jugador"""
        nombre_completo = self.descripciones_pokemon[pokemon_tipo]["nombre"]
        print(f"✅ Has elegido a {nombre_completo}!")

        # 🟢 CREAR EL STARTER USANDO LA MISMA FUNCIÓN QUE LOS RIVALES
        starter = self._preparar_pokemon_pool(pokemon_tipo, 5)  # Nivel 5

        if not starter:
            print("❌ Error creando starter")
            return

        # Asignar el starter al jugador
        self.starter_ya_elegido = True
        self.tiene_pokemon = True
        self.jugador.tiene_pokemon = True
        self.starter_elegido = pokemon_tipo
        self.jugador.nombre = nombre_completo

        # Copiar todos los stats del starter al jugador
        self.jugador.tipo = starter.tipo
        self.jugador.tipo2 = starter.tipo2
        self.jugador.hp_max = starter.hp_max
        self.jugador.hp_actual = starter.hp_max
        self.jugador.ataque = starter.ataque
        self.jugador.defensa = starter.defensa
        self.jugador.ataque_especial = starter.ataque_especial
        self.jugador.defensa_especial = starter.defensa_especial
        self.jugador.velocidad = starter.velocidad
        self.jugador.nivel = 5
        self.jugador.ataques = starter.ataques.copy()

        # Cargar imagen de jugador
        try:
            ruta_player = f"asets/imagenes/POKEMON_EN_BATALLA/{pokemon_tipo}_player.png"
            img_player = pygame.image.load(ruta_player).convert_alpha()
            img_player = pygame.transform.scale(img_player, (153, 108))
            self.jugador.frames_batalla = [img_player, img_player]

            # Asignar frames al starter
            starter.frames_batalla_jugador = self.jugador.frames_batalla
        except:
            # Si no hay imagen player, usar la imagen del enemigo volteada
            if starter.frames_batalla_enemigo:
                img_volteada = pygame.transform.flip(starter.frames_batalla_enemigo[0], True, False)
                self.jugador.frames_batalla = [img_volteada, img_volteada]
                starter.frames_batalla_jugador = self.jugador.frames_batalla

        # Agregar al equipo
        self.jugador.equipo = [starter]
        self.jugador.pokemon_activo = 0

        print(f"✅ Starter {nombre_completo} creado correctamente")
        print(f"   Stats: HP={starter.hp_max}, ATK={starter.ataque}, DEF={starter.defensa}")
        print(f"   ATK ESP={starter.ataque_especial}, DEF ESP={starter.defensa_especial}")
        print(f"   El jugador ES {self.jugador.nombre} con HP={self.jugador.hp_actual}")

        # Mensaje de confirmación
        self.activar_mensaje_mision(
            "¡STARTER ELEGIDO!",
            f"Has elegido a {nombre_completo}. ¡Ahora tienes un Pokémon!"
        )
    def activar_mensaje_mision(self, titulo, descripcion):
        """Activa el mensaje de misión que se mostrará en exploración"""
        self.mostrando_mensaje_mision = True
        self.titulo_mision = titulo
        self.descripcion_mision = descripcion
        self.tiempo_inicio_mensaje = pygame.time.get_ticks()
        print(f"📋 Misión activada: {titulo}")

    def _iniciar_video_final(self):
        """Inicializa el video de finalización"""
        import cv2

        # Ruta del video final (cámbiala por la tuya)
        self.video_final_path = "asets/video/final.mp4"

        try:
            self.cap_final = cv2.VideoCapture(self.video_final_path)
            self.video_final_terminado = False

            # Cargar audio del video si existe
            try:
                self.sonido_video_final = pygame.mixer.Sound("asets/music/final_audio.mp3")
                self.sonido_video_final.set_volume(0.5)
                self.audio_final_reproducido = False
            except:
                self.sonido_video_final = None
                self.audio_final_reproducido = True

            print("🎬 Video final cargado")
        except Exception as e:
            print(f"❌ Error cargando video final: {e}")
            # Si no hay video, volver al menú de inicio
            self.estado_juego = "MENU_INICIO"

    def _actualizar_video_final(self):
        """Actualiza el video final"""
        if not hasattr(self, 'cap_final') or self.cap_final is None:
            print("⚠️ No hay video, pasando a créditos")
            self.estado_juego = "CREDITOS"
            self.tiempo_creditos = pygame.time.get_ticks()
            return

        ret, frame = self.cap_final.read()

        if ret:
            # Procesar frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.transpose(frame)
            self.surface_video_final = pygame.surfarray.make_surface(frame)
            self.surface_video_final = pygame.transform.scale(self.surface_video_final, (self.ancho, self.alto))

            # 🟢 REPRODUCIR AUDIO (IMPORTANTE)
            if hasattr(self, 'sonido_video_final') and self.sonido_video_final:
                if not self.audio_final_reproducido:
                    print("🔊 Reproduciendo audio del video")
                    self.sonido_video_final.play()
                    self.audio_final_reproducido = True
        else:
            # Video terminado
            print("🎬 Video terminado, pasando a créditos")
            if hasattr(self, 'cap_final') and self.cap_final:
                self.cap_final.release()
                self.cap_final = None

            # Detener audio si está sonando
            if hasattr(self, 'sonido_video_final') and self.sonido_video_final:
                self.sonido_video_final.stop()

            self.estado_juego = "CREDITOS"
            self.tiempo_creditos = pygame.time.get_ticks()

    def _dibujar_video_final(self):
        """Dibuja el video final con texto superpuesto"""

        if hasattr(self, 'surface_video_final'):
            # Dibujar el frame actual del video
            self.ventana.blit(self.surface_video_final, (0, 0))

            # 🟢 Crear una superficie semitransparente para el texto
            overlay = pygame.Surface((self.ancho, 150), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Negro semitransparente

            # Posicionar el overlay en el centro de la pantalla
            overlay_rect = overlay.get_rect(center=(self.ancho // 2, self.alto // 2))
            self.ventana.blit(overlay, overlay_rect)

            # 🟢 Texto principal "GRACIAS POR JUGAR"
            try:
                fuente_grande = pygame.font.Font("asets/FuenteDeTexto/pokemon.otf", 60)
            except:
                fuente_grande = pygame.font.Font(None, 60)

            texto_gracias = fuente_grande.render("GRACIAS POR JUGAR", True, (255, 215, 0))
            texto_gracias_rect = texto_gracias.get_rect(center=(self.ancho // 2, self.alto // 2 - 20))
            self.ventana.blit(texto_gracias, texto_gracias_rect)

            # 🟢 Texto secundario (opcional)
            try:
                fuente_mediana = pygame.font.Font("asets/FuenteDeTexto/pokemon.otf", 30)
            except:
                fuente_mediana = pygame.font.Font(None, 30)

            texto_secundario = fuente_mediana.render("Has completado UNIMON", True, (255, 255, 255))
            texto_secundario_rect = texto_secundario.get_rect(center=(self.ancho // 2, self.alto // 2 + 30))
            self.ventana.blit(texto_secundario, texto_secundario_rect)

            # 🟢 Efecto de parpadeo para "Presiona ESPACIO"
            if pygame.time.get_ticks() % 1000 < 500:  # Parpadea cada segundo
                try:
                    fuente_pequena = pygame.font.Font("asets/FuenteDeTexto/pokemon.otf", 20)
                except:
                    fuente_pequena = pygame.font.Font(None, 20)

                texto_espacio = fuente_pequena.render("Presiona ESPACIO para saltar", True, (255, 255, 255))
                texto_espacio_rect = texto_espacio.get_rect(center=(self.ancho // 2, self.alto - 50))
                self.ventana.blit(texto_espacio, texto_espacio_rect)
        else:
            # Fallback si no hay video
            self.ventana.fill((0, 0, 0))
            texto = self.fuente.render("¡FELICIDADES!", True, (255, 215, 0))
            texto2 = self.fuente.render("Has derrotado a todos los líderes", True, (255, 255, 255))
            self.ventana.blit(texto, (self.ancho // 2 - texto.get_width() // 2, 200))
            self.ventana.blit(texto2, (self.ancho // 2 - texto2.get_width() // 2, 300))

    def _dibujar_creditos(self):
        """Dibuja la pantalla de créditos"""
        self.ventana.fill((0, 0, 0))

        # 🟢 Asegurar que tenemos una fuente
        try:
            fuente_creditos = pygame.font.Font("asets/FuenteDeTexto/pokemon.otf", 25)
        except:
            fuente_creditos = pygame.font.Font(None, 25)

        # Título grande
        try:
            fuente_titulo = pygame.font.Font("asets/FuenteDeTexto/pokemon.otf", 40)
        except:
            fuente_titulo = pygame.font.Font(None, 40)

        titulo = fuente_titulo.render("CRÉDITOS", True, (255, 215, 0))
        self.ventana.blit(titulo, (self.ancho // 2 - titulo.get_width() // 2, 30))

        creditos = [
            "UNIMON - El Camino del Ingeniero",
            "",
            "Desarrollado por:",
            "JUAN PAJAR",
            "BRUNO",
            "",
            "Gracias por jugar",
            "",
            "Profesores:",
            "Profesor Quillas",
            "Profesor Janampa",
            "Profesor Yury",
            "Profesor Chirinos",
            "Profesor Wattson",
            "Profesor Chavez",
            "",
            "Presiona ESPACIO para volver al menú"
        ]

        y = 120
        for linea in creditos:
            if linea == "":
                y += 15
            else:
                texto = fuente_creditos.render(linea, True, (255, 255, 255))
                self.ventana.blit(texto, (self.ancho // 2 - texto.get_width() // 2, y))
                y += 35

        # Opcional: Dibujar un mensaje de "Presiona ESPACIO" más visible
        if pygame.time.get_ticks() % 1000 < 500:  # Parpadeo
            texto_espacio = fuente_creditos.render("Presiona ESPACIO para continuar", True, (255, 255, 0))
            self.ventana.blit(texto_espacio, (self.ancho // 2 - texto_espacio.get_width() // 2, 500))

        # Auto-retorno después de 15 segundos
        if pygame.time.get_ticks() - self.tiempo_creditos > 15000:
            print("⏰ Tiempo de créditos terminado, volviendo al menú")
            self.estado_juego = "MENU_INICIO"
            # Restaurar música del menú
            try:
                pygame.mixer.music.load("asets/music/musica_menu.mp3")
                pygame.mixer.music.play(-1)
            except:
                pass

    def _dibujar_cartel_mision(self):
        """Dibuja un cartel de misión en el centro de la pantalla (solo en exploración)"""
        if not self.mostrando_mensaje_mision:
            return

        # Verificar si ya pasó el tiempo
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.tiempo_inicio_mensaje > self.duracion_mensaje:
            self.mostrando_mensaje_mision = False
            return

        # Crear un fondo semitransparente
        ancho_cartel = 650
        alto_cartel = 220
        x = (self.ancho - ancho_cartel) // 2
        y = (self.alto - alto_cartel) // 2

        # Fondo negro semitransparente
        fondo = pygame.Surface((ancho_cartel, alto_cartel))
        fondo.set_alpha(220)
        fondo.fill((0, 0, 0))
        self.ventana.blit(fondo, (x, y))

        # Borde dorado
        pygame.draw.rect(self.ventana, (255, 215, 0), (x, y, ancho_cartel, alto_cartel), 5)

        # Título
        try:
            fuente_titulo = pygame.font.Font("asets/FuenteDeTexto/pokemon.otf", 45)
        except:
            fuente_titulo = pygame.font.Font(None, 45)

        titulo_surf = fuente_titulo.render(self.titulo_mision, True, (255, 255, 0))
        titulo_rect = titulo_surf.get_rect(center=(self.ancho // 2, y + 50))
        self.ventana.blit(titulo_surf, titulo_rect)

        # Descripción
        try:
            fuente_desc = pygame.font.Font("asets/FuenteDeTexto/pokemon.otf", 25)
        except:
            fuente_desc = pygame.font.Font(None, 25)

        palabras = self.descripcion_mision.split(' ')
        lineas = []
        linea_actual = ""

        for palabra in palabras:
            prueba = linea_actual + " " + palabra if linea_actual else palabra
            if fuente_desc.size(prueba)[0] < 600:
                linea_actual = prueba
            else:
                lineas.append(linea_actual)
                linea_actual = palabra

        if linea_actual:
            lineas.append(linea_actual)

        y_offset = y + 100
        for linea in lineas:
            linea_surf = fuente_desc.render(linea, True, (255, 255, 255))
            linea_rect = linea_surf.get_rect(center=(self.ancho // 2, y_offset))
            self.ventana.blit(linea_surf, linea_rect)
            y_offset += 35

    def obtener_ataques_por_pokemon(self, nombre):
        """Devuelve ataques según el tipo de Pokémon"""
        nombre = nombre.lower().strip()

        # Ataques por Pokémon
        if "hitmonlee" in nombre:
            return ["PATADA SALTO", "GOLPE KARMA", "FINTE", "PATADA BAJA"]
        elif "hitmonchan" in nombre:
            return ["PUÑO MACHETE", "PUÑO DINÁMICO", "FINTE", "PUÑO MACHACA"]
        elif "onix" in nombre:
            return ["TERREMOTO", "DESLIZAR", "ROCA AFILADA", "COLISIÓN"]
        elif "pikachu" in nombre:
            return ["IMPACTRUENO", "ATAQUE RÁPIDO", "CHISPA", "PLACAJE"]
        elif "magnamite" in nombre or "magnemite" in nombre:
            return ["CHISPA", "SONICBOOM", "RAYO CARGA", "IMPACTO"]
        elif "charmander" in nombre:
            return ["ASCUAS", "ARAÑAZO", "GRUÑIDO", "PLACAJE"]
        elif "squirtle" in nombre:
            return ["PISTOLA AGUA", "ARAÑAZO", "GRUÑIDO", "PLACAJE"]
        elif "bulbasaur" in nombre:
            return ["LÁTIGO CEPA", "ABSORBER", "GRUÑIDO", "PLACAJE"]
        elif "pidgey" in nombre:
            return ["ATAQUE ALA", "REMOLINO", "PLACAJE", "GRUÑIDO"]
        elif "horsea" in nombre:
            return ["PISTOLA AGUA", "BURBUJA", "ÁCIDO", "PLACAJE"]
        elif "rhyhorn" in nombre:
            return ["TERREMOTO", "DERRIBO", "ATIZAR", "PLACAJE"]
        elif "tangela" in nombre:
            return ["LÁTIGO CEPA", "ABSORBER", "ENREDADERA", "PLACAJE"]
        else:
            # Ataques genéricos
            return ["PLACAJE", "GRUÑIDO", "PATADA", "GOLPE"]

    def iniciar_batalla_entrenador(self, entrenador):
        """Inicia una batalla contra un entrenador NPC"""
        print(f"🔍 INICIANDO BATALLA CONTRA {entrenador.nombre_entrenador}")

        if not entrenador.equipo or len(entrenador.equipo) == 0:
            print(f"⚠️ {entrenador.nombre_entrenador} no tiene Pokémon")
            return

        # 🟢 CREAR COPIAS DE LOS POKÉMON
        equipo_copia = []
        for pokemon in entrenador.equipo:
            copia = self._preparar_pokemon_pool(pokemon.nombre, pokemon.nivel)
            if copia:
                equipo_copia.append(copia)
                print(f"   ✅ Copia de {pokemon.nombre} creada (ID: {id(copia)})")

        if not equipo_copia:
            print("❌ No se pudieron crear copias de los Pokémon")
            return

        # 🟢 AHORA: REEMPLAZAR el equipo del entrenador con las COPIAS
        entrenador.equipo = equipo_copia  # ¡ESTO ES LO QUE FALTABA!

        # Guardar referencia al entrenador (ahora con las copias)
        self.entrenador_rival = entrenador
        self.equipo_entrenador = equipo_copia

        # Verificar que el jugador tenga Pokémon
        if not self.tiene_pokemon or not self.jugador.tiene_pokemon:
            print("❌ El jugador no tiene Pokémon")
            return

        # Iniciar batalla con el primer Pokémon (copia)
        self.pokemon_pendiente = equipo_copia[0]
        self.transicion_batalla = True
        print(f"⚔️ Batalla contra {entrenador.nombre_entrenador} iniciada!")
        print(f"   Pokémon en batalla: {self.pokemon_pendiente.nombre} (ID: {id(self.pokemon_pendiente)})")
        print(f"   Total Pokémon en equipo: {len(entrenador.equipo)}")


    async def ejecutar(self):
        while not self.game_over:
            # 1. Procesamos eventos
            self.manejar_eventos()

            # 🆕 ESTADO: VIDEO FINAL (ponerlo AL PRINCIPIO)
            if self.estado_juego == "VIDEO_FINAL":
                self._actualizar_video_final()
                self._dibujar_video_final()
                pygame.display.update()
                fps = getattr(self, 'video_final_fps', 30)
                self.reloj.tick(fps)
                await asyncio.sleep(0)
                continue

            # 🆕 ESTADO: CREDITOS
            if self.estado_juego == "CREDITOS":
                self._dibujar_creditos()
                pygame.display.update()
                self.reloj.tick(30)
                await asyncio.sleep(0)
                continue

            # --- ESTADO 0: INTRODUCCIÓN (VIDEO) ---
            if self.estado_juego == "INTRO":
                if not getattr(self, 'audio_intro_reproducido', False):
                    pygame.mixer.music.stop()
                    if hasattr(self, 'sonido_intro') and self.sonido_intro:
                        self.sonido_intro.play()
                    self.audio_intro_reproducido = True

                self.reproducir_video()
                pygame.display.update()

                fps_video = getattr(self, 'video_fps', 30)
                self.reloj.tick(fps_video)

                # Al terminar el video (dentro de reproducir_video cambia el estado)
                if self.estado_juego == "MENU_INICIO":
                    if hasattr(self, 'sonido_intro') and self.sonido_intro:
                        self.sonido_intro.stop()

            elif self.estado_juego == "INTRO_OAK":
                # Llamamos a actualizar para que se pueda avanzar el diálogo con E
                self.actualizar()
                self.dibujar()
                self.reloj.tick(60)


            # --- OTROS ESTADOS (CORREN A 60 FPS) ---
            else:
                if self.estado_juego == "MENU_INICIO":
                    # --- LÓGICA DE MÚSICA DE MENÚ ---
                    if not getattr(self, 'musica_menu_iniciada', False):
                        try:
                            pygame.mixer.music.load("asets/music/musica_menu.mp3")
                            pygame.mixer.music.play(-1)
                            self.musica_menu_iniciada = True
                        except:
                            print("Error al cargar música del menú")

                    # --- CORRECCIÓN: LLAMAMOS A ACTUALIZAR PARA ACTIVAR ANIMACIÓN ---
                    self.actualizar()
                    self.dibujar()

                elif self.estado_juego == "EXPLORACION":
                    if getattr(self, 'musica_menu_iniciada', False):
                        pygame.mixer.music.stop()
                        self.musica_menu_iniciada = False

                    if not pygame.mixer.music.get_busy():
                        try:
                            pygame.mixer.music.load("asets/music/A1.mp3")
                            pygame.mixer.music.play(-1)
                        except:
                            pass

                    self.actualizar()
                    self.dibujar()

                elif self.estado_juego == "MENU_PAUSA":
                    # Si quieres que el menú de pausa tenga animaciones, también debes actualizar
                    # self.actualizar()
                    self.dibujar()

                elif self.estado_juego == "BATALLA":
                    if self.instancia_batalla.batalla_finalizada:

                        # 🟢 Variable para controlar el video
                        reproducir_video_final = False

                        # Verificar resultado con entrenador
                        if hasattr(self, 'entrenador_rival') and self.entrenador_rival:
                            entrenador = self.entrenador_rival
                            if hasattr(self.instancia_batalla, 'resultado_batalla'):
                                if self.instancia_batalla.resultado_batalla == "gano":
                                    entrenador.derrotado = True
                                    entrenador.le_gano_al_jugador = False
                                    print(f"✅ {entrenador.nombre_entrenador} derrotado")

                                    # Verificar si es el líder final
                                    if hasattr(entrenador, 'es_lider_final') and entrenador.es_lider_final:
                                        print("🎬 ¡LÍDER FINAL DERROTADO! Reproduciendo video...")
                                        reproducir_video_final = True

                                elif self.instancia_batalla.resultado_batalla == "perdio":
                                    entrenador.derrotado = False
                                    entrenador.le_gano_al_jugador = True
                                    print(f"⚠️ {entrenador.nombre_entrenador} te ganó")

                        # Finalizar la batalla
                        self.instancia_batalla.finalizar_batalla()

                        # 🟢 DETENER TODA LA MÚSICA ANTES DEL VIDEO
                        pygame.mixer.music.stop()
                        pygame.mixer.stop()  # Detiene todos los sonidos

                        # 🟢 Decidir el siguiente estado
                        if reproducir_video_final:
                            self.estado_juego = "VIDEO_FINAL"
                            self._iniciar_video_final()
                            print("🎬 Cambiando a VIDEO_FINAL")
                        else:
                            self.estado_juego = "EXPLORACION"
                            print("👣 Cambiando a EXPLORACION")

                        self.instancia_batalla = None

                        # Volver a la música de exploración (solo si no es video)
                        if not reproducir_video_final:
                            try:
                                pygame.mixer.music.load("asets/music/A1.mp3")
                                pygame.mixer.music.play(-1)
                            except:
                                print("Error al volver a cargar música de exploración")

                    else:
                        # Batalla en curso
                        self.instancia_batalla.dibujar(self.ventana)
                        pygame.display.update()

                self.reloj.tick(55)

            await asyncio.sleep(0)
# --- EJECUCIÓN ---
async def main():
    juego = Juego()

    # --- ACTIVACIÓN DE MÚSICA PARA PYCHARM Y WEB ---
    try:
        if pygame.mixer.get_init():
            # Usamos la variable que definiste en el __init__
            pygame.mixer.music.load(juego.musica_ambiente)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            print("Música iniciada")
    except Exception as e:
        print(f"No se pudo reproducir la música: {e}")
    # -----------------------------------------------

    await juego.ejecutar()

if __name__ == "__main__":
    asyncio.run(main())

