-- Agrega columna de contraseña para acceso de empresa al sistema
ALTER TABLE empresa
ADD COLUMN IF NOT EXISTS contrasena VARCHAR(255);

INSERT INTO empresa (id_empresa, nombre, nit, telefono, email, direccion, estado)
VALUES (1, 'Constructora Pinares', '123456789', '70000000', 'pinares@gmail.com', 'Santa Cruz', 'Activo')
ON CONFLICT (id_empresa) DO NOTHING;

-- Contraseña inicial de prueba para la empresa principal
-- Solo pone contraseña inicial a empresas que no tengan contraseña
UPDATE empresa
SET contrasena = '123456'
WHERE contrasena IS NULL;

/*AND contrasena IS NULL;*/ 

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

-- USUARIO ADMIN
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

-- CLIENTE
INSERT INTO cliente (
    id_cliente, nombre, telefono, direccion
)
VALUES (
    1,
    'Cliente Demo',
    '70000001',
    'Zona Central - Caranavi'
)
ON CONFLICT (id_cliente) DO NOTHING;

-- PROYECTO
INSERT INTO proyecto (
    id_proyecto,
    id_usuarios,
    nombre,
    ubicacion,
    fecha_inicio,
    fecha_fin,
    estado
)
VALUES (
    1,
    1,
    'Casa familiar de 100 m2',
    'Caranavi',
    '2026-05-07',
    NULL,
    'En planificación'
)
ON CONFLICT (id_proyecto) DO NOTHING;

-- MATERIALES
INSERT INTO material (
    id_material, nombre, precio, stock
)
VALUES
    (1, 'Cemento bolsa 50 kg', 55.00, 100),
    (2, 'Arena fina m3', 120.00, 50),
    (3, 'Grava m3', 140.00, 40),
    (4, 'Ladrillo unidad', 1.20, 5000),
    (5, 'Fierro 12 mm barra', 65.00, 200),
    (6, 'Calamina unidad', 75.00, 100),
    (7, 'Pintura balde', 180.00, 30),
    (8, 'Madera tabla', 35.00, 80),
    (9, 'Clavos kg', 18.00, 60),
    (10, 'Tubo PVC unidad', 22.00, 100)
ON CONFLICT (id_material) DO NOTHING;

-- PROVEEDOR
INSERT INTO proveedor (
    id_proveedor, nombre, contacto
)
VALUES (
    1,
    'Proveedor Materiales Demo',
    '72000001'
)
ON CONFLICT (id_proveedor) DO NOTHING;

-- MOVIMIENTO FINANCIERO
INSERT INTO movimiento_financiero (
    id_movimiento,
    id_proyecto,
    tipo_movimiento,
    categoria,
    monto,
    fecha,
    descripcion
)
VALUES (
    1,
    1,
    'Egreso',
    'Compra de materiales',
    1510.00,
    '2026-05-07',
    'Compra inicial de materiales para prueba'
)
ON CONFLICT (id_movimiento) DO NOTHING;

-- COMPRA
INSERT INTO compra (
    id_compra,
    id_proveedor,
    id_movimiento,
    id_usuarios,
    fecha,
    total
)
VALUES (
    1,
    1,
    1,
    1,
    '2026-05-07',
    1510.00
)
ON CONFLICT (id_compra) DO NOTHING;

-- DETALLE COMPRA
INSERT INTO detalle_compra (
    id,
    id_compra,
    id_material,
    cantidad,
    precio
)
VALUES
    (1, 1, 1, 10, 55.00),
    (2, 1, 2, 3, 120.00),
    (3, 1, 4, 500, 1.20)
ON CONFLICT (id) DO NOTHING;

-- EMPLEADOS
INSERT INTO empleados (
    id_empleados,
    nombre,
    cargo,
    salario,
    telefono
)
VALUES
    (1, 'Juan Albañil', 'Albañil', 120.00, '71000001'),
    (2, 'Pedro Ayudante', 'Ayudante', 90.00, '71000002'),
    (3, 'Carlos Maestro', 'Maestro de obra', 180.00, '71000003')
ON CONFLICT (id_empleados) DO NOTHING;

-- PLANILLAS
INSERT INTO planillas (
    id_planillas,
    id_usuarios,
    id_empleados,
    id_proyecto,
    id_movimiento,
    fecha,
    pago,
    periodo
)
VALUES
    (1, 1, 1, 1, NULL, '2026-05-07', 600.00, '5 días'),
    (2, 1, 2, 1, NULL, '2026-05-07', 450.00, '5 días'),
    (3, 1, 3, 1, NULL, '2026-05-07', 900.00, '5 días')
ON CONFLICT (id_planillas) DO NOTHING;

-- ACTIVOS FIJOS
INSERT INTO activos_fijos (
    id_activo,
    id_proyecto,
    nombre,
    tipo_activo,
    codigo_activo,
    fechacompra,
    valor_compra,
    vida_util,
    valor_residual,
    estado
)
VALUES
    (
        1,
        1,
        'Mezcladora de cemento',
        'Maquinaria',
        'ACT-MEZ-001',
        '2025-01-10',
        7000.00,
        1000,
        1000.00,
        'Activo'
    ),
    (
        2,
        1,
        'Compactadora manual',
        'Herramienta',
        'ACT-COM-001',
        '2025-03-15',
        3500.00,
        800,
        500.00,
        'Activo'
    )
ON CONFLICT (id_activo) DO NOTHING;

-- para usuarios q no tienen contraseña se les colocara 123456 
UPDATE usuario
SET contrasena = '123456'
WHERE contrasena IS NULL;

-- ============================================================
-- ACTUALIZAR SECUENCIAS
-- ============================================================

SELECT setval(pg_get_serial_sequence('empresa', 'id_empresa'), COALESCE(MAX(id_empresa), 1)) FROM empresa;
SELECT setval(pg_get_serial_sequence('rol', 'id_rol'), COALESCE(MAX(id_rol), 1)) FROM rol;
SELECT setval(pg_get_serial_sequence('usuario', 'id_usuarios'), COALESCE(MAX(id_usuarios), 1)) FROM usuario;
SELECT setval(pg_get_serial_sequence('cliente', 'id_cliente'), COALESCE(MAX(id_cliente), 1)) FROM cliente;
SELECT setval(pg_get_serial_sequence('proyecto', 'id_proyecto'), COALESCE(MAX(id_proyecto), 1)) FROM proyecto;
SELECT setval(pg_get_serial_sequence('material', 'id_material'), COALESCE(MAX(id_material), 1)) FROM material;
SELECT setval(pg_get_serial_sequence('proveedor', 'id_proveedor'), COALESCE(MAX(id_proveedor), 1)) FROM proveedor;
SELECT setval(pg_get_serial_sequence('movimiento_financiero', 'id_movimiento'), COALESCE(MAX(id_movimiento), 1)) FROM movimiento_financiero;
SELECT setval(pg_get_serial_sequence('compra', 'id_compra'), COALESCE(MAX(id_compra), 1)) FROM compra;
SELECT setval(pg_get_serial_sequence('detalle_compra', 'id'), COALESCE(MAX(id), 1)) FROM detalle_compra;
SELECT setval(pg_get_serial_sequence('empleados', 'id_empleados'), COALESCE(MAX(id_empleados), 1)) FROM empleados;
SELECT setval(pg_get_serial_sequence('planillas', 'id_planillas'), COALESCE(MAX(id_planillas), 1)) FROM planillas;
SELECT setval(pg_get_serial_sequence('activos_fijos', 'id_activo'), COALESCE(MAX(id_activo), 1)) FROM activos_fijos;