-- Created by Vertabelo (http://vertabelo.com)
-- Last modification date: 2015-08-18 21:01:51.574




-- tables
-- Table: "Bairro"
CREATE TABLE "Bairro" (
    "nome" text  NOT NULL,
    "bairro_id" int  NOT NULL,
    "Localidade_id" int  NOT NULL,
    CONSTRAINT "Bairro_pk" PRIMARY KEY ("nome","bairro_id")
);


COMMENT ON TABLE "Bairro" IS 'Lista de bairros por localidade';


-- Table: "CID10"
CREATE TABLE "CID10" (
    "nome" varchar(128)  NOT NULL,
    "codigo" varchar(5)  NOT NULL,
    CONSTRAINT "CID10_pk" PRIMARY KEY ("codigo")
);



-- Table: "Clima_Satelite"
CREATE TABLE "Clima_Satelite" (
    "id" int  NOT NULL,
    "data" date  NOT NULL,
    "Municipio_geocodigo" int  NOT NULL,
    "ndvi" int  NOT NULL,
    "Localidade_id" int  NOT NULL,
    "temperatura_max" decimal(4,2)  NOT NULL,
    "temperaruta_min" decimal(4,2)  NOT NULL,
    "precipitacao" int  NOT NULL,
    "enso_qual" real  NOT NULL,
    CONSTRAINT "Clima_Satelite_pk" PRIMARY KEY ("id")
);

CREATE INDEX "Clima_Satelite_idx_data" on "Clima_Satelite" ("id" ASC);



COMMENT ON TABLE "Clima_Satelite" IS 'Precipitação, temperatura e NVDI
(Normalized Difference Vegetation Index)';


-- Table: "Clima_cemaden"
CREATE TABLE "Clima_cemaden" (
    "chuva" real  NOT NULL,
    "intensidade_precip" real  NOT NULL,
    "id" int  NOT NULL,
    "datahora" timestamp  NOT NULL,
    "Estacao_cemaden_codestacao" varchar(10)  NOT NULL,
    CONSTRAINT "Clima_cemaden_pk" PRIMARY KEY ("id")
);


COMMENT ON TABLE "Clima_cemaden" IS 'dados de clima - CEMADEN';


-- Table: "Clima_wu"
CREATE TABLE "Clima_wu" (
    "temp_minima" real  NOT NULL,
    "temp_maxima" real  NOT NULL,
    "temp_media" real  NOT NULL,
    "data_dia" date  NOT NULL,
    "umid_min" real  NOT NULL,
    "umid_med" real  NOT NULL,
    "umid_max" real  NOT NULL,
    "pressao_min" real  NOT NULL,
    "pressao_med" real  NOT NULL,
    "pressao_max" real  NOT NULL,
    "Estacao_wu_estacao_id" varchar(4)  NOT NULL,
    "id" int  NOT NULL,
    CONSTRAINT "Clima_wu_pk" PRIMARY KEY ("id")
);

CREATE INDEX "Temperatura_idx_data" on "Clima_wu" ("data_dia" DESC);



COMMENT ON TABLE "Clima_wu" IS 'série temporal de variaveis meteorologicas diarias do WU';


-- Table: "Estacao_cemaden"
CREATE TABLE "Estacao_cemaden" (
    "codestacao" varchar(10)  NOT NULL,
    "nome" varchar(128)  NOT NULL,
    "latitude" real  NOT NULL,
    "longitude" real  NOT NULL,
    "Localidade_id" int  NOT NULL,
    CONSTRAINT "Estacao_cemaden_pk" PRIMARY KEY ("codestacao")
);


COMMENT ON TABLE "Estacao_cemaden" IS 'Metadados da estação do cemaden';


-- Table: "Estacao_wu"
CREATE TABLE "Estacao_wu" (
    "estacao_id" varchar(4)  NOT NULL,
    "latitude" real  NOT NULL,
    "longitude" real  NOT NULL,
    "Localidades_id" int  NOT NULL,
    "nome" varchar(128)  NOT NULL,
    CONSTRAINT "Estacao_wu_pk" PRIMARY KEY ("estacao_id")
);


COMMENT ON TABLE "Estacao_wu" IS 'metadados das estacoes meteorologicas da WU';


-- Table: "Historico_alerta"
CREATE TABLE "Historico_alerta" (
    "data_iniSE" date  NOT NULL,
    "SE" int  NOT NULL,
    "casos_est" int  NOT NULL,
    "Localidade_id" int  NOT NULL,
    "nivel" smallint  NOT NULL,
    "id" int  NOT NULL,
    "versao_modelo" varchar(40)  NOT NULL,
    CONSTRAINT "Historico_alerta_pk" PRIMARY KEY ("id")
);

CREATE INDEX "Alerta_idx_data" on "Historico_alerta" ("data_iniSE" DESC);



COMMENT ON TABLE "Historico_alerta" IS 'Resultados  do alerta, conforme publicado.';


-- Table: "Localidade"
CREATE TABLE "Localidade" (
    "nome" varchar(32)  NOT NULL,
    "populacao" int  NOT NULL,
    "geojson" text  NOT NULL,
    "id" int  NOT NULL,
    "Municipio_geocodigo" int  NOT NULL,
    CONSTRAINT "Localidade_pk" PRIMARY KEY ("id")
);


COMMENT ON TABLE "Localidade" IS 'Sub-unidades de analise no municipio';


-- Table: "Municipio"
CREATE TABLE "Municipio" (
    "geocodigo" int  NOT NULL,
    "nome" varchar(128)  NOT NULL,
    "geojson" text  NOT NULL,
    "populacao" bigint  NOT NULL,
    "uf" varchar(2)  NOT NULL,
    CONSTRAINT "Municipio_pk" PRIMARY KEY ("geocodigo")
);

CREATE INDEX "Municipio_idx_gc" on "Municipio" ("geocodigo" ASC);


CREATE INDEX "Municipio_idx_n" on "Municipio" ("nome" ASC);



COMMENT ON TABLE "Municipio" IS 'Municipio integrado ao sistema de alerta';


-- Table: "Notificacao"
CREATE TABLE "Notificacao" (
    "dt_notific" date  NOT NULL,
    "SE_notif" int  NOT NULL,
    "ano_notif" int  NOT NULL,
    "dt_sin_pri" date  NOT NULL,
    "SE_sin_pri" date  NOT NULL,
    "dt_digita" date  NOT NULL,
    "Bairro_nome" text  NOT NULL,
    "Bairro_bairro_id" int  NOT NULL,
    "nu_notific" int  NOT NULL,
    "CID10_codigo" varchar(5)  NOT NULL,
    CONSTRAINT "Notificacao_pk" PRIMARY KEY ("nu_notific")
);

CREATE INDEX "Dengue_idx_data" on "Notificacao" ("dt_notific" DESC,"SE_notif" DESC);



COMMENT ON TABLE "Notificacao" IS 'Casos de notificacao de dengue';


-- Table: "Ovitrampa"
CREATE TABLE "Ovitrampa" (
    "Municipio_geocodigo" int  NOT NULL,
    "latitude" real  NOT NULL,
    "longitude" real  NOT NULL,
    "Arm_codigo" int  NOT NULL,
    "Perdida" boolean  NOT NULL,
    "Positiva" boolean  NOT NULL,
    "Ovos" int  NOT NULL,
    "Localidade_id" int  NOT NULL,
    "id" int  NOT NULL,
    CONSTRAINT "Ovitrampa_pk" PRIMARY KEY ("id")
);



-- Table: "Tweet"
CREATE TABLE "Tweet" (
    "Municipio_geocodigo" int  NOT NULL,
    "data_dia" date  NOT NULL,
    "numero" int  NOT NULL,
    "CID10_codigo" varchar(5)  NOT NULL,
    CONSTRAINT "Tweet_pk" PRIMARY KEY ("Municipio_geocodigo")
);

CREATE INDEX "Tweets_idx_data" on "Tweet" ("data_dia" DESC);



COMMENT ON TABLE "Tweet" IS 'Série de tweets diários';






-- foreign keys
-- Reference:  "Alerta_Localidade" (table: "Historico_alerta")


ALTER TABLE "Historico_alerta" ADD CONSTRAINT "Alerta_Localidade" 
    FOREIGN KEY ("Localidade_id")
    REFERENCES "Localidade" ("id")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Bairro_Localidade" (table: "Bairro")


ALTER TABLE "Bairro" ADD CONSTRAINT "Bairro_Localidade" 
    FOREIGN KEY ("Localidade_id")
    REFERENCES "Localidade" ("id")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Clima_cemaden_Estacao_cemaden" (table: "Clima_cemaden")


ALTER TABLE "Clima_cemaden" ADD CONSTRAINT "Clima_cemaden_Estacao_cemaden" 
    FOREIGN KEY ("Estacao_cemaden_codestacao")
    REFERENCES "Estacao_cemaden" ("codestacao")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Clima_wu_Estacao_wu" (table: "Clima_wu")


ALTER TABLE "Clima_wu" ADD CONSTRAINT "Clima_wu_Estacao_wu" 
    FOREIGN KEY ("Estacao_wu_estacao_id")
    REFERENCES "Estacao_wu" ("estacao_id")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Dengue_Bairro" (table: "Notificacao")


ALTER TABLE "Notificacao" ADD CONSTRAINT "Dengue_Bairro" 
    FOREIGN KEY ("Bairro_nome","Bairro_bairro_id")
    REFERENCES "Bairro" ("nome","bairro_id")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Dengue_CID10" (table: "Notificacao")


ALTER TABLE "Notificacao" ADD CONSTRAINT "Dengue_CID10" 
    FOREIGN KEY ("CID10_codigo")
    REFERENCES "CID10" ("codigo")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Estacao_cemaden_Localidade" (table: "Estacao_cemaden")


ALTER TABLE "Estacao_cemaden" ADD CONSTRAINT "Estacao_cemaden_Localidade" 
    FOREIGN KEY ("Localidade_id")
    REFERENCES "Localidade" ("id")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Estacao_wu_Localidades" (table: "Estacao_wu")


ALTER TABLE "Estacao_wu" ADD CONSTRAINT "Estacao_wu_Localidades" 
    FOREIGN KEY ("Localidades_id")
    REFERENCES "Localidade" ("id")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Localidades_Municipio" (table: "Localidade")


ALTER TABLE "Localidade" ADD CONSTRAINT "Localidades_Municipio" 
    FOREIGN KEY ("Municipio_geocodigo")
    REFERENCES "Municipio" ("geocodigo")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "NDVI_Localidade" (table: "Clima_Satelite")


ALTER TABLE "Clima_Satelite" ADD CONSTRAINT "NDVI_Localidade" 
    FOREIGN KEY ("Localidade_id")
    REFERENCES "Localidade" ("id")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Ovitrampa_Localidade" (table: "Ovitrampa")


ALTER TABLE "Ovitrampa" ADD CONSTRAINT "Ovitrampa_Localidade" 
    FOREIGN KEY ("Localidade_id")
    REFERENCES "Localidade" ("id")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Tweet_CID10" (table: "Tweet")


ALTER TABLE "Tweet" ADD CONSTRAINT "Tweet_CID10" 
    FOREIGN KEY ("CID10_codigo")
    REFERENCES "CID10" ("codigo")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Tweets_Municipio" (table: "Tweet")


ALTER TABLE "Tweet" ADD CONSTRAINT "Tweets_Municipio" 
    FOREIGN KEY ("Municipio_geocodigo")
    REFERENCES "Municipio" ("geocodigo")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;






-- End of file.

