USE biblioteca_duoc;

-- 1. TIPOS DE USUARIO
INSERT INTO tipo_usuario (idtipousuario, nombre) VALUES 
(1, 'Administrador'), 
(2, 'Estudiante')
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

-- 2. USUARIOS / ALUMNOS 
INSERT INTO usuario (rut, nombre, correo, password, idtipousuario) VALUES 
('22163627-9', 'Magdalena Zuñiga', 'magd.zuniga@duocuc.cl', 'magda', 2),
('22182484-9', 'Felipe Cea', 'feli.cea@duocuc.cl', 'felipollas', 2),
('22130895-6', 'Sebastian Orellana', 'seba.orellanav@duocuc.cl', 'admin123', 1)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), correo=VALUES(correo), password=VALUES(password), idtipousuario=VALUES(idtipousuario);

-- 3. TIPOS DE MATERIAL
INSERT INTO tipo_material (idtipo, nombre, activo) VALUES 
(1, 'Libro', 1), 
(2, 'Revista', 1), 
(3, 'Tesis', 1), 
(4, 'Material Digital', 0)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), activo=VALUES(activo);

-- 4. MATERIAL BIBLIOGRÁFICO GENERAL 
INSERT INTO material (idmaterial, titulo, autor, idtipo) VALUES
(1, 'Ingeniería de Software: Un Enfoque Práctico', 'Roger S. Pressman', 1),
(2, 'Clean Code', 'Robert C. Martin', 1),
(3, 'Base de Datos Relacionales y SQL', 'Thomas Connolly', 1),
(4, 'Revista ACM Computing Surveys', 'ACM', 2)
ON DUPLICATE KEY UPDATE titulo=VALUES(titulo), autor=VALUES(autor), idtipo=VALUES(idtipo);

-- 5. COPIAS O EJEMPLARES FÍSICOS (Las que el alumno realmente reserva)
-- Creamos un par de copias por cada material para tener stock
INSERT INTO copia (idcopia, idmaterial, estado) VALUES
(1, 1, 'Disponible'), -- Copia 1 de Pressman
(2, 1, 'Disponible'), -- Copia 2 de Pressman
(3, 2, 'Disponible'), -- Copia 1 de Clean Code
(4, 3, 'Disponible'), -- Copia 1 de SQL
(5, 4, 'Disponible')  -- Copia 1 de la Revista
ON DUPLICATE KEY UPDATE idmaterial=VALUES(idmaterial), estado=VALUES(estado);
