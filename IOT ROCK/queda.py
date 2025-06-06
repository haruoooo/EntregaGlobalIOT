import cv2
import mediapipe as mp
import numpy as np
import screen_brightness_control as sbc
import time


# Limitar para detectar a queda de brilho (ex: 0.7 = queda de 30%)
LIMIAR_QUEDA_BRILHO = 0.7
# Níveis de brilho do monitor (0 a 100)
BRILHO_MAXIMO = 100
BRILHO_PADRAO = 50
# Tempo de "cooldown" em segundos após um gesto para evitar detecções múltiplas
COOLDOWN_GESTO = 3.0

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# Variáveis de estado
brilho_anterior = 128  # Começa com um valor médio
status_brilho = "Padrão"
ultimo_gesto_tempo = 0

# Função para verificar se a mão é um punho fechado
def is_fist_closed(hand_landmarks):
    #Verifica se a mão está fechada comparando a posição Y dos dedos com as juntas.
    # Pontas dos dedos (polegar é mais complexo, então focamos nos outros 4)
    tip_ids = [8, 12, 16, 20]
    # Juntas inferiores (base dos dedos)
    dip_ids = [6, 10, 14, 18]

    for i in range(len(tip_ids)):
        # Se a ponta do dedo (tip) estiver acima da junta (dip), a mão está aberta
        if hand_landmarks.landmark[tip_ids[i]].y < hand_landmarks.landmark[dip_ids[i]].y:
            return False
    return True

print("Assistente de Brilho iniciado. Pressione a tecla 'q' para sair.")
# Define o brilho inicial como padrão
try:
    sbc.set_brightness(BRILHO_PADRAO)
except Exception as e:
    print(f"Não foi possível ajustar o brilho inicial: {e}")


while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignorando quadro vazio da câmera.")
        continue
    
    #visualização tipo espelho
    image = cv2.flip(image, 1)
    
    #Análise de Brilho
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brilho_atual = np.mean(gray_image)
    
    # Verifica se houve uma queda brusca e o brilho ainda não está no máximo
    if brilho_atual < (brilho_anterior * LIMIAR_QUEDA_BRILHO) and status_brilho != "Máximo":
        print(f"Queda de brilho detectada! Brilho médio: {int(brilho_atual)}")
        try:
            sbc.set_brightness(BRILHO_MAXIMO)
            status_brilho = "Máximo"
            print("Brilho da tela aumentado para 100%.")
        except Exception as e:
            print(f"Erro ao ajustar o brilho: {e}")

    # Atualiza o brilho anterior para a próxima iteração
    brilho_anterior = brilho_atual

    
    # Converte a imagem de BGR para RGB para o MediaPipe
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    
    tempo_atual = time.time()
    
    # Verifica se uma mão foi detectada e se o cooldown já passou
    if results.multi_hand_landmarks and (tempo_atual - ultimo_gesto_tempo > COOLDOWN_GESTO):
        for hand_landmarks in results.multi_hand_landmarks:
            # Desenha os landmarks na imagem para feedback
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            if is_fist_closed(hand_landmarks):
                print("Punho fechado detectado!")
                try:
                    sbc.set_brightness(BRILHO_PADRAO)
                    status_brilho = "Padrao (reset por gesto)"
                    print("Brilho da tela retornado ao padrao.")
                    ultimo_gesto_tempo = tempo_atual # Reinicia o cooldown
                except Exception as e:
                    print(f"Erro ao ajustar o brilho: {e}")
                # Interrompe o loop de mãos para evitar processamento duplo
                break 

    # Mostra o status na tela
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
# Opcional: retornar o brilho ao padrão ao fechar a mão
try:
    sbc.set_brightness(BRILHO_PADRAO)
    print("Brilho retornado ao padrão ao finalizar.")
except Exception as e:
    print(f"Não foi possível ajustar o brilho ao finalizar: {e}")