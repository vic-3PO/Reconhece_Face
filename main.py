import cv2
from deepface import DeepFace
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time
import uuid


PASTAS_NIVEIS = {
    1: "img/1/",
    2: "img/2/",
    3: "img/3/"
}


LIMITE_IMAGENS = 5


for pasta in PASTAS_NIVEIS.values():
    os.makedirs(pasta, exist_ok=True)

def salvar_imagem_capturada(frame, nivel_seguranca):
    """Salva a imagem capturada em um diretório específico para o nível de segurança e mantém um limite de 5 imagens."""
    pasta_nivel = PASTAS_NIVEIS[nivel_seguranca]
    
    
    imagens_existentes = sorted(os.listdir(pasta_nivel), key=lambda x: os.path.getctime(os.path.join(pasta_nivel, x)))
    
    
    if len(imagens_existentes) >= LIMITE_IMAGENS:
        imagem_mais_antiga = imagens_existentes[0]
        os.remove(os.path.join(pasta_nivel, imagem_mais_antiga))
        print(f"Imagem removida: {imagem_mais_antiga}")

    
    nome_imagem = f"{uuid.uuid4()}.jpg"
    caminho_completo = os.path.join(pasta_nivel, nome_imagem)

    
    cv2.imwrite(caminho_completo, frame)
    print(f"Imagem capturada salva em: {caminho_completo}")

def calcular_media_similaridade(imagem_path, nivel_seguranca):
    """Compara a imagem fornecida com todas as imagens existentes para o nível de segurança e calcula a média de similaridade."""
    pasta_nivel = PASTAS_NIVEIS[nivel_seguranca]
    imagens_existentes = [os.path.join(pasta_nivel, img) for img in os.listdir(pasta_nivel)]

    similaridades = []

    for img_referencia in imagens_existentes:
        try:
            result = DeepFace.verify(img1_path=imagem_path, img2_path=img_referencia, enforce_detection=False)
            similaridade = 1 - result["distance"]  
            similaridades.append(similaridade)
        except Exception as e:
            print(f"Erro ao comparar com {img_referencia}: {str(e)}")

    if similaridades:
        media_similaridade = sum(similaridades) / len(similaridades)
        return media_similaridade
    else:
        return 0

def reconhecer_com_camera_ou_imagens(nivel_seguranca, usar_camera=True):
    """Realiza o reconhecimento facial com a câmera ou imagem e calcula a média de similaridade com imagens existentes."""
    
    if usar_camera:
        max_tentativas = 5 if nivel_seguranca == 1 else (3 if nivel_seguranca == 2 else 1)
        video_capture = cv2.VideoCapture(0)

        if not video_capture.isOpened():
            messagebox.showerror("Erro", "Câmera não detectada! Selecione uma imagem manualmente.")
            return

        tentativas = 0
        reconhecido = False

        while tentativas < max_tentativas and not reconhecido:
            contagem_regressiva(3)
            ret, frame = video_capture.read()

            if not ret:
                print("Erro ao acessar a câmera. Tentativa:", tentativas + 1)
                tentativas += 1
                continue

            
            cv2.imshow('Camera', frame)

            
            frame_path = "frame_atual.jpg"
            cv2.imwrite(frame_path, frame)

            
            media_similaridade = calcular_media_similaridade(frame_path, nivel_seguranca)

            if media_similaridade >= 0.4:  
                messagebox.showinfo("Sucesso", f"Acesso concedido! Média de similaridade: {media_similaridade:.2f}")
                salvar_imagem_capturada(frame, nivel_seguranca)
                reconhecido = True
            else:
                messagebox.showwarning("Falha", f"Tentativa {tentativas + 1} falhou. Similaridade média: {media_similaridade:.2f}")

            tentativas += 1

        if not reconhecido:
            messagebox.showwarning("Falha", "Máximo de tentativas atingido. Acesso negado.")

        video_capture.release()
        cv2.destroyAllWindows()

    else:
        
        label_timer.config(text="Abrindo explorador de arquivos para selecionar uma imagem...", fg="yellow")
        root.update()

        
        caminho_imagem = filedialog.askopenfilename(title="Selecione uma imagem para verificação", filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        
        if not caminho_imagem:
            messagebox.showerror("Erro", "Nenhuma imagem selecionada.")
            label_timer.config(text="Nenhuma imagem selecionada", fg="red")
            return

        
        label_timer.config(text="Verificando similaridade da imagem selecionada...", fg="yellow")
        root.update()

        media_similaridade = calcular_media_similaridade(caminho_imagem, nivel_seguranca)

        if media_similaridade >= 0.4:
            messagebox.showinfo("Sucesso", f"Acesso concedido! Média de similaridade: {media_similaridade:.2f}")
            label_timer.config(text="Acesso concedido!", fg="green")
        else:
            messagebox.showwarning("Falha", f"Similaridade insuficiente. Média de similaridade: {media_similaridade:.2f}")
            label_timer.config(text="Acesso negado", fg="red")

def contagem_regressiva(segundos):
    for i in range(segundos, 0, -1):
        label_timer.config(text=f"Tirando foto em: {i}s")
        root.update()
        time.sleep(1)
    label_timer.config(text="Capturando imagem...")

def iniciar_reconhecimento(nivel_seguranca, usar_camera=True):
    reconhecer_com_camera_ou_imagens(nivel_seguranca, usar_camera)


root = tk.Tk()
root.title("Sistema de Reconhecimento Facial - Governo Secreto")
root.geometry("700x500")
root.config(bg="black")

style_terminal = {
    "bg": "black",
    "fg": "green",
    "font": ("Courier", 12)
}

titulo = tk.Label(root, text="ACESSO RESTRITO - GOVERNO FEDERAL", **style_terminal)
titulo.pack(pady=10)

mensagem_alerta = tk.Label(root, text="Escolha seu nível de segurança e insira sua credencial facial.", **style_terminal)
mensagem_alerta.pack(pady=5)

label_referencia = tk.Label(root, text="Nenhuma imagem de referência selecionada", **style_terminal)
label_referencia.pack(pady=10)


nivel1_btn = tk.Button(root, text="Nível de Segurança 1 (Câmera)", command=lambda: iniciar_reconhecimento(1, usar_camera=True), bg="gray", fg="white", font=("Courier", 12))
nivel1_btn.pack(pady=5)

nivel2_btn = tk.Button(root, text="Nível de Segurança 2 (Câmera)", command=lambda: iniciar_reconhecimento(2, usar_camera=True), bg="gray", fg="white", font=("Courier", 12))
nivel2_btn.pack(pady=5)

nivel3_btn = tk.Button(root, text="Nível de Segurança 3 (Câmera)", command=lambda: iniciar_reconhecimento(3, usar_camera=True), bg="gray", fg="white", font=("Courier", 12))
nivel3_btn.pack(pady=5)


nivel1_btn_foto = tk.Button(root, text="Nível de Segurança 1 (Imagem)", command=lambda: iniciar_reconhecimento(1, usar_camera=False), bg="gray", fg="white", font=("Courier", 12))
nivel1_btn_foto.pack(pady=5)

nivel2_btn_foto = tk.Button(root, text="Nível de Segurança 2 (Imagem)", command=lambda: iniciar_reconhecimento(2, usar_camera=False), bg="gray", fg="white", font=("Courier", 12))
nivel2_btn_foto.pack(pady=5)

nivel3_btn_foto = tk.Button(root, text="Nível de Segurança 3 (Imagem)", command=lambda: iniciar_reconhecimento(3, usar_camera=False), bg="gray", fg="white", font=("Courier", 12))
nivel3_btn_foto.pack(pady=5)

label_timer = tk.Label(root, text="", **style_terminal)
label_timer.pack(pady=10)

rodape = tk.Label(root, text="Sistema Secreto - Nível Máximo de Segurança", **style_terminal)
rodape.pack(side=tk.BOTTOM, pady=20)

root.mainloop()
