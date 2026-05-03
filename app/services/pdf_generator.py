import fitz  # PyMuPDF
import qrcode
from io import BytesIO

def procesar_pdf(nombre: str, curso: str, url_validacion: str, plantilla_bytes: bytes) -> bytes:
    # 1. Generar el código QR en memoria
    qr = qrcode.QRCode(version=1, box_size=4, border=1)
    qr.add_data(url_validacion)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    stream_qr = BytesIO()
    img_qr.save(stream_qr, format="PNG")
    bytes_qr = stream_qr.getvalue()

    # 2. Cargar la plantilla
    documento = fitz.open(stream=plantilla_bytes, filetype="pdf")
    pagina = documento[0]

    # 3. Estampar el Nombre
    coordenadas_nombre = pagina.search_for("{{NOMBRE COMPLETO PARTICIPANTE}}")
    if coordenadas_nombre:
        rect_nombre = coordenadas_nombre[0]
        pagina.draw_rect(rect_nombre, color=(1, 1, 1), fill=(1, 1, 1))
        punto_texto = fitz.Point(rect_nombre.x0, rect_nombre.y1)
        pagina.insert_text(punto_texto, nombre, fontsize=24, fontname="helv", color=(0, 0, 0))

    # 4. Estampar el Curso
    coordenadas_curso = pagina.search_for("{{CURSO}}")
    if coordenadas_curso:
        rect_curso = coordenadas_curso[0]
        # Borramos la etiqueta visualmente
        pagina.draw_rect(rect_curso, color=(1, 1, 1), fill=(1, 1, 1))
        punto_curso = fitz.Point(rect_curso.x0, rect_curso.y1)
        pagina.insert_text(punto_curso, curso, fontsize=18, fontname="helv", color=(0, 0, 0))

    # 5. Estampar el Código QR
    coordenadas_qr = pagina.search_for("{{QR}}")
    if coordenadas_qr:
        rect_qr = coordenadas_qr[0]
        pagina.draw_rect(rect_qr, color=(1, 1, 1), fill=(1, 1, 1))
        pagina.insert_image(rect_qr, stream=bytes_qr)

    # 6. Guardar los cambios
    pdf_salida = BytesIO()
    documento.save(pdf_salida)
    documento.close()
    
    return pdf_salida.getvalue()