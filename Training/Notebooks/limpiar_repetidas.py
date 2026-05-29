from pathlib import Path
import cv2
import shutil

# CAMBIA ESTA RUTA
CARPETA_IMAGENES = Path(r"D:\Aplicaciones multiplataforma\002 - RelojChecador IA\Training\DataSet\Validation\SantosSet")

CARPETA_REPETIDAS = CARPETA_IMAGENES / "_repetidas"
CARPETA_REPETIDAS.mkdir(exist_ok=True)

EXTENSIONES = [".jpg", ".jpeg", ".png", ".webp"]

# Entre más bajo, más estricto.
# 0 = idénticas visualmente
# 5 = casi iguales
# 10 = más agresivo
UMBRAL_DIFERENCIA = 10


def calcular_hash_promedio(ruta_imagen):
    img = cv2.imread(str(ruta_imagen), cv2.IMREAD_GRAYSCALE)

    if img is None:
        return None

    img = cv2.resize(img, (8, 8))
    promedio = img.mean()

    bits = img > promedio
    return bits.flatten()


def diferencia_hash(hash1, hash2):
    return (hash1 != hash2).sum()


imagenes = [
    archivo for archivo in CARPETA_IMAGENES.iterdir()
    if archivo.suffix.lower() in EXTENSIONES and archivo.is_file()
]

imagenes.sort()

hashes_unicos = []
movidas = 0

for imagen in imagenes:
    hash_actual = calcular_hash_promedio(imagen)

    if hash_actual is None:
        print(f"No se pudo leer: {imagen.name}")
        continue

    es_repetida = False

    for hash_guardado in hashes_unicos:
        diferencia = diferencia_hash(hash_actual, hash_guardado)

        if diferencia <= UMBRAL_DIFERENCIA:
            es_repetida = True
            break

    if es_repetida:
        destino = CARPETA_REPETIDAS / imagen.name
        shutil.move(str(imagen), str(destino))
        movidas += 1
        print(f"Repetida movida: {imagen.name}")
    else:
        hashes_unicos.append(hash_actual)

print()
print("Proceso terminado")
print(f"Imágenes revisadas: {len(imagenes)}")
print(f"Imágenes repetidas movidas: {movidas}")
print(f"Imágenes únicas conservadas: {len(hashes_unicos)}")