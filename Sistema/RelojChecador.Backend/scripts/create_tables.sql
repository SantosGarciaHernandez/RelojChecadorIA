CREATE TABLE Usuarios (
    IdUsuario INT IDENTITY(1,1) PRIMARY KEY,
    NumeroEmpleado NVARCHAR(50) NOT NULL UNIQUE,
    Nombre NVARCHAR(150) NOT NULL,
    NombreEtiquetaModelo NVARCHAR(100) NULL,
    Correo NVARCHAR(150) NULL,
    Rol NVARCHAR(30) NOT NULL DEFAULT 'Usuario',
    Activo BIT NOT NULL DEFAULT 1,
    FechaCreacion DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    PasswordHash NVARCHAR(255) NULL
);
GO

CREATE TABLE Equipos (
    IdEquipo INT IDENTITY(1,1) PRIMARY KEY,
    NombrePc NVARCHAR(100) NOT NULL UNIQUE,
    Accion NVARCHAR(20) NOT NULL,
    Activo BIT NOT NULL DEFAULT 1,
    FechaCreacion DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT CK_Equipos_Accion CHECK (Accion IN ('Entrada', 'Salida'))
);
GO

CREATE TABLE RegistroUsuarios (
    IdRegistro INT IDENTITY(1,1) PRIMARY KEY,
    IdUsuario INT NOT NULL,
    IdEquipo INT NOT NULL,
    TipoRegistro NVARCHAR(20) NOT NULL,
    FechaHora DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    ConfianzaModelo FLOAT NOT NULL,
    CONSTRAINT FK_RegistroUsuarios_Usuarios FOREIGN KEY (IdUsuario) REFERENCES Usuarios(IdUsuario),
    CONSTRAINT FK_RegistroUsuarios_Equipos FOREIGN KEY (IdEquipo) REFERENCES Equipos(IdEquipo),
    CONSTRAINT CK_RegistroUsuarios_TipoRegistro CHECK (TipoRegistro IN ('Entrada', 'Salida'))
);
GO

CREATE TABLE RegistroIntrusos (
    IdIntruso INT IDENTITY(1,1) PRIMARY KEY,
    IdEquipo INT NOT NULL,
    TipoUbicacion NVARCHAR(20) NOT NULL,
    FechaHora DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    ConfianzaModelo FLOAT NOT NULL,
    MensajeAlerta NVARCHAR(300) NOT NULL,
    EstadoAlerta NVARCHAR(30) NOT NULL DEFAULT 'Pendiente',
    ImagenBinaria VARBINARY(MAX) NULL,
    CONSTRAINT FK_RegistroIntrusos_Equipos FOREIGN KEY (IdEquipo) REFERENCES Equipos(IdEquipo),
    CONSTRAINT CK_RegistroIntrusos_TipoUbicacion CHECK (TipoUbicacion IN ('Entrada', 'Salida')),
    CONSTRAINT CK_RegistroIntrusos_Estado CHECK (EstadoAlerta IN ('Pendiente', 'Atendida', 'Ignorada'))
);
GO

CREATE TABLE ConfiguracionSistema (
    IdConfiguracion INT IDENTITY(1,1) PRIMARY KEY,
    PermitirMultiplesEntradas BIT NOT NULL DEFAULT 0,
    PermitirMultiplesSalidas BIT NOT NULL DEFAULT 0,
    TiempoMinimoEntreRegistrosSegundos INT NOT NULL DEFAULT 60,
    UmbralConfianzaIntruso FLOAT NOT NULL DEFAULT 0.70,
    AlertasSonorasActivas BIT NOT NULL DEFAULT 1,
    CorreosActivos BIT NOT NULL DEFAULT 0
);
GO

CREATE UNIQUE INDEX IX_Usuarios_NombreEtiquetaModelo
ON Usuarios (NombreEtiquetaModelo)
WHERE NombreEtiquetaModelo IS NOT NULL;
GO

CREATE INDEX IX_RegistroUsuarios_Usuario_Equipo_Fecha
ON RegistroUsuarios (IdUsuario, IdEquipo, FechaHora DESC);
GO

CREATE INDEX IX_RegistroUsuarios_Fecha
ON RegistroUsuarios (FechaHora DESC);
GO

CREATE INDEX IX_RegistroIntrusos_Fecha_Estado
ON RegistroIntrusos (FechaHora DESC, EstadoAlerta);
GO

INSERT INTO ConfiguracionSistema (
    PermitirMultiplesEntradas,
    PermitirMultiplesSalidas,
    TiempoMinimoEntreRegistrosSegundos,
    UmbralConfianzaIntruso,
    AlertasSonorasActivas,
    CorreosActivos
)
VALUES (0, 0, 60, 0.70, 1, 0);
GO
