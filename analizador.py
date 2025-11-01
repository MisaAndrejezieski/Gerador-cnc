import re
from tkinter import messagebox
import matplotlib.pyplot as plt

class AnalisadorGCode:
    def analisar_gcode(self, caminho_arquivo):
        total_linhas=0; movimentos_g0=0; movimentos_g1=0; velocidades=[]; alturas_z=[]
        try:
            with open(caminho_arquivo,"r") as f:
                for linha in f:
                    linha = linha.strip()
                    if not linha or linha.startswith(";"): continue
                    total_linhas += 1
                    if linha.upper().startswith("G0"): movimentos_g0+=1
                    elif linha.upper().startswith("G1"): movimentos_g1+=1
                    match_f = re.search(r'F([\d.]+)',linha,re.IGNORECASE)
                    if match_f: velocidades.append(float(match_f.group(1)))
                    match_z = re.search(r'Z(-?[\d.]+)',linha,re.IGNORECASE)
                    if match_z: alturas_z.append(float(match_z.group(1)))
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao ler G-code: {e}"); return

        velocidade_max=max(velocidades) if velocidades else 0
        velocidade_min=min(velocidades) if velocidades else 0
        velocidade_media=sum(velocidades)/len(velocidades) if velocidades else 0
        altura_max=max(alturas_z) if alturas_z else 0
        altura_min=min(alturas_z) if alturas_z else 0

        msg=(f"Total de linhas: {total_linhas}\nMovimentos G0: {movimentos_g0}\n"
             f"Movimentos G1: {movimentos_g1}\nVelocidade máxima(F): {velocidade_max}\n"
             f"Velocidade mínima(F): {velocidade_min}\nVelocidade média(F): {velocidade_media:.2f}\n"
             f"Altura máxima(Z): {altura_max}\nAltura mínima(Z): {altura_min}")
        messagebox.showinfo("Resumo do G-code", msg)

        if velocidades and alturas_z:
            plt.figure(figsize=(12,5))
            plt.subplot(1,2,1)
            plt.plot(velocidades, color='blue'); plt.title("Velocidade F"); plt.xlabel("Linha"); plt.ylabel("F")
            plt.subplot(1,2,2)
            plt.plot(alturas_z, color='green'); plt.title("Altura Z"); plt.xlabel("Linha"); plt.ylabel("Z")
            plt.tight_layout(); plt.show()
