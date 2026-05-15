import fitz  # PyMuPDF
import qrcode
from io import BytesIO

PLACEHOLDERS_REQUERIDOS = ["{{NOMBRE COMPLETO PARTICIPANTE}}", "{{CURSO}}", "{{QR}}"]

def calcular_coordenadas_y_fuente_hoja(rect_placeholder, texto, ancho_pagina, fontname="helv", base_fontsize=24):
    """
    Calcula dinámicamente el tamaño de la fuente y las coordenadas.
    """
    fontsize_calculado = base_fontsize
    margen = 60 
    
    
    centro_x = (rect_placeholder.x0 + rect_placeholder.x1) / 2.0
    
    
    distancia_izq = centro_x - margen
    distancia_der = (ancho_pagina - margen) - centro_x
    
    
    distancia_izq = max(distancia_izq, 10)
    distancia_der = max(distancia_der, 10)
    
    
    ancho_maximo_permitido = 2 * min(distancia_izq, distancia_der)
    
    
    ancho_texto = fitz.get_text_length(texto, fontname=fontname, fontsize=fontsize_calculado)
    
    
    if ancho_texto > ancho_maximo_permitido:
        fontsize_calculado = fontsize_calculado * (ancho_maximo_permitido / ancho_texto)
        ancho_texto = fitz.get_text_length(texto, fontname=fontname, fontsize=fontsize_calculado)
        
    
    inicio_x = centro_x - (ancho_texto / 2.0)
    
    
    centro_y = (rect_placeholder.y0 + rect_placeholder.y1) / 2.0
    inicio_y = centro_y + (fontsize_calculado / 3.0)
    
    return fitz.Point(inicio_x, inicio_y), fontsize_calculado

def calcular_rectangulo_qr_desplazado(rect_placeholder, ancho_pagina, alto_pagina, tamano_ideal=100):
    """
    Calcula un rectángulo cuadrado perfecto (100x100).
    Intenta centrarlo en el placeholder original, pero si choca con los márgenes,
    lo "desliza" hacia adentro de la hoja para mantener su tamaño intacto sin cortarse.
    """
    margen_seguridad = 60
    mitad = tamano_ideal / 2.0
    
    # 1. Encontrar el centro original dictado por la etiqueta
    centro_x = (rect_placeholder.x0 + rect_placeholder.x1) / 2.0
    centro_y = (rect_placeholder.y0 + rect_placeholder.y1) / 2.0
    
    # 2. Crear las coordenadas iniciales del QR ideal (100x100)
    x0 = centro_x - mitad
    x1 = centro_x + mitad
    y0 = centro_y - mitad
    y1 = centro_y + mitad
    
    # 3. Deslizamiento Horizontal (Proteger Eje X)
    if x0 < margen_seguridad:
        # Está chocando con el margen izquierdo -> Lo empujamos a la derecha
        desplazamiento = margen_seguridad - x0
        x0 += desplazamiento
        x1 += desplazamiento
    elif x1 > (ancho_pagina - margen_seguridad):
        # Está chocando con el margen derecho -> Lo empujamos a la izquierda
        desplazamiento = x1 - (ancho_pagina - margen_seguridad)
        x0 -= desplazamiento
        x1 -= desplazamiento
        
    # 4. Deslizamiento Vertical (Proteger Eje Y)
    if y0 < margen_seguridad:
        # Está chocando con el margen superior -> Lo empujamos hacia abajo
        desplazamiento = margen_seguridad - y0
        y0 += desplazamiento
        y1 += desplazamiento
    elif y1 > (alto_pagina - margen_seguridad):
        # Está chocando con el margen inferior -> Lo empujamos hacia arriba
        desplazamiento = y1 - (alto_pagina - margen_seguridad)
        y0 -= desplazamiento
        y1 -= desplazamiento
        
    return fitz.Rect(x0, y0, x1, y1)

def validar_plantilla(plantilla_bytes: bytes) -> dict:
    documento = fitz.open(stream=plantilla_bytes, filetype="pdf")
    pagina = documento[0]
    encontrados = []
    faltantes = []
    
    for ph in PLACEHOLDERS_REQUERIDOS:
        if pagina.search_for(ph):
            encontrados.append(ph)
        else:
            faltantes.append(ph)
            
    documento.close()
    
    return {
        "es_valida": len(faltantes) == 0,
        "placeholders_encontrados": encontrados,
        "placeholders_faltantes": faltantes
    }

def procesar_pdf(nombre: str, curso: str, url_validacion: str, plantilla_bytes: bytes) -> bytes:
    # 1. Generar el código QR
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(url_validacion)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    stream_qr = BytesIO()
    img_qr.save(stream_qr, format="PNG")
    bytes_qr = stream_qr.getvalue()

    # 2. Cargar la plantilla
    documento = fitz.open(stream=plantilla_bytes, filetype="pdf")
    pagina = documento[0]
    ancho_pagina = pagina.rect.width

    # 3. Estampar el Nombre
    coordenadas_nombre = pagina.search_for("{{NOMBRE COMPLETO PARTICIPANTE}}")
    if coordenadas_nombre:
        rect_nombre = coordenadas_nombre[0]
        pagina.draw_rect(rect_nombre, color=(1, 1, 1), fill=(1, 1, 1))
        
        # Usamos tamaño 24 por defecto para el nombre
        punto_insercion, fontsize_dinamico = calcular_coordenadas_y_fuente_hoja(rect_nombre, nombre, ancho_pagina, base_fontsize=24)
        pagina.insert_text(punto_insercion, nombre, fontsize=fontsize_dinamico, fontname="helv", color=(0, 0, 0))

    # 4. Estampar el Curso
    coordenadas_curso = pagina.search_for("{{CURSO}}")
    if coordenadas_curso:
        rect_curso = coordenadas_curso[0]
        pagina.draw_rect(rect_curso, color=(1, 1, 1), fill=(1, 1, 1))
        
        # Usamos tamaño 18 por defecto para el curso
        punto_insercion, fontsize_dinamico = calcular_coordenadas_y_fuente_hoja(rect_curso, curso, ancho_pagina, base_fontsize=18)
        pagina.insert_text(punto_insercion, curso, fontsize=fontsize_dinamico, fontname="helv", color=(0, 0, 0))

    # 5. Estampar el Código QR con protección de deslizamiento
    coordenadas_qr = pagina.search_for("{{QR}}")
    if coordenadas_qr:
        rect_qr = coordenadas_qr[0]
        pagina.draw_rect(rect_qr, color=(1, 1, 1), fill=(1, 1, 1))
        
        alto_pagina = pagina.rect.height
        # Llama a la nueva función de deslizamiento
        rect_cuadrado_seguro = calcular_rectangulo_qr_desplazado(rect_qr, ancho_pagina, alto_pagina, tamano_ideal=100)
        
        pagina.insert_image(rect_cuadrado_seguro, stream=bytes_qr)

    # 6. Guardar los cambios
    pdf_salida = BytesIO()
    documento.save(pdf_salida)
    documento.close()
    
    return pdf_salida.getvalue()