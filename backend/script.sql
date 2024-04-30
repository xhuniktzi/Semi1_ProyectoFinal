-- Creación de la tabla Usuarios
CREATE TABLE Usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nickname VARCHAR(255) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    rutaFotoPerfil VARCHAR(255),
    description VARCHAR(255) NOT NULL,
    UNIQUE (nickname)
);

-- Creación de la tabla de Rangos
CREATE TABLE Rangos (
    RangoID INT AUTO_INCREMENT PRIMARY KEY,
    Descripcion VARCHAR(255) NOT NULL
);

-- Insertar rangos predefinidos
INSERT INTO Rangos (Descripcion) VALUES
('Bombero III Clase'),
('Bombero II Clase'),
('Bombero I Clase'),
('Galonista III'),
('Galonista II'),
('Galonista I'),
('Mayor');




-- Creación de la tabla de Estaciones
CREATE TABLE Estaciones (
    EstacionID INT AUTO_INCREMENT PRIMARY KEY,
    Direccion VARCHAR(255) NOT NULL
);



-- Creación de la tabla de Vehículos
CREATE TABLE Vehiculos (
    Placa VARCHAR(20) PRIMARY KEY,
    Tipo VARCHAR(50) NOT NULL,
    EstacionID INT NOT NULL,
    KilometrajeActual INT NOT NULL,
    FOREIGN KEY (EstacionID) REFERENCES Estaciones(EstacionID)
);
CREATE INDEX idx_vehiculo_estacion ON Vehiculos(EstacionID);


-- Creación de la tabla de Hospitales
CREATE TABLE Hospitales (
    HospitalID INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(255) NOT NULL,
    Direccion VARCHAR(255) NOT NULL
);


