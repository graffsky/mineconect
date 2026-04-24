--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

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

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schema, since initdb creates it


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: comentarios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comentarios (
    id integer NOT NULL,
    discusion_id integer NOT NULL,
    usuario_id integer NOT NULL,
    contenido text NOT NULL,
    fecha_comentario timestamp without time zone,
    parent_id integer
);


--
-- Name: comentarios_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.comentarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: comentarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.comentarios_id_seq OWNED BY public.comentarios.id;


--
-- Name: convocatoria_postulaciones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.convocatoria_postulaciones (
    id integer NOT NULL,
    convocatoria_id integer NOT NULL,
    empresario_id integer NOT NULL,
    nombre_proyecto character varying(200) NOT NULL,
    descripcion text NOT NULL,
    fecha_postulacion timestamp without time zone,
    estado character varying(50)
);


--
-- Name: convocatoria_postulaciones_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.convocatoria_postulaciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: convocatoria_postulaciones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.convocatoria_postulaciones_id_seq OWNED BY public.convocatoria_postulaciones.id;


--
-- Name: discusiones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.discusiones (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    titulo character varying(200) NOT NULL,
    categoria character varying(100),
    contenido text NOT NULL,
    fecha_creacion timestamp without time zone
);


--
-- Name: discusiones_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.discusiones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: discusiones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.discusiones_id_seq OWNED BY public.discusiones.id;


--
-- Name: emprendedor_proyectos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.emprendedor_proyectos (
    id integer NOT NULL,
    emprendedor_id integer NOT NULL,
    titulo character varying(150) NOT NULL,
    descripcion text NOT NULL,
    tipo_apoyo_buscado character varying(100),
    capital_requerido character varying(50),
    estado character varying(50),
    fecha_creacion timestamp without time zone
);


--
-- Name: emprendedor_proyectos_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.emprendedor_proyectos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: emprendedor_proyectos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.emprendedor_proyectos_id_seq OWNED BY public.emprendedor_proyectos.id;


--
-- Name: emprendedores; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.emprendedores (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    nombre_completo character varying(150) NOT NULL,
    tipo_documento character varying(10) NOT NULL,
    numero_documento character varying(30) NOT NULL,
    numero_celular character varying(15) NOT NULL,
    programa_formacion character varying(150) NOT NULL,
    titulo_proyecto character varying(150) NOT NULL,
    descripcion_proyecto text NOT NULL,
    relacion_sector character varying(250) NOT NULL,
    tipo_apoyo character varying(50) NOT NULL
);


--
-- Name: emprendedores_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.emprendedores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: emprendedores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.emprendedores_id_seq OWNED BY public.emprendedores.id;


--
-- Name: empresario_alianzas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.empresario_alianzas (
    id integer NOT NULL,
    empresario_id integer NOT NULL,
    tipo_oferta character varying(100) NOT NULL,
    descripcion text NOT NULL,
    ubicacion character varying(100),
    fecha_publicacion timestamp without time zone
);


--
-- Name: empresario_alianzas_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.empresario_alianzas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: empresario_alianzas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.empresario_alianzas_id_seq OWNED BY public.empresario_alianzas.id;


--
-- Name: empresario_diagnostico; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.empresario_diagnostico (
    id integer NOT NULL,
    empresario_id integer NOT NULL,
    fecha timestamp without time zone,
    tipo character varying(50),
    respuestas json,
    puntaje_global double precision
);


--
-- Name: empresario_diagnostico_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.empresario_diagnostico_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: empresario_diagnostico_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.empresario_diagnostico_id_seq OWNED BY public.empresario_diagnostico.id;


--
-- Name: empresario_discusiones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.empresario_discusiones (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    titulo character varying(200) NOT NULL,
    categoria character varying(100),
    contenido text NOT NULL,
    fecha_creacion timestamp without time zone
);


--
-- Name: empresario_discusiones_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.empresario_discusiones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: empresario_discusiones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.empresario_discusiones_id_seq OWNED BY public.empresario_discusiones.id;


--
-- Name: empresario_mensajes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.empresario_mensajes (
    id integer NOT NULL,
    remitente_id integer NOT NULL,
    destinatario_id integer,
    contenido text NOT NULL,
    fecha_envio timestamp without time zone,
    leido boolean,
    tipo character varying(50),
    eliminado_por_remitente boolean DEFAULT false,
    eliminado_por_destinatario boolean DEFAULT false
);


--
-- Name: empresario_mensajes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.empresario_mensajes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: empresario_mensajes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.empresario_mensajes_id_seq OWNED BY public.empresario_mensajes.id;


--
-- Name: empresario_mercado; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.empresario_mercado (
    id integer NOT NULL,
    empresario_id integer NOT NULL,
    titulo character varying(150) NOT NULL,
    tipo character varying(50) NOT NULL,
    precio character varying(50) NOT NULL,
    ubicacion character varying(100) NOT NULL,
    imagen_url text,
    fecha_publicacion timestamp without time zone,
    activo boolean
);


--
-- Name: empresario_mercado_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.empresario_mercado_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: empresario_mercado_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.empresario_mercado_id_seq OWNED BY public.empresario_mercado.id;


--
-- Name: empresarios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.empresarios (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    nombre_completo character varying(150) NOT NULL,
    tipo_documento_personal character varying(10) NOT NULL,
    numero_documento_personal character varying(30) NOT NULL,
    numero_celular character varying(15) NOT NULL,
    nombre_empresa character varying(150) NOT NULL,
    tipo_contribuyente character varying(20) NOT NULL,
    numero_documento_contribuyente character varying(30),
    nit character varying(30),
    tamano character varying(20) NOT NULL,
    sector_produccion character varying(100) NOT NULL,
    sector_transformacion character varying(100) NOT NULL,
    sector_comercializacion character varying(100) NOT NULL
);


--
-- Name: empresarios_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.empresarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: empresarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.empresarios_id_seq OWNED BY public.empresarios.id;


--
-- Name: institucion_convocatorias; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.institucion_convocatorias (
    id integer NOT NULL,
    institucion_id integer NOT NULL,
    titulo character varying(200) NOT NULL,
    descripcion text NOT NULL,
    requisitos text,
    fecha_cierre date NOT NULL,
    publico_objetivo character varying(100),
    estado character varying(50)
);


--
-- Name: institucion_convocatorias_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.institucion_convocatorias_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: institucion_convocatorias_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.institucion_convocatorias_id_seq OWNED BY public.institucion_convocatorias.id;


--
-- Name: institucion_noticias; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.institucion_noticias (
    id integer NOT NULL,
    institucion_id integer,
    titulo character varying(200) NOT NULL,
    categoria character varying(50),
    contenido text NOT NULL,
    imagen_url text,
    vistas integer,
    fecha_publicacion timestamp without time zone
);


--
-- Name: institucion_noticias_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.institucion_noticias_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: institucion_noticias_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.institucion_noticias_id_seq OWNED BY public.institucion_noticias.id;


--
-- Name: institucion_programas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.institucion_programas (
    id integer NOT NULL,
    institucion_id integer NOT NULL,
    nombre character varying(200) NOT NULL,
    modalidad character varying(50) NOT NULL,
    duracion character varying(50),
    cupos_totales integer,
    cupos_ocupados integer,
    estado character varying(50),
    descripcion text
);


--
-- Name: institucion_programas_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.institucion_programas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: institucion_programas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.institucion_programas_id_seq OWNED BY public.institucion_programas.id;


--
-- Name: instituciones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.instituciones (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    nombre_completo character varying(150) NOT NULL,
    nit character varying(30) NOT NULL,
    tipo_institucion character varying(50) NOT NULL,
    municipio character varying(100) NOT NULL,
    descripcion text NOT NULL,
    area_especializacion character varying(100) NOT NULL,
    participacion_activa character varying(255)
);


--
-- Name: instituciones_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.instituciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: instituciones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.instituciones_id_seq OWNED BY public.instituciones.id;


--
-- Name: instituciones_mensajes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.instituciones_mensajes (
    id integer NOT NULL,
    remitente_id integer NOT NULL,
    destinatario_id integer,
    contenido text NOT NULL,
    fecha_envio timestamp without time zone,
    leido boolean,
    tipo character varying(50),
    eliminado_por_remitente boolean DEFAULT false,
    eliminado_por_destinatario boolean DEFAULT false
);


--
-- Name: instituciones_mensajes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.instituciones_mensajes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: instituciones_mensajes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.instituciones_mensajes_id_seq OWNED BY public.instituciones_mensajes.id;


--
-- Name: inversionistas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inversionistas (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    nombre_completo character varying(150) NOT NULL,
    tipo_documento character varying(10) NOT NULL,
    numero_documento character varying(30) NOT NULL,
    numero_celular character varying(15) NOT NULL,
    nombre_fondo character varying(150),
    tipo_inversion character varying(50) NOT NULL,
    etapas_interes character varying(255),
    areas_interes character varying(255)
);


--
-- Name: inversionistas_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.inversionistas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: inversionistas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.inversionistas_id_seq OWNED BY public.inversionistas.id;


--
-- Name: programa_postulaciones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.programa_postulaciones (
    id integer NOT NULL,
    programa_id integer NOT NULL,
    empresario_id integer NOT NULL,
    fecha_postulacion timestamp without time zone,
    estado character varying(50)
);


--
-- Name: programa_postulaciones_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.programa_postulaciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: programa_postulaciones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.programa_postulaciones_id_seq OWNED BY public.programa_postulaciones.id;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(200) NOT NULL,
    tipo_perfil character varying(13) NOT NULL,
    is_admin boolean DEFAULT false NOT NULL,
    activo boolean,
    fecha_registro timestamp without time zone,
    ultima_conexion timestamp without time zone
);


--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- Name: comentarios id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comentarios ALTER COLUMN id SET DEFAULT nextval('public.comentarios_id_seq'::regclass);


--
-- Name: convocatoria_postulaciones id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.convocatoria_postulaciones ALTER COLUMN id SET DEFAULT nextval('public.convocatoria_postulaciones_id_seq'::regclass);


--
-- Name: discusiones id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.discusiones ALTER COLUMN id SET DEFAULT nextval('public.discusiones_id_seq'::regclass);


--
-- Name: emprendedor_proyectos id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.emprendedor_proyectos ALTER COLUMN id SET DEFAULT nextval('public.emprendedor_proyectos_id_seq'::regclass);


--
-- Name: emprendedores id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.emprendedores ALTER COLUMN id SET DEFAULT nextval('public.emprendedores_id_seq'::regclass);


--
-- Name: empresario_alianzas id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresario_alianzas ALTER COLUMN id SET DEFAULT nextval('public.empresario_alianzas_id_seq'::regclass);


--
-- Name: empresario_diagnostico id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresario_diagnostico ALTER COLUMN id SET DEFAULT nextval('public.empresario_diagnostico_id_seq'::regclass);


--
-- Name: empresario_discusiones id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresario_discusiones ALTER COLUMN id SET DEFAULT nextval('public.empresario_discusiones_id_seq'::regclass);


--
-- Name: empresario_mensajes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresario_mensajes ALTER COLUMN id SET DEFAULT nextval('public.empresario_mensajes_id_seq'::regclass);


--
-- Name: empresario_mercado id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresario_mercado ALTER COLUMN id SET DEFAULT nextval('public.empresario_mercado_id_seq'::regclass);


--
-- Name: empresarios id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresarios ALTER COLUMN id SET DEFAULT nextval('public.empresarios_id_seq'::regclass);


--
-- Name: institucion_convocatorias id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.institucion_convocatorias ALTER COLUMN id SET DEFAULT nextval('public.institucion_convocatorias_id_seq'::regclass);


--
-- Name: institucion_noticias id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.institucion_noticias ALTER COLUMN id SET DEFAULT nextval('public.institucion_noticias_id_seq'::regclass);


--
-- Name: institucion_programas id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.institucion_programas ALTER COLUMN id SET DEFAULT nextval('public.institucion_programas_id_seq'::regclass);


--
-- Name: instituciones id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instituciones ALTER COLUMN id SET DEFAULT nextval('public.instituciones_id_seq'::regclass);


--
-- Name: instituciones_mensajes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instituciones_mensajes ALTER COLUMN id SET DEFAULT nextval('public.instituciones_mensajes_id_seq'::regclass);


--
-- Name: inversionistas id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inversionistas ALTER COLUMN id SET DEFAULT nextval('public.inversionistas_id_seq'::regclass);


--
-- Name: programa_postulaciones id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.programa_postulaciones ALTER COLUMN id SET DEFAULT nextval('public.programa_postulaciones_id_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
ad83241b7fa3
\.


--
-- Data for Name: comentarios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.comentarios (id, discusion_id, usuario_id, contenido, fecha_comentario, parent_id) FROM stdin;
\.


--
-- Data for Name: convocatoria_postulaciones; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.convocatoria_postulaciones (id, convocatoria_id, empresario_id, nombre_proyecto, descripcion, fecha_postulacion, estado) FROM stdin;
\.


--
-- Data for Name: discusiones; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.discusiones (id, usuario_id, titulo, categoria, contenido, fecha_creacion) FROM stdin;
\.


--
-- Data for Name: emprendedor_proyectos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.emprendedor_proyectos (id, emprendedor_id, titulo, descripcion, tipo_apoyo_buscado, capital_requerido, estado, fecha_creacion) FROM stdin;
\.


--
-- Data for Name: emprendedores; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.emprendedores (id, usuario_id, nombre_completo, tipo_documento, numero_documento, numero_celular, programa_formacion, titulo_proyecto, descripcion_proyecto, relacion_sector, tipo_apoyo) FROM stdin;
\.


--
-- Data for Name: empresario_alianzas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.empresario_alianzas (id, empresario_id, tipo_oferta, descripcion, ubicacion, fecha_publicacion) FROM stdin;
\.


--
-- Data for Name: empresario_diagnostico; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.empresario_diagnostico (id, empresario_id, fecha, tipo, respuestas, puntaje_global) FROM stdin;
\.


--
-- Data for Name: empresario_discusiones; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.empresario_discusiones (id, usuario_id, titulo, categoria, contenido, fecha_creacion) FROM stdin;
\.


--
-- Data for Name: empresario_mensajes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.empresario_mensajes (id, remitente_id, destinatario_id, contenido, fecha_envio, leido, tipo, eliminado_por_remitente, eliminado_por_destinatario) FROM stdin;
\.


--
-- Data for Name: empresario_mercado; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.empresario_mercado (id, empresario_id, titulo, tipo, precio, ubicacion, imagen_url, fecha_publicacion, activo) FROM stdin;
\.


--
-- Data for Name: empresarios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.empresarios (id, usuario_id, nombre_completo, tipo_documento_personal, numero_documento_personal, numero_celular, nombre_empresa, tipo_contribuyente, numero_documento_contribuyente, nit, tamano, sector_produccion, sector_transformacion, sector_comercializacion) FROM stdin;
\.


--
-- Data for Name: institucion_convocatorias; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.institucion_convocatorias (id, institucion_id, titulo, descripcion, requisitos, fecha_cierre, publico_objetivo, estado) FROM stdin;
\.


--
-- Data for Name: institucion_noticias; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.institucion_noticias (id, institucion_id, titulo, categoria, contenido, imagen_url, vistas, fecha_publicacion) FROM stdin;
\.


--
-- Data for Name: institucion_programas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.institucion_programas (id, institucion_id, nombre, modalidad, duracion, cupos_totales, cupos_ocupados, estado, descripcion) FROM stdin;
\.


--
-- Data for Name: instituciones; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.instituciones (id, usuario_id, nombre_completo, nit, tipo_institucion, municipio, descripcion, area_especializacion, participacion_activa) FROM stdin;
\.


--
-- Data for Name: instituciones_mensajes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.instituciones_mensajes (id, remitente_id, destinatario_id, contenido, fecha_envio, leido, tipo, eliminado_por_remitente, eliminado_por_destinatario) FROM stdin;
\.


--
-- Data for Name: inversionistas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inversionistas (id, usuario_id, nombre_completo, tipo_documento, numero_documento, numero_celular, nombre_fondo, tipo_inversion, etapas_interes, areas_interes) FROM stdin;
\.


--
-- Data for Name: programa_postulaciones; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.programa_postulaciones (id, programa_id, empresario_id, fecha_postulacion, estado) FROM stdin;
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.usuarios (id, email, password_hash, tipo_perfil, is_admin, activo, fecha_registro, ultima_conexion) FROM stdin;
\.


--
-- Name: comentarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.comentarios_id_seq', 1, false);


--
-- Name: convocatoria_postulaciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.convocatoria_postulaciones_id_seq', 1, false);


--
-- Name: discusiones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.discusiones_id_seq', 2, true);


--
-- Name: emprendedor_proyectos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.emprendedor_proyectos_id_seq', 1, false);


--
-- Name: emprendedores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.emprendedores_id_seq', 1, false);


--
-- Name: empresario_alianzas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.empresario_alianzas_id_seq', 1, false);


--
-- Name: empresario_diagnostico_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.empresario_diagnostico_id_seq', 1, false);


--
-- Name: empresario_discusiones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.empresario_discusiones_id_seq', 1, false);


--
-- Name: empresario_mensajes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.empresario_mensajes_id_seq', 1, false);


--
-- Name: empresario_mercado_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.empresario_mercado_id_seq', 1, false);


--
-- Name: empresarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.empresarios_id_seq', 1, false);


--
-- Name: institucion_convocatorias_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.institucion_convocatorias_id_seq', 1, false);


--
-- Name: institucion_noticias_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.institucion_noticias_id_seq', 1, false);


--
-- Name: institucion_programas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.institucion_programas_id_seq', 1, false);


--
-- Name: instituciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.instituciones_id_seq', 1, false);


--
-- Name: instituciones_mensajes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.instituciones_mensajes_id_seq', 1, false);


--
-- Name: inversionistas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inversionistas_id_seq', 1, false);


--
-- Name: programa_postulaciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.programa_postulaciones_id_seq', 1, false);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: comentarios comentarios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comentarios
    ADD CONSTRAINT comentarios_pkey PRIMARY KEY (id);


--
-- Name: convocatoria_postulaciones convocatoria_postulaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.convocatoria_postulaciones
    ADD CONSTRAINT convocatoria_postulaciones_pkey PRIMARY KEY (id);


--
-- Name: discusiones discusiones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.discusiones
    ADD CONSTRAINT discusiones_pkey PRIMARY KEY (id);


--
-- Name: emprendedor_proyectos emprendedor_proyectos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.emprendedor_proyectos
    ADD CONSTRAINT emprendedor_proyectos_pkey PRIMARY KEY (id);


--
-- Name: emprendedores emprendedores_numero_documento_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.emprendedores
    ADD CONSTRAINT emprendedores_numero_documento_key UNIQUE (numero_documento);


--
-- Name: emprendedores emprendedores_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.emprendedores
    ADD CONSTRAINT emprendedores_pkey PRIMARY KEY (id);


--
-- Name: emprendedores emprendedores_usuario_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.emprendedores
    ADD CONSTRAINT emprendedores_usuario_id_key UNIQUE (usuario_id);


--
-- Name: empresario_alianzas empresario_alianzas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresario_alianzas
    ADD CONSTRAINT empresario_alianzas_pkey PRIMARY KEY (id);


--
-- Name: empresario_diagnostico empresario_diagnostico_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresario_diagnostico
    ADD CONSTRAINT empresario_diagnostico_pkey PRIMARY KEY (id);


--
-- Name: empresario_discusiones empresario_discusiones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresario_discusiones
    ADD CONSTRAINT empresario_discusiones_pkey PRIMARY KEY (id);


--
-- Name: empresario_mensajes empresario_mensajes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresario_mensajes
    ADD CONSTRAINT empresario_mensajes_pkey PRIMARY KEY (id);


--
-- Name: empresario_mercado empresario_mercado_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresario_mercado
    ADD CONSTRAINT empresario_mercado_pkey PRIMARY KEY (id);


--
-- Name: empresarios empresarios_nit_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresarios
    ADD CONSTRAINT empresarios_nit_key UNIQUE (nit);


--
-- Name: empresarios empresarios_numero_documento_contribuyente_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresarios
    ADD CONSTRAINT empresarios_numero_documento_contribuyente_key UNIQUE (numero_documento_contribuyente);


--
-- Name: empresarios empresarios_numero_documento_personal_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresarios
    ADD CONSTRAINT empresarios_numero_documento_personal_key UNIQUE (numero_documento_personal);


--
-- Name: empresarios empresarios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresarios
    ADD CONSTRAINT empresarios_pkey PRIMARY KEY (id);


--
-- Name: empresarios empresarios_usuario_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresarios
    ADD CONSTRAINT empresarios_usuario_id_key UNIQUE (usuario_id);


--
-- Name: institucion_convocatorias institucion_convocatorias_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.institucion_convocatorias
    ADD CONSTRAINT institucion_convocatorias_pkey PRIMARY KEY (id);


--
-- Name: institucion_noticias institucion_noticias_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.institucion_noticias
    ADD CONSTRAINT institucion_noticias_pkey PRIMARY KEY (id);


--
-- Name: institucion_programas institucion_programas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.institucion_programas
    ADD CONSTRAINT institucion_programas_pkey PRIMARY KEY (id);


--
-- Name: instituciones_mensajes instituciones_mensajes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instituciones_mensajes
    ADD CONSTRAINT instituciones_mensajes_pkey PRIMARY KEY (id);


--
-- Name: instituciones instituciones_nit_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instituciones
    ADD CONSTRAINT instituciones_nit_key UNIQUE (nit);


--
-- Name: instituciones instituciones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instituciones
    ADD CONSTRAINT instituciones_pkey PRIMARY KEY (id);


--
-- Name: instituciones instituciones_usuario_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instituciones
    ADD CONSTRAINT instituciones_usuario_id_key UNIQUE (usuario_id);


--
-- Name: inversionistas inversionistas_numero_documento_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inversionistas
    ADD CONSTRAINT inversionistas_numero_documento_key UNIQUE (numero_documento);


--
-- Name: inversionistas inversionistas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inversionistas
    ADD CONSTRAINT inversionistas_pkey PRIMARY KEY (id);


--
-- Name: inversionistas inversionistas_usuario_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inversionistas
    ADD CONSTRAINT inversionistas_usuario_id_key UNIQUE (usuario_id);


--
-- Name: programa_postulaciones programa_postulaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.programa_postulaciones
    ADD CONSTRAINT programa_postulaciones_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: comentarios comentarios_discusion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comentarios
    ADD CONSTRAINT comentarios_discusion_id_fkey FOREIGN KEY (discusion_id) REFERENCES public.empresario_discusiones(id) ON DELETE CASCADE;


--
-- Name: comentarios comentarios_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comentarios
    ADD CONSTRAINT comentarios_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.comentarios(id) ON DELETE CASCADE;


--
-- Name: comentarios comentarios_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comentarios
    ADD CONSTRAINT comentarios_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: convocatoria_postulaciones convocatoria_postulaciones_convocatoria_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.convocatoria_postulaciones
    ADD CONSTRAINT convocatoria_postulaciones_convocatoria_id_fkey FOREIGN KEY (convocatoria_id) REFERENCES public.institucion_convocatorias(id) ON DELETE CASCADE;


--
-- Name: convocatoria_postulaciones convocatoria_postulaciones_empresario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.convocatoria_postulaciones
    ADD CONSTRAINT convocatoria_postulaciones_empresario_id_fkey FOREIGN KEY (empresario_id) REFERENCES public.empresarios(id) ON DELETE CASCADE;


--
-- Name: discusiones discusiones_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.discusiones
    ADD CONSTRAINT discusiones_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: emprendedor_proyectos emprendedor_proyectos_emprendedor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.emprendedor_proyectos
    ADD CONSTRAINT emprendedor_proyectos_emprendedor_id_fkey FOREIGN KEY (emprendedor_id) REFERENCES public.emprendedores(id) ON DELETE CASCADE;


--
-- Name: emprendedores emprendedores_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.emprendedores
    ADD CONSTRAINT emprendedores_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: empresario_alianzas empresario_alianzas_empresario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresario_alianzas
    ADD CONSTRAINT empresario_alianzas_empresario_id_fkey FOREIGN KEY (empresario_id) REFERENCES public.empresarios(id) ON DELETE CASCADE;


--
-- Name: empresario_diagnostico empresario_diagnostico_empresario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresario_diagnostico
    ADD CONSTRAINT empresario_diagnostico_empresario_id_fkey FOREIGN KEY (empresario_id) REFERENCES public.empresarios(id) ON DELETE CASCADE;


--
-- Name: empresario_discusiones empresario_discusiones_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresario_discusiones
    ADD CONSTRAINT empresario_discusiones_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: empresario_mensajes empresario_mensajes_destinatario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresario_mensajes
    ADD CONSTRAINT empresario_mensajes_destinatario_id_fkey FOREIGN KEY (destinatario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: empresario_mensajes empresario_mensajes_remitente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresario_mensajes
    ADD CONSTRAINT empresario_mensajes_remitente_id_fkey FOREIGN KEY (remitente_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: empresario_mercado empresario_mercado_empresario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresario_mercado
    ADD CONSTRAINT empresario_mercado_empresario_id_fkey FOREIGN KEY (empresario_id) REFERENCES public.empresarios(id) ON DELETE CASCADE;


--
-- Name: empresarios empresarios_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresarios
    ADD CONSTRAINT empresarios_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: institucion_convocatorias institucion_convocatorias_institucion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.institucion_convocatorias
    ADD CONSTRAINT institucion_convocatorias_institucion_id_fkey FOREIGN KEY (institucion_id) REFERENCES public.instituciones(id) ON DELETE CASCADE;


--
-- Name: institucion_noticias institucion_noticias_institucion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.institucion_noticias
    ADD CONSTRAINT institucion_noticias_institucion_id_fkey FOREIGN KEY (institucion_id) REFERENCES public.instituciones(id);


--
-- Name: institucion_programas institucion_programas_institucion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.institucion_programas
    ADD CONSTRAINT institucion_programas_institucion_id_fkey FOREIGN KEY (institucion_id) REFERENCES public.instituciones(id) ON DELETE CASCADE;


--
-- Name: instituciones_mensajes instituciones_mensajes_destinatario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instituciones_mensajes
    ADD CONSTRAINT instituciones_mensajes_destinatario_id_fkey FOREIGN KEY (destinatario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: instituciones_mensajes instituciones_mensajes_remitente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instituciones_mensajes
    ADD CONSTRAINT instituciones_mensajes_remitente_id_fkey FOREIGN KEY (remitente_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: instituciones instituciones_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instituciones
    ADD CONSTRAINT instituciones_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: inversionistas inversionistas_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inversionistas
    ADD CONSTRAINT inversionistas_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: programa_postulaciones programa_postulaciones_empresario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.programa_postulaciones
    ADD CONSTRAINT programa_postulaciones_empresario_id_fkey FOREIGN KEY (empresario_id) REFERENCES public.empresarios(id) ON DELETE CASCADE;


--
-- Name: programa_postulaciones programa_postulaciones_programa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.programa_postulaciones
    ADD CONSTRAINT programa_postulaciones_programa_id_fkey FOREIGN KEY (programa_id) REFERENCES public.institucion_programas(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

