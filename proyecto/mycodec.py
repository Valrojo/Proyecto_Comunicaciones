import numpy as np
import cv2 as cv
from scipy import fftpack
from scipy.signal import medfilt
from collections import Counter
import heapq
import json

def denoise(frame):
    # Función que elimina el ruido de la imagen
    def create_mask(dims, frequency, size=10):
       freq_int = int(frequency*dims[0])
       mask = np.ones(shape=(dims[0], dims[1]))
       mask[dims[0]//2-size-freq_int:dims[0]//2+size-freq_int,dims[1]//2-size:dims[1]//2+size] = 0
       mask[dims[0]//2-size+freq_int:dims[0]//2+size+freq_int, dims[1]//2-size:dims[1]//2+size] = 0
       
       return mask
    
    S_img= fftpack.fftshift(fftpack.fft2(frame))
    espectro_filtrado = S_img*create_mask(S_img.shape, 0.06)
    
    frame = np.real(fftpack.ifft2(fftpack.ifftshift(espectro_filtrado)))
    
    #filtro sal y pimienta
    img_filtered = medfilt(frame, 5)
           
    return img_filtered

def code(img_filtered):
    #
    # Implementa en esta función el bloque transmisor: Transformación + Cuantización + Codificación de fuente
    #
    # Se recorre la imagen en bloques de 8x8
    imsize = img_filtered.shape
    colores_matrix = np.zeros(shape=imsize)
    for i in range(0, imsize[0], 8):
       for j in range(0, imsize[1], 8):
       
          colores_matrix[i:(i+8),j:(j+8)] = img_filtered[i:(i+8),j:(j+8)]
    
    colores_matrix = colores_matrix.astype(int)
    m = 7
    new_colores = np.array([x-x%m for x in colores_matrix])
    #Se comprimen en una lista de largo flexible
    colores_list= np.concatenate(new_colores.tolist())
    def compress(l):
       acum = 0
       vAcum = []
       lcomp = []
       for i in range(len(l)):
           if (i + 1) < len(l) and l[i] == l[i+1]:
              acum += 1
              vAcum = [acum, l[i]]
              continue
           if vAcum:
              vAcum[0] += 1
              lcomp.append(vAcum[0])
              lcomp.append(vAcum[1])
              vAcum = []
              acum = 0
           else:
              lcomp.append(1)
              lcomp.append(l[i])
       return lcomp
    strcolores_compressed = compress(colores_list)  
    p = np.linspace(0.01, 0.99, num=100)
    H = -p*np.log2(p) - (1-p)*np.log2(1-p)
 

    # Construir dendograma con las probabilidades ordenadas
    dendograma = [[frequencia/len(strcolores_compressed), [simbolo, ""]] for simbolo, frequencia in Counter(strcolores_compressed).items()]
    heapq.heapify(dendograma)
    
    def take_second(elem):
       return len(elem[1])
          
    # Crear el código
    while len(dendograma) > 1:
       lo = heapq.heappop(dendograma)
       hi = heapq.heappop(dendograma)
       for codigo in lo[1:]:
          codigo[1] = '0' + codigo[1]
       for codigo in hi[1:]:
          codigo[1] = '1' + codigo[1]
       heapq.heappush(dendograma, [lo[0] + hi[0]] + lo[1:] + hi[1:])

    # Convertir código a diccionario
    dendograma=sorted(heapq.heappop(dendograma)[1:],key=take_second)
    dendograma = {simbolo : codigo for simbolo, codigo in dendograma} 

    strcolores_compressed_codificado = ""
    for letra in strcolores_compressed:
        strcolores_compressed_codificado += dendograma[letra]
    #json
    message=[str(dendograma),strcolores_compressed_codificado]
    message_json = json.dumps(message)
    
    return message_json

def decode(message_json):

    message_rec = json.loads(message_json)
    dendograma_rec=eval(message_rec[0])
    strcolores_compressed_codificado_rec=message_rec[1]
    colores_compressed_rec=[]
    lista_valores = list(dendograma_rec.values())
    lista_llaves = list(dendograma_rec.keys())
    i=0
    cont=len(strcolores_compressed_codificado_rec)
    while(len(strcolores_compressed_codificado_rec)!=0):
       if(lista_valores[i]==strcolores_compressed_codificado_rec[:len(lista_valores[i])]):
          colores_compressed_rec.append(lista_llaves[i])
          strcolores_compressed_codificado_rec=strcolores_compressed_codificado_rec[len(lista_valores[i]):]
          i=0
       else:
          i+=1

    seq = colores_compressed_rec
    lista_decompressed = []
    for i in range(0,len(seq),2):
       for j in range(seq[i]):
          lista_decompressed.append(seq[i+1])
    lista = [lista_decompressed[i:i+64] for i in range(0,len(lista_decompressed),64)]

    while (len(lista)%8 != 0):
       lista.append(lista[-1])
    lista2=[]
    for i in lista:
       lista2.append([i[j:j+8] for j in range(0,len(i),8)])
    lista3 = np.asarray(lista2)
    lista3 = lista3.reshape(480,848)

    return lista3
    

