# Feito por:

Gabriel Toledo RM:551654 |
João Saborido RM: 98184 |
Matheus Haruo RM: 97663 

# Problema:
Em situações de queda de energia ou ao apagar as luzes de um ambiente, a tela do computador se torna a única fonte de luz. No entanto, o brilho geralmente está em um nível baixo ou intermediário, dificultando a visualização do teclado, do mouse ou do ambiente ao redor. Ajustar o brilho manualmente no escuro pode ser uma tarefa difícil e demorada.

Este projeto foi criado para resolver esse problema, oferecendo uma solução automática e inteligente que reage instantaneamente a mudanças de luminosidade e permite o controle por um simples gesto.

Além disso, nosso projeto está preparado para futuras melhorias, com potencial de expansão para além do notebook, podendo ser implementado em diversos dispositivos eletrônicos.

# Solução:
Ao detectar uma queda súbita de luz, ele automaticamente eleva o brilho da tela para o nível máximo, iluminando o espaço e o teclado imediatamente.

Para devolver o controle ao usuário de forma intuitiva, o sistema também utiliza reconhecimento de gestos. Se o usuário desejar reduzir o brilho novamente, basta fechar a mão em um punho na frente da câmera, e o brilho retornará ao nível padrão pré-definido.

# Requisitos:
Instalar : pip install opencv-python mediapipe numpy screen-brightness-control
Python: Necessário ser a versão 3.10 ou inferior.

# Como executar?:
Comando "python queda.py"

# Link do vídeo:
https://youtu.be/qzrCabCQUq0

# Código Fonte:
import cv2
import mediapipe as mp
import numpy as np
import screen_brightness_control as sbc
import time

LIMIAR_QUEDA_BRILHO = 0.7
BRILHO_MAXIMO = 100
BRILHO_PADRAO = 50
COOLDOWN_GESTO = 3.0

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

brilho_anterior = 128
status_brilho = "Padrão"
ultimo_gesto_tempo = 0

def is_fist_closed(hand_landmarks):
    tip_ids = [8, 12, 16, 20]
    dip_ids = [6, 10, 14, 18]

    for i in range(len(tip_ids)):
        if hand_landmarks.landmark[tip_ids[i]].y < hand_landmarks.landmark[dip_ids[i]].y:
            return False
    return True

print("Assistente de Brilho iniciado. Pressione 'q' para sair.")
try:
    sbc.set_brightness(BRILHO_PADRAO)
except Exception as e:
    print(f"Não foi possível ajustar o brilho inicial: {e}")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignorando quadro vazio da câmera.")
        continue

    image = cv2.flip(image, 1)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brilho_atual = np.mean(gray_image)

    if brilho_atual < (brilho_anterior * LIMIAR_QUEDA_BRILHO) and status_brilho != "Máximo":
        print(f"Queda de brilho detectada! Brilho médio: {int(brilho_atual)}")
        try:
            sbc.set_brightness(BRILHO_MAXIMO)
            status_brilho = "Máximo"
            print("Brilho da tela aumentado para 100%.")
        except Exception as e:
            print(f"Erro ao ajustar o brilho: {e}")

    brilho_anterior = brilho_atual

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    
    tempo_atual = time.time()
    
    if results.multi_hand_landmarks and (tempo_atual - ultimo_gesto_tempo > COOLDOWN_GESTO):
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            if is_fist_closed(hand_landmarks):
                print("Punho fechado detectado!")
                try:
                    sbc.set_brightness(BRILHO_PADRAO)
                    status_brilho = "Padrão (reset por gesto)"
                    print("Brilho da tela retornado ao padrão.")
                    ultimo_gesto_tempo = tempo_atual
                except Exception as e:
                    print(f"Erro ao ajustar o brilho: {e}")
                break

    texto_status = f"Status: {status_brilho}"
    texto_brilho_medio = f"Brilho Ambiente (0-255): {int(brilho_atual)}"
    
    cv2.putText(image, texto_status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(image, texto_brilho_medio, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    cv2.imshow('Assistente de Brilho | Pressione "q" para sair', image)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

hands.close()
cap.release()
cv2.destroyAllWindows()

try:
    sbc.set_brightness(BRILHO_PADRAO)
    print("Brilho retornado ao padrão ao finalizar.")
except Exception as e:
    print(f"Não foi possível ajustar o brilho ao finalizar: {e}")

