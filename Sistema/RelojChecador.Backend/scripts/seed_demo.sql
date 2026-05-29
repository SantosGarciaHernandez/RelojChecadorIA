INSERT INTO Usuarios (NumeroEmpleado, Nombre, NombreEtiquetaModelo, Correo, Rol, Activo)
VALUES
('E001', 'Santos Garcia Hernandez', 'SantosSet', 'santos@example.com', 'Administrador', 1),
('E002', 'Naomi Avigail Alvarado Mendoza', 'NaomiSet', 'naomi@example.com', 'Usuario', 1),
('E003', 'Jesus Guzman', 'Jesus Guzman', 'jesus@example.com', 'Usuario', 1),
('E004', 'Lizbeth Castañeda Rivas', 'Lizbeth Castañeda Rivas', 'lizbeth@example.com', 'Usuario', 1),
('E005', 'Daniel Demo', 'DanielSet', 'daniel@example.com', 'Usuario', 1),
('E006', 'Coto Demo', 'CotoSet', 'coto@example.com', 'Usuario', 1),
('G001', 'Guardia Demo', NULL, 'guardia@example.com', 'Guardia', 1);
GO

INSERT INTO Equipos (NombrePc, Accion, Activo)
VALUES
('PC-ENTRADA-01', 'Entrada', 1),
('PC-SALIDA-01', 'Salida', 1);
GO
