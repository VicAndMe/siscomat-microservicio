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

    # 5. Estampar el Código QR
    coordenadas_qr = pagina.search_for("{{QR}}")
    if coordenadas_qr:
        rect_qr = coordenadas_qr[0]
        pagina.draw_rect(rect_qr, color=(1, 1, 1), fill=(1, 1, 1))
        
        tamano_fijo_qr = 100
        rect_cuadrado = fitz.Rect(rect_qr.x0, rect_qr.y0, rect_qr.x0 + tamano_fijo_qr, rect_qr.y0 + tamano_fijo_qr)
        pagina.insert_image(rect_cuadrado, stream=bytes_qr)

    # 6. Guardar los cambios
    pdf_salida = BytesIO()
    documento.save(pdf_salida)
    documento.close()
    
    return pdf_salida.getvalue()