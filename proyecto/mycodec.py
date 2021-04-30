import numpy as np
import cv2 as cv
from scipy import fftpack
from scipy.signal import medfilt

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
    m = 5
    new_colores = np.array([x-x%m for x in colores_matrix])
    #Se comprimen en una lista de largo flexible
    strcolores_compressed = ""

    actual = new_colores[0, 0]
    anterior = actual
    contador = 0

    for i in range(imsize[0]):
    
       for j in range(imsize[1]):
        
          actual = new_colores[i, j]
        
          if (actual == anterior):
            
             contador += 1
        
          else:
             strcolores_compressed += str(contador) + "!" + str(anterior) + "!"
             anterior = actual
             contador = 1
            
    if (strcolores_compressed[-2] == str(actual)):
        
       strcolores_compressed += str(contador) + '!' + str(actual) + '!'
  

    return strcolores_compressed

def decode(message):
    #
    # Reemplaza la linea 24...
    #
    seq = message.split("!")
    seq.pop()

    lista_decompressed = []
    for i in range(0,len(seq),2):
       for j in range(int(seq[i])):
          lista_decompressed.append(int(seq[i+1]))
        
    while (len(lista_decompressed)%64 != 0):
       lista_decompressed.append(1)
    lista = [lista_decompressed[i:i+64] for i in range(0,len(lista_decompressed),64)]
    lista2=[]
    for i in lista:
       lista2.append([i[j:j+8] for j in range(0,len(i),8)])
    
    lista3 = np.asarray(lista2)

    lista3 = lista3.reshape(480,848)

    return lista3
    

