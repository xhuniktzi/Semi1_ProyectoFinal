import base64
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql.cursors
import hashlib
import boto3
import dotenv
import botocore
import requests
import ast
import random


# Configuración de la conexión a la base de datos
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_SCHEMA"),
        cursorclass=pymysql.cursors.DictCursor,
    )


# Función para generar MD5
def generate_md5(data):
    return hashlib.md5(data.encode()).hexdigest()


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
dotenv.load_dotenv()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("S3_PUBLIC_ACCESS"),
    aws_secret_access_key=os.getenv("S3_SECRET_ACCESS"),
    region_name="us-east-1",
)

rekognition_client = boto3.client(
    "rekognition",
    aws_access_key_id=os.getenv("REKOGNITION_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("REKOGNITION_SECRET_ACCESS"),
    region_name="us-east-1",
)

translate_url = "https://s6dgyaa3di.execute-api.us-east-1.amazonaws.com/deploy/translate"  # Endpoint de la API Gateway para el servicio de traducción

polly_client = boto3.client(
    "polly",
    aws_access_key_id=os.getenv("POLLY_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("POLLY_SECRET_ACCESS"),
    region_name="us-east-1",
)


@app.route("/usuarios/registro", methods=["POST"])
def registro_usuario():
    data = request.json
    nickname = data["usuario"]
    nombre = data["nombre_completo"]
    password = generate_md5(data["password"])
    photo_base64 = data["photo_base64"]
    description = data["description"]

    # Convierte la imagen base64 a bytes
    photo_data = base64.b64decode(photo_base64)
    photo_path = f"Fotos_perfil/{nickname}.jpg"

    # Subir la foto a S3
    s3_client.put_object(Bucket=os.getenv("S3_BUCKET"), Key=photo_path, Body=photo_data)

    # Guardar en la base de datos
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO Usuarios (nickname, nombre, password, rutaFotoPerfil, description) VALUES (%s, %s, %s, %s)",
            (nickname, nombre, password, photo_path, description),
        )
        connection.commit()

    return jsonify({"message": "Usuario registrado con éxito"}), 201


@app.route("/usuarios/login", methods=["POST"])
def login_usuario():
    data = request.json
    nickname = data["usuario"]
    password = data.get("password")
    photo_base64 = data.get("photo_base64")
    connection = get_db_connection()

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Usuarios WHERE nickname = %s", (nickname,))
        user = cursor.fetchone()

    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404

    # Autenticación con contraseña
    if password:
        if generate_md5(password) == user["password"]:
            return jsonify({"message": "Login exitoso"}), 200
        else:
            return jsonify({"message": "Contraseña incorrecta"}), 401

    # Autenticación con foto
    if photo_base64:
        # Convierte la imagen base64 a bytes y la guarda temporalmente
        photo_data = base64.b64decode(photo_base64)
        temp_photo_path = f"temp_{nickname}.jpg"
        with open(temp_photo_path, "wb") as file:
            file.write(photo_data)

        # Obtener la imagen del usuario desde S3
        bucket_name = os.getenv("S3_BUCKET")
        object_key = user[
            "rutaFotoPerfil"
        ]  # Asumiendo que rutaFotoPerfil contiene la clave del objeto en S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        user_image_bytes = response["Body"].read()

        try:
            # Realiza la comparación de rostros con AWS Rekognition
            response = rekognition_client.compare_faces(
                SourceImage={"Bytes": user_image_bytes},
                TargetImage={"Bytes": open(temp_photo_path, "rb").read()},
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "InvalidParameterException":
                # Elimina la foto temporal
                os.remove(temp_photo_path)
                return (
                    jsonify(
                        {"message": "La imagen enviada no contiene una cara válida"}
                    ),
                    400,
                )
            else:
                raise e

        # Elimina la foto temporal
        os.remove(temp_photo_path)

        # Verifica si los rostros coinciden
        if response["FaceMatches"]:
            return jsonify({"message": "Login exitoso con foto"}), 200
        else:
            return jsonify({"message": "Login fallido con foto"}), 401

    return (
        jsonify(
            {"message": "Debe proporcionar una contraseña o una foto para el login"}
        ),
        400,
    )


@app.route("/usuarios/perfil/<username>", methods=["GET"])
def obtener_perfil(username):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Usuarios WHERE nickname = %s", (username,))
        user = cursor.fetchone()

    if user:
        del user["password"]  # No devolver la contraseña
        del user["id"]  # No devolver el ID

        # Obtener la foto del usuario desde S3
        bucket_name = os.getenv("S3_BUCKET")
        object_key = user["rutaFotoPerfil"]
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        user_image_bytes = response["Body"].read()

        # Obtener la descripción de la foto con AWS Rekognition
        response = rekognition_client.detect_faces(
            Image={"Bytes": user_image_bytes}, Attributes=["ALL"]
        )

        if response["FaceDetails"]:
            face_details = response["FaceDetails"][0]
            age_range = face_details["AgeRange"]
            gender = face_details["Gender"]["Value"]
            emotions = [
                emotion["Type"]
                for emotion in face_details["Emotions"]
                if emotion["Confidence"] > 50
            ]
            accessories = face_details.get("Accessories", [])
            accessories = [
                accessor for accessor in accessories if accessor["Confidence"] > 50
            ]

            description = f"Persona {gender} de entre {age_range['Low']} y {age_range['High']} años de edad"
            if emotions:
                description += f" con expresiones de {', '.join(emotions)}"
            if accessories:
                description += (
                    f" usando {', '.join(accessor['Type'] for accessor in accessories)}"
                )

            # Agregar la descripción al diccionario del usuario
            user["descripcion"] = description

        return jsonify(user), 200
    else:
        return jsonify({"message": "Usuario no encontrado"}), 404


def translate_text(text, target_language):
    if target_language == "Inglés":
        target_language = "en"
    if target_language == "Español":
        target_language = "es"
    if target_language == "Chino Mandarín":
        target_language = "zh"
    if target_language == "Hindi":
        target_language = "hi"
    if target_language == "Árabe":
        target_language = "ar"
    headers = {"Content-Type": "application/json"}
    payload = {"region": "us-east-1", "text": text, "target_language": target_language}
    response = requests.post(translate_url, json=payload, headers=headers, timeout=5)
    if response.status_code == 200:
        return ast.literal_eval(response.json()["body"])["translated_text"]
    else:
        return f"Error: {response.json()['error']}"


# # Función para convertir texto a habla utilizando AWS Polly
# def text_to_speech(text):
#     response = polly_client.synthesize_speech(
#         Text=text, OutputFormat="mp3", VoiceId="Joanna"
#     )
#     return base64.b64encode(response["AudioStream"].read()).decode("utf-8")
def text_to_speech(text, target_language):
    # Mapa de voces para cada idioma
    voices = {
        "Chino Mandarín": "Zhiyu",
        "Español": "Penelope",
        "Inglés": "Joanna",
        "Hindi": "Aditi",
        "Árabe": "Zeina"
    }
    
    # Obtener la voz correspondiente al idioma
    voice_id = voices.get(target_language, "Joanna")  # Si el idioma no tiene una voz específica, se usará la voz "Joanna"
    
    # Generar el habla utilizando la voz seleccionada
    response = polly_client.synthesize_speech(
        Text=text, OutputFormat="mp3", VoiceId=voice_id
    )
    return base64.b64encode(response["AudioStream"].read()).decode("utf-8")



# Función para traducir texto utilizando AWS Translate a través de API Gateway
@app.route("/traducir", methods=["POST"])
def traducir_texto():
    data = request.json
    text = data.get("text")
    target_language = data.get("target_language")

    if not text or not target_language:
        return jsonify({"message": "Texto y lenguaje objetivo son necesarios"}), 400

    translated_text = translate_text(text, target_language)
    if "Error:" in translated_text:
        return jsonify({"error": translated_text}), 400
    return jsonify({"translated_text": translated_text}), 200
    

# Función para convertir texto a habla utilizando AWS Polly
@app.route("/texto-a-habla", methods=["POST"])
def texto_a_habla():
    data = request.json
    text = data.get("text")
    target_language = data.get("target_language")

    if not text:
        return jsonify({"message": "Texto es necesario para generar habla"}), 400

    text = translate_text(text,target_language)
    print(text)

    speech_base64 = text_to_speech(text, target_language)
    return jsonify({"audio_base64": speech_base64}), 200


@app.route("/vehiculos/registro", methods=["POST"])
def registro_vehiculo():
    data = request.json
    tipo = data["tipo"]
    estacion_id = data["estacion_id"]
    placa_base = f"{tipo[0].upper()}{estacion_id}-"  # Genera una placa base como 'A2-' para ambulancias de estación 2
    kilometraje_inicial = data["kilometraje_inicial"]

    connection = get_db_connection()
    with connection.cursor() as cursor:
        # Busca el número máximo de vehículo ya registrado para esta estación y tipo
        cursor.execute(
            "SELECT MAX(Placa) AS last_placa FROM Vehiculos WHERE Placa LIKE %s",
            (f"{placa_base}%",),
        )
        result = cursor.fetchone()
        last_number = (
            int(result["last_placa"].split("-")[1]) if result["last_placa"] else 0
        )
        new_placa = f"{placa_base}{last_number + 1}"

        # Inserta el nuevo vehículo con la placa generada
        cursor.execute(
            "INSERT INTO Vehiculos (Placa, Tipo, EstacionID, KilometrajeActual) VALUES (%s, %s, %s, %s)",
            (new_placa, tipo, estacion_id, kilometraje_inicial),
        )
        connection.commit()

    return (
        jsonify({"message": "Vehículo registrado con éxito", "placa": new_placa}),
        201,
    )


@app.route("/reportes/crear", methods=["POST"])
def crear_reporte():
    data = request.json
    # estacion_id = data["estacion_id"]
    placa = data["placa"]
    kilometraje_nuevo = data["kilometraje_nuevo"]
    # descripcion = data["descripcion"]
    # Se asume que el bombero está autenticado y su id es obtenido del contexto de autenticación
    # bombero_id = request.bombero_id

    connection = get_db_connection()
    with connection.cursor() as cursor:
        # Actualiza el kilometraje del vehículo
        cursor.execute(
            "UPDATE Vehiculos SET KilometrajeActual = %s WHERE Placa = %s",
            (kilometraje_nuevo, placa),
        )

        # Crea el reporte en una tabla de reportes supuesta (la creación real no es posible sin modificar la DB)
        # INSERT INTO Reportes (EstacionID, BomberoID, Placa, Descripcion) VALUES (%s, %s, %s, %s)
        # cursor.execute(...)

        connection.commit()

    return jsonify({"message": "Reporte creado con éxito"}), 201


@app.route("/vehiculos/estacion/<int:estacion_id>", methods=["GET"])
def listar_vehiculos_por_estacion(estacion_id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Vehiculos WHERE EstacionID = %s", (estacion_id,))
        vehiculos = cursor.fetchall()

    if vehiculos:
        return jsonify(vehiculos), 200
    else:
        return (
            jsonify({"message": "No se encontraron vehículos para esta estación"}),
            404,
        )


@app.route("/hospitales", methods=["GET"])
def listar_hospitales():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Hospitales")
        hospitales = cursor.fetchall()

    return jsonify(hospitales), 200

@app.route("/hola", methods=["GET"])
def listar_hospitales2():
    print("gg")

    return jsonify("hospitales"), 200

@app.route("/estaciones", methods=["GET"])
def listar_estaciones():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Estaciones")
        estaciones = cursor.fetchall()

    return jsonify(estaciones), 200

@app.route("/estaciones/agregar", methods=["POST"])
def agregar_estacion():
    data = request.json
    direccion = data.get("direccion")

    if not direccion:
        return jsonify({"message": "La dirección es necesaria"}), 400

    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO Estaciones (Direccion) VALUES (%s)", (direccion,))
        connection.commit()

    return jsonify({"message": "Estación agregada con éxito"}), 201


@app.route("/hospitales/agregar", methods=["POST"])
def agregar_hospital():
    data = request.json
    nombre = data.get("nombre")
    direccion = data.get("direccion")

    if not nombre or not direccion:
        return jsonify({"message": "Nombre y dirección son requeridos"}), 400

    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO Hospitales (Nombre, Direccion) VALUES (%s, %s)",
            (nombre, direccion),
        )
        connection.commit()

    return jsonify({"message": "Hospital agregado con éxito"}), 201


@app.route('/api/botsito', methods=['POST'])
def chatbotRespuesta():
    lex_client = boto3.client('lexv2-runtime',
                          region_name='us-east-1', 
                          aws_access_key_id=os.getenv("AWS_LEX_ACCESS_KEY_ID"),
                          aws_secret_access_key=os.getenv("AWS_LEX_SECRET_ACCESS_KEY"))
    
    mensaje = request.json['mensaje']
    params = {
        'botAliasId': '6FB0ROZXXU',  
        'botId': 'NODRY6V8LB', 
        'localeId': 'es_419', 
        'text': mensaje,        
        'sessionId': '100' 
    }

    # Llama al servicio de Amazon Lex para enviar el mensaje
    titulo = "" 
    descripcion = ""
    try:
        response = lex_client.recognize_text(**params)
        for interpretation in response.get('interpretations', []):
            print(interpretation.get('intent', {}).get('name'))
            if interpretation.get('intent', {}).get('confirmationState') == "Confirmed":
                if interpretation.get('intent', {}).get('name') == "Hospital":
                    slots = interpretation.get('intent', {}).get('slots', {})
                    for slot_name, slot_data in slots.items():
                        if slot_name == "respUno":
                            titulo = f"{slot_data['value']['interpretedValue']}"
                        if slot_name == "respDos":
                            descripcion = f"{slot_data['value']['interpretedValue']}"
                    connection = get_db_connection()
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO Hospitales (Nombre, Direccion) VALUES (%s, %s)",
                            (titulo, descripcion),
                        )
                        connection.commit()
                if interpretation.get('intent', {}).get('name') == "Estacion":
                    slots = interpretation.get('intent', {}).get('slots', {})
                    for slot_name, slot_data in slots.items():
                        if slot_name == "respUno":
                            titulo = f"{slot_data['value']['interpretedValue']}"
                    connection = get_db_connection()
                    with connection.cursor() as cursor:
                        cursor.execute("INSERT INTO Estaciones (Direccion) VALUES (%s)", (titulo,))
                        connection.commit()
        messages = []

        for message in response.get('messages', []):
            messages.append(message.get('content'))
        random.shuffle(messages)
        response_string = ' '.join(messages)
        return jsonify({"message": response_string})
    except Exception as e:
        print(e)
        return jsonify({'error': 'Hubo un error al enviar el mensaje'}), 500
    
@app.route('/check', methods=['GET'])
def check():
    return '', 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
