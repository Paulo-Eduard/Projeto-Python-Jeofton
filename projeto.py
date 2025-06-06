import pygame
import sys
import random
import tkinter as tk
from tkinter import simpledialog
import os

pygame.init()

# --- Configurações da tela ---
LARGURA, ALTURA = 1280, 720
screen = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("NexBlade")

# --- Cores ---
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)
AMARELO = (255, 255, 0)
AZUL = (0, 100, 255)
CINZA = (50, 50, 50)
ROXO = (128, 0, 128)

# Fontes
fonte = pygame.font.SysFont("Arial", 22)
fonte_pequena = pygame.font.SysFont("Arial", 16)
fonte_grande = pygame.font.SysFont("Arial", 30)

clock = pygame.time.Clock()

# --- Tamanhos das imagens ---
TAMANHO_PERSONAGEM = (250, 250)  # Aumentado de 150x150
TAMANHO_INIMIGO = (220, 220)     # Aumentado proporcionalmente

# --- Função para carregar imagens ---
def carregar_imagem(caminho, tamanho=TAMANHO_PERSONAGEM):
    try:
        img = pygame.image.load(caminho).convert_alpha()
        img = pygame.transform.scale(img, tamanho)
        return img
    except Exception as e:
        print(f"Erro ao carregar imagem '{caminho}': {e}")
        surf = pygame.Surface(tamanho)
        surf.fill((random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)))
        return surf

# Inicializa o mixer de áudio
pygame.mixer.init()
try:
    pygame.mixer.music.load("musica_fundo.mp3")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
except:
    print("Erro ao carregar música de fundo")

# Carrega as imagens com os novos tamanhos
img_fundo = carregar_imagem("fundo.jpg", (LARGURA, ALTURA))
img_historia_fundo = carregar_imagem("imagem/historia.png", (LARGURA, ALTURA))

img_espadachim = carregar_imagem("imagem/espadachim.png")
img_feiticeiro = carregar_imagem("imagem/mago.png")
img_arqueiro = carregar_imagem("imagem/arqueiro.png")
img_tanque = carregar_imagem("imagem/suporte.png")

img_slime = carregar_imagem("imagem/slime.png", TAMANHO_INIMIGO)
img_aranha = carregar_imagem("imagem/aranha.png", TAMANHO_INIMIGO)
img_goblin = carregar_imagem("imagem/goblin.png", TAMANHO_INIMIGO)
img_dragao = carregar_imagem("imagem/dragao.png", (300, 300))  # Dragão maior que os outros

# --- Classes de Personagem ---
class Personagem:
    def __init__(self, nome, classe, vida_max, ataque, defesa, skills, imagem, pos):
        self.nome = nome
        self.classe = classe
        self.vida_max = vida_max
        self.vida = vida_max
        self.ataque = ataque
        self.defesa = defesa
        self.skills = skills  # dict skill_name: (multiplicador, descricao)
        self.imagem = imagem
        self.pos = pos
        self.status = []  # para futuros status
        self.skill_selecionada = None  # Habilidade atualmente selecionada
        self.vida_barras = 3 if nome.lower() == "dragao" else 1
        if self.vida_barras > 1:
            self.vida_por_barra = self.vida_max / self.vida_barras

    def esta_vivo(self):
        return self.vida > 0

    def levar_dano(self, dano):
        self.vida = max(0, self.vida - dano)

    def curar(self, valor):
        self.vida = min(self.vida_max, self.vida + valor)

    def calcular_dano(self, skill_multiplicador=1.0):
        base = random.uniform(0.85, 1.0) * self.ataque * skill_multiplicador
        return int(base)

    def desenhar(self, com_barra_vida=True):
        screen.blit(self.imagem, self.pos)
        # Nome centralizado
        txt_nome = fonte.render(self.nome, True, BRANCO)
        nome_x = self.pos[0] + self.imagem.get_width() // 2 - txt_nome.get_width() // 2
        screen.blit(txt_nome, (nome_x, self.pos[1] - 30))
        if com_barra_vida:
            self.desenhar_barra_vida()

    def desenhar_barra_vida(self):
        largura_barra = self.imagem.get_width()
        altura_barra = 15
        x = self.pos[0]
        y = self.pos[1] - 10

        if self.vida_barras == 1:
            proporcao = self.vida / self.vida_max
            # Fundo
            pygame.draw.rect(screen, CINZA, (x, y, largura_barra, altura_barra))
            # Cor conforme vida
            cor = VERDE if proporcao > 0.5 else AMARELO if proporcao > 0.2 else VERMELHO
            pygame.draw.rect(screen, cor, (x, y, int(largura_barra * proporcao), altura_barra))
            pygame.draw.rect(screen, BRANCO, (x, y, largura_barra, altura_barra), 2)
        else:
            # Desenha as 3 barras para o dragão
            for i in range(self.vida_barras):
                barra_x = x + i * (largura_barra // self.vida_barras + 5)
                vida_na_barra = max(0, min(self.vida_por_barra, self.vida - i * self.vida_por_barra))
                proporcao = vida_na_barra / self.vida_por_barra
                # Fundo barra
                pygame.draw.rect(screen, CINZA, (barra_x, y, largura_barra // self.vida_barras, altura_barra))
                # Cor da barra
                cor = VERDE if proporcao > 0.5 else AMARELO if proporcao > 0.2 else VERMELHO
                largura_atual = int((largura_barra // self.vida_barras) * proporcao)
                pygame.draw.rect(screen, cor, (barra_x, y, largura_atual, altura_barra))
                pygame.draw.rect(screen, BRANCO, (barra_x, y, largura_barra // self.vida_barras, altura_barra), 2)

# --- Botão para interação ---
class Botao:
    def __init__(self, texto, x, y, largura=180, altura=50, cor_fundo=AZUL, cor_texto=BRANCO, cor_selecionado=ROXO):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.cor_fundo = cor_fundo
        self.cor_texto = cor_texto
        self.cor_selecionado = cor_selecionado
        self.selecionado = False

    def desenhar(self):
        cor = self.cor_selecionado if self.selecionado else self.cor_fundo
        pygame.draw.rect(screen, cor, self.rect, border_radius=8)
        txt = fonte.render(self.texto, True, self.cor_texto)
        txt_rect = txt.get_rect(center=self.rect.center)
        screen.blit(txt, txt_rect)

    def clicado(self, pos):
        return self.rect.collidepoint(pos)

# --- Funções de texto (consolidadas) ---
def mostrar_texto(texto, espera_espaco=True, posicao="inferior"):
    if posicao == "inferior":
        # Desenha o fundo do jogo normal
        screen.blit(img_fundo, (0, 0))
        
        # Cria uma área semi-transparente para o texto
        overlay = pygame.Surface((LARGURA, 140), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, ALTURA - 140))
        
        linhas = texto.split('\n')
        for i, linha in enumerate(linhas):
            txt = fonte.render(linha, True, BRANCO)
            screen.blit(txt, (20, ALTURA - 130 + i * 30))
    else:  # Tela cheia (para mostrar_texto_tela)
        screen.blit(img_historia_fundo, (0, 0))
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        linhas = texto.split('\n')
        for i, linha in enumerate(linhas):
            txt = fonte.render(linha, True, BRANCO)
            screen.blit(txt, (LARGURA//2 - txt.get_width()//2, 150 + i * 30))
    
    pygame.display.flip()
    
    if espera_espaco:
        esperando = True
        while esperando:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    esperando = False
            clock.tick(30)

def mostrar_texto_tela(texto, botao_texto="Continuar"):
    rodando = True
    botao = Botao(botao_texto, LARGURA//2 - 90, ALTURA - 100, 180, 50)
    
    mostrar_texto(texto, False, "tela")
    botao.desenhar()
    pygame.display.flip()

    while rodando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if botao.clicado(pos):
                    rodando = False
            if event.type == pygame.MOUSEMOTION:
                pos = event.pos
                botao.selecionado = botao.clicado(pos)
        
        clock.tick(30)

# --- Funções de progresso ---
def salvar_progresso(nome, classe, vida_atual):
    with open("savegame.txt", "w") as arquivo:
        arquivo.write(f"{nome}\n{classe}\n{vida_atual}\n")

def carregar_progresso():
    if not os.path.exists("savegame.txt"):
        return None
    try:
        with open("savegame.txt", "r") as arquivo:
            linhas = arquivo.read().splitlines()
            return (linhas[0], linhas[1], int(linhas[2])) if len(linhas) >= 3 else None
    except:
        return None

# --- Menu inicial ---
def menu_inicial():
    rodando = True
    textos = ["Novo Jogo", "Continuar"]
    largura_botao = 200
    altura_botao = 60
    espacamento = 40
    total_largura = len(textos) * largura_botao + (len(textos)-1)*espacamento
    start_x = (LARGURA - total_largura) // 2
    y = ALTURA // 2
    botoes = [Botao(texto, start_x + i*(largura_botao + espacamento), y, largura_botao, altura_botao) 
              for i, texto in enumerate(textos)]

    while rodando:
        screen.blit(img_historia_fundo, (0, 0))
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        titulo = fonte_grande.render("NexBlade", True, BRANCO)
        screen.blit(titulo, (LARGURA//2 - titulo.get_width()//2, ALTURA//4))
        
        for bot in botoes:
            bot.desenhar()
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                for bot in botoes:
                    if bot.clicado(pos):
                        if bot.texto == "Novo Jogo":
                            return None
                        elif bot.texto == "Continuar":
                            progresso = carregar_progresso()
                            if progresso:
                                return progresso
                            mostrar_texto_tela("Nenhum progresso encontrado.\nIniciando novo jogo.", "Continuar")
                            return None
        clock.tick(30)

# --- Função auxiliar para escolher classe por nome ---
def escolher_classe_por_nome(classe_nome):
    classes = {
        "Espadachim": {
            "vida_max": 280,
            "ataque": 75,
            "defesa": 65,
            "skills": {
                "Fúria Relâmpago": (1.3, "Corte rápido (+30% dano) - 3 turnos de recarga"),
                "Corte do Dragão": (2.0, "Golpe devastador (+100% dano) - 5 turnos de recarga"),
                "Lâmina do Juízo": (2.5, "Ataque final (+150% dano) - Único por batalha")
            },
            "imagem": img_espadachim,
            "pos": (150, 200)
        },
        "Feiticeiro": {
            "vida_max": 180,
            "ataque": 85,
            "defesa": 35,
            "skills": {
                "Chama Arcana": (1.5, "Queima o inimigo por 3 turnos"),
                "Gelo Abissal": (1.8, "Congela e reduz velocidade do inimigo"),
                "Explosão do Caos": (2.2, "Dano massivo em área - Alta recarga")
            },
            "imagem": img_feiticeiro,
            "pos": (150, 200)
        },
        "Arqueiro": {
            "vida_max": 200,
            "ataque": 80,
            "defesa": 50,
            "skills": {
                "Flecha Venenosa": (1.2, "Envenena o alvo por 3 turnos"),
                "Chuva Letal": (1.6, "Tempestade de flechas em área"),
                "Flecha Solar": (2.0, "Flecha explosiva com chance de crítico")
            },
            "imagem": img_arqueiro,
            "pos": (150, 200)
        },
        "Tanque": {
            "vida_max": 300,
            "ataque": 50,
            "defesa": 80,
            "skills": {
                "Martelo Sísmico": (1.1, "Treme a terra, pode atordoar"),
                "Escudo Inabalável": (0.0, "Aumenta defesa por 3 turnos"),
                "Investida Colossal": (1.4, "Empurra o inimigo com força")
            },
            "imagem": img_tanque,
            "pos": (150, 200)
        }
    }
    return classe_nome, classes[classe_nome]

# --- Função para escolher a classe do jogador ---
def escolher_classe():
    rodando = True
    classes = {
        "Espadachim": {
            "vida_max": 280,
            "ataque": 75,
            "defesa": 65,
            "skills": {
                "Fúria Relâmpago": (1.3, "Corte rápido (+30% dano) - 3 turnos de recarga"),
                "Corte do Dragão": (2.0, "Golpe devastador (+100% dano) - 5 turnos de recarga"),
                "Lâmina do Juízo": (2.5, "Ataque final (+150% dano) - Único por batalha")
            },
            "imagem": img_espadachim
        },
        "Feiticeiro": {
            "vida_max": 180,
            "ataque": 85,
            "defesa": 35,
            "skills": {
                "Chama Arcana": (1.5, "Queima o inimigo por 3 turnos"),
                "Gelo Abissal": (1.8, "Congela e reduz velocidade do inimigo"),
                "Explosão do Caos": (2.2, "Dano massivo em área - Alta recarga")
            },
            "imagem": img_feiticeiro
        },
        "Arqueiro": {
            "vida_max": 200,
            "ataque": 80,
            "defesa": 50,
            "skills": {
                "Flecha Venenosa": (1.2, "Envenena o alvo por 3 turnos"),
                "Chuva Letal": (1.6, "Tempestade de flechas em área"),
                "Flecha Solar": (2.0, "Flecha explosiva com chance de crítico")
            },
            "imagem": img_arqueiro
        },
        "Tanque": {
            "vida_max": 300,
            "ataque": 50,
            "defesa": 80,
            "skills": {
                "Martelo Sísmico": (1.1, "Treme a terra, pode atordoar"),
                "Escudo Inabalável": (0.0, "Aumenta defesa por 3 turnos"),
                "Investida Colossal": (1.4, "Empurra o inimigo com força")
            },
            "imagem": img_tanque
        }
    }