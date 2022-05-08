CREATE DATABASE IF NOT EXISTS welcomp_apps;

USE welcomp_apps;

CREATE TABLE IF NOT EXISTS facture
(
  id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  facture_number VARCHAR(255)   NOT NULL,
  due_date       VARCHAR(255)   NOT NULL,
  sold           VARCHAR(255)   NOT NULL,
  paid_status    VARCHAR(255),
  iban           VARCHAR(255)   NOT NULL,
  created_at     DATETIME,
  modified_at    DATETIME
);