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

def calcular_rectangulo_qr_seguro(rect_placeholder, ancho_pagina, alto_pagina, tamano_ideal=100):
    """
    Calcula un rectángulo cuadrado perfecto centrado en el placeholder original.
    Si está muy cerca de cualquier margen, reduce su tamaño proporcionalmente.
    """
    margen_seguridad = 60
    
    # 1. Encontrar el centro absoluto del placeholder
    centro_x = (rect_placeholder.x0 + rect_placeholder.x1) / 2.0
    centro_y = (rect_placeholder.y0 + rect_placeholder.y1) / 2.0
    
    # 2. Medir distancia a los bordes horizontales (Izquierda y Derecha)
    distancia_izq = centro_x - margen_seguridad
    distancia_der = (ancho_pagina - margen_seguridad) - centro_x
    distancia_x_segura = min(distancia_izq, distancia_der)
    
    # 3. Medir distancia a los bordes verticales (Arriba y Abajo)
    distancia_arriba = centro_y - margen_seguridad
    distancia_abajo = (alto_pagina - margen_seguridad) - centro_y
    distancia_y_segura = min(distancia_arriba, distancia_abajo)
    
    # 4. El tamaño máximo seguro es el doble de la distancia más restrictiva
    tamano_maximo = max(2 * min(distancia_x_segura, distancia_y_segura), 20) # Mínimo 20x20
    
    # 5. Elegimos el tamaño final (ideal o el máximo permitido, el que sea menor)
    tamano_final = min(tamano_ideal, tamano_maximo)
    
    # 6. Construir el nuevo rectángulo matemático perfectamente centrado
    mitad = tamano_final / 2.0
    return fitz.Rect(
        centro_x - mitad,
        centro_y - mitad,
        centro_x + mitad,
        centro_y + mitad
    )

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

    # 5. Estampar el Código QR con protección geométrica
    coordenadas_qr = pagina.search_for("{{QR}}")
    if coordenadas_qr:
        rect_qr = coordenadas_qr[0]
        # Borrar el texto de la etiqueta
        pagina.draw_rect(rect_qr, color=(1, 1, 1), fill=(1, 1, 1))
        
        # Calcular el rectángulo seguro y centrado
        alto_pagina = pagina.rect.height
        rect_cuadrado_seguro = calcular_rectangulo_qr_seguro(rect_qr, ancho_pagina, alto_pagina, tamano_ideal=100)
        
        # Insertar imagen en la zona segura
        pagina.insert_image(rect_cuadrado_seguro, stream=bytes_qr)

    # 6. Guardar los cambios
    pdf_salida = BytesIO()
    documento.save(pdf_salida)
    documento.close()
    
    return pdf_salida.getvalue()