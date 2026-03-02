import random
import math
import pygame


class SistemaBatalla:
    def __init__(self, jugador, enemigo, fuente,es_entrenador=False, entrenador_nombre="Rival",equipo_entrenador=None):
        # --- 1. DATOS DE ATAQUES (AGREGADO AQUÍ PARA EVITAR ERROR) ---
        self.jugador = jugador
        self.enemigo = enemigo
        self.fuente = fuente

        # --- Sonidos ---
        self.sonido_huida = pygame.mixer.Sound("asets/music/huida.mp3")
        self.sonido_impacto = pygame.mixer.Sound("asets/music/golpe.mp3")
        self.sonido_impacto.set_volume(1.5)
        self.sonido_seleccionar = pygame.mixer.Sound("asets/music/E1.mp3")
        self.sonido_seleccionar_es = pygame.mixer.Sound("asets/music/E2.mp3")

        # --- Control de Animaciones ---
        self.animando_ataque = False
        self.timer_animacion = 0
        self.mensaje_completo = ""
        self.mensaje_visible = ""
        self.indice_letra = 0
        self.velocidad_texto = 80
        self.timer_texto = pygame.time.get_ticks()
        self.escapando = False
        self.offset_x_huida = 0

        # --- Configuración Visual Fondo ---
        imagen_original = pygame.image.load("asets/imagenes/INTERFAZ/fase_de_batalla.png").convert()
        self.fondo_img = pygame.transform.scale(imagen_original, (800, 450))
        self.y_fondo = 0
        self.base_jugador = pygame.image.load("asets/imagenes/INTERFAZ/base_mio.png").convert_alpha()
        self.base_rival = pygame.image.load("asets/imagenes/INTERFAZ/base_rival.png").convert_alpha()
        self.base_jugador = pygame.transform.scale(self.base_jugador, (456, 66))
        self.base_rival = pygame.transform.scale(self.base_rival, (399, 216))

        # --- Lógica de Entrada ---
        self.intro_terminada = False
        self.alpha_fondo = 0
        self.pos_x_base_rival = 850
        self.pos_x_base_jugador = -350
        self.target_x_rival = 450
        self.target_x_jugador = -20
        self.velocidad_deslize = 12

        # --- CARGA DINÁMICA DEL RIVAL (CORREGIDA) ---
        # --- CARGA DINÁMICA DEL RIVAL ---
        nombre_pkmn = enemigo.nombre.lower().strip()

        try:
            # Usamos animaciones_escaladas[0] porque ahí guardamos el frente
            anim_rival = enemigo.animaciones_escaladas[0]
            img1_raw = anim_rival[0]
            img2_raw = anim_rival[1] if len(anim_rival) > 1 else img1_raw
        except:
            img1_raw = enemigo.image
            img2_raw = enemigo.image

        # ==========================================
        # 🎯 ESCALADO PERSONALIZADO POR POKÉMON
        # ==========================================
        if nombre_pkmn == "onix":
            alto_deseado = 180  # Onix es gigante
            ancho_extra = 1  # Factor extra de ancho
        elif nombre_pkmn == "magnamite":
            alto_deseado = 80 # Más pequeño que el estándar
            ancho_extra = 0.8  # Un poco más estrecho

        else:
            alto_deseado = 120  # Tamaño estándar
            ancho_extra = 1.0

        # Calcular dimensiones manteniendo proporción
        ancho1 = int(img1_raw.get_width() * (alto_deseado / img1_raw.get_height()) * ancho_extra)
        ancho2 = int(img2_raw.get_width() * (alto_deseado / img2_raw.get_height()) * ancho_extra)

        self.frames_rival = [
            pygame.transform.scale(img1_raw, (ancho1, alto_deseado)),
            pygame.transform.scale(img2_raw, (ancho2, alto_deseado))
        ]


        # --- Tu Pokémon (con el starter elegido) ---
        if hasattr(self.jugador, 'frames_batalla') and self.jugador.frames_batalla:
            # Usar los frames guardados del starter
            self.frames_mio = self.jugador.frames_batalla
            print(f"✅ Usando frames de {self.jugador.nombre} para batalla")
        else:
            # Fallback a Bulbasaur por defecto
            print("⚠️ No hay frames de batalla, usando Bulbasaur por defecto")
            self.frames_mio = [
                pygame.image.load("asets/imagenes/POKEMON_EN_BATALLA/bulbasaur_batalla_p.png").convert_alpha(),
                pygame.image.load("asets/imagenes/POKEMON_EN_BATALLA/bulbasaur_batalla_p.png").convert_alpha()
            ]
            self.frames_mio = [pygame.transform.scale(f, (153, 108)) for f in self.frames_mio]


        # --- HUD ---
        self.hud_rival = pygame.image.load("asets/imagenes/INTERFAZ/hub_rival.png").convert_alpha()
        self.hud_mio = pygame.image.load("asets/imagenes/INTERFAZ/hub_mio.png").convert_alpha()
        self.hud_rival = pygame.transform.scale(self.hud_rival, (260, 60))
        self.hud_mio = pygame.transform.scale(self.hud_mio, (260, 80))
        self.fuente_hud = pygame.font.Font("asets/FuenteDeTexto/pokemon.otf", 30)
        self.fuente_hp_pequeña = pygame.font.Font("asets/FuenteDeTexto/pixel.ttf", 11)

        # --- Estados de Juego ---
        self.fase = "INTRO"
        self.turno = "jugador"
        self.batalla_finalizada = False
        self.opciones = ["ATACAR", "POKEMON", "BOLSA", "ESCAPAR"]
        self.indice_seleccionado = 0
        if hasattr(self.jugador, 'ataques') and self.jugador.ataques:
            self.ataques = self.jugador.ataques
            print(f"✅ Usando ataques de {self.jugador.nombre}: {self.ataques}")


        self.indice_ataque = 0

        self.nuevo_mensaje(f"¡Un {enemigo.nombre.upper()} salvaje aparecio!")
        self.fase = "INTRO"

        self.capturando = False
        self.animacion_captura = 0  # 0 = no activa, 1 = lanzando, 2 = atrapando, 3 = éxito, 4 = fallo
        self.timer_captura = 0
        self.frame_captura = 0
        self.parpadeos_captura = 0
        self.captura_exitosa = False
        self.pokemon_visible = True

        self.mostrando_equipo = False
        self.indice_equipo = 0

        # 🆕 Cargar imagen de pokebola para captura
        try:
            self.img_pokebola_captura = pygame.image.load("asets/imagenes/INICIO_RECTOR/pokebola.png").convert_alpha()
            self.img_pokebola_captura = pygame.transform.scale(self.img_pokebola_captura, (40, 40))
        except:
            self.img_pokebola_captura = None

        # Escalar frames del rival



        print(f"🔍 INICIO BATALLA - Equipo del jugador: {len(jugador.equipo)} Pokémon")
        if hasattr(jugador, 'equipo') and jugador.equipo:
            for i, p in enumerate(jugador.equipo):
                print(f"   {i}: {p.nombre} (HP: {p.hp_actual}/{p.hp_max})")

        if not hasattr(jugador, 'tiene_pokemon') or not jugador.tiene_pokemon:
            raise Exception("El jugador no tiene Pokémon para batallar")



        self.es_entrenador = es_entrenador
        self.entrenador_nombre = entrenador_nombre

        self.equipo_entrenador = equipo_entrenador if equipo_entrenador else []
        self.indice_pokemon_entrenador = 0

        # Si es entrenador, el primer enemigo es el primer Pokémon de su equipo
        if es_entrenador and self.equipo_entrenador:
            self.enemigo = self.equipo_entrenador[0]
            print(f"👥 Entrenador {entrenador_nombre} tiene {len(self.equipo_entrenador)} Pokémon")



        if es_entrenador:
            self.nuevo_mensaje(f"¡{entrenador_nombre} quiere combatir!")
            self.intro_terminada = True
            self.fase = "MENSAJE"
            self.alpha_fondo = 255
            self.pos_x_base_rival = self.target_x_rival
            self.pos_x_base_jugador = self.target_x_jugador
        else:
            self.nuevo_mensaje(f"¡Un {enemigo.nombre.upper()} salvaje apareció!")
            # Para batallas salvajes, la intro se maneja en actualizar_intro
            self.intro_terminada = False

        self.resultado_batalla = None
        if self.jugador.hp_actual <= 0:
            self.resultado_batalla = "perdio"

        # Cuando el enemigo se debilita
        if self.enemigo.hp_actual <= 0:
            self.resultado_batalla = "gano"

        try:
            self.imagen_menu_batalla = pygame.image.load("asets/imagenes/INTERFAZ/menu_batalla.png").convert_alpha()
            # Escalar al tamaño del cuadro de menú (760x100 como en tu código)
            self.imagen_menu_batalla = pygame.transform.scale(self.imagen_menu_batalla, (798, 148))
            print("✅ Imagen de menú de batalla cargada")
        except Exception as e:
            print(f"⚠️ No se pudo cargar imagen de menú: {e}")
            self.imagen_menu_batalla = None

        try:
            self.imagen_menu_equipo = pygame.image.load("asets/imagenes/INTERFAZ/menu_equipo.png").convert_alpha()
            # Escalar al tamaño del cuadro de menú (760x100 no es suficiente, necesitamos algo más grande)
            # El menú de equipo ocupará casi toda la pantalla
            self.imagen_menu_equipo = pygame.transform.scale(self.imagen_menu_equipo, (760, 400))
            print("✅ Imagen de menú de equipo cargada")
        except Exception as e:
            print(f"⚠️ No se pudo cargar imagen de menú de equipo: {e}")
            self.imagen_menu_equipo = None

        self.fuente_pequeña = pygame.font.Font("asets/FuenteDeTexto/pokemon.otf", 20)

        try:
            self.imagen_slot_pokemon = pygame.image.load("asets/imagenes/INTERFAZ/slot_pokemon.png").convert_alpha()
            # Escalar al tamaño del slot (ajusta según necesites)
            self.imagen_slot_pokemon = pygame.transform.scale(self.imagen_slot_pokemon, (230, 90))
            print("✅ Imagen de slot de Pokémon cargada")
        except Exception as e:
            print(f"⚠️ No se pudo cargar imagen de slot: {e}")
            self.imagen_slot_pokemon = None

        self.es_entrenador = es_entrenador



        # 🟢 VARIABLES SEPARADAS PARA CADA TIPO
        if es_entrenador:
            self.enemigo_entrenador = enemigo  # Pokémon actual del entrenador
            self.enemigo_salvaje = None
            self.equipo_entrenador = equipo_entrenador if equipo_entrenador else []
            self.indice_pokemon_entrenador = 0
            self.enemigo = self.enemigo_entrenador  # Para compatibilidad con código existente
            print(f"👥 Batalla de ENTRENADOR - Primer Pokémon: {self.enemigo.nombre}")
        else:
            self.enemigo_salvaje = enemigo  # Pokémon salvaje
            self.enemigo_entrenador = None
            self.equipo_entrenador = []
            self.enemigo = self.enemigo_salvaje  # Para compatibilidad
            print(f"🌿 Batalla SALVAJE - Pokémon: {self.enemigo.nombre}")

        self.mostrando_equipo = False
        self.indice_equipo = 0

        # 🟢 VARIABLES PARA LA BOLSA
        self.mostrando_bolsa = False
        self.indice_bolsa = 0
        self.items_bolsa = ["POKEBOLA", "POCION", "ANTIDOTO", "SALIR"]

        # En SistemaBatalla.__init__, agrega:

        self.tabla_tipos = {
            "normal": {"roca": 0.5, "fantasma": 0, "acero": 0.5},
            "fuego": {"planta": 2, "hielo": 2, "bicho": 2, "acero": 2, "fuego": 0.5, "agua": 0.5, "roca": 0.5,
                      "dragon": 0.5},
            "agua": {"fuego": 2, "tierra": 2, "roca": 2, "agua": 0.5, "planta": 0.5, "dragon": 0.5},
            "planta": {"agua": 2, "tierra": 2, "roca": 2, "fuego": 0.5, "planta": 0.5, "veneno": 0.5, "volador": 0.5,
                       "bicho": 0.5, "dragon": 0.5},
            "electrico": {"agua": 2, "volador": 2, "electrico": 0.5, "planta": 0.5, "dragon": 0.5, "tierra": 0},
            "hielo": {"planta": 2, "tierra": 2, "volador": 2, "dragon": 2, "fuego": 0.5, "agua": 0.5, "hielo": 0.5,
                      "acero": 0.5},
            "lucha": {"normal": 2, "hielo": 2, "roca": 2, "siniestro": 2, "acero": 2, "veneno": 0.5, "volador": 0.5,
                      "psiquico": 0.5, "bicho": 0.5, "fantasma": 0},
            "veneno": {"planta": 2, "veneno": 0.5, "tierra": 0.5, "roca": 0.5, "fantasma": 0.5, "acero": 0},
            "tierra": {"fuego": 2, "electrico": 2, "veneno": 2, "roca": 2, "acero": 2, "planta": 0.5, "bicho": 0.5,
                       "volador": 0},
            "volador": {"planta": 2, "lucha": 2, "bicho": 2, "electrico": 0.5, "roca": 0.5, "acero": 0.5},
            "psiquico": {"lucha": 2, "veneno": 2, "psiquico": 0.5, "acero": 0.5, "siniestro": 0},
            "bicho": {"planta": 2, "psiquico": 2, "siniestro": 2, "fuego": 0.5, "lucha": 0.5, "veneno": 0.5,
                      "fantasma": 0.5, "acero": 0.5},
            "roca": {"fuego": 2, "hielo": 2, "volador": 2, "bicho": 2, "lucha": 0.5, "tierra": 0.5, "acero": 0.5},
            "fantasma": {"psiquico": 2, "fantasma": 2, "siniestro": 0.5, "normal": 0},
            "dragon": {"dragon": 2, "acero": 0.5},
            "siniestro": {"psiquico": 2, "fantasma": 2, "lucha": 0.5, "siniestro": 0.5, "hada": 0.5},
            "acero": {"hielo": 2, "roca": 2, "hada": 2, "fuego": 0.5, "agua": 0.5, "electrico": 0.5, "acero": 0.5}
        }

        self.datos_ataques = {
            # Ataques de tipo normal
            "PLACAJE": {"daño": 40, "tipo": "normal", "precision": 100, "categoria": "fisico",
                        "desc": "Embestida básica"},
            "ARAÑAZO": {"daño": 40, "tipo": "normal", "precision": 100, "categoria": "fisico",
                        "desc": "Arañazo afilado"},
            "GOLPE": {"daño": 50, "tipo": "normal", "precision": 100, "categoria": "fisico",
                      "desc": "Golpe contundente"},
            "PATADA": {"daño": 50, "tipo": "lucha", "precision": 100, "categoria": "fisico", "desc": "Patada poderosa"},

            # Ataques de tipo fuego
            "ASCUAS": {"daño": 40, "tipo": "fuego", "precision": 100, "categoria": "especial",
                       "desc": "Pequeñas llamas"},
            "LANZA LLAMAS": {"daño": 90, "tipo": "fuego", "precision": 100, "categoria": "especial",
                             "desc": "Llamarada intensa"},

            # Ataques de tipo agua
            "PISTOLA AGUA": {"daño": 40, "tipo": "agua", "precision": 100, "categoria": "especial",
                             "desc": "Disparo de agua"},
            "HIDROBOMBA": {"daño": 110, "tipo": "agua", "precision": 80, "categoria": "especial",
                           "desc": "Cañón de agua"},

            # Ataques de tipo planta
            "LÁTIGO CEPA": {"daño": 45, "tipo": "planta", "precision": 100, "categoria": "fisico",
                            "desc": "Látigo de cepa"},
            "ABSORBER": {"daño": 20, "tipo": "planta", "precision": 100, "categoria": "especial",
                         "desc": "Absorbe vida", "cura": 0.5},
            "HOJA AFILADA": {"daño": 55, "tipo": "planta", "precision": 95, "categoria": "fisico",
                             "desc": "Hojas cortantes"},

            # Ataques de tipo eléctrico
            "IMPACTRUENO": {"daño": 40, "tipo": "electrico", "precision": 100, "categoria": "especial",
                            "desc": "Descarga eléctrica"},
            "CHISPA": {"daño": 65, "tipo": "electrico", "precision": 100, "categoria": "especial", "desc": "Chispazo"},
            "RAYO": {"daño": 90, "tipo": "electrico", "precision": 100, "categoria": "especial",
                     "desc": "Rayo poderoso"},

            # Ataques de tipo tierra
            "TERREMOTO": {"daño": 100, "tipo": "tierra", "precision": 100, "categoria": "fisico",
                          "desc": "Sacudida sísmica"},
            "DISPARO LIMO": {"daño": 55, "tipo": "tierra", "precision": 95, "categoria": "especial",
                             "desc": "Bola de lodo"},

            # Ataques de tipo roca
            "LANZARROCAS": {"daño": 50, "tipo": "roca", "precision": 90, "categoria": "fisico",
                            "desc": "Lanza piedras"},
            "ROCA AFILADA": {"daño": 75, "tipo": "roca", "precision": 95, "categoria": "fisico",
                             "desc": "Rocas puntiagudas"},

            # Ataques de tipo lucha
            "GOLPE KARMA": {"daño": 50, "tipo": "lucha", "precision": 100, "categoria": "fisico",
                            "desc": "Golpe de artes marciales"},
            "PATADA SALTO": {"daño": 70, "tipo": "lucha", "precision": 95, "categoria": "fisico",
                             "desc": "Patada voladora"},

            # Ataques de tipo volador
            "ATAQUE ALA": {"daño": 60, "tipo": "volador", "precision": 100, "categoria": "fisico",
                           "desc": "Ataque alado"},

            # Ataques de tipo veneno
            "ÁCIDO": {"daño": 40, "tipo": "veneno", "precision": 100, "categoria": "especial",
                      "desc": "Ácido corrosivo"},

            # Ataques de tipo bicho
            "DISP. DEMORA": {"daño": 20, "tipo": "bicho", "precision": 100, "categoria": "especial",
                             "desc": "Disparo demorado"},
            "SONICBOOM": {"daño": 40, "tipo": "bicho", "precision": 90, "categoria": "especial", "desc": "Onda sónica"},

            # Ataques de tipo dragón
            "DRAGON COLUMNA": {"daño": 150, "tipo": "dragon", "precision": 90, "categoria": "especial",
                               "desc": "Poder dragón"},

            # Ataques de tipo psíquico
            "CONFUSIÓN": {"daño": 50, "tipo": "psiquico", "precision": 100, "categoria": "especial",
                          "desc": "Poder mental"},

            # Ataques de tipo fantasma
            "LENGÜETAZO": {"daño": 30, "tipo": "fantasma", "precision": 100, "categoria": "fisico",
                           "desc": "Lengüetazo fantasmal"},

            # Ataques de tipo hielo
            "POLVO NIEVE": {"daño": 40, "tipo": "hielo", "precision": 100, "categoria": "especial",
                            "desc": "Nieve helada"},

            # Ataques de tipo acero
            "CAÑÓN": {"daño": 50, "tipo": "acero", "precision": 100, "categoria": "especial",
                      "desc": "Disparo metálico"},

            # Ataques de estado
            "GRUÑIDO": {"daño": 0, "tipo": "normal", "precision": 100, "categoria": "estado", "desc": "Baja el ataque",
                        "efecto": "bajar_ataque"},
            "MALICIOSO": {"daño": 0, "tipo": "normal", "precision": 100, "categoria": "estado",
                          "desc": "Baja la defensa", "efecto": "bajar_defensa"},
            "DANZA ESPADA": {"daño": 0, "tipo": "normal", "precision": 100, "categoria": "estado",
                             "desc": "Sube el ataque", "efecto": "subir_ataque"},
            "DEFENSA FÉRREA": {"daño": 0, "tipo": "acero", "precision": 100, "categoria": "estado",
                               "desc": "Sube la defensa", "efecto": "subir_defensa"},
        }

        self.animando_vida = False
        self.vida_anterior = 0
        self.vida_destino = 0
        self.vida_actual_anim = 0
        self.velocidad_animacion_vida = 0.3  # Píxeles por frame
        self.pokemon_animando = None  # "jugador" o "enemigo"

        try:
            self.sonido_lanzar_pokebola = pygame.mixer.Sound("asets/music/lanzar_pokebola.mp3")
            self.sonido_lanzar_pokebola.set_volume(1)

            self.sonido_golpe_pokebola = pygame.mixer.Sound("asets/music/golpe_pokebola.mp3")
            self.sonido_golpe_pokebola.set_volume(1)

            self.sonido_vibracion = pygame.mixer.Sound("asets/music/vibracion_pokebola.mp3")
            self.sonido_vibracion.set_volume(1)

            self.sonido_captura_exitosa = pygame.mixer.Sound("asets/music/captura_exitosa.mp3")
            self.sonido_captura_exitosa.set_volume(1)

            self.sonido_captura_fallida = pygame.mixer.Sound("asets/music/captura_fallida.mp3")
            self.sonido_captura_fallida.set_volume(1)

            print("✅ Sonidos de captura cargados")
        except Exception as e:
            print(f"⚠️ No se pudieron cargar sonidos de captura: {e}")
            self.sonido_lanzar_pokebola = None
            self.sonido_golpe_pokebola = None
            self.sonido_vibracion = None
            self.sonido_captura_exitosa = None
            self.sonido_captura_fallida = None

        self.inventario = jugador.inventario if hasattr(jugador, 'inventario') else {
            "pokebola": 0,
            "pocion": 0,
            "antidoto": 0
        }

        # 🟢 Generar items de bolsa dinámicamente
        self.items_bolsa = self._generar_items_bolsa()

    def _generar_items_bolsa(self):
        """Genera la lista de items basada en el inventario real"""
        items = []

        # Solo mostrar items que el jugador tiene (o al menos mostrar con cantidad)
        if self.inventario.get("pokebola", 0) > 0:
            items.append(f"POKEBOLA x{self.inventario['pokebola']}")
        else:
            items.append("POKEBOLA (0)")

        if self.inventario.get("pocion", 0) > 0:
            items.append(f"POCION x{self.inventario['pocion']}")
        else:
            items.append("POCION (0)")

        if self.inventario.get("antidoto", 0) > 0:
            items.append(f"ANTIDOTO x{self.inventario['antidoto']}")
        else:
            items.append("ANTIDOTO (0)")

        items.append("SALIR")

        return items








    def actualizar_intro(self):
        """Maneja el movimiento de las bases y el fade del fondo"""
        # Si ya está terminada, no hacer nada
        if self.intro_terminada:
            return

        # 1. Aparecer fondo
        if self.alpha_fondo < 255:
            self.alpha_fondo += 5
            self.fondo_img.set_alpha(self.alpha_fondo)

        # 2. Deslizar base rival
        if self.pos_x_base_rival > self.target_x_rival:
            self.pos_x_base_rival -= self.velocidad_deslize

        # 3. Deslizar base jugador
        if self.pos_x_base_jugador < self.target_x_jugador:
            self.pos_x_base_jugador += self.velocidad_deslize

        # 4. Verificar si ya terminó
        if (self.pos_x_base_rival <= self.target_x_rival and
                self.pos_x_base_jugador >= self.target_x_jugador and
                self.alpha_fondo >= 255):
            self.intro_terminada = True
            self.fase = "MENSAJE"
            print("✅ Intro de batalla terminada")

    def dibujar(self, ventana):
        # 1. Actualizar Lógicas de Animación
        self.actualizar_intro()
        self.actualizar_texto_animado()  # Nueva función para las letras
        self.actualizar_animacion_vida()  # 🟢 NUEVO

        if self.escapando:
            self.offset_x_huida -= 20

        # 2. Fondo
        ventana.fill((0, 0, 0))
        self.fondo_img.set_alpha(self.alpha_fondo)
        ventana.blit(self.fondo_img, (0, self.y_fondo))

        # 3. Bases
        y_base_rival = self.y_fondo + 70
        y_base_mio = self.y_fondo + 385



        ventana.blit(self.base_rival, (self.pos_x_base_rival, y_base_rival))
        ventana.blit(self.base_jugador, (self.pos_x_base_jugador, y_base_mio))

        # 4. Lógica de Tiempo y Frames
        tiempo_actual = pygame.time.get_ticks()
        frame_actual = (tiempo_actual // 500) % 2
        dibujar_rival = True
        dibujar_mio = True
        offset_mio = [0, 0]

        # --- Lógica de Daño/Ataque (se mantiene igual) ---
        if self.animando_ataque:
            t = tiempo_actual - self.timer_animacion
            if t < 200:
                offset_mio = [30, -10]
            elif t < 400:
                offset_mio = [0, 0]
            if t < 800 and (t // 100) % 2 == 0:
                dibujar_rival = False
            else:
                self.animando_ataque = False

        if getattr(self, 'animando_daño_mio', False):
            t_daño = tiempo_actual - self.timer_daño_mio
            if t_daño < 800 and (t_daño // 100) % 2 == 0:
                dibujar_mio = False
            else:
                self.animando_daño_mio = False

        # 5. Dibujar Pokémon Rival
        if dibujar_rival and self.pokemon_visible:
            img_actual = self.frames_rival[frame_actual]
            rect_rival = img_actual.get_rect()
            rect_rival.centerx = self.pos_x_base_rival + 170
            rect_rival.bottom = y_base_rival + 140
            ventana.blit(img_actual, rect_rival)

            # 🆕 Animación de captura con vibración MÁS LENTA
        if self.capturando:
            tiempo_actual = pygame.time.get_ticks()

            if self.animacion_captura == 1:  # Lanzando pokebola (trayectoria parabólica)
                progreso = (tiempo_actual - self.timer_captura) / 800  # 0.8 segundos

                if progreso < 1:
                    x_inicio = self.pos_x_base_jugador + 185
                    y_inicio = y_base_mio + 50
                    x_fin = self.pos_x_base_rival + 170
                    y_fin = y_base_rival + 100

                    # Punto medio para la parábola (más alto)
                    x_medio = (x_inicio + x_fin) / 2
                    y_medio = min(y_inicio, y_fin) - 80

                    # Parábola
                    t = progreso
                    x = (1 - t) ** 2 * x_inicio + 2 * (1 - t) * t * x_medio + t ** 2 * x_fin
                    y = (1 - t) ** 2 * y_inicio + 2 * (1 - t) * t * y_medio + t ** 2 * y_fin

                    if self.img_pokebola_captura:
                        ventana.blit(self.img_pokebola_captura, (x, y))
                else:
                    # La pokebola llegó al Pokémon - Pokémon desaparece
                    self.animacion_captura = 2
                    self.timer_captura = tiempo_actual
                    self.pokemon_visible = False
                    self.parpadeos_captura = 0
                    self.angulo_pokebola = 0
                    self.direccion_rotacion = 1



            elif self.animacion_captura == 2:  # Pokémon desapareció - pokebola vibra
                # Posición de la pokebola (donde estaba el Pokémon)
                x_pokebola = self.pos_x_base_rival + 170 - 20
                y_pokebola = y_base_rival + 100 - 20

                # Calcular tiempo para la vibración
                tiempo_transcurrido = tiempo_actual - self.timer_captura

                # 🎵 CONTROL DE SONIDO DE VIBRACIÓN
                if hasattr(self, 'ultima_vibracion_sonido'):
                    vibracion_actual_sonido = tiempo_transcurrido // 1200  # Cada 1.2 segundos
                    if vibracion_actual_sonido != self.ultima_vibracion_sonido:
                        if self.sonido_vibracion:
                            self.sonido_vibracion.stop()
                            self.sonido_vibracion.play()
                        self.ultima_vibracion_sonido = vibracion_actual_sonido
                else:
                    self.ultima_vibracion_sonido = -1

                # 🐌 VIBRACIÓN CON PAUSA
                duracion_movimiento = 500  # 0.6 segundos de movimiento
                duracion_pausa = 600  # 0.4 segundos de pausa
                duracion_total_ciclo =duracion_movimiento + duracion_pausa # 1.6 segundos por ciclo completo

                # Determinar en qué ciclo estamos (0, 1, 2, 3)
                ciclo_actual = tiempo_transcurrido // duracion_total_ciclo

                if ciclo_actual < 3:  # Máximo 4 ciclos
                    # Tiempo dentro del ciclo actual
                    tiempo_en_ciclo = tiempo_transcurrido % duracion_total_ciclo

                    # Determinar si estamos en movimiento o en pausa
                    if tiempo_en_ciclo < duracion_movimiento:
                        # 🟢 ESTAMOS EN MOVIMIENTO
                        progreso_movimiento = tiempo_en_ciclo / duracion_movimiento

                        # Ángulo máximo de 80 grados
                        angulo_maximo = 80

                        # Movimiento: va de 0 a 80 y vuelve a 0
                        if progreso_movimiento < 0.5:
                            # Primer medio ciclo: va de 0 a ángulo_maximo
                            angulo = angulo_maximo * (progreso_movimiento * 2)
                        else:
                            # Segundo medio ciclo: vuelve de ángulo_maximo a 0
                            angulo = angulo_maximo * (1 - (progreso_movimiento - 0.5) * 2)

                        # Alternar dirección en cada ciclo
                        if ciclo_actual % 2 == 0:
                            angulo = angulo  # Vibración hacia la derecha
                        else:
                            angulo = -angulo  # Vibración hacia la izquierda

                        # Dibujar pokebola rotada
                        if self.img_pokebola_captura:
                            pokebola_rotada = pygame.transform.rotate(self.img_pokebola_captura, angulo)
                            rect = pokebola_rotada.get_rect(center=(x_pokebola + 20, y_pokebola + 20))
                            ventana.blit(pokebola_rotada, rect)

                    else:
                        # 🟢 ESTAMOS EN PAUSA - pokebola quieta en posición normal
                        if self.img_pokebola_captura:
                            rect = self.img_pokebola_captura.get_rect(center=(x_pokebola + 20, y_pokebola + 20))
                            ventana.blit(self.img_pokebola_captura, rect)

                    self.parpadeos_captura = ciclo_actual

                else:
                    if self.captura_exitosa:
                        if self.sonido_captura_exitosa:
                            self.sonido_captura_exitosa.play()

                        # 🟢 CAMBIO: Guardamos la posición final de la pokebola
                        self.pos_pokebola_final = (self.pos_x_base_rival + 170 - 20, y_base_rival + 100 - 20)
                        self.mostrar_pokebola_captura = True  # Nueva variable para mantener la pokebola visible

                        self.procesar_captura_exitosa()
                        self.nuevo_mensaje(f"¡Has capturado a {self.enemigo.nombre.upper()}!")

                        self.capturando = False  # Terminamos la animación pero mantenemos la pokebola
                        self.pokemon_visible = False
                        self.fase = "MENSAJE"
                        self.turno = "captura_exitosa"




                    else:
                        if self.sonido_captura_fallida:
                            self.sonido_captura_fallida.play()
                        self.nuevo_mensaje("¡Oh no! El Pokémon escapó")
                        self.pokemon_visible = True
                        self.capturando = False
                        self.turno = "espera_enemigo"

            # 6. Dibujar Mi Pokémon
        if dibujar_mio:
            img_mio_actual = self.frames_mio[frame_actual]
            rect_mio = img_mio_actual.get_rect()
            # Añadimos self.offset_x_huida a la posición X
            rect_mio.centerx = self.pos_x_base_jugador + 185 + offset_mio[0] + self.offset_x_huida
            rect_mio.bottom = y_base_mio + 68 + offset_mio[1]
            ventana.blit(img_mio_actual, rect_mio)

        # 7. Interfaz (HUD y Cuadro de Texto)
        if self.intro_terminada:
            self.dibujar_hud(ventana)

            y_cuadro = 452

            # Usar imagen de fondo si existe
            if self.imagen_menu_batalla:
                ventana.blit(self.imagen_menu_batalla, (0, y_cuadro))
            else:
                # Fallback: fondo blanco
                pygame.draw.rect(ventana, (255, 255, 255), (20, y_cuadro, 760, 100))
                pygame.draw.rect(ventana, (0, 0, 0), (20, y_cuadro, 760, 100), 4)

            if self.fase == "MENU":
                posiciones = [(120, y_cuadro + 20), (450, y_cuadro + 20),
                              (120, y_cuadro + 90), (450, y_cuadro + 90)]
                for i, opcion in enumerate(self.opciones):
                    color = (200, 0, 0) if i == self.indice_seleccionado else (0, 0, 0)
                    if i == self.indice_seleccionado:
                        ventana.blit(self.fuente.render(">", True, color), (posiciones[i][0] - 25, posiciones[i][1]))
                    ventana.blit(self.fuente.render(opcion, True, color), posiciones[i])

            elif self.fase == "MENU_ATAQUES":
                posiciones = [(70, y_cuadro + 20), (350, y_cuadro + 20),
                              (70, y_cuadro + 60), (350, y_cuadro + 60)]
                for i, ataque in enumerate(self.ataques):
                    color = (0, 0, 200) if i == self.indice_ataque else (0, 0, 0)
                    if i == self.indice_ataque:
                        ventana.blit(self.fuente.render(">", True, color), (posiciones[i][0] - 25, posiciones[i][1]))
                    ventana.blit(self.fuente.render(ataque, True, color), posiciones[i])


            elif self.fase == "MENU_EQUIPO":
                y_cuadro = 470

                # 🟢 FONDO DEL MENÚ DE EQUIPO
                if self.imagen_menu_equipo:
                    # El menú de equipo es más grande, lo posicionamos más arriba
                    y_menu_equipo = 28
                    ventana.blit(self.imagen_menu_equipo, (25, y_menu_equipo))
                else:
                    # Fallback: fondo blanco más grande
                    pygame.draw.rect(ventana, (255, 255, 255), (20, 100, 760, 400))
                    pygame.draw.rect(ventana, (0, 0, 0), (20, 100, 760, 400), 4)

                # Configuración de la cuadrícula 3x2
                equipo = self.jugador.equipo
                activo = self.jugador.pokemon_activo

                # Posiciones de los 6 slots (3 columnas x 2 filas)
                # [ (x, y) para cada slot ]
                posiciones_slots = [
                    (40, 130),  # Slot 0 (fila 0, columna 0) - Pokémon activo normalmente
                    (290, 130),  # Slot 1 (fila 0, columna 1)
                    (540, 130),  # Slot 2 (fila 0, columna 2)
                    (40, 250),  # Slot 3 (fila 1, columna 0)
                    (290, 250),  # Slot 4 (fila 1, columna 1)
                    (540, 250),  # Slot 5 (fila 1, columna 2)
                ]

                ancho_slot = 230
                alto_slot = 90

                for i in range(6):  # Siempre 6 slots, aunque estén vacíos
                    x, y = posiciones_slots[i]

                    if self.imagen_slot_pokemon:
                        ventana.blit(self.imagen_slot_pokemon, (x, y))
                    else:
                        # Fallback: rectángulo gris
                        pygame.draw.rect(ventana, (100, 100, 100), (x, y, ancho_slot, alto_slot))
                        pygame.draw.rect(ventana, (50, 50, 50), (x, y, ancho_slot, alto_slot), 2)

                        # Si hay un Pokémon en este slot
                    if i < len(equipo):
                        pokemon = equipo[i]

                        if i == self.jugador.pokemon_activo:
                            # Es el Pokémon activo - usar la vida del jugador (que está en batalla)
                            vida_mostrar = self.jugador.hp_actual
                            print(
                                f"🔴 Pokémon ACTIVO ({pokemon.nombre}): usando vida del jugador = {vida_mostrar}/{pokemon.hp_max}")
                        else:
                            # Es otro Pokémon del equipo - usar su vida guardada
                            vida_mostrar = pokemon.hp_actual
                            print(
                                f"🔵 Pokémon en RESERVA ({pokemon.nombre}): usando vida guardada = {vida_mostrar}/{pokemon.hp_max}")




                        # 🟢 MARCADOR DE SELECCIÓN
                        if i == self.indice_equipo:
                            # Recuadro amarillo para el seleccionado
                            pygame.draw.rect(ventana, (255, 255, 0), (x, y, ancho_slot, alto_slot), 4)
                        elif i == activo:
                            # Recuadro verde para el Pokémon activo
                            pygame.draw.rect(ventana, (0, 255, 0), (x, y, ancho_slot, alto_slot), 4)


                        # 🟢 NOMBRE DEL POKÉMON
                        nombre_color = (0, 0, 0)


                        nombre_texto = self.fuente.render(pokemon.nombre, True, nombre_color)
                        ventana.blit(nombre_texto, (x + 10, y))

                        # 🟢 NIVEL
                        nivel_texto = self.fuente_pequeña.render(f"Nv. {pokemon.nivel}", True, (0, 0, 0))
                        ventana.blit(nivel_texto, (x + 10, y + 30))

                        # 🟢 BARRA DE VIDA
                        ancho_barra = 142
                        alto_barra = 6
                        x_barra = x + 71  # Posición X de la barra
                        y_barra = y + 61  # Posición Y de la barra

                        # 🟢 CALCULAR PORCENTAJE CON LA VIDA ACTUAL DEL POKÉMON
                        porcentaje =vida_mostrar  / pokemon.hp_max

                        # DEBUG: Imprimir para verificar
                        if i == 0:  # Solo el primer Pokémon para no saturar
                            print(
                                f"📊 Menú equipo - {pokemon.nombre}: HP {pokemon.hp_actual}/{pokemon.hp_max} = {porcentaje:.2%}")



                        # Color según la vida
                        if porcentaje > 0.5:
                            color_vida = (0, 255, 0)  # Verde
                        elif porcentaje > 0.2:
                            color_vida = (255, 255, 0)  # Amarillo
                        else:
                            color_vida = (255, 0, 0)  # Rojo

                        # Barra de vida actual
                        ancho_vida = int(ancho_barra * porcentaje)
                        if ancho_vida > 0:
                            pygame.draw.rect(ventana, color_vida, (x + 71 , y + 61, ancho_vida, alto_barra))

            elif self.fase == "MENU_BOLSA":
                y_cuadro = 452
                if self.imagen_menu_batalla:
                    ventana.blit(self.imagen_menu_batalla, (0, y_cuadro))
                else:
                    pygame.draw.rect(ventana, (255, 255, 255), (20, y_cuadro, 760, 100))
                    pygame.draw.rect(ventana, (0, 0, 0), (20, y_cuadro, 760, 100), 4)

                posiciones = [(70, y_cuadro + 20), (350, y_cuadro + 20),
                              (70, y_cuadro + 60), (350, y_cuadro + 60)]

                for i, item_texto in enumerate(self.items_bolsa):
                    # Determinar color
                    if i == self.indice_bolsa:
                        color = (0, 150, 0)
                        # Flecha de selección
                        ventana.blit(self.fuente.render(">", True, color),
                                     (posiciones[i][0] - 25, posiciones[i][1]))
                    else:
                        color = (0, 0, 0)

                    # Si el item tiene (0), ponerlo gris
                    if "(0)" in item_texto:
                        color = (100, 100, 100)

                    ventana.blit(self.fuente.render(item_texto, True, color), posiciones[i])





            else:
                # CAMBIO FINAL: Renderizamos el mensaje animado
                txt_mensaje = self.fuente.render(self.mensaje_visible, True, (0, 0, 0))
                ventana.blit(txt_mensaje, (40, y_cuadro + 35))

    def dibujar_hud(self, ventana):
        COLOR_TX = (0, 0, 0)  # Negro
        COLOR_MACHO = (0, 100, 255)  # Azul
        COLOR_HEMBRA = (255, 50, 150)  # Rosa

        # --- 1. HUD RIVAL ---
        x_r, y_r = 540, 10  # Posición base rival
        ventana.blit(self.hud_rival, (x_r, y_r))

        # Nombre Rival
        nombre_rival = str(self.enemigo.nombre).upper()  # Forzamos a que use el nombre del objeto
        txt_nom_r = self.fuente_hud.render(nombre_rival, True, COLOR_TX)
        ventana.blit(txt_nom_r, (x_r + 30, y_r + 7))

        # --- AGREGADO: SEXO RIVAL ---
        sexo_r = getattr(self.enemigo, 'sexo', "M")
        simbolo_r = "♂" if sexo_r == "M" else "♀"
        col_s_r = COLOR_MACHO if sexo_r == "M" else COLOR_HEMBRA
        txt_sexo_r = self.fuente_hud.render(simbolo_r, True, col_s_r)
        # Se posiciona después del nombre (ajusta el +120 si el nombre es largo)
        ventana.blit(txt_sexo_r, (x_r + 175, y_r + 7))

        # Nivel Rival
        lvl_r = getattr(self.enemigo, 'nivel', 5)
        txt_lvl_r = self.fuente_hud.render(f"{lvl_r}", True, COLOR_TX)
        ventana.blit(txt_lvl_r, (x_r + 215, y_r + 7))

        # --- Barra Rival (Fondo Negro + Vida) ---
        ancho_max_r = 100
        # 1. Primero dibujamos el fondo negro (siempre mide 100px)
        pygame.draw.rect(ventana, (35, 35, 35), (x_r + 146, y_r + 35, ancho_max_r, 6))

        if self.animando_vida and self.pokemon_animando == "enemigo":
            vida_mostrar = self.vida_actual_anim
        else:
            vida_mostrar = self.enemigo.hp_actual

        # 2. Luego calculamos el color y la vida actual
        porcentaje_r = (vida_mostrar/ self.enemigo.hp_max)
        hp_r = porcentaje_r * ancho_max_r

        color_r = (0, 255, 0)  # Verde
        if porcentaje_r < 0.2:
            color_r = (255, 0, 0)
        elif porcentaje_r < 0.5:
            color_r = (255, 255, 0)

        # 3. Dibujamos la barra de vida sobre el negro
        pygame.draw.rect(ventana, color_r, (x_r + 146, y_r + 35, hp_r, 6))

        hp_texto_r = f"{int( self.enemigo.hp_actual)}               {int(self.enemigo.hp_max)}"
        # USAMOS LA FUENTE PEQUEÑA AQUÍ:
        txt_hp_r = self.fuente_hp_pequeña.render(hp_texto_r, True, COLOR_TX)
        ventana.blit(txt_hp_r, (x_r + 150, y_r + 47))

        # --- 2. HUD MÍO ---
        x_m, y_m = 0, 230  # Posición base tuya
        ventana.blit(self.hud_mio, (x_m, y_m))

        # Nombre Jugador
        nombre_j = getattr(self.jugador, 'nombre', "???").upper()
        txt_nom_m = self.fuente_hud.render(nombre_j, True, COLOR_TX)
        ventana.blit(txt_nom_m, (x_m + 15, y_m + 12))

        # --- AGREGADO: SEXO JUGADOR ---
        sexo_j = getattr(self.jugador, 'sexo', "M")
        simbolo_j = "♂" if sexo_j == "M" else "♀"
        col_s_j = COLOR_MACHO if sexo_j == "M" else COLOR_HEMBRA
        txt_sexo_j = self.fuente_hud.render(simbolo_j, True, col_s_j)
        # Se posiciona después del nombre
        ventana.blit(txt_sexo_j, (x_m + 140, y_m + 15))

        # Nivel Jugador
        lvl_j = getattr(self.jugador, 'nivel', 5)
        txt_lvl_m = self.fuente_hud.render(f"{lvl_j}", True, COLOR_TX)
        ventana.blit(txt_lvl_m, (x_m + 180, y_m + 18))

        # --- Barra Mía (Fondo Negro + Vida) ---
        ancho_max_m = 102
        # 1. Primero el fondo negro
        pygame.draw.rect(ventana, (35, 35, 35), (x_m + 107, y_m + 54, ancho_max_m, 8))

        if self.animando_vida and self.pokemon_animando == "jugador":
            vida_mostrar_m = self.vida_actual_anim
        else:
            vida_mostrar_m = self.jugador.hp_actual

        # 2. Calculamos color y vida
        porcentaje_m = vida_mostrar_m / self.jugador.hp_max
        hp_m = porcentaje_m * ancho_max_m

        color_m = (0, 255, 0)  # Verde
        if porcentaje_m < 0.2:
            color_m = (255, 0, 0)
        elif porcentaje_m < 0.5:
            color_m = (255, 255, 0)

        # 3. Dibujamos la vida sobre el negro
        pygame.draw.rect(ventana, color_m, (x_m + 107, y_m + 54, hp_m, 8))

    def actualizar_texto_animado(self):
        # Solo animamos si el mensaje visible es más corto que el completo
        if len(self.mensaje_visible) < len(self.mensaje_completo):
            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - self.timer_texto > self.velocidad_texto:
                self.mensaje_visible = self.mensaje_completo[:self.indice_letra + 1]
                self.indice_letra += 1
                self.timer_texto = tiempo_actual

    def nuevo_mensaje(self, texto):
        self.mensaje_completo = texto
        self.mensaje_visible = ""
        self.indice_letra = 0
        self.fase = "MENSAJE"

    def manejar_input(self, eventos):
        for evento in eventos:
            if evento.type == pygame.KEYDOWN:

                if self.fase == "MENSAJE":
                    # Lógica para saltar la animación del texto
                    if evento.key == pygame.K_SPACE:
                        if len(self.mensaje_visible) < len(self.mensaje_completo):
                            self.mensaje_visible = self.mensaje_completo
                            self.indice_letra = len(self.mensaje_completo)
                        else:
                            if self.turno == "captura_exitosa":
                                self.batalla_finalizada = True

                            elif self.turno == "ir_al_menu":
                                self.fase = "MENU"
                                self.turno = "jugador"

                            # --- MÁQUINA DE ESTADOS DE TURNOS ---
                            elif self.turno == "ejecutar_golpe_jugador":
                                # 🟢 Usar el método según el tipo de batalla
                                if self.es_entrenador:
                                    self.aplicar_daño_a_entrenador()
                                else:
                                    self.aplicar_daño_a_salvaje()

                            elif self.turno == "espera_enemigo":
                                self.preparar_ataque_enemigo()

                            elif self.turno == "ejecutar_golpe_enemigo":
                                self.aplicar_daño_enemigo_real()

                            elif self.turno == "muerte_enemigo":
                                self.ganar_experiencia()

                            elif self.turno == "subir_nivel_pendiente":
                                self.subir_de_nivel()

                            elif self.turno == "derrota_jugador":
                                self.batalla_finalizada = True

                            elif self.turno == "fin_batalla_pendiente":
                                self.batalla_finalizada = True

                            elif self.turno in ["jugador", "espera_jugador"]:
                                self.fase = "MENU"
                                self.turno = "jugador"
                            else:
                                self.fase = "MENU"
                                self.turno = "jugador"

                # --- 2. MENU PRINCIPAL ---
                elif self.fase == "MENU":
                    tecla_movida = False

                    if evento.key in [pygame.K_LEFT, pygame.K_a]:
                        if self.indice_seleccionado in [1, 3]:
                            self.indice_seleccionado -= 1
                            tecla_movida = True
                    elif evento.key in [pygame.K_RIGHT, pygame.K_d]:
                        if self.indice_seleccionado in [0, 2]:
                            self.indice_seleccionado += 1
                            tecla_movida = True
                    elif evento.key in [pygame.K_UP, pygame.K_w]:
                        if self.indice_seleccionado in [2, 3]:
                            self.indice_seleccionado -= 2
                            tecla_movida = True
                    elif evento.key in [pygame.K_DOWN, pygame.K_s]:
                        if self.indice_seleccionado in [0, 1]:
                            self.indice_seleccionado += 2
                            tecla_movida = True

                    if tecla_movida and self.sonido_seleccionar:
                        self.sonido_seleccionar.play()

                    elif evento.key == pygame.K_SPACE:
                        if self.sonido_seleccionar_es:
                            self.sonido_seleccionar_es.play()
                        self.ejecutar_opcion()

                # --- 3. MENU DE ATAQUES ---
                elif self.fase == "MENU_ATAQUES":
                    tecla_movida = False

                    if evento.key in [pygame.K_LEFT, pygame.K_a]:
                        if self.indice_ataque in [1, 3]:
                            self.indice_ataque -= 1
                            tecla_movida = True
                    elif evento.key in [pygame.K_RIGHT, pygame.K_d]:
                        if self.indice_ataque in [0, 2]:
                            self.indice_ataque += 1
                            tecla_movida = True
                    elif evento.key in [pygame.K_UP, pygame.K_w]:
                        if self.indice_ataque in [2, 3]:
                            self.indice_ataque -= 2
                            tecla_movida = True
                    elif evento.key in [pygame.K_DOWN, pygame.K_s]:
                        if self.indice_ataque in [0, 1]:
                            self.indice_ataque += 2
                            tecla_movida = True

                    if tecla_movida and self.sonido_seleccionar:
                        self.sonido_seleccionar.play()

                    elif evento.key == pygame.K_ESCAPE:
                        self.fase = "MENU"

                    elif evento.key == pygame.K_SPACE:
                        if self.sonido_seleccionar_es:
                            self.sonido_seleccionar_es.play()
                        self.ejecutar_ataque_seleccionado()


                elif self.fase == "MENU_BOLSA":
                    if evento.key == pygame.K_w or evento.key == pygame.K_UP:
                        self.indice_bolsa = (self.indice_bolsa - 1) % len(self.items_bolsa)
                        if self.sonido_seleccionar:
                            self.sonido_seleccionar.play()
                    elif evento.key == pygame.K_s or evento.key == pygame.K_DOWN:
                        self.indice_bolsa = (self.indice_bolsa + 1) % len(self.items_bolsa)
                        if self.sonido_seleccionar:
                            self.sonido_seleccionar.play()
                    elif evento.key == pygame.K_SPACE:
                        if self.sonido_seleccionar_es:
                            self.sonido_seleccionar_es.play()

                        item_texto = self.items_bolsa[self.indice_bolsa]

                        # Extraer el nombre del item (sin la cantidad)
                        if "POKEBOLA" in item_texto:
                            self.usar_pokebola()
                        elif "POCION" in item_texto:
                            self.usar_pocion()
                        elif "ANTIDOTO" in item_texto:
                            self.usar_antidoto()
                        elif item_texto == "SALIR":
                            self.fase = "MENU"
                            self.mostrando_bolsa = False

                    elif evento.key == pygame.K_ESCAPE:
                        self.fase = "MENU"
                        self.mostrando_bolsa = False


                elif self.fase == "MENU_EQUIPO":
                    if evento.key == pygame.K_w or evento.key == pygame.K_UP:
                        # Mover hacia arriba (disminuir en 3 para pasar de fila 1 a fila 0)
                        nuevo_indice = self.indice_equipo - 3
                        if nuevo_indice >= 0:
                            self.indice_equipo = nuevo_indice
                        if self.sonido_seleccionar:
                            self.sonido_seleccionar.play()

                    elif evento.key == pygame.K_s or evento.key == pygame.K_DOWN:
                        # Mover hacia abajo (aumentar en 3 para pasar de fila 0 a fila 1)
                        nuevo_indice = self.indice_equipo + 3
                        if nuevo_indice < len(self.jugador.equipo):
                            self.indice_equipo = nuevo_indice
                        if self.sonido_seleccionar:
                            self.sonido_seleccionar.play()

                    elif evento.key == pygame.K_a or evento.key == pygame.K_LEFT:
                        # Mover a la izquierda
                        if self.indice_equipo > 0:
                            self.indice_equipo -= 1
                        if self.sonido_seleccionar:
                            self.sonido_seleccionar.play()

                    elif evento.key == pygame.K_d or evento.key == pygame.K_RIGHT:
                        # Mover a la derecha
                        if self.indice_equipo < len(self.jugador.equipo) - 1:
                            self.indice_equipo += 1
                        if self.sonido_seleccionar:
                            self.sonido_seleccionar.play()

                    elif evento.key == pygame.K_SPACE:
                        if self.sonido_seleccionar_es:
                            self.sonido_seleccionar_es.play()
                        self.cambiar_pokemon_activo(self.indice_equipo)

                    elif evento.key == pygame.K_ESCAPE:
                        self.fase = "MENU"
                        self.mostrando_equipo = False

    def usar_pocion(self):
        """Usa una poción para curar 20 HP (consume del inventario)"""

        # Verificar si tiene pociones
        if self.inventario.get("pocion", 0) <= 0:
            self.nuevo_mensaje("¡No tienes pociones!")
            self.fase = "MENSAJE"
            self.turno = "jugador"
            return

        # Verificar si necesita curación
        if self.jugador.hp_actual >= self.jugador.hp_max:
            self.nuevo_mensaje("¡La salud ya está al máximo!")
            self.fase = "MENSAJE"
            self.turno = "jugador"
            return

        # Consumir una poción
        self.inventario["pocion"] -= 1

        # Curar 20 HP (sin exceder el máximo)
        curacion = min(20, self.jugador.hp_max - self.jugador.hp_actual)
        self.jugador.hp_actual += curacion

        # También actualizar el Pokémon en el equipo
        if hasattr(self.jugador, 'pokemon_activo') and len(self.jugador.equipo) > 0:
            pokemon_activo = self.jugador.equipo[self.jugador.pokemon_activo]
            pokemon_activo.hp_actual = self.jugador.hp_actual

        self.nuevo_mensaje(
            f"¡{self.jugador.nombre} recuperó {curacion} HP! Pociones restantes: {self.inventario['pocion']}")

        # Actualizar la lista de items
        self.items_bolsa = self._generar_items_bolsa()

        self.fase = "MENSAJE"
        self.turno = "espera_enemigo"

    def usar_antidoto(self):
        """Usa un antídoto para curar envenenamiento (consume del inventario)"""

        # Verificar si tiene antídotos
        if self.inventario.get("antidoto", 0) <= 0:
            self.nuevo_mensaje("¡No tienes antídotos!")
            self.fase = "MENSAJE"
            self.turno = "jugador"
            return

        # Verificar si está envenenado (asumiendo que tienes un sistema de estados)
        if not hasattr(self.jugador, 'estado') or self.jugador.estado != "envenenado":
            self.nuevo_mensaje("¡No está envenenado!")
            self.fase = "MENSAJE"
            self.turno = "jugador"
            return

        # Consumir un antídoto
        self.inventario["antidoto"] -= 1

        # Curar envenenamiento
        self.jugador.estado = None

        self.nuevo_mensaje(
            f"¡El envenenamiento de {self.jugador.nombre} ha sido curado! Antídotos restantes: {self.inventario['antidoto']}")

        # Actualizar la lista de items
        self.items_bolsa = self._generar_items_bolsa()

        self.fase = "MENSAJE"
        self.turno = "espera_enemigo"

    def usar_pokebola(self):
        """Método auxiliar para usar pokebola"""
        if self.inventario.get("pokebola", 0) > 0:
            self.iniciar_captura()
        else:
            self.nuevo_mensaje("¡No tienes pokebolas!")
            self.fase = "MENSAJE"


    def ejecutar_opcion(self):
        opcion = self.opciones[self.indice_seleccionado]
        if opcion == "ATACAR":
            self.fase = "MENU_ATAQUES"
            self.indice_ataque = 0

        elif opcion == "POKEMON":
            print(f"📋 Verificando equipo: {len(self.jugador.equipo)} Pokémon")
            if len(self.jugador.equipo) > 0:
                self.mostrando_equipo = True
                self.fase = "MENU_EQUIPO"
                self.indice_equipo = 0
                print("✅ Mostrando menú de equipo")
            else:
                self.nuevo_mensaje("¡No tienes otros Pokémon!")
                print("❌ Equipo vacío")
        elif opcion == "BOLSA":
            # Mostrar menú de la bolsa (por ahora solo pokebolas)
            self.mostrando_bolsa = True
            self.fase = "MENU_BOLSA"
            self.indice_bolsa = 0
            print("✅ Mostrando menú de bolsa")

        elif opcion == "ESCAPAR":
            if self.es_entrenador:
                # No se puede escapar de entrenadores
                self.nuevo_mensaje("¡No puedes escapar de una batalla de entrenadores!")
                self.fase = "MENSAJE"
                # El turno sigue siendo del jugador después del mensaje
                self.turno = "jugador"
                print("🚫 Intento de escape en batalla de entrenador - DENEGADO")

            else:
                import random
                if random.random() < 0.8:  # 80% de probabilidad de éxito
                    self.nuevo_mensaje("¡Escapaste de la batalla con éxito!")
                    self.turno = "fin_batalla_pendiente"
                    self.escapando = True  # Activamos la animación
                    if self.sonido_huida:
                        self.sonido_huida.play()  # <--- El sonido suena aquí
                        pygame.mixer.music.stop()  # Esto detiene la música de fondo (si usas mixer.music)

                else:
                    self.nuevo_mensaje("¡No pudiste escapar!")
                    self.turno = "espera_enemigo"  # Si fallas, el enemigo te ataca





    def ejecutar_ataque_seleccionado(self):
        """Ejecuta el ataque seleccionado con cálculo de daño real"""
        print(f"🟣 Ejecutando ataque - ataques disponibles: {self.ataques}")
        ataque = self.ataques[self.indice_ataque]

        print(f"🟣 Ataque elegido: {ataque}")

        # Calcular daño
        daño, mensaje = self.calcular_daño(self.jugador, self.enemigo, ataque)

        if daño == 0 and mensaje == "fallo":
            self.nuevo_mensaje(f"¡{self.jugador.nombre} falló!")
            self.turno = "espera_enemigo"
            return

        self.daño_proximo_golpe = daño
        self.mensaje_efectividad = mensaje

        # Mostrar mensaje del ataque
        if mensaje:
            self.nuevo_mensaje(f"¡{self.jugador.nombre} usó {ataque}! {mensaje}")
        else:
            self.nuevo_mensaje(f"¡{self.jugador.nombre} usó {ataque}!")

        self.turno = "ejecutar_golpe_jugador"

    def aplicar_daño_a_entrenador(self):
        """Versión específica para batallas de entrenador con cálculo de daño real"""
        self.animando_ataque = True
        self.timer_animacion = pygame.time.get_ticks()

        if self.sonido_impacto:
            self.sonido_impacto.play()

        daño = self.daño_proximo_golpe


        self.vida_anterior = self.enemigo.hp_actual
        self.enemigo.hp_actual -= daño
        self.vida_destino = max(0, self.enemigo.hp_actual)

        # Iniciar animación de vida
        self.animando_vida = True
        self.vida_actual_anim = self.vida_anterior
        self.pokemon_animando = "enemigo"

        # La vida real ya se actualizó
        self.enemigo.hp_actual = self.vida_destino

        # Mostrar mensaje de efectividad si existe
        if hasattr(self, 'mensaje_efectividad') and self.mensaje_efectividad:
            # El mensaje ya se mostró en ejecutar_ataque_seleccionado
            pass

        if self.enemigo.hp_actual <= 0:
            self.enemigo.hp_actual = 0

            # Verificar si hay más Pokémon en el equipo del entrenador
            if self.indice_pokemon_entrenador + 1 < len(self.equipo_entrenador):
                self.indice_pokemon_entrenador += 1
                self.enemigo = self.equipo_entrenador[self.indice_pokemon_entrenador]
                self.nuevo_mensaje(f"¡{self.entrenador_nombre} saca a {self.enemigo.nombre.upper()}!")

                # Actualizar frames
                if hasattr(self.enemigo, 'frames_batalla_enemigo'):
                    self.frames_rival = self.enemigo.frames_batalla_enemigo

                self.turno = "espera_enemigo"
            else:
                # No hay más Pokémon, entrenador derrotado
                self.nuevo_mensaje(f"¡Has derrotado a {self.entrenador_nombre}!")
                self.resultado_batalla = "gano"
                self.turno = "muerte_enemigo"
        else:
            self.turno = "espera_enemigo"

    def aplicar_efecto(self, objetivo, efecto):
        """Aplica efectos como subir/bajar stats"""
        if efecto == "bajar_ataque":
            objetivo.modificador_ataque = max(objetivo.modificador_ataque - 1, -6)
            return f"¡El ataque de {objetivo.nombre} bajó!"
        elif efecto == "bajar_defensa":
            objetivo.modificador_defensa = max(objetivo.modificador_defensa - 1, -6)
            return f"¡La defensa de {objetivo.nombre} bajó!"
        elif efecto == "subir_ataque":
            objetivo.modificador_ataque = min(objetivo.modificador_ataque + 1, 6)
            return f"¡El ataque de {objetivo.nombre} subió!"
        elif efecto == "subir_defensa":
            objetivo.modificador_defensa = min(objetivo.modificador_defensa + 1, 6)
            return f"¡La defensa de {objetivo.nombre} subió!"
        return ""

    def aplicar_daño_a_salvaje(self):
        """Versión específica para Pokémon salvajes con cálculo de daño real"""
        self.animando_ataque = True
        self.timer_animacion = pygame.time.get_ticks()

        if self.sonido_impacto:
            self.sonido_impacto.play()

        daño = self.daño_proximo_golpe


        self.vida_anterior = self.enemigo.hp_actual
        self.enemigo.hp_actual -= daño
        self.vida_destino = max(0, self.enemigo.hp_actual)

        # Iniciar animación de vida
        self.animando_vida = True
        self.vida_actual_anim = self.vida_anterior
        self.pokemon_animando = "enemigo"

        # La vida real ya se actualizó
        self.enemigo.hp_actual = self.vida_destino
        print(
            f"💥 Daño aplicado a {self.enemigo.nombre}: {daño} - HP ahora: {self.enemigo.hp_actual}/{self.enemigo.hp_max}")

        # Mostrar mensaje de efectividad si existe
        if hasattr(self, 'mensaje_efectividad') and self.mensaje_efectividad:
            # El mensaje ya se mostró en ejecutar_ataque_seleccionado
            pass

        if self.enemigo.hp_actual <= 0:
            self.enemigo.hp_actual = 0
            self.nuevo_mensaje(f"¡El {self.enemigo.nombre} enemigo se ha debilitado!")
            self.resultado_batalla = "gano"
            self.turno = "muerte_enemigo"
        else:
            self.turno = "espera_enemigo"

    def calcular_daño(self, atacante, defensor, ataque):
        info_ataque = self.datos_ataques.get(ataque,
                                             {"daño": 40, "tipo": "normal", "precision": 100, "categoria": "fisico"})

        print(f"\n🔍 CALCULANDO DAÑO: {atacante.nombre} usó {ataque}")
        print(f"   Tipo ataque: {info_ataque['tipo']}")

        # 1. Verificar precisión
        if random.randint(1, 100) > info_ataque["precision"]:
            print("   ❌ Ataque falló!")
            return 0, "fallo"

        # 2. Stats según categoría
        if info_ataque["categoria"] == "fisico":
            ataque_stat = atacante.ataque
            defensa_stat = defensor.defensa
            print(f"   Ataque físico: ATK={ataque_stat}, DEF={defensa_stat}")
        else:
            ataque_stat = atacante.ataque_especial
            defensa_stat = defensor.defensa_especial
            print(f"   Ataque especial: ATK ESP={ataque_stat}, DEF ESP={defensa_stat}")

        # 3. Nivel y poder base
        nivel = atacante.nivel
        potencia = info_ataque["daño"]
        print(f"   Nivel: {nivel}, Potencia: {potencia}")

        # 4. Fórmula OFICIAL de Pokémon
        # Paso 1: (2 * nivel / 5 + 2)
        paso1 = (2 * nivel / 5 + 2)
        print(f"   Paso 1 (2*nivel/5+2): {paso1}")

        # Paso 2: paso1 * potencia * ataque_stat / defensa_stat
        paso2 = paso1 * potencia * ataque_stat / defensa_stat
        print(f"   Paso 2 (paso1 * pot * atk / def): {paso2}")

        # Paso 3: paso2 / 50
        paso3 = paso2 / 50
        print(f"   Paso 3 (paso2 / 50): {paso3}")

        # Paso 4: paso3 + 2
        paso4 = paso3 + 10
        print(f"   Paso 4 (paso3 + 2): {paso4}")

        # Daño base (sin modificadores)
        daño_base = int(paso4)
        print(f"   Daño base (sin modificadores): {daño_base}")

        # 5. Modificadores por stats (si aplican)
        modificador_atacante = (atacante.modificador_ataque if info_ataque["categoria"] == "fisico"
                                else atacante.modificador_ataque_especial)
        modificador_defensor = (defensor.modificador_defensa if info_ataque["categoria"] == "fisico"
                                else defensor.modificador_defensa_especial)

        if modificador_atacante != 0 or modificador_defensor != 0:
            daño_base = int(daño_base * (1 + modificador_atacante * 0.5) / (1 + modificador_defensor * 0.5))
            print(f"   Daño con modificadores: {daño_base}")

        # 6. STAB (Same Type Attack Bonus) - 1.5x si el tipo del ataque coincide con el tipo del atacante
        stab = 1.0
        if info_ataque["tipo"] == atacante.tipo or (
                hasattr(atacante, 'tipo2') and info_ataque["tipo"] == atacante.tipo2):
            stab = 1.5
            print(f"   STAB: 1.5x (coincidencia de tipos)")

        # 7. Efectividad por tipos
        efectividad = self.calcular_efectividad(info_ataque["tipo"], defensor.tipo, defensor.tipo2)
        print(f"   Efectividad: {efectividad}x")

        # 8. Variación aleatoria (85% a 100%)
        variacion = random.randint(85, 100) / 100
        print(f"   Variación: {variacion}")

        # Daño final con TODOS los modificadores
        daño_final = int(daño_base * stab * efectividad * variacion)

        mensaje_efectividad = ""
        if efectividad >= 2:
            mensaje_efectividad = "¡Es muy efectivo!"
        elif efectividad <= 0.5 and efectividad > 0:
            mensaje_efectividad = "No es muy efectivo..."
        elif efectividad == 0:
            mensaje_efectividad = "¡No afecta!"

        print(f"   STAB: {stab}x")
        print(f"   DAÑO FINAL: {daño_final} - {mensaje_efectividad}")
        print("-" * 40)

        return max(1, daño_final), mensaje_efectividad

    def calcular_efectividad(self, tipo_ataque, tipo_defensor, tipo_defensor2=None):
        """Calcula la efectividad de un tipo contra otro"""
        efectividad = 1.0

        # Tipo principal
        if tipo_ataque in self.tabla_tipos and tipo_defensor in self.tabla_tipos[tipo_ataque]:
            efectividad *= self.tabla_tipos[tipo_ataque][tipo_defensor]

        # Tipo secundario
        if tipo_defensor2 and tipo_ataque in self.tabla_tipos and tipo_defensor2 in self.tabla_tipos[tipo_ataque]:
            efectividad *= self.tabla_tipos[tipo_ataque][tipo_defensor2]

        return efectividad

    def ganar_experiencia(self):
        exp_ganada = self.enemigo.nivel * 20
        self.jugador.exp_actual += exp_ganada
            # CAMBIO AQUÍ
        self.nuevo_mensaje(f"¡{self.jugador.nombre} ganó {exp_ganada} puntos de EXP!")

        if self.jugador.exp_actual >= self.jugador.exp_siguiente_nivel:
            self.turno = "subir_nivel_pendiente"
        else:
            self.turno = "fin_batalla_pendiente"

    def subir_de_nivel(self):
        self.jugador.nivel += 1
        self.jugador.exp_actual = 0
        self.jugador.exp_siguiente_nivel = int(self.jugador.exp_siguiente_nivel * 1.2)

        # 1. Aumentamos la vida máxima
        self.jugador.hp_max += 10

        # 2. En lugar de igualar al máximo, sumamos un pequeño bono (ej. 10 puntos)
        self.jugador.hp_actual += 10

        # 3. IMPORTANTE: Validamos que la vida actual no supere el nuevo máximo
        if self.jugador.hp_actual > self.jugador.hp_max:
            self.jugador.hp_actual = self.jugador.hp_max

        self.nuevo_mensaje(f"¡Subiste al nivel {self.jugador.nivel}!")
        self.turno = "fin_batalla_pendiente"

    def preparar_ataque_enemigo(self):
        """El enemigo elige un ataque de su lista"""
        import random

        # Obtener los ataques del enemigo
        if hasattr(self.enemigo, 'ataques') and self.enemigo.ataques:
            ataques_disponibles = self.enemigo.ataques
        else:
            # Fallback si no tiene ataques
            ataques_disponibles = ["PLACAJE"]

        # Elegir un ataque aleatorio
        ataque_elegido = random.choice(ataques_disponibles)

        # Guardar el ataque para usarlo después
        self.ataque_enemigo = ataque_elegido

        # Calcular daño (para mostrarlo después)
        daño, mensaje = self.calcular_daño(self.enemigo, self.jugador, ataque_elegido)
        self.daño_proximo_golpe_enemigo = daño

        # Mostrar mensaje
        self.nuevo_mensaje(f"¡El {self.enemigo.nombre} enemigo usó {ataque_elegido}!")
        self.turno = "ejecutar_golpe_enemigo"



    def aplicar_daño_enemigo_real(self):
        """Aplica el daño del ataque del enemigo"""
        daño = self.daño_proximo_golpe_enemigo

        self.jugador.hp_actual -= daño

        # También actualizar el Pokémon activo en el equipo
        if hasattr(self.jugador, 'pokemon_activo') and len(self.jugador.equipo) > 0:
            pokemon_activo = self.jugador.equipo[self.jugador.pokemon_activo]
            pokemon_activo.hp_actual = self.jugador.hp_actual

        # Mostrar mensaje de efectividad si existe
        if hasattr(self, 'mensaje_efectividad_enemigo') and self.mensaje_efectividad_enemigo:
            pass  # Ya se mostró

        # --- SONIDO DE IMPACTO ---
        if self.sonido_impacto:
            self.sonido_impacto.play()

        # Animación de daño al jugador
        self.animando_daño_mio = True
        self.timer_daño_mio = pygame.time.get_ticks()

        # Restar vida
        self.vida_anterior = self.jugador.hp_actual
        self.jugador.hp_actual -= daño
        self.vida_destino = max(0, self.jugador.hp_actual)

        self.animando_vida = True
        self.vida_actual_anim = self.vida_anterior
        self.pokemon_animando = "jugador"

        self.jugador.hp_actual = self.vida_destino

        # --- LÓGICA DE DERROTA ---
        if self.jugador.hp_actual <= 0:
            self.jugador.hp_actual = 0
            self.nuevo_mensaje(f"¡{self.jugador.nombre} se ha debilitado!")
            self.perdio_jugador = True
            self.resultado_batalla = "perdio"
            self.turno = "fin_batalla_pendiente"
        else:
            self.turno = "espera_jugador"

    def iniciar_captura(self):
        """Inicia la animación de captura (consume una pokebola)"""
        import random

        # Verificar si es batalla de entrenador
        if self.es_entrenador:
            self.nuevo_mensaje("¡No puedes capturar el Pokémon de otro entrenador!")
            self.fase = "MENSAJE"
            return

        # Verificar si tiene pokebolas
        if self.inventario.get("pokebola", 0) <= 0:
            self.nuevo_mensaje("¡No tienes pokebolas!")
            self.fase = "MENSAJE"
            self.turno = "jugador"
            return

        # Consumir una pokebola
        self.inventario["pokebola"] -= 1

        # Actualizar la lista de items
        self.items_bolsa = self._generar_items_bolsa()

        self.capturando = True
        self.animacion_captura = 1
        self.timer_captura = pygame.time.get_ticks()
        self.pokemon_visible = True
        self.parpadeos_captura = 0

        if self.sonido_lanzar_pokebola:
            self.sonido_lanzar_pokebola.play()

        self.nuevo_mensaje(f"¡{self.jugador.nombre} lanzó una POKEBOLA! (Quedan: {self.inventario['pokebola']})")

        # Calcular probabilidad de captura
        prob_final = 80  # 80% de éxito
        self.captura_exitosa = random.randint(1, 100) <= prob_final

        print(f"🎯 Probabilidad: {prob_final}% - {'ÉXITO' if self.captura_exitosa else 'FALLO'}")

    def obtener_ataques_por_pokemon(self, nombre):
        """Devuelve ataques específicos para cada Pokémon"""
        nombre = nombre.lower().strip()

        if "bulbasaur" in nombre:
            return ["LÁTIGO CEPA", "ABSORBER", "GRUÑIDO", "PLACAJE"]
        elif "charmander" in nombre:
            return ["ASCUAS", "ARAÑAZO", "GRUÑIDO", "PLACAJE"]
        elif "squirtle" in nombre:
            return ["PISTOLA AGUA", "ARAÑAZO", "GRUÑIDO", "PLACAJE"]
        elif "pikachu" in nombre:
            return ["IMPACTRUENO", "ATAQUE RÁPIDO", "CHISPA", "PLACAJE"]
        elif "onix" in nombre:
            return ["TERREMOTO", "DESLIZAR", "ROCA AFILADA", "COLISIÓN"]
        elif "magnemite" in nombre or "magnamite" in nombre:
            return ["CHISPA", "SONICBOOM", "RAYO CARGA", "IMPACTO"]
        elif "hitmonlee" in nombre:
            return ["PATADA SALTO", "GOLPE KARMA", "FINTE", "PATADA BAJA"]
        elif "hitmonchan" in nombre:
            return ["PUÑO MACHETE", "PUÑO DINÁMICO", "FINTE", "PUÑO MACHACA"]
        elif "pidgey" in nombre:
            return ["ATAQUE ALA", "REMOLINO", "PLACAJE", "GRUÑIDO"]
        elif "horsea" in nombre:
            return ["PISTOLA AGUA", "BURBUJA", "ÁCIDO", "PLACAJE"]
        elif "rhyhorn" in nombre:
            return ["TERREMOTO", "DERRIBO", "ATIZAR", "PLACAJE"]
        elif "tangela" in nombre:
            return ["LÁTIGO CEPA", "ABSORBER", "ENREDADERA", "PLACAJE"]
        else:
            print(f"⚠️ No hay ataques definidos para {nombre}, usando genéricos")
            return ["PLACAJE", "GRUÑIDO", "PATADA", "GOLPE"]

    def procesar_captura_exitosa(self):
        """Procesa cuando la captura es exitosa"""
        print(f"\n🔵 CAPTURA EXITOSA DE {self.enemigo.nombre}")

        # 1. El Pokémon capturado es el enemigo
        pokemon_capturado = self.enemigo
        nombre_pkmn = pokemon_capturado.nombre.lower()
        print(f"   Pokémon: {pokemon_capturado.nombre}")

        # 2. Restaurar vida al máximo
        vida_antes = pokemon_capturado.hp_actual
        pokemon_capturado.hp_actual = pokemon_capturado.hp_max
        print(f"   Vida: {vida_antes} -> {pokemon_capturado.hp_actual} (restaurada)")

        if "onix" in nombre_pkmn:
            pokemon_capturado.ataques = ["TERREMOTO", "DESLIZAR", "ROCA AFILADA", "COLISIÓN"]
            print(f"   ✅ Ataques de Onix asignados: {pokemon_capturado.ataques}")
        elif "hitmonlee" in nombre_pkmn:
            pokemon_capturado.ataques = ["PATADA SALTO", "GOLPE KARMA", "FINTE", "PATADA BAJA"]
        elif "hitmonchan" in nombre_pkmn:
            pokemon_capturado.ataques = ["PUÑO MACHETE", "PUÑO DINÁMICO", "FINTE", "PUÑO MACHACA"]
        elif "pikachu" in nombre_pkmn:
            pokemon_capturado.ataques = ["IMPACTRUENO", "ATAQUE RÁPIDO", "CHISPA", "PLACAJE"]
        elif "magnemite" in nombre_pkmn or "magnamite" in nombre_pkmn:
            pokemon_capturado.ataques = ["CHISPA", "SONICBOOM", "RAYO CARGA", "IMPACTO"]
        elif "charmander" in nombre_pkmn:
            pokemon_capturado.ataques = ["ASCUAS", "ARAÑAZO", "GRUÑIDO", "PLACAJE"]
        elif "squirtle" in nombre_pkmn:
            pokemon_capturado.ataques = ["PISTOLA AGUA", "ARAÑAZO", "GRUÑIDO", "PLACAJE"]
        elif "bulbasaur" in nombre_pkmn:
            pokemon_capturado.ataques = ["LÁTIGO CEPA", "ABSORBER", "GRUÑIDO", "PLACAJE"]
        else:
            # Ataques genéricos
            pokemon_capturado.ataques = ["PLACAJE", "GRUÑIDO", "PATADA", "GOLPE"]
            print(f"   ⚠️ Ataques genéricos asignados a {nombre_pkmn}")

        print(f"🟢 procesar_captura - {nombre_pkmn} recibe ataques: {pokemon_capturado.ataques}")

        # 3. 🟢 CARGAR LA IMAGEN DE JUGADOR ESPECÍFICA (*_player.png)
        try:
            # Intentar cargar la imagen de jugador
            ruta_player = f"asets/imagenes/POKEMON_EN_BATALLA/{nombre_pkmn}_player.png"
            img_player = pygame.image.load(ruta_player).convert_alpha()

            # Escalar la imagen (tamaño estándar para batalla)
            img_player = pygame.transform.scale(img_player, (153, 108))

            # Guardar frames de jugador (usar la misma imagen para ambos frames)
            pokemon_capturado.frames_batalla_jugador = [img_player, img_player]
            print(f"   ✅ Imagen de jugador cargada para {pokemon_capturado.nombre}")

        except Exception as e:
            print(f"   ⚠️ No se pudo cargar imagen de jugador para {nombre_pkmn}: {e}")
            # Fallback: crear desde imagen enemigo
            if hasattr(pokemon_capturado, 'frames_batalla_enemigo') and pokemon_capturado.frames_batalla_enemigo:
                frames_jugador = []
                for img in pokemon_capturado.frames_batalla_enemigo:
                    img_volteada = pygame.transform.flip(img, True, False)
                    frames_jugador.append(img_volteada)
                pokemon_capturado.frames_batalla_jugador = frames_jugador
                print(f"   ✅ Frames de jugador creados desde enemigo (volteados)")

        # 4. AGREGAR AL EQUIPO
        if len(self.jugador.equipo) < 6:
            self.jugador.equipo.append(pokemon_capturado)
            print(f"   ✅ {pokemon_capturado.nombre} AGREGADO al equipo")
            print(f"   Nuevo equipo: {len(self.jugador.equipo)} Pokémon")

            self.nuevo_mensaje(f"¡Has capturado a {pokemon_capturado.nombre.upper()}!")
        else:
            print(f"   ❌ Equipo lleno")
            self.nuevo_mensaje(f"¡Capturaste a {pokemon_capturado.nombre.upper()}! pero el equipo está lleno")

        #self.batalla_finalizada = True
        #self.capturando = False

    def actualizar_animacion_vida(self):
        """Actualiza la animación de la barra de vida"""
        if not self.animando_vida:
            return

        # Calcular cuánto debe decrecer
        if self.vida_anterior > self.vida_destino:
            # Está disminuyendo
            self.vida_actual_anim -= self.velocidad_animacion_vida
            if self.vida_actual_anim <= self.vida_destino:
                self.vida_actual_anim = self.vida_destino
                self.animando_vida = False
                self.pokemon_animando = None
        else:
            # Está aumentando (raro, pero por si acaso)
            self.vida_actual_anim += self.velocidad_animacion_vida
            if self.vida_actual_anim >= self.vida_destino:
                self.vida_actual_anim = self.vida_destino
                self.animando_vida = False
                self.pokemon_animando = None

    def cambiar_pokemon_activo(self, indice):
        """Cambia el Pokémon activo en batalla MANTENIENDO su vida actual"""

        pokemon_anterior = self.jugador.equipo[self.jugador.pokemon_activo]
        pokemon_anterior.hp_actual = self.jugador.hp_actual
        print(f"💾 Guardando vida de {pokemon_anterior.nombre}: {pokemon_anterior.hp_actual}")

        # Verificar que el índice sea válido
        if indice < 0 or indice >= len(self.jugador.equipo):
            self.nuevo_mensaje("¡Índice de Pokémon inválido!")
            return False

        # El Pokémon que estaba en batalla (actual) guarda su vida actual
        # (Esto ya se mantiene automáticamente porque self.jugador es la referencia)

        # Intentar cambiar en el objeto jugador
        if self.jugador.cambiar_pokemon(indice):
            # 🟢 IMPORTANTE: NO crear nuevo Pokémon, solo actualizar referencias

            # Actualizar frames (esto es solo visual)
            if hasattr(self.jugador, 'frames_batalla') and self.jugador.frames_batalla:
                self.frames_mio = self.jugador.frames_batalla
                print(f"✅ Frames de batalla actualizados a {self.jugador.nombre}")

            # Actualizar ataques (esto es solo para el menú)
            if hasattr(self.jugador, 'ataques') and self.jugador.ataques:
                self.ataques = self.jugador.ataques.copy()
                print(f"✅ Ataques actualizados a: {self.ataques}")

            # Mostrar mensaje de cambio
            self.nuevo_mensaje(f"¡Ve, {self.jugador.nombre}!")
            self.fase = "MENSAJE"
            self.mostrando_equipo = False

            # 🟢 El turno pasa al jugador para que pueda atacar
            self.turno = "jugador"

            print(f"🔄 Cambiado a {self.jugador.nombre} - HP: {self.jugador.hp_actual}/{self.jugador.hp_max}")
            return True
        else:
            self.nuevo_mensaje("¡No puedes cambiar a ese Pokémon!")
            return False

    def finalizar_batalla(self):
        """Finaliza la batalla y limpia referencias"""
        print("\n🔚 FINALIZANDO BATALLA")

        # 🟢 REINICIAR LA VARIABLE DE ENTRENADOR
        self.es_entrenador = False
        self.entrenador_nombre = "Rival"
        self.equipo_entrenador = []

        # Limpiar según el tipo de batalla
        if self.es_entrenador:
            if self.enemigo_entrenador:
                print(f"   Limpiando entrenador: {self.enemigo_entrenador.nombre}")
                self.enemigo_entrenador.hp_actual = self.enemigo_entrenador.hp_max
                self.enemigo_entrenador = None

            if self.equipo_entrenador:
                for pokemon in self.equipo_entrenador:
                    if pokemon:
                        pokemon.hp_actual = pokemon.hp_max
                self.equipo_entrenador = None
        else:
            if self.enemigo_salvaje:
                print(f"   Limpiando salvaje: {self.enemigo_salvaje.nombre}")
                self.enemigo_salvaje.hp_actual = self.enemigo_salvaje.hp_max
                self.enemigo_salvaje = None

        # Limpiar referencia común
        self.enemigo = None
        self.jugador = None

        pygame.mixer.stop()
        print("✅ Batalla finalizada\n")