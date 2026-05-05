import fitz  # PyMuPDF
import qrcode
from io import BytesIO

PLACEHOLDERS_REQUERIDOS = ["{{NOMBRE COMPLETO PARTICIPANTE}}", "{{CURSO}}", "{{QR}}"]

def validar_plantilla(plantilla_bytes: bytes) -> dict:
    """Verifica qué placeholders existen en la plantilla PDF."""
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

    # 3. Estampar el Nombre (Centrado matemático usando el método seguro original)
    coordenadas_nombre = pagina.search_for("{{NOMBRE COMPLETO PARTICIPANTE}}")
    if coordenadas_nombre:
        rect_nombre = coordenadas_nombre[0]
        # Borramos el placeholder visualmente
        pagina.draw_rect(rect_nombre, color=(1, 1, 1), fill=(1, 1, 1))
        
        # Calculamos el centro exacto del placeholder
        centro_x = (rect_nombre.x0 + rect_nombre.x1) / 2.0
        # Medimos el ancho de la cadena de texto real
        ancho_texto = fitz.get_text_length(nombre, fontname="helv", fontsize=24)
        # Recorremos el inicio hacia la izquierda la mitad del ancho del texto
        inicio_x = centro_x - (ancho_texto / 2.0)
        
        # Usamos insert_text, que jamás falla ni recorta el texto
        punto_texto = fitz.Point(inicio_x, rect_nombre.y1)
        pagina.insert_text(punto_texto, nombre, fontsize=24, fontname="helv", color=(0, 0, 0))

    # 4. Estampar el Curso (Centrado matemático usando el método seguro original)
    coordenadas_curso = pagina.search_for("{{CURSO}}")
    if coordenadas_curso:
        rect_curso = coordenadas_curso[0]
        pagina.draw_rect(rect_curso, color=(1, 1, 1), fill=(1, 1, 1))
        
        # Centrado matemático
        centro_x = (rect_curso.x0 + rect_curso.x1) / 2.0
        ancho_texto = fitz.get_text_length(curso, fontname="helv", fontsize=18)
        inicio_x = centro_x - (ancho_texto / 2.0)
        
        punto_curso = fitz.Point(inicio_x, rect_curso.y1)
        pagina.insert_text(punto_curso, curso, fontsize=18, fontname="helv", color=(0, 0, 0))

    # 5. Estampar el Código QR (Tamaño fijo para evitar deformaciones)
    coordenadas_qr = pagina.search_for("{{QR}}")
    if coordenadas_qr:
        rect_qr = coordenadas_qr[0]
        pagina.draw_rect(rect_qr, color=(1, 1, 1), fill=(1, 1, 1))
        
        # Forzamos un tamaño exacto (ej. 100x100) desde la esquina superior izquierda
        tamano_fijo_qr = 100
        rect_cuadrado = fitz.Rect(rect_qr.x0, rect_qr.y0, rect_qr.x0 + tamano_fijo_qr, rect_qr.y0 + tamano_fijo_qr)
        pagina.insert_image(rect_cuadrado, stream=bytes_qr)

    # 6. Guardar los cambios
    pdf_salida = BytesIO()
    documento.save(pdf_salida)
    documento.close()
    
    return pdf_salida.getvalue()