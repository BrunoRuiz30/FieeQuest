import pygame
import random


class Personaje():
    def __init__(self, x, y, animaciones, nombre="Entrenador"):
        self.animaciones = animaciones
        self.frame_index = 0
        self.accion = 0
        self.update_time = pygame.time.get_ticks()
        self.nombre = nombre

        self.frames_batalla = None

        # --- PROTECCIÓN PARA POKÉMON FANTASMAS ---
        if self.animaciones is not None:
            self.image = self.animaciones[self.accion][self.frame_index]
        else:
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)

        # --- SOLUCIÓN AL ERROR ---
        # Creamos 'rect' que es lo que Pygame busca por defecto
        self.rect = self.image.get_rect()
        # Creamos 'forma' como una referencia al mismo objeto rect
        # Así, si cambias self.rect.x, self.forma.x cambiará automáticamente
        self.forma = self.rect

        # Ajuste de hitbox (puedes seguir usando self.forma aquí)
        self.forma.width = self.forma.width - 20
        self.forma.height = self.forma.height - 15



        # Posicionamos en el centro
        self.forma.center = (x, y)
        self.en_movimiento = False

        self.equipo = []  # Lista de Pokémon capturados
        self.pokemon_activo = 0

        # 🟢 NUEVOS ATRIBUTOS PARA BATALLA
        self.tipo = "normal"  # Tipo por defecto
        self.tipo2 = None  # Segundo tipo (opcional)

        # Stats base
        self.hp_max = 0
        self.hp_actual = 0
        self.ataque = 0
        self.defensa = 0
        self.ataque_especial = 0
        self.defensa_especial = 0
        self.velocidad = 0
        self.nivel = 0
        self.ataques = []

        # Modificadores de stats (para efectos como Danza Espada)
        self.modificador_ataque = 0
        self.modificador_defensa = 0
        self.modificador_ataque_especial = 0
        self.modificador_defensa_especial = 0
        self.modificador_velocidad = 0
        self.modificador_evasion = 0
        self.modificador_precision = 0

        self.tiene_pokemon = False
        self.exp_actual = 0
        self.exp_siguiente_nivel = 100

        self.inventario = {
            "pokebola": 0,
            "pocion": 0,
            "antidoto": 0,
            "superpocion": 0
        }
        self.dinero = 3000  # Dinero inicial





    def movimiento(self, delta_x, delta_y, obstaculos):
        if delta_x != 0 or delta_y != 0:
            self.en_movimiento = True
        else:
            self.en_movimiento = False

        posicion_anterior = self.forma.copy()

        # 1. Movimiento en X
        self.forma.x += delta_x
        for obstaculo in obstaculos:
            # --- SOLUCIÓN AQUÍ ---
            # Si el obstáculo tiene .forma, la usamos. Si no, es que ya es un Rect.
            rect_colision = obstaculo.forma if hasattr(obstaculo, 'forma') else obstaculo

            if self.forma.colliderect(rect_colision):
                self.forma.x = posicion_anterior.x

        # 2. Movimiento en Y
        self.forma.y += delta_y
        for obstaculo in obstaculos:
            # --- SOLUCIÓN AQUÍ ---
            rect_colision = obstaculo.forma if hasattr(obstaculo, 'forma') else obstaculo

            if self.forma.colliderect(rect_colision):
                self.forma.y = posicion_anterior.y

        # Control de animaciones (acciones)
        if delta_x > 0:
            self.accion = 3
        elif delta_x < 0:
            self.accion = 2
        elif delta_y > 0:
            self.accion = 0
        elif delta_y < 0:
            self.accion = 1

        # Límites del mapa
        self.forma.left = max(0, self.forma.left)
        self.forma.right = min(4000, self.forma.right)
        self.forma.top = max(0, self.forma.top)
        self.forma.bottom = min(4000, self.forma.bottom)
    def update_animacion(self):
        # --- CAMBIO: Solo ejecutar si hay animaciones (No es un fantasma) ---
        if self.animaciones is not None:
            VELOCIDAD_ANIMACION = 150

            if self.en_movimiento == False:
                self.frame_index = 0

            # Ahora esto es seguro porque ya verificamos que animaciones existe
            self.image = self.animaciones[self.accion][self.frame_index]

            if pygame.time.get_ticks() - self.update_time > VELOCIDAD_ANIMACION:
                self.update_time = pygame.time.get_ticks()
                self.frame_index = self.frame_index + 1

            if self.frame_index >= len(self.animaciones[self.accion]):
                self.frame_index = 0
        else:
            # Si es un fantasma, no hacemos nada aquí
            pass



    def dibujar(self,interfaz,offset):
        pos_visual = (self.forma.x - offset.x, self.forma.y - offset.y)
        interfaz.blit(self.image,pos_visual)
        #pygame.draw.rect(interfaz,(255,255,0),self.forma,1)



    def agregar_pokemon(self, pokemon):
        """Agrega un Pokémon capturado al equipo"""
        print(f"📦 Intentando agregar {pokemon.nombre} al equipo")
        print(f"   - Equipo actual: {len(self.equipo)}/6 Pokémon")

        if len(self.equipo) < 6:
            self.equipo.append(pokemon)
            print(f"✅ {pokemon.nombre} agregado al equipo. Ahora tienes {len(self.equipo)} Pokémon")

            # Mostrar el equipo completo
            for i, p in enumerate(self.equipo):
                print(f"   {i}: {p.nombre} (HP: {p.hp_actual}/{p.hp_max})")

            return True
        else:
            print("❌ El equipo está lleno (máximo 6 Pokémon)")
            return False

    # 🆕 Método para cambiar Pokémon activo
    def cambiar_pokemon(self, indice):
        """Cambia el Pokémon activo en batalla MANTENIENDO su vida actual"""
        if 0 <= indice < len(self.equipo):
            # Guardar referencia al Pokémon anterior (por si acaso)
            pokemon_anterior = self.equipo[self.pokemon_activo]

            # Actualizar el índice del Pokémon activo
            self.pokemon_activo = indice

            # Obtener el nuevo Pokémon activo
            pokemon_nuevo = self.equipo[indice]

            print(f"\n🔄 CAMBIANDO DE {pokemon_anterior.nombre} A {pokemon_nuevo.nombre}")
            print(f"   HP anterior: {pokemon_anterior.hp_actual}/{pokemon_anterior.hp_max}")
            print(f"   HP nuevo: {pokemon_nuevo.hp_actual}/{pokemon_nuevo.hp_max}")

            # 🟢 ACTUALIZAR LOS ATRIBUTOS DEL JUGADOR CON LOS DEL POKÉMON NUEVO
            # PERO SIN CREAR UN NUEVO OBJETO

            # Actualizar stats básicos
            self.nombre = pokemon_nuevo.nombre
            self.hp_max = pokemon_nuevo.hp_max
            self.hp_actual = pokemon_nuevo.hp_actual  # ← MANTIENE LA VIDA ACTUAL
            self.nivel = pokemon_nuevo.nivel
            self.ataque = pokemon_nuevo.ataque
            self.defensa = pokemon_nuevo.defensa
            self.ataque_especial = pokemon_nuevo.ataque_especial
            self.defensa_especial = pokemon_nuevo.defensa_especial
            self.velocidad = pokemon_nuevo.velocidad
            self.tipo = pokemon_nuevo.tipo
            self.tipo2 = pokemon_nuevo.tipo2

            # Actualizar ataques
            self.ataques = pokemon_nuevo.ataques.copy()

            # Actualizar frames de batalla (visual)
            if hasattr(pokemon_nuevo, 'frames_batalla_jugador') and pokemon_nuevo.frames_batalla_jugador:
                self.frames_batalla = pokemon_nuevo.frames_batalla_jugador
                print(f"   ✅ Usando frames de JUGADOR para {pokemon_nuevo.nombre}")
            else:
                print(f"   ⚠️ {pokemon_nuevo.nombre} no tiene frames de jugador")
                # Fallback visual
                self.frames_batalla = [
                    pygame.Surface((153, 108)),
                    pygame.Surface((153, 108))
                ]

            print(f"   ✅ Cambio completado - {self.nombre} tiene {self.hp_actual}/{self.hp_max} HP")
            return True

        return False









class ObjetoEstatico:
    def __init__(self, x, y, imagen, colision_manual,tipo=""):
        self.image = imagen
        self.tipo = tipo  # Guardamos el nombre (ej: "pastoc1")
        # Posición de la imagen
        self.rect_dibujo = self.image.get_rect()
        self.rect_dibujo.topleft = (x, y)

        # LÓGICA DE COLISIÓN ADAPTADA
        if colision_manual == (0, 0, 0, 0):
            # Si no hay colisión manual, usamos el tamaño de la imagen
            # Esto permite que el personaje camine POR ENCIMA
            self.forma = pygame.Rect(x, y, self.rect_dibujo.width, self.rect_dibujo.height)
            self.solido = False
        else:
            # Si hay valores, es un objeto sólido (pared, casa, árbol)
            self.forma = pygame.Rect(
                colision_manual[0],
                colision_manual[1],
                colision_manual[2],
                colision_manual[3]
            )
            self.solido = True



    def dibujar(self, interfaz, offset):
        # 1. Dibujar la imagen relativa a la cámara
        pos_img = (self.rect_dibujo.x - offset.x, self.rect_dibujo.y - offset.y)
        interfaz.blit(self.image, pos_img)

        # 2. Dibujar el rectángulo rojo relativo a la cámara
        # SI ESTO NO TIENE EL "- offset.y", el cuadro no se moverá con el mapa
        pos_rect_x = self.forma.x - offset.x
        pos_rect_y = self.forma.y - offset.y

        #pygame.draw.rect(interfaz, (255, 0, 0),
                         #(pos_rect_x, pos_rect_y, self.forma.width, self.forma.height), 2)






class Camara:
    def __init__(self, ancho_ventana, alto_ventana, ancho_mapa, alto_mapa):
        self.offset = pygame.Vector2(0, 0)
        self.ancho_v = ancho_ventana
        self.alto_v = alto_ventana
        self.ancho_m = ancho_mapa
        self.alto_m = alto_mapa

    def seguir(self, objetivo):
        # Calcula el centro
        self.offset.x = objetivo.forma.centerx - self.ancho_v // 2
        self.offset.y = objetivo.forma.centery - self.alto_v // 2

        # Límites para que la cámara no muestre el "vacío" fuera del mapa
        self.offset.x = max(0, min(self.offset.x, self.ancho_m - self.ancho_v))
        self.offset.y = max(0, min(self.offset.y, self.alto_m - self.alto_v))



class Pokemon(Personaje):
    def __init__(self, nombre, x, y, animaciones, sonido=None, limites=None, escala_personalizada=1.0, nivel=5):
        # Guardar atributos ANTES de llamar a super
        self.nombre = nombre
        self.nivel = nivel
        self.sonido = sonido
        self.limites = limites

        # 🟢 OBTENER STATS BASE PRIMERO
        self.stats_base = self.obtener_stats_base(nombre)
        self.tipo = self.stats_base["tipo"]
        self.tipo2 = self.stats_base.get("tipo2", None)

        # Procesar animaciones
        self.animaciones_escaladas = None
        if animaciones is not None:
            if isinstance(animaciones, dict):
                lista_anims = [
                    animaciones.get("abajo", []),
                    animaciones.get("arriba", []),
                    animaciones.get("izquierda", []),
                    animaciones.get("derecha", [])
                ]
                self.animaciones_escaladas = self._generar_escalado(lista_anims, escala_personalizada)
            else:
                self.animaciones_escaladas = self._generar_escalado(animaciones, escala_personalizada)

        # Llamar al padre
        super().__init__(x, y, self.animaciones_escaladas, nombre=nombre)

        # Configurar imagen inicial
        if self.animaciones_escaladas and len(self.animaciones_escaladas) > 0:
            self.image = self.animaciones_escaladas[0][0]
        else:
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)

        self.forma = self.image.get_rect(topleft=(x, y))

        # Variables de IA
        self.interactuando = False
        self.tiempo_interaccion = 0
        self.direccion_ia = pygame.Vector2(0, 0)
        self.ultima_vez_cambio = pygame.time.get_ticks()
        self.tiempo_espera = random.randint(1000, 3000)

        # 🟢 CALCULAR STATS SEGÚN NIVEL (AHORA SÍ, DESPUÉS DEL PADRE)
        self.hp_max = self.calcular_stat(self.stats_base["hp"], nivel)
        self.hp_actual = self.hp_max
        self.ataque = self.calcular_stat(self.stats_base["ataque"], nivel)
        self.defensa = self.calcular_stat(self.stats_base["defensa"], nivel)
        self.ataque_especial = self.calcular_stat(self.stats_base["ataque_especial"], nivel)
        self.defensa_especial = self.calcular_stat(self.stats_base["defensa_especial"], nivel)
        self.velocidad = self.calcular_stat(self.stats_base["velocidad"], nivel)


        self.frames_batalla = None
        self.exp = 0
        self.exp_siguiente_nivel = 100
        self.frames_batalla_enemigo = None
        self.frames_batalla_jugador = None

        # Modificadores de stats (para ataques como Danza Espada)
        self.modificador_ataque = 0
        self.modificador_defensa = 0
        self.modificador_ataque_especial = 0
        self.modificador_defensa_especial = 0
        self.modificador_velocidad = 0
        self.modificador_evasion = 0
        self.modificador_precision = 0

        # Al final del __init__, agrega:
        print(f"🟠 Pokemon.__init__ - {self.nombre} tiene ataques: {self.ataques}")


    def calcular_stat(self, base, nivel):
        """Calcula el stat actual según el nivel (fórmula simplificada)"""
        return int(((2 * base + 15) * nivel) / 100 + 5)

    def obtener_stats_base(self, nombre):
        """Stats base de cada Pokémon"""
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
            "magnemite": {"tipo": "electrico", "tipo2": "acero", "hp": 25, "ataque": 35, "defensa": 70,
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
        }
        return stats.get(nombre, stats["bulbasaur"])  # Por defecto Bulbasaur







    def copia_para_batalla(self):
        """Crea una copia INDEPENDIENTE del Pokémon para usar en batalla"""
        nuevo = Pokemon(
            self.nombre,
            0, 0,
            None,  # No necesitamos animaciones para batalla
            None,  # Sin sonido en la copia
            None,
            1.0,
            self.nivel
        )

        # Copiar TODOS los atributos importantes
        nuevo.nombre = self.nombre
        nuevo.nivel = self.nivel
        nuevo.hp_max = self.hp_max
        nuevo.hp_actual = self.hp_max  # Vida completa
        nuevo.ataques = self.ataques.copy() if self.ataques else ["PLACAJE", "GRUÑIDO"]

        # Copiar frames (importante: crear nuevas superficies, no compartir referencias)
        if hasattr(self, 'frames_batalla_enemigo') and self.frames_batalla_enemigo:
            nuevo.frames_batalla_enemigo = []
            for img in self.frames_batalla_enemigo:
                # Crear una copia de la superficie
                nuevo.frames_batalla_enemigo.append(img.copy())

        if hasattr(self, 'frames_batalla_jugador') and self.frames_batalla_jugador:
            nuevo.frames_batalla_jugador = []
            for img in self.frames_batalla_jugador:
                nuevo.frames_batalla_jugador.append(img.copy())

        return nuevo



    def _generar_escalado(self, anims_originales, factor):
        if anims_originales is None: return None
        if factor == 1.0: return anims_originales

        nuevas = []
        for fila in anims_originales:
            temp = []
            for frame in fila:
                ancho = int(frame.get_width() * factor)
                alto = int(frame.get_height() * factor)
                temp.append(pygame.transform.scale(frame, (ancho, alto)))
            nuevas.append(temp)
        return nuevas


    def mirar_jugador(self, pos_jugador):
        # (Tu lógica de mirar_jugador que ya tienes...)
        dx = pos_jugador.x - self.forma.x
        dy = pos_jugador.y - self.forma.y
        if abs(dx) > abs(dy):
            self.accion = 3 if dx > 0 else 2
        else:
            self.accion = 0 if dy > 0 else 1
        self.image = self.animaciones[self.accion][0]
        self.interactuando = True
        self.tiempo_interaccion = pygame.time.get_ticks()

    def actualizar_ia(self, obstaculos):
        ahora = pygame.time.get_ticks()

        if self.interactuando:
            if ahora - self.tiempo_interaccion > 2000:
                self.interactuando = False
            else:
                return

        if ahora - self.ultima_vez_cambio > self.tiempo_espera:
            opcion = random.randint(0, 4)
            velocidad = 2
            if opcion == 0:
                self.direccion_ia = pygame.Vector2(0, 0)
            elif opcion == 1:
                self.direccion_ia = pygame.Vector2(0, -velocidad)
            elif opcion == 2:
                self.direccion_ia = pygame.Vector2(0, velocidad)
            elif opcion == 3:
                self.direccion_ia = pygame.Vector2(-velocidad, 0)
            elif opcion == 4:
                self.direccion_ia = pygame.Vector2(velocidad, 0)

            self.ultima_vez_cambio = ahora
            self.tiempo_espera = random.randint(1000, 3000)

        # --- MEJORA: COMPROBACIÓN DE LÍMITES ---
        if self.limites:
            # Predecimos la siguiente posición
            futura_pos = self.forma.copy()
            futura_pos.x += self.direccion_ia.x
            futura_pos.y += self.direccion_ia.y

            # Si la futura posición se sale del rectángulo de límites, frena o cambia
            if not self.limites.contains(futura_pos):
                self.direccion_ia = pygame.Vector2(0, 0)  # Se detiene al llegar al borde
                # Opcional: podrías forzarlo a elegir otra dirección inmediatamente

        self.movimiento(self.direccion_ia.x, self.direccion_ia.y, obstaculos)

        if self.direccion_ia.x != 0 or self.direccion_ia.y != 0:
            self.update_animacion()


    def gritar(self):
        if self.sonido:
            self.sonido.play()

    def copia_para_equipo(self):
        """Crea una copia del Pokémon para agregar al equipo"""
        nuevo = Pokemon(
            self.nombre,
            0, 0,  # Posición temporal
            self.animaciones_escaladas,
            None,  # Sin sonido
            None,  # Sin límites
            1.0,  # Escala
            self.nivel
        )
        nuevo.hp_max = self.hp_max
        nuevo.hp_actual = self.hp_max  # Vida completa al capturar
        nuevo.ataques = self.ataques
        nuevo.frames_batalla = self.frames_batalla
        return nuevo


class NPC(Personaje):
    # 1. EL CONSTRUCTOR: Para crear al NPC con sus datos
    def __init__(self, x, y, animaciones, dialogo, sonido_beep,tipo_pokemon=None,equipo=None, nombre_entrenador="Entrenador",es_rival=False,es_lider_final=False):
        super().__init__(x, y, animaciones)
        self.dialogo = dialogo
        self.sonido_beep = sonido_beep
        self.hablando = False  # Estado para saber si mostrar el texto
        self.indice_frase = 0  # Qué frase de la lista está diciendo
        self.dialogo_actual = ""  # El texto que se ve en pantalla
        self.tipo_pokemon = tipo_pokemon  # Nuevo atributo
        self.mostrar_imagen_pokemon = False  # Controlar cuándo mostrar la imagen

        # 🆕 Atributos para entrenador rival
        self.es_rival = equipo is not None  # True si tiene Pokémon
        self.equipo = equipo if equipo else []  # Lista de Pokémon
        self.nombre_entrenador = nombre_entrenador
        self.derrotado = False  # Para no volver a luchar
        self.le_gano_al_jugador = False  # El entrenador le ganó al jugador
        self.es_lider_final = es_lider_final

    # 2. LA VISTA: Para que el NPC gire y te mire
    def actualizar_direccion(self, posicion_jugador):
        dx = posicion_jugador.centerx - self.forma.centerx
        dy = posicion_jugador.centery - self.forma.centery

        if abs(dx) > abs(dy):
            self.accion = 3 if dx > 0 else 2  # Derecha o Izquierda
        else:
            self.accion = 0 if dy > 0 else 1  # Abajo o Arriba

        self.frame_index = 0
        self.image = self.animaciones[self.accion][self.frame_index]

    # 3. LA VOZ: Para que el NPC hable cuando presionas la tecla
    def iniciar_dialogo(self):
        if not self.hablando:
            self.hablando = True
            self.indice_frase = 0
            self.dialogo_actual = self.dialogo[self.indice_frase]
            if self.sonido_beep: self.sonido_beep.play()

            if self.tipo_pokemon:
                self.mostrar_imagen_pokemon = True
        else:
            self.indice_frase += 1
            if self.indice_frase < len(self.dialogo):
                self.dialogo_actual = self.dialogo[self.indice_frase]
                if self.sonido_beep: self.sonido_beep.play()
            else:
                self.hablando = False