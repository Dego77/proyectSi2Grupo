--
-- PostgreSQL database dump
--

\restrict WgmKSgZyg1CpIfbJrAYPkOZADjnLYH0whY6Xt0Hubh8VjxdsBaC6avkXcIfarND

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.venta DROP CONSTRAINT IF EXISTS venta_id_usuarios_fkey;
ALTER TABLE IF EXISTS ONLY public.venta DROP CONSTRAINT IF EXISTS venta_id_movimiento_fkey;
ALTER TABLE IF EXISTS ONLY public.venta DROP CONSTRAINT IF EXISTS venta_id_cliente_fkey;
ALTER TABLE IF EXISTS ONLY public.usuario DROP CONSTRAINT IF EXISTS usuario_id_rol_fkey;
ALTER TABLE IF EXISTS ONLY public.rol_permisos DROP CONSTRAINT IF EXISTS rol_permisos_id_rol_fkey;
ALTER TABLE IF EXISTS ONLY public.rol_permisos DROP CONSTRAINT IF EXISTS rol_permisos_id_permiso_fkey;
ALTER TABLE IF EXISTS ONLY public.proyecto DROP CONSTRAINT IF EXISTS proyecto_id_usuarios_fkey;
ALTER TABLE IF EXISTS ONLY public.presupuesto DROP CONSTRAINT IF EXISTS presupuesto_id_proyecto_fkey;
ALTER TABLE IF EXISTS ONLY public.planillas DROP CONSTRAINT IF EXISTS planillas_id_usuarios_fkey;
ALTER TABLE IF EXISTS ONLY public.planillas DROP CONSTRAINT IF EXISTS planillas_id_proyecto_fkey;
ALTER TABLE IF EXISTS ONLY public.planillas DROP CONSTRAINT IF EXISTS planillas_id_movimiento_fkey;
ALTER TABLE IF EXISTS ONLY public.planillas DROP CONSTRAINT IF EXISTS planillas_id_empleados_fkey;
ALTER TABLE IF EXISTS ONLY public.pago DROP CONSTRAINT IF EXISTS pago_id_venta_fkey;
ALTER TABLE IF EXISTS ONLY public.pago DROP CONSTRAINT IF EXISTS pago_id_proyecto_fkey;
ALTER TABLE IF EXISTS ONLY public.pago DROP CONSTRAINT IF EXISTS pago_id_movimiento_fkey;
ALTER TABLE IF EXISTS ONLY public.movimiento_financiero DROP CONSTRAINT IF EXISTS movimiento_financiero_id_proyecto_fkey;
ALTER TABLE IF EXISTS ONLY public.detalle_presupuesto DROP CONSTRAINT IF EXISTS detalle_presupuesto_id_presupuesto_fkey;
ALTER TABLE IF EXISTS ONLY public.detalle_presupuesto DROP CONSTRAINT IF EXISTS detalle_presupuesto_id_material_fkey;
ALTER TABLE IF EXISTS ONLY public.detalle_compra DROP CONSTRAINT IF EXISTS detalle_compra_id_material_fkey;
ALTER TABLE IF EXISTS ONLY public.detalle_compra DROP CONSTRAINT IF EXISTS detalle_compra_id_compra_fkey;
ALTER TABLE IF EXISTS ONLY public.compra DROP CONSTRAINT IF EXISTS compra_id_usuarios_fkey;
ALTER TABLE IF EXISTS ONLY public.compra DROP CONSTRAINT IF EXISTS compra_id_proveedor_fkey;
ALTER TABLE IF EXISTS ONLY public.compra DROP CONSTRAINT IF EXISTS compra_id_movimiento_fkey;
ALTER TABLE IF EXISTS ONLY public.bitacora DROP CONSTRAINT IF EXISTS bitacora_id_usuarios_fkey;
ALTER TABLE IF EXISTS ONLY public.base_de_datos_empresa DROP CONSTRAINT IF EXISTS base_de_datos_empresa_id_empresa_fkey;
ALTER TABLE IF EXISTS ONLY public.activos_fijos DROP CONSTRAINT IF EXISTS activos_fijos_id_proyecto_fkey;
ALTER TABLE IF EXISTS ONLY public.venta DROP CONSTRAINT IF EXISTS venta_pkey;
ALTER TABLE IF EXISTS ONLY public.usuario DROP CONSTRAINT IF EXISTS usuario_pkey;
ALTER TABLE IF EXISTS ONLY public.rol DROP CONSTRAINT IF EXISTS rol_pkey;
ALTER TABLE IF EXISTS ONLY public.rol_permisos DROP CONSTRAINT IF EXISTS rol_permisos_pkey;
ALTER TABLE IF EXISTS ONLY public.proyecto DROP CONSTRAINT IF EXISTS proyecto_pkey;
ALTER TABLE IF EXISTS ONLY public.proveedor DROP CONSTRAINT IF EXISTS proveedor_pkey;
ALTER TABLE IF EXISTS ONLY public.presupuesto DROP CONSTRAINT IF EXISTS presupuesto_pkey;
ALTER TABLE IF EXISTS ONLY public.planillas DROP CONSTRAINT IF EXISTS planillas_pkey;
ALTER TABLE IF EXISTS ONLY public.permisos DROP CONSTRAINT IF EXISTS permisos_pkey;
ALTER TABLE IF EXISTS ONLY public.pago DROP CONSTRAINT IF EXISTS pago_pkey;
ALTER TABLE IF EXISTS ONLY public.movimiento_financiero DROP CONSTRAINT IF EXISTS movimiento_financiero_pkey;
ALTER TABLE IF EXISTS ONLY public.material DROP CONSTRAINT IF EXISTS material_pkey;
ALTER TABLE IF EXISTS ONLY public.empresa DROP CONSTRAINT IF EXISTS empresa_pkey;
ALTER TABLE IF EXISTS ONLY public.empleados DROP CONSTRAINT IF EXISTS empleados_pkey;
ALTER TABLE IF EXISTS ONLY public.detalle_presupuesto DROP CONSTRAINT IF EXISTS detalle_presupuesto_pkey;
ALTER TABLE IF EXISTS ONLY public.detalle_compra DROP CONSTRAINT IF EXISTS detalle_compra_pkey;
ALTER TABLE IF EXISTS ONLY public.compra DROP CONSTRAINT IF EXISTS compra_pkey;
ALTER TABLE IF EXISTS ONLY public.cliente DROP CONSTRAINT IF EXISTS cliente_pkey;
ALTER TABLE IF EXISTS ONLY public.bitacora DROP CONSTRAINT IF EXISTS bitacora_pkey;
ALTER TABLE IF EXISTS ONLY public.base_de_datos_empresa DROP CONSTRAINT IF EXISTS base_de_datos_empresa_pkey;
ALTER TABLE IF EXISTS ONLY public.activos_fijos DROP CONSTRAINT IF EXISTS activos_fijos_pkey;
ALTER TABLE IF EXISTS public.venta ALTER COLUMN id_venta DROP DEFAULT;
ALTER TABLE IF EXISTS public.usuario ALTER COLUMN id_usuarios DROP DEFAULT;
ALTER TABLE IF EXISTS public.rol ALTER COLUMN id_rol DROP DEFAULT;
ALTER TABLE IF EXISTS public.proyecto ALTER COLUMN id_proyecto DROP DEFAULT;
ALTER TABLE IF EXISTS public.proveedor ALTER COLUMN id_proveedor DROP DEFAULT;
ALTER TABLE IF EXISTS public.presupuesto ALTER COLUMN id_presupuesto DROP DEFAULT;
ALTER TABLE IF EXISTS public.planillas ALTER COLUMN id_planillas DROP DEFAULT;
ALTER TABLE IF EXISTS public.permisos ALTER COLUMN id_permiso DROP DEFAULT;
ALTER TABLE IF EXISTS public.pago ALTER COLUMN id_pago DROP DEFAULT;
ALTER TABLE IF EXISTS public.movimiento_financiero ALTER COLUMN id_movimiento DROP DEFAULT;
ALTER TABLE IF EXISTS public.material ALTER COLUMN id_material DROP DEFAULT;
ALTER TABLE IF EXISTS public.empresa ALTER COLUMN id_empresa DROP DEFAULT;
ALTER TABLE IF EXISTS public.empleados ALTER COLUMN id_empleados DROP DEFAULT;
ALTER TABLE IF EXISTS public.detalle_compra ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.compra ALTER COLUMN id_compra DROP DEFAULT;
ALTER TABLE IF EXISTS public.cliente ALTER COLUMN id_cliente DROP DEFAULT;
ALTER TABLE IF EXISTS public.bitacora ALTER COLUMN id_bitacora DROP DEFAULT;
ALTER TABLE IF EXISTS public.base_de_datos_empresa ALTER COLUMN id_basedatos DROP DEFAULT;
ALTER TABLE IF EXISTS public.activos_fijos ALTER COLUMN id_activo DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.venta_id_venta_seq;
DROP TABLE IF EXISTS public.venta;
DROP SEQUENCE IF EXISTS public.usuario_id_usuarios_seq;
DROP TABLE IF EXISTS public.usuario;
DROP TABLE IF EXISTS public.rol_permisos;
DROP SEQUENCE IF EXISTS public.rol_id_rol_seq;
DROP TABLE IF EXISTS public.rol;
DROP SEQUENCE IF EXISTS public.proyecto_id_proyecto_seq;
DROP TABLE IF EXISTS public.proyecto;
DROP SEQUENCE IF EXISTS public.proveedor_id_proveedor_seq;
DROP TABLE IF EXISTS public.proveedor;
DROP SEQUENCE IF EXISTS public.presupuesto_id_presupuesto_seq;
DROP TABLE IF EXISTS public.presupuesto;
DROP SEQUENCE IF EXISTS public.planillas_id_planillas_seq;
DROP TABLE IF EXISTS public.planillas;
DROP SEQUENCE IF EXISTS public.permisos_id_permiso_seq;
DROP TABLE IF EXISTS public.permisos;
DROP SEQUENCE IF EXISTS public.pago_id_pago_seq;
DROP TABLE IF EXISTS public.pago;
DROP SEQUENCE IF EXISTS public.movimiento_financiero_id_movimiento_seq;
DROP TABLE IF EXISTS public.movimiento_financiero;
DROP SEQUENCE IF EXISTS public.material_id_material_seq;
DROP TABLE IF EXISTS public.material;
DROP SEQUENCE IF EXISTS public.empresa_id_empresa_seq;
DROP TABLE IF EXISTS public.empresa;
DROP SEQUENCE IF EXISTS public.empleados_id_empleados_seq;
DROP TABLE IF EXISTS public.empleados;
DROP TABLE IF EXISTS public.detalle_presupuesto;
DROP SEQUENCE IF EXISTS public.detalle_compra_id_seq;
DROP TABLE IF EXISTS public.detalle_compra;
DROP SEQUENCE IF EXISTS public.compra_id_compra_seq;
DROP TABLE IF EXISTS public.compra;
DROP SEQUENCE IF EXISTS public.cliente_id_cliente_seq;
DROP TABLE IF EXISTS public.cliente;
DROP SEQUENCE IF EXISTS public.bitacora_id_bitacora_seq;
DROP TABLE IF EXISTS public.bitacora;
DROP SEQUENCE IF EXISTS public.base_de_datos_empresa_id_basedatos_seq;
DROP TABLE IF EXISTS public.base_de_datos_empresa;
DROP SEQUENCE IF EXISTS public.activos_fijos_id_activo_seq;
DROP TABLE IF EXISTS public.activos_fijos;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: activos_fijos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activos_fijos (
    id_activo integer NOT NULL,
    id_proyecto integer,
    nombre character varying NOT NULL,
    tipo_activo character varying NOT NULL,
    codigo_activo character varying NOT NULL,
    fechacompra date,
    valor_compra numeric NOT NULL,
    vida_util integer NOT NULL,
    valor_residual numeric NOT NULL,
    estado character varying NOT NULL
);


ALTER TABLE public.activos_fijos OWNER TO postgres;

--
-- Name: activos_fijos_id_activo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.activos_fijos_id_activo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.activos_fijos_id_activo_seq OWNER TO postgres;

--
-- Name: activos_fijos_id_activo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.activos_fijos_id_activo_seq OWNED BY public.activos_fijos.id_activo;


--
-- Name: base_de_datos_empresa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.base_de_datos_empresa (
    id_basedatos integer NOT NULL,
    id_empresa integer,
    nombre_bd character varying NOT NULL,
    host character varying NOT NULL,
    puerto integer NOT NULL,
    usuario_bd character varying NOT NULL,
    password_bd character varying NOT NULL,
    estado boolean NOT NULL,
    fecha_creacion timestamp without time zone
);


ALTER TABLE public.base_de_datos_empresa OWNER TO postgres;

--
-- Name: base_de_datos_empresa_id_basedatos_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.base_de_datos_empresa_id_basedatos_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.base_de_datos_empresa_id_basedatos_seq OWNER TO postgres;

--
-- Name: base_de_datos_empresa_id_basedatos_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.base_de_datos_empresa_id_basedatos_seq OWNED BY public.base_de_datos_empresa.id_basedatos;


--
-- Name: bitacora; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bitacora (
    id_bitacora integer NOT NULL,
    id_usuarios integer NOT NULL,
    fecha_hora timestamp without time zone,
    modulo character varying NOT NULL,
    accion character varying NOT NULL,
    descripcion character varying
);


ALTER TABLE public.bitacora OWNER TO postgres;

--
-- Name: bitacora_id_bitacora_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bitacora_id_bitacora_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bitacora_id_bitacora_seq OWNER TO postgres;

--
-- Name: bitacora_id_bitacora_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bitacora_id_bitacora_seq OWNED BY public.bitacora.id_bitacora;


--
-- Name: cliente; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cliente (
    id_cliente integer NOT NULL,
    nombre character varying NOT NULL,
    telefono character varying NOT NULL,
    direccion character varying NOT NULL
);


ALTER TABLE public.cliente OWNER TO postgres;

--
-- Name: cliente_id_cliente_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cliente_id_cliente_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cliente_id_cliente_seq OWNER TO postgres;

--
-- Name: cliente_id_cliente_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cliente_id_cliente_seq OWNED BY public.cliente.id_cliente;


--
-- Name: compra; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.compra (
    id_compra integer NOT NULL,
    id_proveedor integer,
    id_movimiento integer,
    id_usuarios integer,
    fecha date,
    total numeric NOT NULL
);


ALTER TABLE public.compra OWNER TO postgres;

--
-- Name: compra_id_compra_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.compra_id_compra_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.compra_id_compra_seq OWNER TO postgres;

--
-- Name: compra_id_compra_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.compra_id_compra_seq OWNED BY public.compra.id_compra;


--
-- Name: detalle_compra; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.detalle_compra (
    id integer NOT NULL,
    id_compra integer,
    id_material integer,
    cantidad integer NOT NULL,
    precio numeric NOT NULL
);


ALTER TABLE public.detalle_compra OWNER TO postgres;

--
-- Name: detalle_compra_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.detalle_compra_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.detalle_compra_id_seq OWNER TO postgres;

--
-- Name: detalle_compra_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.detalle_compra_id_seq OWNED BY public.detalle_compra.id;


--
-- Name: detalle_presupuesto; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.detalle_presupuesto (
    id_presupuesto integer NOT NULL,
    id_material integer NOT NULL,
    cantidad integer NOT NULL,
    costo numeric NOT NULL
);


ALTER TABLE public.detalle_presupuesto OWNER TO postgres;

--
-- Name: empleados; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.empleados (
    id_empleados integer NOT NULL,
    nombre character varying NOT NULL,
    cargo character varying NOT NULL,
    salario numeric NOT NULL,
    telefono character varying NOT NULL
);


ALTER TABLE public.empleados OWNER TO postgres;

--
-- Name: empleados_id_empleados_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.empleados_id_empleados_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.empleados_id_empleados_seq OWNER TO postgres;

--
-- Name: empleados_id_empleados_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.empleados_id_empleados_seq OWNED BY public.empleados.id_empleados;


--
-- Name: empresa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.empresa (
    id_empresa integer NOT NULL,
    nombre character varying NOT NULL,
    nit character varying NOT NULL,
    telefono character varying NOT NULL,
    email character varying NOT NULL,
    direccion character varying NOT NULL,
    estado character varying NOT NULL,
    contrasena character varying
);


ALTER TABLE public.empresa OWNER TO postgres;

--
-- Name: empresa_id_empresa_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.empresa_id_empresa_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.empresa_id_empresa_seq OWNER TO postgres;

--
-- Name: empresa_id_empresa_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.empresa_id_empresa_seq OWNED BY public.empresa.id_empresa;


--
-- Name: material; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.material (
    id_material integer NOT NULL,
    nombre character varying NOT NULL,
    precio numeric NOT NULL,
    stock integer NOT NULL
);


ALTER TABLE public.material OWNER TO postgres;

--
-- Name: material_id_material_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.material_id_material_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.material_id_material_seq OWNER TO postgres;

--
-- Name: material_id_material_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.material_id_material_seq OWNED BY public.material.id_material;


--
-- Name: movimiento_financiero; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.movimiento_financiero (
    id_movimiento integer NOT NULL,
    id_proyecto integer,
    tipo_movimiento character varying NOT NULL,
    categoria character varying NOT NULL,
    monto numeric NOT NULL,
    fecha date,
    descripcion character varying
);


ALTER TABLE public.movimiento_financiero OWNER TO postgres;

--
-- Name: movimiento_financiero_id_movimiento_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.movimiento_financiero_id_movimiento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.movimiento_financiero_id_movimiento_seq OWNER TO postgres;

--
-- Name: movimiento_financiero_id_movimiento_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.movimiento_financiero_id_movimiento_seq OWNED BY public.movimiento_financiero.id_movimiento;


--
-- Name: pago; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pago (
    id_pago integer NOT NULL,
    id_venta integer,
    id_movimiento integer,
    id_proyecto integer,
    metodo_pago character varying NOT NULL,
    monto numeric NOT NULL,
    fecha timestamp without time zone,
    estado character varying NOT NULL,
    codigo_transaccion character varying
);


ALTER TABLE public.pago OWNER TO postgres;

--
-- Name: pago_id_pago_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pago_id_pago_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pago_id_pago_seq OWNER TO postgres;

--
-- Name: pago_id_pago_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pago_id_pago_seq OWNED BY public.pago.id_pago;


--
-- Name: permisos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permisos (
    id_permiso integer NOT NULL,
    descripcion character varying
);


ALTER TABLE public.permisos OWNER TO postgres;

--
-- Name: permisos_id_permiso_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.permisos_id_permiso_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.permisos_id_permiso_seq OWNER TO postgres;

--
-- Name: permisos_id_permiso_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.permisos_id_permiso_seq OWNED BY public.permisos.id_permiso;


--
-- Name: planillas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.planillas (
    id_planillas integer NOT NULL,
    id_usuarios integer,
    id_empleados integer,
    id_proyecto integer,
    id_movimiento integer,
    fecha date,
    pago numeric NOT NULL,
    periodo character varying NOT NULL
);


ALTER TABLE public.planillas OWNER TO postgres;

--
-- Name: planillas_id_planillas_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.planillas_id_planillas_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.planillas_id_planillas_seq OWNER TO postgres;

--
-- Name: planillas_id_planillas_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.planillas_id_planillas_seq OWNED BY public.planillas.id_planillas;


--
-- Name: presupuesto; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.presupuesto (
    id_presupuesto integer NOT NULL,
    id_proyecto integer,
    costo_total numeric NOT NULL,
    fecha date
);


ALTER TABLE public.presupuesto OWNER TO postgres;

--
-- Name: presupuesto_id_presupuesto_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.presupuesto_id_presupuesto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.presupuesto_id_presupuesto_seq OWNER TO postgres;

--
-- Name: presupuesto_id_presupuesto_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.presupuesto_id_presupuesto_seq OWNED BY public.presupuesto.id_presupuesto;


--
-- Name: proveedor; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.proveedor (
    id_proveedor integer NOT NULL,
    nombre character varying NOT NULL,
    contacto character varying NOT NULL
);


ALTER TABLE public.proveedor OWNER TO postgres;

--
-- Name: proveedor_id_proveedor_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.proveedor_id_proveedor_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.proveedor_id_proveedor_seq OWNER TO postgres;

--
-- Name: proveedor_id_proveedor_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.proveedor_id_proveedor_seq OWNED BY public.proveedor.id_proveedor;


--
-- Name: proyecto; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.proyecto (
    id_proyecto integer NOT NULL,
    id_usuarios integer,
    nombre character varying NOT NULL,
    ubicacion character varying NOT NULL,
    fecha_inicio date,
    fecha_fin date,
    estado character varying NOT NULL
);


ALTER TABLE public.proyecto OWNER TO postgres;

--
-- Name: proyecto_id_proyecto_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.proyecto_id_proyecto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.proyecto_id_proyecto_seq OWNER TO postgres;

--
-- Name: proyecto_id_proyecto_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.proyecto_id_proyecto_seq OWNED BY public.proyecto.id_proyecto;


--
-- Name: rol; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rol (
    id_rol integer NOT NULL,
    rol character varying NOT NULL,
    descripcion character varying,
    niveljerarquia integer NOT NULL,
    fechacreacion timestamp without time zone
);


ALTER TABLE public.rol OWNER TO postgres;

--
-- Name: rol_id_rol_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rol_id_rol_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rol_id_rol_seq OWNER TO postgres;

--
-- Name: rol_id_rol_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rol_id_rol_seq OWNED BY public.rol.id_rol;


--
-- Name: rol_permisos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rol_permisos (
    id_rol integer NOT NULL,
    id_permiso integer NOT NULL
);


ALTER TABLE public.rol_permisos OWNER TO postgres;

--
-- Name: usuario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario (
    id_usuarios integer NOT NULL,
    id_rol integer NOT NULL,
    nombresusuario character varying NOT NULL,
    nombres character varying NOT NULL,
    apellido character varying NOT NULL,
    email character varying NOT NULL,
    ci character varying,
    genero character varying,
    contrasena character varying NOT NULL,
    fecha_de_nacimiento date,
    telefono character varying,
    direccion character varying
);


ALTER TABLE public.usuario OWNER TO postgres;

--
-- Name: usuario_id_usuarios_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuario_id_usuarios_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuario_id_usuarios_seq OWNER TO postgres;

--
-- Name: usuario_id_usuarios_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuario_id_usuarios_seq OWNED BY public.usuario.id_usuarios;


--
-- Name: venta; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.venta (
    id_venta integer NOT NULL,
    id_cliente integer,
    id_movimiento integer,
    id_usuarios integer,
    total numeric NOT NULL,
    fecha date
);


ALTER TABLE public.venta OWNER TO postgres;

--
-- Name: venta_id_venta_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.venta_id_venta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.venta_id_venta_seq OWNER TO postgres;

--
-- Name: venta_id_venta_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.venta_id_venta_seq OWNED BY public.venta.id_venta;


--
-- Name: activos_fijos id_activo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activos_fijos ALTER COLUMN id_activo SET DEFAULT nextval('public.activos_fijos_id_activo_seq'::regclass);


--
-- Name: base_de_datos_empresa id_basedatos; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.base_de_datos_empresa ALTER COLUMN id_basedatos SET DEFAULT nextval('public.base_de_datos_empresa_id_basedatos_seq'::regclass);


--
-- Name: bitacora id_bitacora; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora ALTER COLUMN id_bitacora SET DEFAULT nextval('public.bitacora_id_bitacora_seq'::regclass);


--
-- Name: cliente id_cliente; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente ALTER COLUMN id_cliente SET DEFAULT nextval('public.cliente_id_cliente_seq'::regclass);


--
-- Name: compra id_compra; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra ALTER COLUMN id_compra SET DEFAULT nextval('public.compra_id_compra_seq'::regclass);


--
-- Name: detalle_compra id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_compra ALTER COLUMN id SET DEFAULT nextval('public.detalle_compra_id_seq'::regclass);


--
-- Name: empleados id_empleados; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.empleados ALTER COLUMN id_empleados SET DEFAULT nextval('public.empleados_id_empleados_seq'::regclass);


--
-- Name: empresa id_empresa; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.empresa ALTER COLUMN id_empresa SET DEFAULT nextval('public.empresa_id_empresa_seq'::regclass);


--
-- Name: material id_material; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material ALTER COLUMN id_material SET DEFAULT nextval('public.material_id_material_seq'::regclass);


--
-- Name: movimiento_financiero id_movimiento; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movimiento_financiero ALTER COLUMN id_movimiento SET DEFAULT nextval('public.movimiento_financiero_id_movimiento_seq'::regclass);


--
-- Name: pago id_pago; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pago ALTER COLUMN id_pago SET DEFAULT nextval('public.pago_id_pago_seq'::regclass);


--
-- Name: permisos id_permiso; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permisos ALTER COLUMN id_permiso SET DEFAULT nextval('public.permisos_id_permiso_seq'::regclass);


--
-- Name: planillas id_planillas; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planillas ALTER COLUMN id_planillas SET DEFAULT nextval('public.planillas_id_planillas_seq'::regclass);


--
-- Name: presupuesto id_presupuesto; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.presupuesto ALTER COLUMN id_presupuesto SET DEFAULT nextval('public.presupuesto_id_presupuesto_seq'::regclass);


--
-- Name: proveedor id_proveedor; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proveedor ALTER COLUMN id_proveedor SET DEFAULT nextval('public.proveedor_id_proveedor_seq'::regclass);


--
-- Name: proyecto id_proyecto; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proyecto ALTER COLUMN id_proyecto SET DEFAULT nextval('public.proyecto_id_proyecto_seq'::regclass);


--
-- Name: rol id_rol; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol ALTER COLUMN id_rol SET DEFAULT nextval('public.rol_id_rol_seq'::regclass);


--
-- Name: usuario id_usuarios; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario ALTER COLUMN id_usuarios SET DEFAULT nextval('public.usuario_id_usuarios_seq'::regclass);


--
-- Name: venta id_venta; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.venta ALTER COLUMN id_venta SET DEFAULT nextval('public.venta_id_venta_seq'::regclass);


--
-- Data for Name: activos_fijos; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: base_de_datos_empresa; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: bitacora; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: cliente; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: compra; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: detalle_compra; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: detalle_presupuesto; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: empleados; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: empresa; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: material; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: movimiento_financiero; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: pago; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: permisos; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: planillas; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: presupuesto; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: proveedor; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: proyecto; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: rol; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.rol (id_rol, rol, descripcion, niveljerarquia, fechacreacion) VALUES (1, 'Administrador', 'Administra todo el sistema de la empresa', 1, '2026-05-12 17:30:20.135858');
INSERT INTO public.rol (id_rol, rol, descripcion, niveljerarquia, fechacreacion) VALUES (2, 'Cliente', 'Usuario cliente del sistema', 2, '2026-05-12 17:30:20.13621');
INSERT INTO public.rol (id_rol, rol, descripcion, niveljerarquia, fechacreacion) VALUES (3, 'Empleado', 'Personal interno de la empresa constructora', 3, '2026-05-12 17:30:20.136359');


--
-- Data for Name: rol_permisos; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.usuario (id_usuarios, id_rol, nombresusuario, nombres, apellido, email, ci, genero, contrasena, fecha_de_nacimiento, telefono, direccion) VALUES (1, 1, 'admin_tajibos', 'Carlos', 'Rojas', 'admin@tajibos.com', NULL, NULL, '123456', NULL, '76543210', 'Santa Cruz');


--
-- Data for Name: venta; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Name: activos_fijos_id_activo_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.activos_fijos_id_activo_seq', 1, false);


--
-- Name: base_de_datos_empresa_id_basedatos_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.base_de_datos_empresa_id_basedatos_seq', 1, false);


--
-- Name: bitacora_id_bitacora_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bitacora_id_bitacora_seq', 1, false);


--
-- Name: cliente_id_cliente_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cliente_id_cliente_seq', 1, false);


--
-- Name: compra_id_compra_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.compra_id_compra_seq', 1, false);


--
-- Name: detalle_compra_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.detalle_compra_id_seq', 1, false);


--
-- Name: empleados_id_empleados_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.empleados_id_empleados_seq', 1, false);


--
-- Name: empresa_id_empresa_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.empresa_id_empresa_seq', 1, false);


--
-- Name: material_id_material_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.material_id_material_seq', 1, false);


--
-- Name: movimiento_financiero_id_movimiento_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.movimiento_financiero_id_movimiento_seq', 1, false);


--
-- Name: pago_id_pago_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pago_id_pago_seq', 1, false);


--
-- Name: permisos_id_permiso_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.permisos_id_permiso_seq', 1, false);


--
-- Name: planillas_id_planillas_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.planillas_id_planillas_seq', 1, false);


--
-- Name: presupuesto_id_presupuesto_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.presupuesto_id_presupuesto_seq', 1, false);


--
-- Name: proveedor_id_proveedor_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.proveedor_id_proveedor_seq', 1, false);


--
-- Name: proyecto_id_proyecto_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.proyecto_id_proyecto_seq', 1, false);


--
-- Name: rol_id_rol_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.rol_id_rol_seq', 1, false);


--
-- Name: usuario_id_usuarios_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuario_id_usuarios_seq', 1, false);


--
-- Name: venta_id_venta_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.venta_id_venta_seq', 1, false);


--
-- Name: activos_fijos activos_fijos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activos_fijos
    ADD CONSTRAINT activos_fijos_pkey PRIMARY KEY (id_activo);


--
-- Name: base_de_datos_empresa base_de_datos_empresa_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.base_de_datos_empresa
    ADD CONSTRAINT base_de_datos_empresa_pkey PRIMARY KEY (id_basedatos);


--
-- Name: bitacora bitacora_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora
    ADD CONSTRAINT bitacora_pkey PRIMARY KEY (id_bitacora);


--
-- Name: cliente cliente_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_pkey PRIMARY KEY (id_cliente);


--
-- Name: compra compra_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_pkey PRIMARY KEY (id_compra);


--
-- Name: detalle_compra detalle_compra_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_compra
    ADD CONSTRAINT detalle_compra_pkey PRIMARY KEY (id);


--
-- Name: detalle_presupuesto detalle_presupuesto_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_presupuesto
    ADD CONSTRAINT detalle_presupuesto_pkey PRIMARY KEY (id_presupuesto, id_material);


--
-- Name: empleados empleados_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.empleados
    ADD CONSTRAINT empleados_pkey PRIMARY KEY (id_empleados);


--
-- Name: empresa empresa_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.empresa
    ADD CONSTRAINT empresa_pkey PRIMARY KEY (id_empresa);


--
-- Name: material material_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material
    ADD CONSTRAINT material_pkey PRIMARY KEY (id_material);


--
-- Name: movimiento_financiero movimiento_financiero_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movimiento_financiero
    ADD CONSTRAINT movimiento_financiero_pkey PRIMARY KEY (id_movimiento);


--
-- Name: pago pago_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pago
    ADD CONSTRAINT pago_pkey PRIMARY KEY (id_pago);


--
-- Name: permisos permisos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permisos
    ADD CONSTRAINT permisos_pkey PRIMARY KEY (id_permiso);


--
-- Name: planillas planillas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planillas
    ADD CONSTRAINT planillas_pkey PRIMARY KEY (id_planillas);


--
-- Name: presupuesto presupuesto_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.presupuesto
    ADD CONSTRAINT presupuesto_pkey PRIMARY KEY (id_presupuesto);


--
-- Name: proveedor proveedor_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proveedor
    ADD CONSTRAINT proveedor_pkey PRIMARY KEY (id_proveedor);


--
-- Name: proyecto proyecto_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proyecto
    ADD CONSTRAINT proyecto_pkey PRIMARY KEY (id_proyecto);


--
-- Name: rol_permisos rol_permisos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol_permisos
    ADD CONSTRAINT rol_permisos_pkey PRIMARY KEY (id_rol, id_permiso);


--
-- Name: rol rol_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_pkey PRIMARY KEY (id_rol);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id_usuarios);


--
-- Name: venta venta_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.venta
    ADD CONSTRAINT venta_pkey PRIMARY KEY (id_venta);


--
-- Name: activos_fijos activos_fijos_id_proyecto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activos_fijos
    ADD CONSTRAINT activos_fijos_id_proyecto_fkey FOREIGN KEY (id_proyecto) REFERENCES public.proyecto(id_proyecto);


--
-- Name: base_de_datos_empresa base_de_datos_empresa_id_empresa_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.base_de_datos_empresa
    ADD CONSTRAINT base_de_datos_empresa_id_empresa_fkey FOREIGN KEY (id_empresa) REFERENCES public.empresa(id_empresa);


--
-- Name: bitacora bitacora_id_usuarios_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora
    ADD CONSTRAINT bitacora_id_usuarios_fkey FOREIGN KEY (id_usuarios) REFERENCES public.usuario(id_usuarios);


--
-- Name: compra compra_id_movimiento_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_id_movimiento_fkey FOREIGN KEY (id_movimiento) REFERENCES public.movimiento_financiero(id_movimiento);


--
-- Name: compra compra_id_proveedor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_id_proveedor_fkey FOREIGN KEY (id_proveedor) REFERENCES public.proveedor(id_proveedor);


--
-- Name: compra compra_id_usuarios_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_id_usuarios_fkey FOREIGN KEY (id_usuarios) REFERENCES public.usuario(id_usuarios);


--
-- Name: detalle_compra detalle_compra_id_compra_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_compra
    ADD CONSTRAINT detalle_compra_id_compra_fkey FOREIGN KEY (id_compra) REFERENCES public.compra(id_compra);


--
-- Name: detalle_compra detalle_compra_id_material_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_compra
    ADD CONSTRAINT detalle_compra_id_material_fkey FOREIGN KEY (id_material) REFERENCES public.material(id_material);


--
-- Name: detalle_presupuesto detalle_presupuesto_id_material_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_presupuesto
    ADD CONSTRAINT detalle_presupuesto_id_material_fkey FOREIGN KEY (id_material) REFERENCES public.material(id_material);


--
-- Name: detalle_presupuesto detalle_presupuesto_id_presupuesto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_presupuesto
    ADD CONSTRAINT detalle_presupuesto_id_presupuesto_fkey FOREIGN KEY (id_presupuesto) REFERENCES public.presupuesto(id_presupuesto);


--
-- Name: movimiento_financiero movimiento_financiero_id_proyecto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movimiento_financiero
    ADD CONSTRAINT movimiento_financiero_id_proyecto_fkey FOREIGN KEY (id_proyecto) REFERENCES public.proyecto(id_proyecto);


--
-- Name: pago pago_id_movimiento_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pago
    ADD CONSTRAINT pago_id_movimiento_fkey FOREIGN KEY (id_movimiento) REFERENCES public.movimiento_financiero(id_movimiento);


--
-- Name: pago pago_id_proyecto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pago
    ADD CONSTRAINT pago_id_proyecto_fkey FOREIGN KEY (id_proyecto) REFERENCES public.proyecto(id_proyecto);


--
-- Name: pago pago_id_venta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pago
    ADD CONSTRAINT pago_id_venta_fkey FOREIGN KEY (id_venta) REFERENCES public.venta(id_venta);


--
-- Name: planillas planillas_id_empleados_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planillas
    ADD CONSTRAINT planillas_id_empleados_fkey FOREIGN KEY (id_empleados) REFERENCES public.empleados(id_empleados);


--
-- Name: planillas planillas_id_movimiento_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planillas
    ADD CONSTRAINT planillas_id_movimiento_fkey FOREIGN KEY (id_movimiento) REFERENCES public.movimiento_financiero(id_movimiento);


--
-- Name: planillas planillas_id_proyecto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planillas
    ADD CONSTRAINT planillas_id_proyecto_fkey FOREIGN KEY (id_proyecto) REFERENCES public.proyecto(id_proyecto);


--
-- Name: planillas planillas_id_usuarios_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planillas
    ADD CONSTRAINT planillas_id_usuarios_fkey FOREIGN KEY (id_usuarios) REFERENCES public.usuario(id_usuarios);


--
-- Name: presupuesto presupuesto_id_proyecto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.presupuesto
    ADD CONSTRAINT presupuesto_id_proyecto_fkey FOREIGN KEY (id_proyecto) REFERENCES public.proyecto(id_proyecto);


--
-- Name: proyecto proyecto_id_usuarios_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proyecto
    ADD CONSTRAINT proyecto_id_usuarios_fkey FOREIGN KEY (id_usuarios) REFERENCES public.usuario(id_usuarios);


--
-- Name: rol_permisos rol_permisos_id_permiso_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol_permisos
    ADD CONSTRAINT rol_permisos_id_permiso_fkey FOREIGN KEY (id_permiso) REFERENCES public.permisos(id_permiso);


--
-- Name: rol_permisos rol_permisos_id_rol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol_permisos
    ADD CONSTRAINT rol_permisos_id_rol_fkey FOREIGN KEY (id_rol) REFERENCES public.rol(id_rol);


--
-- Name: usuario usuario_id_rol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_id_rol_fkey FOREIGN KEY (id_rol) REFERENCES public.rol(id_rol);


--
-- Name: venta venta_id_cliente_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.venta
    ADD CONSTRAINT venta_id_cliente_fkey FOREIGN KEY (id_cliente) REFERENCES public.cliente(id_cliente);


--
-- Name: venta venta_id_movimiento_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.venta
    ADD CONSTRAINT venta_id_movimiento_fkey FOREIGN KEY (id_movimiento) REFERENCES public.movimiento_financiero(id_movimiento);


--
-- Name: venta venta_id_usuarios_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.venta
    ADD CONSTRAINT venta_id_usuarios_fkey FOREIGN KEY (id_usuarios) REFERENCES public.usuario(id_usuarios);


--
-- PostgreSQL database dump complete
--

\unrestrict WgmKSgZyg1CpIfbJrAYPkOZADjnLYH0whY6Xt0Hubh8VjxdsBaC6avkXcIfarND

