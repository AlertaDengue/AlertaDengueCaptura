--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: dengue; Type: DATABASE; Schema: -; Owner: -
--

CREATE DATABASE dengue WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'pt_BR.UTF-8';


\connect dengue

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: Dengue_global; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA "Dengue_global";


--
-- Name: Municipio; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA "Municipio";


--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = "Dengue_global", pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: CID10; Type: TABLE; Schema: Dengue_global; Owner: -; Tablespace:
--

CREATE TABLE "CID10" (
    nome character varying(512) NOT NULL,
    codigo character varying(5) NOT NULL
);


--
-- Name: Municipio; Type: TABLE; Schema: Dengue_global; Owner: -; Tablespace:
--

CREATE TABLE "Municipio" (
    geocodigo integer NOT NULL,
    nome character varying(128) NOT NULL,
    geojson text NOT NULL,
    populacao bigint NOT NULL,
    uf character varying(20) NOT NULL
);


--
-- Name: TABLE "Municipio"; Type: COMMENT; Schema: Dengue_global; Owner: -
--

COMMENT ON TABLE "Municipio" IS 'Municipio integrado ao sistema de alerta';


SET search_path = "Municipio", pg_catalog;

--
-- Name: Bairro; Type: TABLE; Schema: Municipio; Owner: -; Tablespace:
--

CREATE TABLE "Bairro" (
    nome text NOT NULL,
    bairro_id integer NOT NULL,
    "Localidade_id" integer NOT NULL
);


--
-- Name: TABLE "Bairro"; Type: COMMENT; Schema: Municipio; Owner: -
--

COMMENT ON TABLE "Bairro" IS 'Lista de bairros por localidade';


--
-- Name: Clima_Satelite; Type: TABLE; Schema: Municipio; Owner: -; Tablespace:
--

CREATE TABLE "Clima_Satelite" (
    id bigint NOT NULL,
    data date NOT NULL,
    "Municipio_geocodigo" integer NOT NULL,
    ndvi integer NOT NULL,
    "Localidade_id" integer NOT NULL,
    temperatura_max numeric(4,2) NOT NULL,
    temperaruta_min numeric(4,2) NOT NULL,
    precipitacao integer NOT NULL,
    enso_qual real NOT NULL
);


--
-- Name: TABLE "Clima_Satelite"; Type: COMMENT; Schema: Municipio; Owner: -
--

COMMENT ON TABLE "Clima_Satelite" IS 'Precipitação, temperatura e NVDI
(Normalized Difference Vegetation Index)';


--
-- Name: Clima_Satelite_id_seq; Type: SEQUENCE; Schema: Municipio; Owner: -
--

CREATE SEQUENCE "Clima_Satelite_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: Clima_Satelite_id_seq; Type: SEQUENCE OWNED BY; Schema: Municipio; Owner: -
--

ALTER SEQUENCE "Clima_Satelite_id_seq" OWNED BY "Clima_Satelite".id;


--
-- Name: Clima_cemaden; Type: TABLE; Schema: Municipio; Owner: -; Tablespace:
--

CREATE TABLE "Clima_cemaden" (
    valor real NOT NULL,
    sensor character varying(32) NOT NULL,
    id bigint NOT NULL,
    datahora timestamp without time zone NOT NULL,
    "Estacao_cemaden_codestacao" character varying(10) NOT NULL
);


--
-- Name: TABLE "Clima_cemaden"; Type: COMMENT; Schema: Municipio; Owner: -
--

COMMENT ON TABLE "Clima_cemaden" IS 'dados de clima - CEMADEN';


--
-- Name: Clima_cemaden_id_seq; Type: SEQUENCE; Schema: Municipio; Owner: -
--

CREATE SEQUENCE "Clima_cemaden_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: Clima_cemaden_id_seq; Type: SEQUENCE OWNED BY; Schema: Municipio; Owner: -
--

ALTER SEQUENCE "Clima_cemaden_id_seq" OWNED BY "Clima_cemaden".id;


--
-- Name: Clima_wu; Type: TABLE; Schema: Municipio; Owner: -; Tablespace:
--

CREATE TABLE "Clima_wu" (
    temp_min real,
    temp_max real,
    temp_med real,
    data_dia date NOT NULL,
    umid_min real,
    umid_med real,
    umid_max real,
    pressao_min real,
    pressao_med real,
    pressao_max real,
    "Estacao_wu_estacao_id" character varying(4) NOT NULL,
    id bigint NOT NULL
);


--
-- Name: TABLE "Clima_wu"; Type: COMMENT; Schema: Municipio; Owner: -
--

COMMENT ON TABLE "Clima_wu" IS 'série temporal de variaveis meteorologicas diarias do WU';


--
-- Name: Clima_wu_id_seq; Type: SEQUENCE; Schema: Municipio; Owner: -
--

CREATE SEQUENCE "Clima_wu_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: Clima_wu_id_seq; Type: SEQUENCE OWNED BY; Schema: Municipio; Owner: -
--

ALTER SEQUENCE "Clima_wu_id_seq" OWNED BY "Clima_wu".id;


--
-- Name: Estacao_cemaden; Type: TABLE; Schema: Municipio; Owner: -; Tablespace:
--

CREATE TABLE "Estacao_cemaden" (
    codestacao character varying(10) NOT NULL,
    nome character varying(128) NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    "Localidade_id" integer NOT NULL
);


--
-- Name: TABLE "Estacao_cemaden"; Type: COMMENT; Schema: Municipio; Owner: -
--

COMMENT ON TABLE "Estacao_cemaden" IS 'Metadados da estação do cemaden';


--
-- Name: Estacao_wu; Type: TABLE; Schema: Municipio; Owner: -; Tablespace:
--

CREATE TABLE "Estacao_wu" (
    estacao_id character varying(4) NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    "Localidades_id" integer,
    nome character varying(128) NOT NULL
);


--
-- Name: TABLE "Estacao_wu"; Type: COMMENT; Schema: Municipio; Owner: -
--

COMMENT ON TABLE "Estacao_wu" IS 'metadados das estacoes meteorologicas da WU';


--
-- Name: Historico_alerta; Type: TABLE; Schema: Municipio; Owner: -; Tablespace:
--

CREATE TABLE "Historico_alerta" (
    "data_iniSE" date NOT NULL,
    "SE" integer NOT NULL,
    casos_est real NOT NULL,
    casos_est_min integer NOT NULL,
    casos_est_max integer NOT NULL,
    casos integer NOT NULL,
    municipio_geocodigo integer NOT NULL,
    p_rt1 real NOT NULL,
    p_inc100k real NOT NULL,
    "Localidade_id" integer,
    nivel smallint,
    id bigint NOT NULL,
    versao_modelo character varying(40)
);


--
-- Name: TABLE "Historico_alerta"; Type: COMMENT; Schema: Municipio; Owner: -
--

COMMENT ON TABLE "Historico_alerta" IS 'Resultados  do alerta, conforme publicado.';


--
-- Name: Historico_alerta_id_seq; Type: SEQUENCE; Schema: Municipio; Owner: -
--

CREATE SEQUENCE "Historico_alerta_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: Historico_alerta_id_seq; Type: SEQUENCE OWNED BY; Schema: Municipio; Owner: -
--

ALTER SEQUENCE "Historico_alerta_id_seq" OWNED BY "Historico_alerta".id;


--
-- Name: Localidade; Type: TABLE; Schema: Municipio; Owner: -; Tablespace:
--

CREATE TABLE "Localidade" (
    nome character varying(32) NOT NULL,
    populacao integer NOT NULL,
    geojson text NOT NULL,
    id integer NOT NULL,
    "Municipio_geocodigo" integer NOT NULL
);


--
-- Name: TABLE "Localidade"; Type: COMMENT; Schema: Municipio; Owner: -
--

COMMENT ON TABLE "Localidade" IS 'Sub-unidades de analise no municipio';


--
-- Name: Notificacao; Type: TABLE; Schema: Municipio; Owner: -; Tablespace:
--

CREATE TABLE "Notificacao" (
    id bigint NOT NULL,
    dt_notific date,
    se_notif integer,
    ano_notif integer,
    dt_sin_pri date,
    se_sin_pri integer,
    dt_digita date,
    bairro_nome text,
    bairro_bairro_id integer,
    municipio_geocodigo integer,
    nu_notific integer,
    cid10_codigo character varying(5)
);


--
-- Name: TABLE "Notificacao"; Type: COMMENT; Schema: Municipio; Owner: -
--

COMMENT ON TABLE "Notificacao" IS 'Casos de notificacao de dengue';


--
-- Name: Notificacao_id_seq; Type: SEQUENCE; Schema: Municipio; Owner: -
--

CREATE SEQUENCE "Notificacao_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: Notificacao_id_seq; Type: SEQUENCE OWNED BY; Schema: Municipio; Owner: -
--

ALTER SEQUENCE "Notificacao_id_seq" OWNED BY "Notificacao".id;


--
-- Name: Ovitrampa; Type: TABLE; Schema: Municipio; Owner: -; Tablespace:
--

CREATE TABLE "Ovitrampa" (
    "Municipio_geocodigo" integer NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    "Arm_codigo" integer NOT NULL,
    "Perdida" boolean NOT NULL,
    "Positiva" boolean,
    "Ovos" integer,
    "Localidade_id" integer NOT NULL,
    id integer NOT NULL
);


--
-- Name: Ovitrampa_id_seq; Type: SEQUENCE; Schema: Municipio; Owner: -
--

CREATE SEQUENCE "Ovitrampa_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: Ovitrampa_id_seq; Type: SEQUENCE OWNED BY; Schema: Municipio; Owner: -
--

ALTER SEQUENCE "Ovitrampa_id_seq" OWNED BY "Ovitrampa".id;


--
-- Name: Tweet; Type: TABLE; Schema: Municipio; Owner: -; Tablespace:
--

CREATE TABLE "Tweet" (
    id bigint NOT NULL,
    "Municipio_geocodigo" integer NOT NULL,
    data_dia date NOT NULL,
    numero integer NOT NULL,
    "CID10_codigo" character varying(5) NOT NULL
);


--
-- Name: TABLE "Tweet"; Type: COMMENT; Schema: Municipio; Owner: -
--

COMMENT ON TABLE "Tweet" IS 'Série de tweets diários';


--
-- Name: Tweet_id_seq; Type: SEQUENCE; Schema: Municipio; Owner: -
--

CREATE SEQUENCE "Tweet_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: Tweet_id_seq; Type: SEQUENCE OWNED BY; Schema: Municipio; Owner: -
--

ALTER SEQUENCE "Tweet_id_seq" OWNED BY "Tweet".id;


--
-- Name: id; Type: DEFAULT; Schema: Municipio; Owner: -
--

ALTER TABLE ONLY "Clima_Satelite" ALTER COLUMN id SET DEFAULT nextval('"Clima_Satelite_id_seq"'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: Municipio; Owner: -
--

ALTER TABLE ONLY "Clima_cemaden" ALTER COLUMN id SET DEFAULT nextval('"Clima_cemaden_id_seq"'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: Municipio; Owner: -
--

ALTER TABLE ONLY "Clima_wu" ALTER COLUMN id SET DEFAULT nextval('"Clima_wu_id_seq"'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: Municipio; Owner: -
--

ALTER TABLE ONLY "Historico_alerta" ALTER COLUMN id SET DEFAULT nextval('"Historico_alerta_id_seq"'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: Municipio; Owner: -
--

ALTER TABLE ONLY "Notificacao" ALTER COLUMN id SET DEFAULT nextval('"Notificacao_id_seq"'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: Municipio; Owner: -
--

ALTER TABLE ONLY "Ovitrampa" ALTER COLUMN id SET DEFAULT nextval('"Ovitrampa_id_seq"'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: Municipio; Owner: -
--

ALTER TABLE ONLY "Tweet" ALTER COLUMN id SET DEFAULT nextval('"Tweet_id_seq"'::regclass);


SET search_path = "Dengue_global", pg_catalog;

--
-- Name: CID10_pk; Type: CONSTRAINT; Schema: Dengue_global; Owner: -; Tablespace:
--

ALTER TABLE ONLY "CID10"
    ADD CONSTRAINT "CID10_pk" PRIMARY KEY (codigo);


--
-- Name: Municipio_pk; Type: CONSTRAINT; Schema: Dengue_global; Owner: -; Tablespace:
--

ALTER TABLE ONLY "Municipio"
    ADD CONSTRAINT "Municipio_pk" PRIMARY KEY (geocodigo);


SET search_path = "Municipio", pg_catalog;

--
-- Name: Bairro_pk; Type: CONSTRAINT; Schema: Municipio; Owner: -; Tablespace:
--

ALTER TABLE ONLY "Bairro"
    ADD CONSTRAINT "Bairro_pk" PRIMARY KEY (nome, bairro_id);


--
-- Name: Clima_Satelite_pk; Type: CONSTRAINT; Schema: Municipio; Owner: -; Tablespace:
--

ALTER TABLE ONLY "Clima_Satelite"
    ADD CONSTRAINT "Clima_Satelite_pk" PRIMARY KEY (id);


--
-- Name: Clima_cemaden_pk; Type: CONSTRAINT; Schema: Municipio; Owner: -; Tablespace:
--

ALTER TABLE ONLY "Clima_cemaden"
    ADD CONSTRAINT "Clima_cemaden_pk" PRIMARY KEY (id);


--
-- Name: Clima_wu_pk; Type: CONSTRAINT; Schema: Municipio; Owner: -; Tablespace:
--

ALTER TABLE ONLY "Clima_wu"
    ADD CONSTRAINT "Clima_wu_pk" PRIMARY KEY (id);


--
-- Name: Estacao_cemaden_pk; Type: CONSTRAINT; Schema: Municipio; Owner: -; Tablespace:
--

ALTER TABLE ONLY "Estacao_cemaden"
    ADD CONSTRAINT "Estacao_cemaden_pk" PRIMARY KEY (codestacao);


--
-- Name: Estacao_wu_pk; Type: CONSTRAINT; Schema: Municipio; Owner: -; Tablespace:
--

ALTER TABLE ONLY "Estacao_wu"
    ADD CONSTRAINT "Estacao_wu_pk" PRIMARY KEY (estacao_id);


--
-- Name: Historico_alerta_pk; Type: CONSTRAINT; Schema: Municipio; Owner: -; Tablespace:
--

ALTER TABLE ONLY "Historico_alerta"
    ADD CONSTRAINT "Historico_alerta_pk" PRIMARY KEY (id);


--
-- Name: Localidade_pk; Type: CONSTRAINT; Schema: Municipio; Owner: -; Tablespace:
--

ALTER TABLE ONLY "Localidade"
    ADD CONSTRAINT "Localidade_pk" PRIMARY KEY (id);


--
-- Name: Notificacao_pk; Type: CONSTRAINT; Schema: Municipio; Owner: -; Tablespace:
--

ALTER TABLE ONLY "Notificacao"
    ADD CONSTRAINT "Notificacao_pk" PRIMARY KEY (id);


--
-- Name: Ovitrampa_pk; Type: CONSTRAINT; Schema: Municipio; Owner: -; Tablespace:
--

ALTER TABLE ONLY "Ovitrampa"
    ADD CONSTRAINT "Ovitrampa_pk" PRIMARY KEY (id);


--
-- Name: Tweet_pk; Type: CONSTRAINT; Schema: Municipio; Owner: -; Tablespace:
--

ALTER TABLE ONLY "Tweet"
    ADD CONSTRAINT "Tweet_pk" PRIMARY KEY (id);


SET search_path = "Dengue_global", pg_catalog;

--
-- Name: Municipio_idx_gc; Type: INDEX; Schema: Dengue_global; Owner: -; Tablespace:
--

CREATE INDEX "Municipio_idx_gc" ON "Municipio" USING btree (geocodigo);


--
-- Name: Municipio_idx_n; Type: INDEX; Schema: Dengue_global; Owner: -; Tablespace:
--

CREATE INDEX "Municipio_idx_n" ON "Municipio" USING btree (nome);


SET search_path = "Municipio", pg_catalog;

--
-- Name: Alerta_idx_data; Type: INDEX; Schema: Municipio; Owner: -; Tablespace:
--

CREATE INDEX "Alerta_idx_data" ON "Historico_alerta" USING btree ("data_iniSE" DESC);


--
-- Name: Clima_Satelite_idx_data; Type: INDEX; Schema: Municipio; Owner: -; Tablespace:
--

CREATE INDEX "Clima_Satelite_idx_data" ON "Clima_Satelite" USING btree (id);


--
-- Name: Dengue_idx_data; Type: INDEX; Schema: Municipio; Owner: -; Tablespace:
--

CREATE INDEX "Dengue_idx_data" ON "Notificacao" USING btree (dt_notific DESC, se_notif DESC);


--
-- Name: Tweets_idx_data; Type: INDEX; Schema: Municipio; Owner: -; Tablespace:
--

CREATE INDEX "Tweets_idx_data" ON "Tweet" USING btree (data_dia DESC);


--
-- Name: WU_idx_data; Type: INDEX; Schema: Municipio; Owner: -; Tablespace:
--

CREATE INDEX "WU_idx_data" ON "Clima_wu" USING btree (data_dia DESC);


--
-- Name: chuva_idx_data; Type: INDEX; Schema: Municipio; Owner: -; Tablespace:
--

CREATE INDEX chuva_idx_data ON "Clima_cemaden" USING btree (datahora DESC);


--
-- Name: Bairro_Localidade; Type: FK CONSTRAINT; Schema: Municipio; Owner: -
--

ALTER TABLE ONLY "Bairro"
    ADD CONSTRAINT "Bairro_Localidade" FOREIGN KEY ("Localidade_id") REFERENCES "Localidade"(id);


--
-- Name: Estacao_cemaden_Localidade; Type: FK CONSTRAINT; Schema: Municipio; Owner: -
--

ALTER TABLE ONLY "Estacao_cemaden"
    ADD CONSTRAINT "Estacao_cemaden_Localidade" FOREIGN KEY ("Localidade_id") REFERENCES "Localidade"(id);


--
-- Name: NDVI_Localidade; Type: FK CONSTRAINT; Schema: Municipio; Owner: -
--

ALTER TABLE ONLY "Clima_Satelite"
    ADD CONSTRAINT "NDVI_Localidade" FOREIGN KEY ("Localidade_id") REFERENCES "Localidade"(id);


--
-- Name: Ovitrampa_Localidade; Type: FK CONSTRAINT; Schema: Municipio; Owner: -
--

ALTER TABLE ONLY "Ovitrampa"
    ADD CONSTRAINT "Ovitrampa_Localidade" FOREIGN KEY ("Localidade_id") REFERENCES "Localidade"(id);


--
-- Name: Tweet_CID10; Type: FK CONSTRAINT; Schema: Municipio; Owner: -
--

ALTER TABLE ONLY "Tweet"
    ADD CONSTRAINT "Tweet_CID10" FOREIGN KEY ("CID10_codigo") REFERENCES "Dengue_global"."CID10"(codigo);

--
-- Name: casos_unicos; Type: UNIQUE CONSTRAINT; Schema: Municipio; Owner: -


ALTER TABLE ONLY "Municipio"."Notificacao"
    ADD constraint casos_unicos UNIQUE(nu_notific, bairro_nome, dt_digita,municipio_geocodigo);

--
-- PostgreSQL database dump complete
--

