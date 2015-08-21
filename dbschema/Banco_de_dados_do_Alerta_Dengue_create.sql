-- Last modification date: 2015-08-18 21:01:51.574




-- tables
-- Table: "Municipio"."Bairro"
CREATE TABLE "Municipio"."Bairro" (
    "nome" text  NOT NULL,
    "bairro_id" int  NOT NULL,
    "Localidade_id" int  NOT NULL,
    CONSTRAINT "Bairro_pk" PRIMARY KEY ("nome","bairro_id")
);


COMMENT ON TABLE "Municipio"."Bairro" IS 'Lista de bairros por localidade';


-- Table: "CID10"
CREATE TABLE "Dengue_global"."CID10" (
    "nome" varchar(128)  NOT NULL,
    "codigo" varchar(5)  NOT NULL,
    CONSTRAINT "CID10_pk" PRIMARY KEY ("codigo")
);



-- Table: "Municipio"."Clima_Satelite"
CREATE TABLE "Municipio"."Clima_Satelite" (
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

CREATE INDEX "Clima_Satelite_idx_data" on "Municipio"."Clima_Satelite" ("id" ASC);



COMMENT ON TABLE "Municipio"."Clima_Satelite" IS 'Precipitação, temperatura e NVDI
(Normalized Difference Vegetation Index)';


-- Table: "Municipio"."Clima_cemaden"
CREATE TABLE "Municipio"."Clima_cemaden" (
    "chuva" real  NOT NULL,
    "intensidade_precip" real  NOT NULL,
    "id" int  NOT NULL,
    "datahora" timestamp  NOT NULL,
    "Estacao_cemaden_codestacao" varchar(10)  NOT NULL,
    CONSTRAINT "Clima_cemaden_pk" PRIMARY KEY ("id")
);


COMMENT ON TABLE "Municipio"."Clima_cemaden" IS 'dados de clima - CEMADEN';


-- Table: "Municipio"."Clima_wu"
CREATE TABLE "Municipio"."Clima_wu" (
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

CREATE INDEX "Temperatura_idx_data" on "Municipio"."Clima_wu" ("data_dia" DESC);



COMMENT ON TABLE "Municipio"."Clima_wu" IS 'série temporal de variaveis meteorologicas diarias do WU';


-- Table: "Estacao_cemaden"
CREATE TABLE "Municipio"."Estacao_cemaden" (
    "codestacao" varchar(10)  NOT NULL,
    "nome" varchar(128)  NOT NULL,
    "latitude" real  NOT NULL,
    "longitude" real  NOT NULL,
    "Localidade_id" int  NOT NULL,
    CONSTRAINT "Estacao_cemaden_pk" PRIMARY KEY ("codestacao")
);


COMMENT ON TABLE "Municipio"."Estacao_cemaden" IS 'Metadados da estação do cemaden';


-- Table: "Municipio"."Estacao_wu"
CREATE TABLE "Municipio"."Estacao_wu" (
    "estacao_id" varchar(4)  NOT NULL,
    "latitude" real  NOT NULL,
    "longitude" real  NOT NULL,
    "Localidades_id" int  NOT NULL,
    "nome" varchar(128)  NOT NULL,
    CONSTRAINT "Estacao_wu_pk" PRIMARY KEY ("estacao_id")
);


COMMENT ON TABLE "Municipio"."Estacao_wu" IS 'metadados das estacoes meteorologicas da WU';


-- Table: "Municipio"."Historico_alerta"
CREATE TABLE "Municipio"."Historico_alerta" (
    "data_iniSE" date  NOT NULL,
    "SE" int  NOT NULL,
    "casos_est" int  NOT NULL,
    "Localidade_id" int  NOT NULL,
    "nivel" smallint  NOT NULL,
    "id" int  NOT NULL,
    "versao_modelo" varchar(40)  NOT NULL,
    CONSTRAINT "Historico_alerta_pk" PRIMARY KEY ("id")
);

CREATE INDEX "Alerta_idx_data" on "Municipio"."Historico_alerta" ("data_iniSE" DESC);



COMMENT ON TABLE "Municipio"."Historico_alerta" IS 'Resultados  do alerta, conforme publicado.';


-- Table: "Municipio"."Localidade"
CREATE TABLE "Municipio"."Localidade" (
    "nome" varchar(32)  NOT NULL,
    "populacao" int  NOT NULL,
    "geojson" text  NOT NULL,
    "id" int  NOT NULL,
    "Municipio_geocodigo" int  NOT NULL,
    CONSTRAINT "Localidade_pk" PRIMARY KEY ("id")
);


COMMENT ON TABLE "Municipio"."Localidade" IS 'Sub-unidades de analise no municipio';


-- Table: "Dengue_global"."Municipio"
CREATE TABLE "Dengue_global"."Municipio" (
    "geocodigo" int  NOT NULL,
    "nome" varchar(128)  NOT NULL,
    "geojson" text  NOT NULL,
    "populacao" bigint  NOT NULL,
    "uf" varchar(2)  NOT NULL,
    CONSTRAINT "Municipio_pk" PRIMARY KEY ("geocodigo")
);

CREATE INDEX "Municipio_idx_gc" on "Dengue_global"."Municipio" ("geocodigo" ASC);


CREATE INDEX "Municipio_idx_n" on "Dengue_global"."Municipio" ("nome" ASC);



COMMENT ON TABLE "Dengue_global"."Municipio" IS 'Municipio integrado ao sistema de alerta';


-- Table: "Municipio"."Notificacao"
CREATE TABLE "Municipio"."Notificacao" (
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

CREATE INDEX "Dengue_idx_data" on "Municipio"."Notificacao" ("dt_notific" DESC,"SE_notif" DESC);



COMMENT ON TABLE "Municipio"."Notificacao" IS 'Casos de notificacao de dengue';


-- Table: "Municipio"."Ovitrampa"
CREATE TABLE "Municipio"."Ovitrampa" (
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



-- Table: "Municipio"."Tweet"
CREATE TABLE "Municipio"."Tweet" (
    "Municipio_geocodigo" int  NOT NULL,
    "data_dia" date  NOT NULL,
    "numero" int  NOT NULL,
    "CID10_codigo" varchar(5)  NOT NULL,
    CONSTRAINT "Tweet_pk" PRIMARY KEY ("Municipio_geocodigo")
);

CREATE INDEX "Tweets_idx_data" on "Municipio"."Tweet" ("data_dia" DESC);



COMMENT ON TABLE "Municipio"."Tweet" IS 'Série de tweets diários';






-- foreign keys
-- Reference:  "Alerta_Localidade" (table: ""Municipio"."Historico_alerta")


ALTER TABLE "Municipio"."Historico_alerta" ADD CONSTRAINT "Alerta_Localidade"
    FOREIGN KEY ("Localidade_id")
    REFERENCES "Municipio"."Localidade" ("id")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Bairro_Localidade" (table: "Municipio"."Bairro")


ALTER TABLE "Municipio"."Bairro" ADD CONSTRAINT "Bairro_Localidade"
    FOREIGN KEY ("Localidade_id")
    REFERENCES "Municipio"."Localidade" ("id")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Clima_cemaden_Estacao_cemaden" (table: "Municipio"."Clima_cemaden")


ALTER TABLE "Municipio"."Clima_cemaden" ADD CONSTRAINT "Clima_cemaden_Estacao_cemaden"
    FOREIGN KEY ("Estacao_cemaden_codestacao")
    REFERENCES "Municipio"."Estacao_cemaden" ("codestacao")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Clima_wu_Estacao_wu" (table: "Municipio"."Clima_wu")


ALTER TABLE "Municipio"."Clima_wu" ADD CONSTRAINT "Clima_wu_Estacao_wu"
    FOREIGN KEY ("Estacao_wu_estacao_id")
    REFERENCES "Municipio"."Estacao_wu" ("estacao_id")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Dengue_Bairro" (table: "Municipio"."Notificacao")


ALTER TABLE "Municipio"."Notificacao" ADD CONSTRAINT "Dengue_Bairro" 
    FOREIGN KEY ("Bairro_nome","Bairro_bairro_id")
    REFERENCES "Municipio"."Bairro" ("nome","bairro_id")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Dengue_CID10" (table: "Municipio"."Notificacao")


ALTER TABLE "Municipio"."Notificacao" ADD CONSTRAINT "Dengue_CID10" 
    FOREIGN KEY ("CID10_codigo")
    REFERENCES "Dengue_global"."CID10" ("codigo")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Estacao_cemaden_Localidade" (table: "Estacao_cemaden")


ALTER TABLE "Municipio"."Estacao_cemaden" ADD CONSTRAINT "Estacao_cemaden_Localidade"
    FOREIGN KEY ("Localidade_id")
    REFERENCES "Municipio"."Localidade" ("id")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Estacao_wu_Localidades" (table: "Municipio"."Estacao_wu")


ALTER TABLE "Municipio"."Estacao_wu" ADD CONSTRAINT "Estacao_wu_Localidades"
    FOREIGN KEY ("Localidades_id")
    REFERENCES "Municipio"."Localidade" ("id")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Localidades_Municipio" (table: "Municipio"."Localidade")


ALTER TABLE "Municipio"."Localidade" ADD CONSTRAINT "Localidades_Municipio"
    FOREIGN KEY ("Municipio_geocodigo")
    REFERENCES "Dengue_global"."Municipio" ("geocodigo")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "NDVI_Localidade" (table: "Municipio"."Clima_Satelite")


ALTER TABLE "Municipio"."Clima_Satelite" ADD CONSTRAINT "NDVI_Localidade"
    FOREIGN KEY ("Localidade_id")
    REFERENCES "Municipio"."Localidade" ("id")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Ovitrampa_Localidade" (table: "Municipio"."Ovitrampa")


ALTER TABLE "Municipio"."Ovitrampa" ADD CONSTRAINT "Ovitrampa_Localidade" 
    FOREIGN KEY ("Localidade_id")
    REFERENCES "Municipio"."Localidade" ("id")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Tweet_CID10" (table: "Municipio"."Tweet")


ALTER TABLE "Municipio"."Tweet" ADD CONSTRAINT "Tweet_CID10" 
    FOREIGN KEY ("CID10_codigo")
    REFERENCES "Dengue_global"."CID10" ("codigo")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;

-- Reference:  "Tweets_Municipio" (table: "Municipio"."Tweet")


ALTER TABLE "Municipio"."Tweet" ADD CONSTRAINT "Tweets_Municipio" 
    FOREIGN KEY ("Municipio_geocodigo")
    REFERENCES "Dengue_global"."Municipio" ("geocodigo")
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE 
;






-- End of file.

