INSERT INTO empresa (id_empresa, nombre, nit, telefono, email, direccion, estado)
VALUES (1, 'Constructora Pinares', '123456789', '70000000', 'pinares@gmail.com', 'Santa Cruz', 'Activo')
ON CONFLICT (id_empresa) DO NOTHING;

INSERT INTO base_de_datos_empresa (
    id_basedatos,
    id_empresa,
    nombre_bd,
    host,
    puerto,
    usuario_bd,
    password_bd,
    estado,
    fecha_creacion
)
VALUES (
    1,
    1,
    'bd_pinares',
    '127.0.0.1',
    5432,
    'postgres',
    '1234',
    true,
    CURRENT_TIMESTAMP
)
ON CONFLICT (id_basedatos) DO NOTHING;

INSERT INTO rol (id_rol, rol, descripcion, niveljerarquia, fechacreacion)
VALUES 
(1, 'Administrador', 'Administra todo el sistema de la empresa', 1, CURRENT_TIMESTAMP),
(2, 'Cliente', 'Usuario cliente del sistema', 2, CURRENT_TIMESTAMP),
(3, 'Empleado', 'Personal interno de la empresa constructora', 3, CURRENT_TIMESTAMP)
ON CONFLICT (id_rol) DO NOTHING;

INSERT INTO usuario (
    id_usuarios,
    id_rol,
    nombresusuario,
    nombres,
    apellido,
    email,
    ci,
    genero,
    contrasena,
    fecha_de_nacimiento,
    telefono,
    direccion
)
VALUES (
    1,
    1,
    'admin_pinares',
    'Diego',
    'Banegas',
    'dbanegas205@gmail.com',
    '12345678',
    'M',
    '1234',
    '2000-01-01',
    '70000000',
    'Santa Cruz'
)
ON CONFLICT (id_usuarios) DO NOTHING;

--evita q no ahiga Duplicados en la tabla empresa, base_de_datos_empresa, rol y usuario
SELECT setval(pg_get_serial_sequence('empresa', 'id_empresa'), COALESCE(MAX(id_empresa), 1), true) FROM empresa;

SELECT setval(pg_get_serial_sequence('base_de_datos_empresa', 'id_basedatos'), COALESCE(MAX(id_basedatos), 1), true) FROM base_de_datos_empresa;

SELECT setval(pg_get_serial_sequence('rol', 'id_rol'), COALESCE(MAX(id_rol), 1), true) FROM rol;

SELECT setval(pg_get_serial_sequence('usuario', 'id_usuarios'), COALESCE(MAX(id_usuarios), 1), true) FROM usuario;