import numpy as np
import cv2 as cv
from scipy import fftpack

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
    colores_compressed = []
    strcolores_compressed = ""

    actual = new_colores[0, 0]
    anterior = actual
    for i in range(imsize[0]):
    
       contador = 0
    
       for j in range(imsize[1]):
        
           actual = new_colores[i, j]
        
           if (new_colores[i, j] == anterior):
            
              contador += 1
        
           else:
            
              colores_compressed.append(contador)
              colores_compressed.append(anterior)
              strcolores_compressed += str(contador) + "!" + str(anterior) + "!"
              anterior = actual
              
    return strcolores_compressed

def decode(message):
    #
    # Reemplaza la linea 24...
    #
    message_decode = message.split("!")
    lista = [message_decode[i:i+64] for i in range(0,len(message_decode),64)]
    lista_bloques=[]
    for i in lista:
       lista_bloques.append([i[j:j+8] for j in range(0,len(i),8)])
    #frame = np.frombuffer(bytes(memoryview(message)), dtype='uint8').reshape(480, 848)
    #
    # ...con tu implementación del bloque receptor: decodificador + transformación inversa
    #    
    return frame
    

